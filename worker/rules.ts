/**
 * User-defined alert rules (v11).
 *
 * - CRUD for rules created on the Alerts screen.
 * - evaluateRulesForDomain: called from the monitoring cron after each
 *   successful scan. Fires user rules whose threshold conditions match,
 *   creates an inbox alert, and emails the account address when the
 *   Email channel is selected. Anti-spam: each rule fires at most once
 *   per 24 hours.
 * - sendDigests: the daily digest email (first cron run of the UTC day),
 *   per-user summary of domain scores and open alerts.
 *
 * Metrics not yet monitored (expiry, ai_crawler) are stored and simply
 * never fire until their monitors ship.
 */

import type { Env } from './index';
import { getUserBySession } from './auth';
import { emailAlert } from './monitor';
import type { ScanResult } from './scan';

function json(data: unknown, status = 200): Response {
  return Response.json(data, { status });
}

function sameOrigin(request: Request): boolean {
  const origin = request.headers.get('Origin');
  if (!origin) return true;
  try {
    return new URL(origin).host === new URL(request.url).host;
  } catch {
    return false;
  }
}

export interface RuleRow {
  id: number;
  user_id: number;
  name: string;
  domain_id: number | null;
  metric: string;
  condition: string;
  value: string;
  channels: string;
  enabled: number;
  last_fired_at: string | null;
}

const METRICS = ['dmarc_pass_rate', 'dns_change', 'new_sender', 'spf_lookups', 'expiry', 'ai_crawler'];
const CONDITIONS = ['is below', 'is above', 'happens', 'appears', 'is within (days)'];
const CHANNELS = ['email', 'slack', 'teams', 'webhook'];
const METRIC_LABELS: Record<string, string> = {
  dmarc_pass_rate: 'DMARC pass rate',
  dns_change: 'DNS records changed',
  new_sender: 'New sender detected',
  spf_lookups: 'SPF lookup count',
};

function cleanChannels(raw: unknown): string | null {
  if (!Array.isArray(raw)) return null;
  const list = [...new Set(raw.filter((c) => CHANNELS.includes(c as string)))];
  return list.length ? JSON.stringify(list) : null;
}

interface MailEnv {
  DB: D1Database;
  RESEND_API_KEY?: string;
  SEND_EMAIL?: { send(message: unknown): Promise<void> };
}

// ---------------- CRUD ----------------

export async function handleRulesList(request: Request, env: MailEnv): Promise<Response> {
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);
  const rows = await env.DB
    .prepare(
      `SELECT r.id, r.name, r.domain_id, r.metric, r.condition, r.value, r.channels, r.enabled, r.last_fired_at, d.domain AS domain_name
         FROM alert_rules r LEFT JOIN domains d ON d.id = r.domain_id
        WHERE r.user_id = ?1 ORDER BY r.id DESC`,
    )
    .bind(user.id)
    .all<{ id: number; name: string; domain_id: number | null; metric: string; condition: string; value: string; channels: string; enabled: number; last_fired_at: string | null; domain_name: string | null }>();
  return json({
    ok: true,
    rules: (rows.results ?? []).map((r) => ({
      ...r,
      channels: JSON.parse(r.channels || '[]') as string[],
      enabled: Boolean(r.enabled),
    })),
  });
}

export async function handleRulesCreate(request: Request, env: MailEnv): Promise<Response> {
  if (request.method !== 'POST') return json({ ok: false, error: 'POST only.' }, 405);
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);
  let body: { name?: unknown; metric?: unknown; condition?: unknown; value?: unknown; domainId?: unknown; channels?: unknown };
  try {
    body = await request.json() as typeof body;
  } catch {
    return json({ ok: false, error: 'Invalid JSON body.' }, 400);
  }
  const metric = typeof body.metric === 'string' && METRICS.includes(body.metric) ? body.metric : null;
  const condition = typeof body.condition === 'string' && CONDITIONS.includes(body.condition) ? body.condition : null;
  if (!metric || !condition) return json({ ok: false, error: 'Unknown metric or condition.' }, 400);
  const name = typeof body.name === 'string' && body.name.trim() ? body.name.trim().slice(0, 120) : METRIC_LABELS[metric] || metric;
  const value = body.value == null ? '' : String(body.value).slice(0, 40);
  const channels = cleanChannels(body.channels);
  if (!channels) return json({ ok: false, error: 'Pick at least one channel.' }, 400);
  let domainId: number | null = null;
  if (typeof body.domainId === 'number' && Number.isInteger(body.domainId)) {
    const owned = await env.DB.prepare('SELECT id FROM domains WHERE id = ?1 AND user_id = ?2').bind(body.domainId, user.id).first<{ id: number }>();
    if (!owned) return json({ ok: false, error: 'Domain not found on your list.' }, 404);
    domainId = owned.id;
  }
  const ins = await env.DB
    .prepare("INSERT INTO alert_rules (user_id, name, domain_id, metric, condition, value, channels) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)")
    .bind(user.id, name, domainId, metric, condition, value, channels)
    .run();
  return json({ ok: true, id: ins.meta.last_row_id });
}

export async function handleRulesUpdate(request: Request, env: MailEnv): Promise<Response> {
  if (request.method !== 'POST') return json({ ok: false, error: 'POST only.' }, 405);
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);
  let body: { id?: unknown; name?: unknown; metric?: unknown; condition?: unknown; value?: unknown; domainId?: unknown; channels?: unknown; enabled?: unknown };
  try {
    body = await request.json() as typeof body;
  } catch {
    return json({ ok: false, error: 'Invalid JSON body.' }, 400);
  }
  const id = typeof body.id === 'number' && Number.isInteger(body.id) ? body.id : null;
  if (id === null) return json({ ok: false, error: 'Missing rule id.' }, 400);
  const owned = await env.DB
    .prepare('SELECT id FROM alert_rules WHERE id = ?1 AND user_id = ?2')
    .bind(id, user.id)
    .first<{ id: number }>();
  if (!owned) return json({ ok: false, error: 'Rule not found.' }, 404);

  const sets: string[] = [];
  const vals: unknown[] = [];
  if (typeof body.name === 'string') { sets.push('name = ?'); vals.push(body.name.trim().slice(0, 120)); }
  if (typeof body.metric === 'string' && METRICS.includes(body.metric)) { sets.push('metric = ?'); vals.push(body.metric); }
  if (typeof body.condition === 'string' && CONDITIONS.includes(body.condition)) { sets.push('condition = ?'); vals.push(body.condition); }
  if (body.value !== undefined && typeof body.value === 'string') { sets.push('value = ?'); vals.push(body.value.slice(0, 40)); }
  if (body.domainId === null) { sets.push('domain_id = NULL'); }
  else if (typeof body.domainId === 'number' && Number.isInteger(body.domainId)) {
    const dom = await env.DB.prepare('SELECT id FROM domains WHERE id = ?1 AND user_id = ?2').bind(body.domainId, user.id).first<{ id: number }>();
    if (!dom) return json({ ok: false, error: 'Domain not found on your list.' }, 404);
    sets.push('domain_id = ?'); vals.push(dom.id);
  }
  if (body.channels !== undefined) {
    const ch = cleanChannels(body.channels);
    if (!ch) return json({ ok: false, error: 'Pick at least one channel.' }, 400);
    sets.push('channels = ?'); vals.push(ch);
  }
  if (typeof body.enabled === 'boolean') { sets.push('enabled = ?'); vals.push(body.enabled ? 1 : 0); }
  if (!sets.length) return json({ ok: false, error: 'Nothing to update.' }, 400);
  vals.push(id, user.id);
  await env.DB.prepare(`UPDATE alert_rules SET ${sets.join(', ')} WHERE id = ? AND user_id = ?`).bind(...vals).run();
  return json({ ok: true });
}

export async function handleRulesDelete(request: Request, env: MailEnv): Promise<Response> {
  if (request.method !== 'POST') return json({ ok: false, error: 'POST only.' }, 405);
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);
  const id = await (async () => {
    const raw = new URL(request.url).searchParams.get('id');
    const n = raw ? Number.parseInt(raw, 10) : Number.NaN;
    return Number.isInteger(n) ? n : null;
  })();
  if (id === null) return json({ ok: false, error: 'Missing rule id.' }, 400);
  await env.DB.prepare('DELETE FROM alert_rules WHERE id = ?1 AND user_id = ?2').bind(id, user.id).run();
  return json({ ok: true });
}

export async function handleDigestSetting(request: Request, env: MailEnv): Promise<Response> {
  if (request.method !== 'POST') return json({ ok: false, error: 'POST only.' }, 405);
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);
  let body: { enabled?: unknown };
  try {
    body = await request.json() as typeof body;
  } catch {
    return json({ ok: false, error: 'Invalid JSON body.' }, 400);
  }
  if (typeof body.enabled !== 'boolean') return json({ ok: false, error: 'enabled (boolean) required.' }, 400);
  await env.DB.prepare('UPDATE users SET digest_enabled = ?2 WHERE id = ?1').bind(user.id, body.enabled ? 1 : 0).run();
  return json({ ok: true, enabled: body.enabled });
}

// ---------------- evaluation (cron) ----------------

async function dmarcPassRate(db: D1Database, domainId: number): Promise<number | null> {
  const row = await db
    .prepare(
      `SELECT COALESCE(SUM(s.count), 0) AS total,
              COALESCE(SUM(CASE WHEN s.dmarc_result = 'pass' THEN s.count ELSE 0 END), 0) AS passing
         FROM dmarc_sources s JOIN dmarc_reports r ON r.id = s.report_ref
        WHERE r.domain_id = ?1`,
    )
    .bind(domainId)
    .first<{ total: number; passing: number }>();
  if (!row || !row.total) return null;
  return Math.round((row.passing / row.total) * 100);
}

async function newSenders(db: D1Database, domainId: number): Promise<string[]> {
  const latest = await db.prepare('SELECT MAX(id) AS m FROM dmarc_reports WHERE domain_id = ?1').bind(domainId).first<{ m: number | null }>();
  if (!latest || latest.m === null) return [];
  const older = await db
    .prepare('SELECT DISTINCT s.source_ip AS ip FROM dmarc_sources s JOIN dmarc_reports r ON r.id = s.report_ref WHERE r.domain_id = ?1 AND r.id < ?2')
    .bind(domainId, latest.m)
    .all<{ ip: string }>();
  const olderSet = new Set((older.results ?? []).map((r) => r.ip));
  const current = await db
    .prepare('SELECT DISTINCT s.source_ip AS ip FROM dmarc_sources s JOIN dmarc_reports r ON r.id = s.report_ref WHERE r.id = ?1')
    .bind(latest.m)
    .all<{ ip: string }>();
  return (current.results ?? []).map((r) => r.ip).filter((ip) => !olderSet.has(ip));
}

function within24h(ts: string | null): boolean {
  if (!ts) return false;
  return Date.now() - new Date(ts + 'Z').getTime() < 24 * 3600 * 1000;
}

export async function evaluateRulesForDomain(env: MailEnv,
  d: { id: number; user_id: number; domain: string },
  scan: ScanResult,
  diff: string[],
  changed: boolean,
): Promise<void> {
  const db = env.DB;
  const rules = await db
    .prepare('SELECT id, name, metric, condition, value, channels, last_fired_at FROM alert_rules WHERE user_id = ?1 AND enabled = 1 AND (domain_id IS NULL OR domain_id = ?2)')
    .bind(d.user_id, d.id)
    .all<RuleRow>();
  for (const rule of rules.results ?? []) {
    try {
      if (within24h(rule.last_fired_at)) continue;
      let fire = false;
      let title = '';
      let detail = '';
      if (rule.metric === 'dmarc_pass_rate') {
        const rate = await dmarcPassRate(db, d.id);
        const v = Number(rule.value);
        if (rate === null || !Number.isFinite(v)) continue;
        if (rule.condition === 'is below' && rate < v) fire = true;
        if (rule.condition === 'is above' && rate > v) fire = true;
        if (fire) {
          title = `DMARC pass rate is ${rate}% on ${d.domain}`;
          detail = `Rule "${rule.name || METRIC_LABELS[rule.metric]}": pass rate ${rule.condition} ${v}%. Currently ${rate}% based on received aggregate reports.`;
        }
      } else if (rule.metric === 'spf_lookups') {
        const spf = scan.checks.find((c) => c.id === 'spf');
        const m = (spf?.value || '').match(/^(\d+)\/10/);
        if (!m) continue;
        const n = Number(m[1]);
        const v = Number(rule.value);
        if (!Number.isFinite(v)) continue;
        if (rule.condition === 'is above' && n > v) fire = true;
        if (rule.condition === 'is below' && n < v) fire = true;
        if (fire) {
          title = `SPF lookup count is ${n} of 10 on ${d.domain}`;
          detail = `Rule "${rule.name || 'SPF lookups'}": lookup count ${rule.condition} ${v}. Currently ${n} of the 10 DNS lookup limit.`;
        }
      } else if (rule.metric === 'dns_change') {
        if (rule.condition === 'happens' && changed && diff.length) {
          fire = true;
          title = `DNS records changed on ${d.domain}`;
          detail = `Rule "${rule.name || 'DNS records changed'}": ${diff.join('; ')}`.slice(0, 480);
        }
      } else if (rule.metric === 'new_sender') {
        if (rule.condition === 'appears') {
          const fresh = await newSenders(db, d.id);
          if (fresh.length) {
            fire = true;
            title = `New sender detected on ${d.domain}`;
            detail = `Rule "${rule.name || 'New sender detected'}": ${fresh.join(', ')}`;
          }
        }
      }
      // expiry and ai_crawler: stored, fire when their monitors ship.
      if (!fire) continue;
      const channels = JSON.parse(rule.channels || '[]') as string[];
      await db
        .prepare("INSERT INTO alerts (user_id, domain_id, severity, title, detail) VALUES (?1, ?2, 'warning', ?3, ?4)")
        .bind(d.user_id, d.id, title, detail)
        .run();
      await db.prepare("UPDATE alert_rules SET last_fired_at = datetime('now') WHERE id = ?1").bind(rule.id).run();
      if (channels.includes('email')) await emailAlert(env, d.user_id, d.domain, title, detail);
    } catch {
      // one broken rule must not stop the rest of the evaluation
    }
  }
}



// ---------------- daily digest ----------------

export async function sendDigests(env: MailEnv): Promise<number> {
  const users = await env.DB
    .prepare(
      `SELECT id, email FROM users
        WHERE digest_enabled = 1 AND (last_digest_at IS NULL OR last_digest_at < date('now'))`,
    )
    .all<{ id: number; email: string }>();
  let sent = 0;
  for (const user of users.results ?? []) {
    try {
      const domains = await env.DB
        .prepare(
          `SELECT d.id, d.domain, s.score, s.grade
             FROM domains d
             LEFT JOIN snapshots s ON s.id = (SELECT id FROM snapshots WHERE domain_id = d.id ORDER BY id DESC LIMIT 1)
            WHERE d.user_id = ?1 AND d.paused = 0 ORDER BY d.id`,
        )
        .bind(user.id)
        .all<{ id: number; domain: string; score: number | null; grade: string | null }>();
      const list = domains.results ?? [];
      if (!list.length) continue;
      const openAlerts = await env.DB
        .prepare('SELECT COUNT(*) AS n FROM alerts WHERE user_id = ?1 AND read_at IS NULL')
        .bind(user.id)
        .first<{ n: number }>();
      const lines: string[] = ['Your daily PromptDNS summary', ''];
      for (const d of list) {
        const rate = await dmarcPassRate(env.DB, d.id);
        lines.push(`- ${d.domain}: score ${d.score ?? '-'}/100 (${d.grade ?? '-'}), DMARC pass ${rate === null ? 'no reports yet' : rate + '%'}${d.score !== null && d.score < 60 ? ' [needs attention]' : ''}`);
      }
      lines.push('');
      lines.push(`Open alerts: ${openAlerts?.n ?? 0}`);
      lines.push('');
      lines.push('Full detail: https://promptdns.com/app/');
      const text = lines.join('\r\n');
      if (env.RESEND_API_KEY) {
        try {
          const res = await fetch('https://api.resend.com/emails', {
            method: 'POST',
            headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({
              from: 'PromptDNS Digest <digest@promptdns.com>',
              to: [user.email],
              subject: `[PromptDNS] Daily digest - ${list.length} domain${list.length === 1 ? '' : 's'}, ${openAlerts?.n ?? 0} open alerts`,
              text,
            }),
          });
          if (!res.ok) continue;
        } catch {
          continue;
        }
      } else if (env.SEND_EMAIL) {
        try {
          const raw = [
            'From: PromptDNS Digest <digest@promptdns.com>',
            `To: ${user.email}`,
            `Subject: [PromptDNS] Daily digest`,
            '',
            text,
          ].join('\r\n');
          const { EmailMessage } = await import('cloudflare:email');
          await env.SEND_EMAIL.send(new EmailMessage('digest@promptdns.com', user.email, raw));
        } catch {
          continue;
        }
      } else {
        continue;
      }
      await env.DB.prepare("UPDATE users SET last_digest_at = datetime('now') WHERE id = ?1").bind(user.id).run();
      sent++;
    } catch {
      // one user failing must not stop the rest
    }
  }
  return sent;
}
