/**
 * POST /api/waitlist - early-access signups (D1, double opt-in).
 * GET  /api/waitlist/verify?token=... - confirms a signup (token is single-use, hashed at rest).
 *
 * On a NEW signup: a verification email is sent via Resend (from
 * earlyaccess@promptdns.com). Only verified rows count as confirmed; the row
 * and its token exist either way so a re-subscribe can resend.
 */

import type { Env } from './index';

const EMAIL_RE = /^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,24}$/;

function bad(msg: string, status = 400): Response {
  return Response.json({ ok: false, error: msg }, { status });
}

function json(data: unknown, status = 200): Response {
  return Response.json(data, { status });
}

function normalizeDomain(raw: unknown): string | null {
  if (typeof raw !== 'string') return null;
  let d = raw.trim().toLowerCase();
  d = d.replace(/^[a-z]+:\/\//, '').split('/')[0].split(':')[0].replace(/\.$/, '');
  if (!d || d.length > 253) return null;
  if (!/^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$/.test(d)) return null;
  return d;
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

async function hashIp(ip: string): Promise<string> {
  const d = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(ip));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

async function sendVerificationEmail(env: Env, email: string, token: string, domain: string | null): Promise<boolean> {
  if (!env.RESEND_API_KEY) return false;
  const link = `https://promptdns.com/api/waitlist/verify?token=${token}`;
  const body = [
    'Confirm your PromptDNS early access signup:',
    '',
    link,
    '',
    domain ? `Domain you asked us to watch: ${domain}` : '',
    '',
    'If you did not request this, ignore this email and nothing happens.',
    '',
    '- PromptDNS',
  ].filter(Boolean).join('\r\n');
  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: 'PromptDNS Early Access <earlyaccess@promptdns.com>',
        to: [email],
        subject: 'Confirm your PromptDNS early access signup',
        text: body,
      }),
    });
    return res.ok;
  } catch {
    return false;
  }
}

export async function handleWaitlist(request: Request, env: Env): Promise<Response> {
  if (request.method !== 'POST') return bad('POST only.', 405);
  if (!env.DB) {
    return bad('Waitlist storage is not configured. Email earlyaccess@promptdns.com to join.', 503);
  }

  let body: { email?: unknown; domain?: unknown; source?: unknown };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return bad('Invalid JSON body.');
  }

  const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : '';
  if (!email || email.length > 254 || !EMAIL_RE.test(email)) {
    return bad('Enter a valid email address.');
  }
  const domain = normalizeDomain(body.domain);
  const source = typeof body.source === 'string' ? body.source.slice(0, 64) : null;

  const ip = request.headers.get('CF-Connecting-IP') ?? 'unknown';
  const ipHash = await hashIp(ip);

  // Flood limit: 5 signups per hashed IP per hour.
  const recent = await env.DB
    .prepare("SELECT COUNT(*) AS n FROM waitlist WHERE ip_hash = ?1 AND created_at > datetime('now', '-1 hour')")
    .bind(ipHash)
    .first<{ n: number }>();
  if (recent && recent.n >= 5) {
    return bad('Too many submissions from this network. Try again later or email earlyaccess@promptdns.com.', 429);
  }

  const existing = await env.DB
    .prepare('SELECT verified_at FROM waitlist WHERE email = ?1')
    .bind(email)
    .first<{ verified_at: string | null }>();

  if (existing) {
    // Already on the list. If unverified, resend the confirmation link.
    if (!existing.verified_at) {
      const token = randomToken();
      await env.DB
        .prepare('UPDATE waitlist SET token_hash = ?2 WHERE email = ?1')
        .bind(email, await hashHex(token))
        .run();
      const sent = await sendVerificationEmail(env, email, token, domain);
      return json({ ok: true, already: true, verificationSent: sent });
    }
    return json({ ok: true, already: true });
  }

  const token = randomToken();
  const ins = await env.DB
    .prepare('INSERT INTO waitlist (email, domain, source, ip_hash, token_hash) VALUES (?1, ?2, ?3, ?4, ?5)')
    .bind(email, domain, source, ipHash, await hashHex(token))
    .run();
  const created = ins.meta.changes === 1;

  if (created) {
    const sent = await sendVerificationEmail(env, email, token, domain);
    return json({ ok: true, already: false, verificationSent: sent });
  }
  return json({ ok: true, already: true });
}

/** GET /api/waitlist/verify?token=... - confirm a signup (the email link). */
export async function handleWaitlistVerify(request: Request, env: Env): Promise<Response> {
  if (!env.DB) return new Response('Waitlist storage is not configured.', { status: 503 });
  const token = new URL(request.url).searchParams.get('token') ?? '';
  if (!/^[a-f0-9]{64}$/.test(token)) return new Response('This verification link is invalid.', { status: 400 });

  const tokenHash = await hashHex(token);
  const claimed = await env.DB
    .prepare(
      "UPDATE waitlist SET verified_at = datetime('now'), token_hash = NULL WHERE token_hash = ?1 AND verified_at IS NULL RETURNING email",
    )
    .bind(tokenHash)
    .first<{ email: string }>();

  const page = (ok: boolean, msg: string) => new Response(
    `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Email verified - PromptDNS</title><style>body{font-family:system-ui,sans-serif;background:#050810;color:#e6edf7;display:grid;place-items:center;min-height:100vh;margin:0}main{text-align:center;max-width:28rem;padding:2rem}a{color:#22d3ee}</style></head><body><main><h1>${ok ? 'Email verified' : 'Link problem'}</h1><p>${msg}</p><p><a href="/early-access/">Back to early access</a></p></main></body></html>`,
    { status: ok ? 200 : 400, headers: { 'Content-Type': 'text/html; charset=utf-8' } },
  );

  if (!claimed) return page(false, 'This verification link was already used or has expired. Sign up again to receive a fresh one.');
  return page(true, `${claimed.email} is confirmed for PromptDNS early access. We will email you when monitoring opens.`);
}

export async function handleWaitlistVerifyAlias(request: Request, env: Env): Promise<Response> {
  return handleWaitlistVerify(request, env);
}
