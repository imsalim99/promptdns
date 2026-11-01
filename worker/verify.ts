/**
 * Domain ownership verification (TXT challenge).
 *
 * - POST /api/domains/verify/start?id=N: issue (or return) the challenge
 *   token. The user publishes a TXT record `pdns-verify=<token>` at the
 *   zone apex.
 * - POST /api/domains/verify/check?id=N: resolve the domain's TXT records
 *   over DoH and mark the domain verified when the challenge is present.
 *
 * Verification gates managed-record features and plan features; it never
 * changes scanning behavior.
 */

import type { Env } from './index';
import { getUserBySession } from './auth';
import { txtRecords } from './scan';

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

interface VerifyRow {
  id: number;
  domain: string;
  verified: number;
  verification_token: string | null;
}

async function ownedDomain(env: Env, request: Request, id: number): Promise<VerifyRow | null> {
  const user = await getUserBySession(env.DB!, request);
  if (!user) return null;
  return env.DB!
    .prepare('SELECT id, domain, verified, verification_token FROM domains WHERE id = ?1 AND user_id = ?2')
    .bind(id, user.id)
    .first<VerifyRow>();
}

function tokenId(): string {
  const bytes = new Uint8Array(12);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
}

async function resolveId(request: Request): Promise<number | null> {
  const raw = new URL(request.url).searchParams.get('id');
  const id = raw ? Number.parseInt(raw, 10) : Number.NaN;
  return Number.isInteger(id) ? id : null;
}

/** POST /api/domains/verify/start?id=N */
export async function handleVerifyStart(request: Request, env: Env): Promise<Response> {
  if (request.method !== 'POST') return json({ ok: false, error: 'POST only.' }, 405);
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);
  const id = await resolveId(request);
  if (id === null) return json({ ok: false, error: 'Missing domain id.' }, 400);

  const row = await env.DB
    .prepare('SELECT id, domain, verified, verification_token FROM domains WHERE id = ?1 AND user_id = ?2')
    .bind(id, user.id)
    .first<VerifyRow>();
  if (!row) return json({ ok: false, error: 'Domain not found on your list.' }, 404);

  let token = row.verification_token;
  if (!token) {
    token = tokenId();
    await env.DB.prepare('UPDATE domains SET verification_token = ?2 WHERE id = ?1').bind(row.id, token).run();
  }
  return json({
    ok: true,
    verified: Boolean(row.verified),
    record: { name: '@', type: 'TXT', value: 'pdns-verify=' + token },
  });
}

/** POST /api/domains/verify/check?id=N */
export async function handleVerifyCheck(request: Request, env: Env): Promise<Response> {
  if (request.method !== 'POST') return json({ ok: false, error: 'POST only.' }, 405);
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);
  const id = await resolveId(request);
  if (id === null) return json({ ok: false, error: 'Missing domain id.' }, 400);

  const row = await env.DB
    .prepare('SELECT id, domain, verified, verification_token FROM domains WHERE id = ?1 AND user_id = ?2')
    .bind(id, user.id)
    .first<VerifyRow>();
  if (!row) return json({ ok: false, error: 'Domain not found on your list.' }, 404);
  if (row.verified) return json({ ok: true, verified: true });

  let token = row.verification_token;
  if (!token) {
    token = tokenId();
    await env.DB.prepare('UPDATE domains SET verification_token = ?2 WHERE id = ?1').bind(row.id, token).run();
    return json({ ok: true, verified: false, record: { name: '@', type: 'TXT', value: 'pdns-verify=' + token }, message: 'New challenge issued - publish the TXT record and check again.' });
  }

  let txts: string[] = [];
  try {
    txts = await txtRecords(row.domain);
  } catch {
    return json({ ok: false, error: 'DNS lookup failed. Try again in a moment.' }, 502);
  }
  const expect = 'pdns-verify=' + token;
  const found = txts.some((t) => t.replace(/"/g, '').trim().includes(expect));
  if (!found) return json({ ok: true, verified: false });

  await env.DB
    .prepare("UPDATE domains SET verified = 1, verified_at = datetime('now') WHERE id = ?1")
    .bind(row.id)
    .run();
  return json({ ok: true, verified: true });
}
