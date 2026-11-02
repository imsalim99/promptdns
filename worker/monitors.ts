/**
 * DNS monitor checks (v12): SSL status, domain expiry, blocklists.
 *
 * All three run inside the Worker using standard protocols:
 * - SSL: fetch over HTTPS to the site root; failure = SSL problem.
 * - Expiry: RDAP (rdap.org) bootstrap, returns the expiration event.
 * - Blocklists: resolve the domain's A record, then query two public
 *   DNSBLs (Spamhaus Zen, SpamCop) via DoH with the reversed IP.
 *
 * Results are stored in domains.monitors_json by the 6-hour cron and
 * surface on the DNS monitor screen and as alerts when issues appear.
 */

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

export interface MonitorResult {
  ssl: { ok: boolean; error: string };
  expiry: { date: string; days: number } | null;
  blocklists: { hits: number; total: number; listed: string[] };
}

/** 1. SSL: an HTTPS fetch that succeeds means the certificate is valid. */
async function checkSSL(domain: string): Promise<{ ok: boolean; error: string }> {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 8000);
    const res = await fetch('https://' + domain + '/', {
      method: 'HEAD',
      redirect: 'follow',
      signal: controller.signal,
      headers: { 'user-agent': 'PromptDNS-Monitor/1.0' },
    });
    clearTimeout(timer);
    // any HTTP response over TLS means the certificate is valid
    return { ok: true, error: '' };
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    if (msg.includes('abort') || msg.includes('timeout')) return { ok: false, error: 'Connection timed out' };
    if (msg.includes('certificate') || msg.includes('SSL') || msg.includes('TLS')) return { ok: false, error: msg.slice(0, 120) };
    // non-SSL connection failures (site down, DNS issues) are not SSL problems
    return { ok: true, error: '' };
  }
}

/** 2. Domain expiry: RDAP bootstrap lookup. */
async function checkExpiry(domain: string): Promise<{ date: string; days: number } | null> {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 8000);
    const res = await fetch('https://rdap.org/domain/' + encodeURIComponent(domain), {
      headers: { accept: 'application/rdap+json' },
      signal: controller.signal,
    });
    clearTimeout(timer);
    if (!res.ok) return null;
    const data = await res.json() as { events?: { eventAction?: string; eventDate?: string }[] };
    const events = data.events ?? [];
    const exp = events.find((e) => e.eventAction === 'expiration');
    if (!exp || !exp.eventDate) return null;
    const expiryDate = new Date(exp.eventDate);
    if (isNaN(expiryDate.getTime())) return null;
    const days = Math.ceil((expiryDate.getTime() - Date.now()) / (24 * 3600 * 1000));
    return { date: expiryDate.toISOString().slice(0, 10), days };
  } catch {
    return null;
  }
}

/** 3. Blocklists: resolve A record, then query DNSBLs via DoH. */
const DNSBLS: { zone: string; name: string }[] = [
  { zone: 'zen.spamhaus.org', name: 'Spamhaus Zen' },
  { zone: 'bl.spamcop.net', name: 'SpamCop' },
];

async function resolveA(domain: string): Promise<string | null> {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 6000);
    const res = await fetch(`https://cloudflare-dns.com/dns-query?name=${encodeURIComponent(domain)}&type=A`, {
      headers: { accept: 'application/dns-json' },
      signal: controller.signal,
    });
    clearTimeout(timer);
    const data = await res.json() as { Answer?: { type: number; data: string }[] };
    const a = (data.Answer ?? []).find((a) => a.type === 1);
    return a ? a.data : null;
  } catch {
    return null;
  }
}

function reversedIp(ip: string): string | null {
  const parts = ip.split('.');
  if (parts.length !== 4) return null; // IPv6 not supported by most DNSBLs
  return parts.reverse().join('.');
}

async function checkBlocklists(domain: string): Promise<{ hits: number; total: number; listed: string[] }> {
  const ip = await resolveA(domain);
  if (!ip) return { hits: 0, total: DNSBLS.length, listed: [] };
  const rev = reversedIp(ip);
  if (!rev) return { hits: 0, total: DNSBLS.length, listed: [] };
  let hits = 0;
  const listed: string[] = [];
  const results = await Promise.allSettled(
    DNSBLS.map(async (bl) => {
      const query = rev + '.' + bl.zone;
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 6000);
      const res = await fetch(`https://cloudflare-dns.com/dns-query?name=${encodeURIComponent(query)}&type=A`, {
        headers: { accept: 'application/dns-json' },
        signal: controller.signal,
      });
      clearTimeout(timer);
      const data = await res.json() as { Status?: number; Answer?: { data: string }[] };
      // NXDOMAIN (Status 3) = not listed; a 127.0.0.x answer = listed
      if (data.Status === 0 && data.Answer && data.Answer.some((a) => a.data.startsWith('127.0.'))) {
        listed.push(bl.name);
      }
    }),
  );
  hits = listed.length;
  return { hits, total: DNSBLS.length, listed };
}

/** Run all three checks for a domain. */
export async function runMonitors(domain: string): Promise<MonitorResult> {
  const [ssl, expiry, blocklists] = await Promise.all([
    checkSSL(domain),
    checkExpiry(domain),
    checkBlocklists(domain),
  ]);
  return { ssl, expiry, blocklists };
}

/** POST /api/domains/monitors?id=N - run monitors on demand and return results. */
export async function handleMonitorsRefresh(request: Request, env: Env): Promise<Response> {
  if (request.method !== 'POST') return json({ ok: false, error: 'POST only.' }, 405);
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  const { getUserBySession } = await import('./auth');
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);
  const raw = new URL(request.url).searchParams.get('id');
  const id = raw ? Number.parseInt(raw, 10) : Number.NaN;
  if (!Number.isInteger(id)) return json({ ok: false, error: 'Missing domain id.' }, 400);

  const owned = await env.DB
    .prepare('SELECT id, domain FROM domains WHERE id = ?1 AND user_id = ?2')
    .bind(id, user.id)
    .first<{ id: number; domain: string }>();
  if (!owned) return json({ ok: false, error: 'Domain not found on your list.' }, 404);

  const result = await runMonitors(owned.domain);
  await env.DB
    .prepare("UPDATE domains SET monitors_json = ?2, monitored_at = datetime('now') WHERE id = ?1")
    .bind(owned.id, JSON.stringify(result))
    .run();
  return json({ ok: true, monitors: result });
}
