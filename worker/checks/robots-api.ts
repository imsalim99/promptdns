/**
 * worker/checks/robots-api.ts
 *
 * JSON endpoint behind /robots-txt-checker/:
 *   GET  /api/check/robots?domain=<domain>  fetch + parse the live file
 *   POST /api/check/robots { "content": "..." }  parse pasted content
 *
 * One-way imports only (robots.ts, ai-crawlers.ts for the shared domain
 * normalizer). Nothing is stored; a short in-memory cache keeps repeat
 * fetches polite.
 */

import { fetchRobots, parseRobots, type RobotsFetch } from './robots';
import { normalizeDomain } from './ai-crawlers';

const CACHE_TTL_MS = 120_000;
const CACHE_MAX = 50;
const robotsCache = new Map<string, { at: number; payload: unknown }>();

export async function handleRobotsCheck(request: Request, env: { ASSETS?: { fetch(request: Request): Promise<Response> } }): Promise<Response> {
  if (request.method === 'POST') {
    const body = (await request.json().catch(() => null)) as { content?: string } | null;
    if (!body || typeof body.content !== 'string' || !body.content.trim()) {
      return Response.json({ ok: false, error: 'Provide robots.txt content to parse.' }, { status: 400 });
    }
    const parsed = parseRobots(body.content.slice(0, 600_000));
    return Response.json({
      ok: true,
      mode: 'content',
      robots: { classification: 'ok', status: null, note: '', finalUrl: null, bytes: parsed.bytes, truncated: parsed.truncated },
      groups: parsed.groups,
      sitemaps: parsed.sitemaps,
      errors: parsed.errors,
      notes: parsed.notes,
      managed: parsed.managed,
      contentSignals: parsed.contentSignals,
    });
  }

  const url = new URL(request.url);
  const domain = normalizeDomain(url.searchParams.get('domain') || '');
  if (!domain) {
    return Response.json({ ok: false, error: 'Provide a valid domain, e.g. example.com.' }, { status: 400 });
  }
  const cacheKey = 'GET:' + domain;
  const hit = robotsCache.get(cacheKey);
  if (hit && Date.now() - hit.at < CACHE_TTL_MS) return Response.json(hit.payload);

  // A Worker fetching its own zone re-enters the same Worker route, which
  // Cloudflare blocks in production ( surfacing as 522 ): serve self-domain
  // scans straight from the asset bundle instead of the network.
  const selfHost = normalizeDomain(url.hostname) || '';
  let fetched: RobotsFetch;
  if (env.ASSETS && domain === selfHost) {
    const res = await env.ASSETS.fetch(new Request('https://' + domain + '/robots.txt'));
    const body = res.ok ? await res.text() : null;
    fetched = {
      status: res.status,
      classification: res.ok ? 'ok' : res.status >= 400 && res.status < 500 ? 'unavailable-4xx' : 'unreachable-5xx',
      body,
      finalUrl: 'https://' + domain + '/robots.txt',
      redirects: 0,
      note: 'self-domain scan: served from the same asset bundle',
    };
  } else {
    fetched = await fetchRobots(domain);
  }
  if (fetched.body === null) {
    const payload = {
      ok: true,
      mode: 'domain',
      robots: { classification: fetched.classification, status: fetched.status, note: fetched.note, finalUrl: fetched.finalUrl, bytes: 0, truncated: false },
      groups: [], sitemaps: [], errors: [] as string[], notes: [] as string[], managed: false, contentSignals: false,
    };
    return Response.json(payload);
  }
  const parsed = parseRobots(fetched.body);
  const payload = {
    ok: true,
    mode: 'domain',
    robots: { classification: fetched.classification, status: fetched.status, note: fetched.note, finalUrl: fetched.finalUrl, bytes: parsed.bytes, truncated: parsed.truncated },
    groups: parsed.groups,
    sitemaps: parsed.sitemaps,
    errors: parsed.errors,
    notes: parsed.notes,
    managed: parsed.managed,
    contentSignals: parsed.contentSignals,
  };
  robotsCache.set(cacheKey, { at: Date.now(), payload });
  if (robotsCache.size > CACHE_MAX) {
    const oldest = robotsCache.keys().next().value;
    if (oldest) robotsCache.delete(oldest);
  }
  return Response.json(payload);
}
