/**
 * Domain CRUD for signed-in users (Phase 4b).
 * - POST /api/domains {domain}: add + instant first scan (max 3 while
 *   monitoring is in development).
 * - GET /api/domains: list with latest snapshot.
 * - DELETE /api/domains?id=N: remove domain + its snapshots.
 * All state-changing routes enforce same-origin; all routes require a session.
 */

import type { Env } from './index';
import { getUserBySession } from './auth';
import { scanDomainServer } from './scan';

const MAX_DOMAINS = 3; // development cap; becomes the plan limit when billing ships

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

function normalizeDomain(raw: unknown): string | null {
  if (typeof raw !== 'string') return null;
  let d = raw.trim().toLowerCase();
  d = d.replace(/^[a-z]+:\/\//, '').split('/')[0].split(':')[0].replace(/\.$/, '');
  if (!d || d.length > 253) return null;
  if (!/^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$/.test(d)) return null;
  return d;
}

interface SessionEnv extends Env {
  OWNER_EMAIL?: string;
}

async function requireUser(request: Request, env: SessionEnv): Promise<{ id: number; email: string } | Response> {
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);
  const user = await getUserBySession(env.DB, request);
  return user ?? json({ ok: false, error: 'Sign in first.' }, 401);
}

export async function handleDomainsList(request: Request, env: SessionEnv): Promise<Response> {
  const userOrRes = await requireUser(request, env);
  if (userOrRes instanceof Response) return userOrRes;
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);

  const rows = await env.DB
    .prepare(
      `SELECT d.id, d.domain, d.created_at, d.paused,
              s.score, s.grade, s.checks_json, s.checked_at
         FROM domains d
         LEFT JOIN snapshots s ON s.id = (
           SELECT id FROM snapshots WHERE domain_id = d.id ORDER BY id DESC LIMIT 1
         )
        WHERE d.user_id = ?1
        ORDER BY d.id`,
    )
    .bind(userOrRes.id)
    .all<{ id: number; domain: string; created_at: string; score: number | null; grade: string | null; checks_json: string | null; checked_at: string | null }>();

  const domains = (rows.results ?? []).map((r) => ({
    id: r.id,
    domain: r.domain,
    addedAt: r.created_at,
    paused: Boolean(r.paused),
    score: r.score,
    grade: r.grade,
    checkedAt: r.checked_at,
    checks: r.checks_json ? (JSON.parse(r.checks_json) as unknown) : null,
  }));
  return json({ ok: true, domains, max: MAX_DOMAINS });
}

export async function handleDomainsAdd(request: Request, env: SessionEnv): Promise<Response> {
  if (request.method !== 'POST') return json({ ok: false, error: 'POST only.' }, 405);
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  const userOrRes = await requireUser(request, env);
  if (userOrRes instanceof Response) return userOrRes;
  const user = userOrRes;
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);

  let body: { domain?: unknown };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return json({ ok: false, error: 'Invalid JSON body.' }, 400);
  }
  const domain = normalizeDomain(body.domain);
  if (!domain) return json({ ok: false, error: 'Enter a valid domain, e.g. example.com.' }, 400);

  const count = await env.DB
    .prepare('SELECT COUNT(*) AS n FROM domains WHERE user_id = ?1')
    .bind(user.id)
    .first<{ n: number }>();
  if (count && count.n >= MAX_DOMAINS) {
    return json({ ok: false, error: `Up to ${MAX_DOMAINS} domains while monitoring is in development.` }, 400);
  }

  const existing = await env.DB
    .prepare('SELECT id FROM domains WHERE user_id = ?1 AND domain = ?2')
    .bind(user.id, domain)
    .first<{ id: number }>();
  if (existing) return json({ ok: false, error: 'That domain is already on your list.' }, 400);

  // Scan first: only keep the domain if DNS answers for it at all.
  const scan = await scanDomainServer(domain);
  const resolvable = scan.checks.some((c) => c.id === 'ns' && c.earned > 0);
  if (!resolvable) {
    return json({ ok: false, error: `DNS for ${domain} did not resolve. Check the spelling; only domains you control are useful here.` }, 400);
  }

  const ins = await env.DB
    .prepare('INSERT INTO domains (user_id, domain) VALUES (?1, ?2)')
    .bind(user.id, domain)
    .run();
  const domainId = ins.meta.last_row_id;
  await env.DB
    .prepare('INSERT INTO snapshots (domain_id, score, grade, checks_json) VALUES (?1, ?2, ?3, ?4)')
    .bind(domainId, scan.score, scan.grade, JSON.stringify(scan.checks))
    .run();

  return json({ ok: true, domain: { id: domainId, domain, score: scan.score, grade: scan.grade, checkedAt: new Date().toISOString(), checks: scan.checks } });
}

export async function handleDomainsDelete(request: Request, env: SessionEnv): Promise<Response> {
  if (request.method !== 'POST' && request.method !== 'DELETE') return json({ ok: false, error: 'DELETE only.' }, 405);
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  const userOrRes = await requireUser(request, env);
  if (userOrRes instanceof Response) return userOrRes;
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);

  const idParam = new URL(request.url).searchParams.get('id');
  const id = idParam ? Number.parseInt(idParam, 10) : Number.NaN;
  if (!Number.isInteger(id)) return json({ ok: false, error: 'Missing domain id.' }, 400);

  const owned = await env.DB
    .prepare('SELECT id FROM domains WHERE id = ?1 AND user_id = ?2')
    .bind(id, userOrRes.id)
    .first<{ id: number }>();
  if (!owned) return json({ ok: false, error: 'Domain not found on your list.' }, 404);

  await env.DB.prepare('DELETE FROM snapshots WHERE domain_id = ?1').bind(id).run();
  await env.DB.prepare('DELETE FROM scan_runs WHERE domain_id = ?1').bind(id).run();
  await env.DB.prepare('DELETE FROM alerts WHERE domain_id = ?1').bind(id).run();
  await env.DB.prepare('DELETE FROM domains WHERE id = ?1').bind(id).run();
  return json({ ok: true });
}

/** POST /api/domains/pause {id, paused} - include/exclude from the automatic cycle. */
export async function handleDomainsPause(request: Request, env: SessionEnv): Promise<Response> {
  if (request.method !== 'POST') return json({ ok: false, error: 'POST only.' }, 405);
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  const userOrRes = await requireUser(request, env);
  if (userOrRes instanceof Response) return userOrRes;
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);

  let body: { id?: unknown; paused?: unknown };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return json({ ok: false, error: 'Invalid JSON body.' }, 400);
  }
  const id = typeof body.id === 'number' ? body.id : Number.NaN;
  const paused = body.paused === true;
  if (!Number.isInteger(id)) return json({ ok: false, error: 'Missing domain id.' }, 400);

  const owned = await env.DB
    .prepare('SELECT id FROM domains WHERE id = ?1 AND user_id = ?2')
    .bind(id, userOrRes.id)
    .first<{ id: number }>();
  if (!owned) return json({ ok: false, error: 'Domain not found on your list.' }, 404);

  await env.DB.prepare('UPDATE domains SET paused = ?2 WHERE id = ?1').bind(id, paused ? 1 : 0).run();
  return json({ ok: true, paused });
}
