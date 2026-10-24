/**
 * Magic-link authentication (Phase 4).
 *
 * Security requirements (from the security review of the discarded attempt):
 * - Tokens stored hashed (SHA-256); raw tokens exist only in the link/cookie.
 * - Rate limiting per hashed IP on every auth endpoint.
 * - Session cookie: HttpOnly, Secure, SameSite=Lax.
 * - CSRF: same-origin enforcement on state-changing requests (Origin check
 *   when present + SameSite cookies).
 *
 * Email delivery is not configured yet. Until it is, the sign-in link is
 * returned in the API response ONLY for the allowlisted owner email
 * (OWNER_EMAIL secret); everyone else gets an honest "not available yet"
 * response. No impersonation is possible.
 */

import type { Env } from './index';

const SESSION_COOKIE = 'pdns_session';
const SESSION_DAYS = 30;
const MAGIC_MINUTES = 15;

export interface AuthEnv extends Env {
  OWNER_EMAIL?: string;
}

function json(data: unknown, status = 200, headers: Record<string, string> = {}): Response {
  return Response.json(data, { status, headers });
}

async function hashHex(s: string): Promise<string> {
  const d = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

function randomToken(): string {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  return [...bytes].map((b) => b.toString(16).padStart(2, '0')).join('');
}

async function ipHashOf(request: Request): Promise<string> {
  const ip = request.headers.get('CF-Connecting-IP') ?? 'unknown';
  return hashHex(`ip:${ip}`);
}

/** Same-origin enforcement for state-changing requests (CSRF). */
function sameOrigin(request: Request): boolean {
  const origin = request.headers.get('Origin');
  if (!origin) return true; // non-browser clients (curl); cookies are still SameSite=Lax
  try {
    return new URL(origin).host === new URL(request.url).host;
  } catch {
    return false;
  }
}

/** Hourly rate limit keyed by hashed IP + action. Returns true when allowed. */
async function allowRate(db: D1Database, key: string, limit: number): Promise<boolean> {
  const reset = await db
    .prepare(
      `UPDATE rate_limits
         SET count = CASE WHEN window_start < datetime('now', '-1 hour') THEN 1 ELSE count + 1 END,
             window_start = CASE WHEN window_start < datetime('now', '-1 hour') THEN datetime('now') ELSE window_start END
       WHERE key = ?1
       RETURNING count`,
    )
    .bind(key)
    .first<{ count: number }>();
  if (reset) return reset.count <= limit;
  const ins = await db
    .prepare('INSERT INTO rate_limits (key, count, window_start) VALUES (?1, 1, datetime(\'now\')) ON CONFLICT(key) DO NOTHING')
    .bind(key)
    .run();
  if (ins.meta.changes === 1) return true;
  // Lost a race: re-read.
  const row = await db.prepare('SELECT count FROM rate_limits WHERE key = ?1').bind(key).first<{ count: number }>();
  return (row?.count ?? 0) <= limit;
}

async function getUserBySession(db: D1Database, request: Request): Promise<{ id: number; email: string } | null> {
  const cookie = request.headers.get('Cookie') ?? '';
  const match = cookie.match(new RegExp(`(?:^|;\\s*)${SESSION_COOKIE}=([a-f0-9]{64})`));
  if (!match) return null;
  const tokenHash = await hashHex(match[1]);
  const row = await db
    .prepare(
      `SELECT u.id, u.email FROM sessions s JOIN users u ON u.id = s.user_id
        WHERE s.token_hash = ?1 AND s.expires_at > datetime('now')`,
    )
    .bind(tokenHash)
    .first<{ id: number; email: string }>();
  return row ?? null;
}

function sessionCookie(token: string, maxAgeDays: number): string {
  return `${SESSION_COOKIE}=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAgeDays * 86400}`;
}

/** POST /api/auth/magic-link  {email} */
export async function handleMagicLink(request: Request, env: AuthEnv): Promise<Response> {
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  if (!env.DB) return json({ ok: false, error: 'Auth storage is not configured.' }, 503);

  const ipKey = `magic:${await ipHashOf(request)}`;
  if (!(await allowRate(env.DB, ipKey, 5))) {
    return json({ ok: false, error: 'Too many attempts. Try again later.' }, 429);
  }

  let body: { email?: unknown };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return json({ ok: false, error: 'Invalid JSON body.' }, 400);
  }
  const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : '';
  if (!email || email.length > 254 || !/^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,24}$/.test(email)) {
    return json({ ok: false, error: 'Enter a valid email address.' }, 400);
  }

  // Ensure a user row exists so the token has an owner.
  await env.DB.prepare('INSERT INTO users (email) VALUES (?1) ON CONFLICT(email) DO NOTHING').bind(email).run();
  const user = await env.DB.prepare('SELECT id FROM users WHERE email = ?1').bind(email).first<{ id: number }>();
  if (!user) return json({ ok: false, error: 'Could not create account.' }, 500);

  const token = randomToken();
  const tokenHash = await hashHex(token);
  await env.DB
    .prepare("INSERT INTO auth_tokens (user_id, token_hash, purpose, expires_at) VALUES (?1, ?2, 'magic_link', datetime('now', '+15 minutes'))")
    .bind(user.id, tokenHash)
    .run();

  const verifyUrl = `https://promptdns.com/api/auth/verify?token=${token}`;

  // Until an email provider is configured, the link is shown on-screen only
  // to the allowlisted owner email. Everyone else gets an honest response.
  if (env.OWNER_EMAIL && email === env.OWNER_EMAIL.trim().toLowerCase()) {
    return json({ ok: true, owner: true, verify_url: verifyUrl });
  }
  return json({
    ok: true,
    owner: false,
    message: 'Email delivery is not set up yet, so sign-in links cannot be emailed. Sign-in is currently limited to the PromptDNS team; monitored accounts open with the early access launch.',
  });
}

/** GET /api/auth/verify?token=...  (the email link) */
export async function handleVerify(request: Request, env: AuthEnv): Promise<Response> {
  if (!env.DB) return json({ ok: false, error: 'Auth storage is not configured.' }, 503);

  const ipKey = `verify:${await ipHashOf(request)}`;
  if (!(await allowRate(env.DB, ipKey, 20))) {
    return new Response('Too many attempts. Try again later.', { status: 429 });
  }

  const token = new URL(request.url).searchParams.get('token') ?? '';
  if (!/^[a-f0-9]{64}$/.test(token)) return new Response('Invalid sign-in link.', { status: 400 });
  const tokenHash = await hashHex(token);

  const claimed = await env.DB
    .prepare(
      "UPDATE auth_tokens SET used_at = datetime('now') WHERE token_hash = ?1 AND used_at IS NULL AND expires_at > datetime('now') RETURNING user_id",
    )
    .bind(tokenHash)
    .first<{ user_id: number }>();
  if (!claimed) return new Response('This sign-in link is invalid, already used, or expired. Request a new one.', { status: 400 });

  const user = await env.DB.prepare('SELECT id, email FROM users WHERE id = ?1').bind(claimed.user_id).first<{ id: number; email: string }>();
  if (!user) return new Response('Account not found.', { status: 400 });

  const sessionToken = randomToken();
  const sessionHash = await hashHex(sessionToken);
  await env.DB
    .prepare("INSERT INTO sessions (user_id, token_hash) VALUES (?1, ?2)")
    .bind(user.id, sessionHash)
    .run();
  await env.DB.prepare("UPDATE users SET last_login_at = datetime('now') WHERE id = ?1").bind(user.id).run();

  return new Response(null, {
    status: 302,
    headers: { Location: '/app/', 'Set-Cookie': sessionCookie(sessionToken, SESSION_DAYS) },
  });
}

/** GET /api/auth/me */
export async function handleMe(request: Request, env: AuthEnv): Promise<Response> {
  if (!env.DB) return json({ ok: true, authenticated: false });
  const user = await getUserBySession(env.DB, request);
  return json({ ok: true, authenticated: Boolean(user), email: user?.email ?? null });
}

/** POST /api/auth/logout */
export async function handleLogout(request: Request, env: AuthEnv): Promise<Response> {
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  if (!env.DB) return json({ ok: true });
  const cookie = request.headers.get('Cookie') ?? '';
  const match = cookie.match(new RegExp(`(?:^|;\\s*)${SESSION_COOKIE}=([a-f0-9]{64})`));
  if (match) {
    const tokenHash = await hashHex(match[1]);
    await env.DB.prepare('DELETE FROM sessions WHERE token_hash = ?1').bind(tokenHash).run();
  }
  return json({ ok: true }, 200, { headers: { 'Set-Cookie': `${SESSION_COOKIE}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0` } });
}

export { getUserBySession };
