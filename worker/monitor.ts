/**
 * Monitoring engine (Phase 5).
 *
 * - scanAndCompare: scans a domain, diffs against the latest snapshot,
 *   stores a new snapshot only when something changed (snapshot-on-change),
 *   and creates an alert row for the owner when it did.
 * - Transient-outage guard: a run where the domain does not resolve at all
 *   (both NS and Website checks fail) increments fail_count instead of
 *   comparing - two consecutive unresolvable runs are required before a
 *   "domain stopped resolving" alert, so a DoH blip never fabricates
 *   "everything vanished" alerts.
 * - handleRescan: POST /api/domains/rescan {id} - the same pipeline on
 *   demand ("Scan now" button).
 * - runScheduled: the cron entry - scans every monitored domain.
 * - handleAlertsList / handleAlertsRead: alert inbox endpoints.
 */

import type { Env } from './index';
import { getUserBySession } from './auth';
import { scanDomainServer, type ScanCheck, type ScanResult } from './scan';

interface DomainRow {
  id: number;
  user_id: number;
  domain: string;
  fail_count: number;
  paused: number;
}

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

interface SessionEnv extends Env {
  OWNER_EMAIL?: string;
  SEND_EMAIL?: { send(message: unknown): Promise<void> };
}

interface CompareOutcome {
  changed: boolean;
  unresolvable: boolean;
  scan: ScanResult;
  diff: string[];
  severity: 'info' | 'warn' | 'fail';
}

async function emailAlert(env: SessionEnv, userId: number, domainName: string, title: string, detail: string): Promise<void> {
  if (!env.SEND_EMAIL || !env.DB) return;
  try {
    const user = await env.DB.prepare('SELECT email FROM users WHERE id = ?1').bind(userId).first<{ email: string }>();
    if (!user) return;
    // Cloudflare Email Sending delivers only to addresses verified on the
    // account; unverified destinations throw and are skipped silently until
    // a transactional provider (Resend) takes over customer-scale sending.
    const raw = [
      'From: PromptDNS Alerts <alerts@promptdns.com>',
      `To: ${user.email}`,
      `Subject: [PromptDNS] ${title}`,
      '',
      title,
      '',
      detail,
      '',
      'Open your dashboard: https://promptdns.com/app/',
      '',
      `You receive this because ${domainName} is monitored on your PromptDNS account. Manage alert channels in Settings.`,
      '',
    ].join('\r\n');
    const { EmailMessage } = await import('cloudflare:email');
    await env.SEND_EMAIL.send(new EmailMessage('alerts@promptdns.com', user.email, raw));
  } catch {
    // the alert stays in the inbox regardless; email is best-effort
  }
}

async function scanAndCompare(env: SessionEnv, d: DomainRow): Promise<CompareOutcome> {
  const db = env.DB!;
  const scan = await scanDomainServer(d.domain);

  const nsOk = scan.checks.some((c) => c.id === 'ns' && c.earned > 0);
  const webOk = scan.checks.some((c) => c.id === 'website' && c.earned > 0);

  if (!nsOk && !webOk) {
    const failCount = d.fail_count + 1;
    await db.prepare('UPDATE domains SET fail_count = ?2, last_checked_at = datetime(\'now\') WHERE id = ?1')
      .bind(d.id, failCount)
      .run();
    await db
      .prepare("INSERT INTO scan_runs (domain_id, outcome, score, changes) VALUES (?1, 'unresolvable', NULL, 0)")
      .bind(d.id)
      .run();
    if (failCount === 2) {
      const title = `${d.domain} stopped resolving`;
      const detail = 'Two consecutive checks could not resolve this domain\'s nameservers. It may have expired, been deleted, or its DNS provider is down. Verify at your registrar.';
      await db.prepare(
        "INSERT INTO alerts (user_id, domain_id, severity, title, detail) VALUES (?1, ?2, 'fail', ?3, ?4)",
      ).bind(d.user_id, d.id, title, detail).run();
      await emailAlert(env, d.user_id, d.domain, title, detail);
    }
    return { changed: false, unresolvable: true, scan, diff: [], severity: 'info' };
  }

  // Resolvable again after failures: reset the counter.
  if (d.fail_count > 0) {
    await db.prepare('UPDATE domains SET fail_count = 0 WHERE id = ?1').bind(d.id).run();
  }

  const prev = await db
    .prepare('SELECT checks_json FROM snapshots WHERE domain_id = ?1 ORDER BY id DESC LIMIT 1')
    .bind(d.id)
    .first<{ checks_json: string }>();

  let changed = false;
  const diff: string[] = [];
  let severity: CompareOutcome['severity'] = 'info';

  if (prev) {
    const old = (JSON.parse(prev.checks_json) as ScanCheck[]) ?? [];
    const oldById = new Map(old.map((c) => [c.id, c]));
    for (const c of scan.checks) {
      const o = oldById.get(c.id);
      if (!o) continue;
      if (o.status !== c.status || o.value !== c.value) {
        changed = true;
        diff.push(`${c.label}: "${o.value}" -> "${c.value}"`);
        if (c.status === 'fail') severity = 'fail';
        else if (c.status === 'warn' && severity !== 'fail') severity = 'warn';
        else if (c.status === 'pass' && severity === 'info') severity = 'info';
      }
    }
  } else {
    // First snapshot ever: record it, no alert.
    changed = true;
  }

  if (changed) {
    await db
      .prepare('INSERT INTO snapshots (domain_id, score, grade, checks_json, records_json) VALUES (?1, ?2, ?3, ?4, ?5)')
      .bind(d.id, scan.score, scan.grade, JSON.stringify(scan.checks), JSON.stringify(scan.records))
      .run();
    if (prev && diff.length) {
      const changedCount = diff.length;
      const title = `${d.domain}: ${changedCount} check${changedCount > 1 ? 's' : ''} changed`;
      const detail = diff.join('\n');
      await db.prepare(
        'INSERT INTO alerts (user_id, domain_id, severity, title, detail) VALUES (?1, ?2, ?3, ?4, ?5)',
      ).bind(d.user_id, d.id, severity, title, detail).run();
      await emailAlert(env, d.user_id, d.domain, title, detail);
    }
  }

  await db
    .prepare("INSERT INTO scan_runs (domain_id, outcome, score, changes) VALUES (?1, ?2, ?3, ?4)")
    .bind(d.id, changed ? 'changed' : 'ok', scan.score, diff.length)
    .run();
  await db.prepare("UPDATE domains SET last_checked_at = datetime('now') WHERE id = ?1").bind(d.id).run();
  return { changed, unresolvable: false, scan, diff, severity };
}

export async function handleRescan(request: Request, env: SessionEnv): Promise<Response> {
  if (request.method !== 'POST') return json({ ok: false, error: 'POST only.' }, 405);
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);

  const idParam = new URL(request.url).searchParams.get('id');
  const id = idParam ? Number.parseInt(idParam, 10) : Number.NaN;
  if (!Number.isInteger(id)) return json({ ok: false, error: 'Missing domain id.' }, 400);

  const row = await env.DB
    .prepare('SELECT id, user_id, domain, fail_count, paused FROM domains WHERE id = ?1 AND user_id = ?2')
    .bind(id, user.id)
    .first<DomainRow>();
  if (!row) return json({ ok: false, error: 'Domain not found on your list.' }, 404);

  const outcome = await scanAndCompare(env, row);
  if (outcome.unresolvable) {
    return json({ ok: false, error: `${row.domain} did not resolve on this run. Try again later.` }, 502);
  }
  return json({
    ok: true,
    changed: outcome.changed,
    score: outcome.scan.score,
    grade: outcome.scan.grade,
    checks: outcome.scan.checks,
    diff: outcome.diff,
  });
}

/** The cron entry: scan every monitored domain, 5 at a time. */
export async function runScheduled(env: SessionEnv): Promise<void> {
  if (!env.DB) return;
  const rows = await env.DB
    .prepare('SELECT id, user_id, domain, fail_count, paused FROM domains WHERE paused = 0')
    .all<DomainRow>();
  const domains = rows.results ?? [];
  for (let i = 0; i < domains.length; i += 5) {
    const batch = domains.slice(i, i + 5);
    await Promise.allSettled(batch.map((d) => scanAndCompare(env, d)));
  }
}

export async function handleAlertsList(request: Request, env: SessionEnv): Promise<Response> {
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);

  const rows = await env.DB
    .prepare(
      `SELECT a.id, a.severity, a.title, a.detail, a.created_at, a.read_at, d.domain
         FROM alerts a JOIN domains d ON d.id = a.domain_id
        WHERE a.user_id = ?1
        ORDER BY a.id DESC LIMIT 50`,
    )
    .bind(user.id)
    .all<{ id: number; severity: string; title: string; detail: string; created_at: string; read_at: string | null; domain: string }>();
  return json({ ok: true, alerts: rows.results ?? [] });
}

export async function handleAlertsRead(request: Request, env: SessionEnv): Promise<Response> {
  if (request.method !== 'POST') return json({ ok: false, error: 'POST only.' }, 405);
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);
  await env.DB
    .prepare("UPDATE alerts SET read_at = datetime('now') WHERE user_id = ?1 AND read_at IS NULL")
    .bind(user.id)
    .run();
  return json({ ok: true });
}

/** GET /api/domains/history?id=N - run log + alerts for one domain. */
export async function handleHistory(request: Request, env: SessionEnv): Promise<Response> {
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);

  const idParam = new URL(request.url).searchParams.get('id');
  const id = idParam ? Number.parseInt(idParam, 10) : Number.NaN;
  if (!Number.isInteger(id)) return json({ ok: false, error: 'Missing domain id.' }, 400);

  const owned = await env.DB
    .prepare('SELECT id FROM domains WHERE id = ?1 AND user_id = ?2')
    .bind(id, user.id)
    .first<{ id: number }>();
  if (!owned) return json({ ok: false, error: 'Domain not found on your list.' }, 404);

  const runs = await env.DB
    .prepare('SELECT outcome, score, changes, ran_at FROM scan_runs WHERE domain_id = ?1 ORDER BY id DESC LIMIT 30')
    .bind(id)
    .all<{ outcome: string; score: number | null; changes: number; ran_at: string }>();
  const alerts = await env.DB
    .prepare('SELECT severity, title, detail, created_at, read_at FROM alerts WHERE domain_id = ?1 ORDER BY id DESC LIMIT 20')
    .bind(id)
    .all<{ severity: string; title: string; detail: string; created_at: string; read_at: string | null }>();

  return json({ ok: true, runs: runs.results ?? [], alerts: alerts.results ?? [] });
}
