/**
 * worker/checks/asn-api.ts
 * GET /api/check/asn?q=<asn-or-ip-or-prefix-or-domain>
 */

import { asnLookup, type AsnResult } from './asn';
import { normalizeDomain } from './ai-crawlers';

const CACHE_TTL_MS = 10 * 60_000;
const CACHE_MAX = 200;
const cache = new Map<string, { at: number; result: AsnResult }>();

export async function handleAsnCheck(request: Request, _env: unknown): Promise<Response> {
  const url = new URL(request.url);
  const raw = (url.searchParams.get('q') || '').trim();
  if (!raw) {
    return Response.json({ ok: false, error: 'Provide an ASN (AS13335), IP (1.1.1.1), prefix (1.1.1.0/24), or domain name.' }, { status: 400 });
  }

  // Normalize domain inputs
  let query = raw;
  if (!/^AS?\d{1,10}$/i.test(raw) && !/^\d{1,3}(\.\d{1,3}){3}$/.test(raw) && !raw.includes(':')) {
    const d = normalizeDomain(raw);
    if (d && d.includes('.')) query = d;
  }

  const cacheKey = query.toLowerCase();
  const hit = cache.get(cacheKey);
  if (hit && Date.now() - hit.at < CACHE_TTL_MS) return Response.json({ ok: true, ...hit.result });

  const result = await asnLookup(query);
  cache.set(cacheKey, { at: Date.now(), result });
  if (cache.size > CACHE_MAX) {
    const oldest = cache.keys().next().value;
    if (oldest) cache.delete(oldest);
  }
  return Response.json({ ok: true, ...result });
}
