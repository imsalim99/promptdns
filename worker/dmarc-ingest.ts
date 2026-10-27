/**
 * DMARC aggregate report ingestion (Phase 6).
 *
 * Inbound path: mailbox providers email zipped XML aggregate reports to
 * reports@promptdns.com; the Email Routing rule invokes this worker's
 * `email` handler; reports are matched to monitored domains by the
 * policy_published domain and stored for the sources view.
 *
 * - MIME via postal-mime, unzip/gunzip via fflate, XML via fast-xml-parser.
 * - De-duplication: UNIQUE(domain_id, org_name, report_id).
 * - Reports for domains nobody monitors are accepted and dropped (no data
 *   hoarding), consistent with the privacy promise.
 * - Only the dedicated reporting inbox is processed; other mail is ignored.
 */

import PostalMime from 'postal-mime';
import { unzipSync, gunzipSync } from 'fflate';
import { XMLParser } from 'fast-xml-parser';
import { getUserBySession } from './auth';
import type { Env } from './index';

const parser = new XMLParser({ ignoreAttributes: true });

const xmlsFromAttachment = (filename: string, contentType: string, content: Uint8Array): string[] => {
  const lower = filename.toLowerCase();
  try {
    if (lower.endsWith('.gz') || lower.endsWith('.gzip') || contentType === 'application/gzip') {
      return [new TextDecoder().decode(gunzipSync(content))];
    }
    if (lower.endsWith('.zip') || contentType === 'application/zip') {
      const files = unzipSync(content);
      return Object.keys(files)
        .filter((n) => n.toLowerCase().endsWith('.xml'))
        .map((n) => new TextDecoder().decode(files[n]));
    }
    if (lower.endsWith('.xml') || contentType.includes('xml')) {
      return [new TextDecoder().decode(content)];
    }
  } catch {
    return [];
  }
  return [];
};

const toIso = (epoch: unknown): string | null => {
  const n = typeof epoch === 'string' || typeof epoch === 'number' ? Number(epoch) : NaN;
  return Number.isFinite(n) ? new Date(n * 1000).toISOString().slice(0, 10) : null;
};

export interface DmarcAggregate {
  domain: string;
  org: string;
  reportId: string;
  begin: string | null;
  end: string | null;
  policyP: string;
  records: { ip: string; count: number; disposition: string; spf: string; dkim: string; dmarc: string; headerFrom: string }[];
}

export function parseAggregateXml(xml: string): DmarcAggregate | null {
  try {
    const doc = parser.parse(xml) as Record<string, never>;
    const fb = (doc as { feedback?: Record<string, unknown> }).feedback;
    if (!fb) return null;
    const meta = (fb.report_metadata ?? {}) as Record<string, never>;
    const published = (fb.policy_published ?? {}) as Record<string, never>;
    const domain = String(published.domain ?? '').toLowerCase();
    if (!domain) return null;
    const raw = fb.record;
    const recordsRaw = Array.isArray(raw) ? raw : raw ? [raw] : [];
    const records = recordsRaw.map((rec) => {
      const r = rec as Record<string, never>;
      const row = (r.row ?? {}) as Record<string, never>;
      const ev = (row.policy_evaluated ?? {}) as Record<string, never>;
      const idents = (r.identifiers ?? {}) as Record<string, never>;
      const spf = String(ev.spf ?? '?').toLowerCase();
      const dkim = String(ev.dkim ?? '?').toLowerCase();
      return {
        ip: String(row.source_ip ?? '?'),
        count: Number(row.count ?? 0),
        disposition: String(ev.disposition ?? '?').toLowerCase(),
        spf,
        dkim,
        dmarc: spf === 'pass' || dkim === 'pass' ? 'pass' : 'fail',
        headerFrom: String(idents.header_from ?? '?'),
      };
    });
    const range = (meta.date_range ?? {}) as Record<string, never>;
    return {
      domain,
      org: String(meta.org_name ?? 'unknown'),
      reportId: String(meta.report_id ?? ''),
      begin: toIso(range.begin),
      end: toIso(range.end),
      policyP: String(published.p ?? ''),
      records,
    };
  } catch {
    return null;
  }
}

async function storeReport(db: D1Database, agg: DmarcAggregate): Promise<boolean> {
  const normalizedDomain = agg.domain.replace(/\.+$/, '').toLowerCase();
  const domainRows = await db.prepare('SELECT id FROM domains WHERE domain = ?1').bind(normalizedDomain).all<{ id: number }>();
  console.log('[DMARC] storeReport: looking up domain:', normalizedDomain, 'found:', (domainRows.results ?? []).length, 'rows');
  let stored = false;
  for (const row of domainRows.results ?? []) {
    const ins = await db
      .prepare(
        "INSERT OR IGNORE INTO dmarc_reports (domain_id, org_name, report_id, date_begin, date_end, policy_published, messages_total) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
      )
      .bind(row.id, agg.org, agg.reportId, agg.begin, agg.end, agg.policyP, agg.records.reduce((s, r) => s + r.count, 0))
      .run();
    if (ins.meta.changes === 0) continue; // duplicate report
    stored = true;
    for (const rec of agg.records) {
      await db
        .prepare(
          'INSERT INTO dmarc_sources (report_ref, source_ip, header_from, count, spf_result, dkim_result, dmarc_result, disposition) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)',
        )
        .bind(ins.meta.last_row_id, rec.ip, rec.headerFrom, rec.count, rec.spf, rec.dkim, rec.dmarc, rec.disposition)
        .run();
    }
  }
  return stored;
}

export async function handleDmarcEmail(message: ForwardableEmailMessage, env: Env): Promise<void> {
  console.log('[DMARC] email handler invoked, to:', message.to);
  if (!env.DB) {
    console.error('[DMARC] DB not configured');
    message.setRejectReason('Storage not configured');
    return;
  }
  if (!message.to.toLowerCase().startsWith('reports@')) {
    console.log('[DMARC] not reports@, skipping:', message.to);
    return;
  }
  console.log('[DMARC] parsing MIME...');
  const parsed = await PostalMime.parse(message.raw);
  console.log('[DMARC] MIME parsed, attachments:', (parsed.attachments ?? []).length, 'subjects:', parsed.subject);
  let xmls: string[] = [];
  for (const att of parsed.attachments ?? []) {
    console.log('[DMARC] attachment:', att.filename, 'type:', att.type, 'size:', att.content?.length);
    xmls.push(...xmlsFromAttachment(att.filename ?? '', att.type ?? '', att.content));
  }
  console.log('[DMARC] XMLs extracted:', xmls.length);
  if (!xmls.length) {
    console.log('[DMARC] no XML found, accepting and dropping');
    return;
  }
  for (const xml of xmls) {
    console.log('[DMARC] parsing XML, length:', xml.length);
    const agg = parseAggregateXml(xml);
    console.log('[DMARC] parsed:', agg ? `domain=${agg.domain} org=${agg.org} records=${agg.records.length}` : 'PARSE FAILED');
    if (agg) {
      const stored = await storeReport(env.DB, agg);
      console.log('[DMARC] stored:', stored);
    }
  }
  console.log('[DMARC] processing complete');
}

function json(data: unknown, status = 200): Response {
  return Response.json(data, { status });
}

/** GET /api/domains/dmarc?id=N - sources aggregation + report list for one domain. */
export async function handleDmarcQuery(request: Request, env: Env): Promise<Response> {
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);

  const idParam = new URL(request.url).searchParams.get('id');
  const id = idParam ? Number.parseInt(idParam, 10) : Number.NaN;
  if (!Number.isInteger(id)) return json({ ok: false, error: 'Missing domain id.' }, 400);

  const owned = await env.DB
    .prepare('SELECT id, domain FROM domains WHERE id = ?1 AND user_id = ?2')
    .bind(id, user.id)
    .first<{ id: number; domain: string }>();
  if (!owned) return json({ ok: false, error: 'Domain not found on your list.' }, 404);

  const totals = await env.DB
    .prepare(
      `SELECT COUNT(DISTINCT r.id) AS reports,
              COALESCE(SUM(r.messages_total), 0) AS messages,
              COUNT(DISTINCT r.org_name) AS orgs
         FROM dmarc_reports r WHERE r.domain_id = ?1`,
    )
    .bind(id)
    .first<{ reports: number; messages: number; orgs: number }>();

  const passRow = await env.DB
    .prepare(
      `SELECT COALESCE(SUM(s.count), 0) AS total,
              COALESCE(SUM(CASE WHEN s.dmarc_result = 'pass' THEN s.count ELSE 0 END), 0) AS passing
         FROM dmarc_sources s JOIN dmarc_reports r ON r.id = s.report_ref
        WHERE r.domain_id = ?1`,
    )
    .bind(id)
    .first<{ total: number; passing: number }>();

  const sources = await env.DB
    .prepare(
      `SELECT s.source_ip AS ip,
              SUM(s.count) AS volume,
              SUM(CASE WHEN s.dmarc_result = 'pass' THEN s.count ELSE 0 END) AS dmarcPass,
              SUM(CASE WHEN s.spf_result = 'pass' THEN s.count ELSE 0 END) AS spfPass,
              SUM(CASE WHEN s.dkim_result = 'pass' THEN s.count ELSE 0 END) AS dkimPass,
              MAX(s.header_from) AS headerFrom,
              MAX(s.disposition) AS disposition,
              MAX(r.date_end) AS lastReport
         FROM dmarc_sources s JOIN dmarc_reports r ON r.id = s.report_ref
        WHERE r.domain_id = ?1
        GROUP BY s.source_ip
        ORDER BY volume DESC
        LIMIT 50`,
    )
    .bind(id)
    .all<{ ip: string; volume: number; dmarcPass: number; spfPass: number; dkimPass: number; headerFrom: string; disposition: string; lastReport: string | null }>();

  const reports = await env.DB
    .prepare(
      'SELECT org_name, report_id, date_begin, date_end, messages_total, received_at FROM dmarc_reports WHERE domain_id = ?1 ORDER BY id DESC LIMIT 20',
    )
    .bind(id)
    .all<{ org_name: string; report_id: string; date_begin: string | null; date_end: string | null; messages_total: number; received_at: string }>();

  const daily = await env.DB
    .prepare(
      `SELECT r.date_end AS date,
              SUM(s.count) AS total,
              SUM(CASE WHEN s.dmarc_result = 'pass' THEN s.count ELSE 0 END) AS passing
         FROM dmarc_sources s JOIN dmarc_reports r ON r.id = s.report_ref
        WHERE r.domain_id = ?1 AND r.date_end IS NOT NULL
        GROUP BY r.date_end ORDER BY r.date_end DESC LIMIT 30`,
    )
    .bind(id)
    .all<{ date: string; total: number; passing: number }>();

  const marks = await env.DB
    .prepare('SELECT source_ip, mark FROM dmarc_marks WHERE domain_id = ?1')
    .bind(id)
    .all<{ source_ip: string; mark: string }>();

  const total = passRow?.total ?? 0;
  const passing = passRow?.passing ?? 0;
  return json({
    ok: true,
    domain: owned.domain,
    summary: {
      reports: totals?.reports ?? 0,
      messages: totals?.messages ?? 0,
      orgs: totals?.orgs ?? 0,
      passRate: total > 0 ? Math.round((passing / total) * 100) : null,
    },
    sources: sources.results ?? [],
    reports: reports.results ?? [],
    daily: (daily.results ?? []).slice().reverse(),
    marks: marks.results ?? [],
  });
}

/** POST /api/domains/dmarc/mark {id, ip, mark: 'me'|'notme'} - persist source identification. */
export async function handleDmarcMark(request: Request, env: Env): Promise<Response> {
  if (request.method !== 'POST') return json({ ok: false, error: 'POST only.' }, 405);
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);
  const origin = request.headers.get('Origin');
  if (origin) {
    try {
      if (new URL(origin).host !== new URL(request.url).host) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
    } catch {
      return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
    }
  }
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);

  let body: { id?: unknown; ip?: unknown; mark?: unknown };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return json({ ok: false, error: 'Invalid JSON body.' }, 400);
  }
  const id = typeof body.id === 'number' ? body.id : Number.NaN;
  const ip = typeof body.ip === 'string' ? body.ip.trim() : '';
  const mark = body.mark === 'me' || body.mark === 'notme' ? body.mark : null;
  if (!Number.isInteger(id) || !ip || ip.length > 45 || !mark) return json({ ok: false, error: 'id, ip and mark (me|notme) required.' }, 400);

  const owned = await env.DB
    .prepare('SELECT id FROM domains WHERE id = ?1 AND user_id = ?2')
    .bind(id, user.id)
    .first<{ id: number }>();
  if (!owned) return json({ ok: false, error: 'Domain not found on your list.' }, 404);

  await env.DB
    .prepare(
      "INSERT INTO dmarc_marks (domain_id, source_ip, mark) VALUES (?1, ?2, ?3) ON CONFLICT(domain_id, source_ip) DO UPDATE SET mark = excluded.mark, updated_at = datetime('now')",
    )
    .bind(id, ip, mark)
    .run();
  return json({ ok: true, mark });
}
