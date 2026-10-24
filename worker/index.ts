/**
 * PromptDNS Worker - API routes for the static site (Workers static assets).
 *
 * Static asset requests never reach this script (the asset layer answers
 * first); only non-asset paths like /api/* arrive here. Everything else
 * falls through to the asset layer, which serves the Astro 404 page.
 *
 * Route: POST /api/waitlist - early-access signups (D1).
 */

interface Env {
  DB?: D1Database;
  ASSETS: { fetch(request: Request): Promise<Response> };
}

const EMAIL_RE = /^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,24}$/;

function bad(msg: string, status = 400): Response {
  return Response.json({ ok: false, error: msg }, { status });
}

function normalizeDomain(raw: unknown): string | null {
  if (typeof raw !== 'string') return null;
  let d = raw.trim().toLowerCase();
  d = d.replace(/^[a-z]+:\/\//, '').split('/')[0].split(':')[0].replace(/\.$/, '');
  if (!d || d.length > 253) return null;
  if (!/^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$/.test(d)) return null;
  return d;
}

async function hashIp(ip: string): Promise<string> {
  const data = new TextEncoder().encode(ip);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

async function handleWaitlist(request: Request, env: Env): Promise<Response> {
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

  const res = await env.DB
    .prepare('INSERT OR IGNORE INTO waitlist (email, domain, source, ip_hash) VALUES (?1, ?2, ?3, ?4)')
    .bind(email, domain, source, ipHash)
    .run();

  return Response.json({ ok: true, already: res.meta.changes === 0 });
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === '/api/waitlist') {
      return handleWaitlist(request, env);
    }
    return env.ASSETS.fetch(request);
  },
} satisfies ExportedHandler<Env>;
