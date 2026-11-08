/**
 * worker/checks/rdap-api.ts
 *
 * JSON endpoint behind /domain-age-checker/ (and the Phase 3 expiry monitor):
 *   GET /api/check/rdap?domains=<d1,d2,...>   1 to 10 domains
 * Also behind /ip-lookup/:
 *   GET /api/check/rdap?ip=<address>          one IP network (RIR data)
 *
 * One-way imports only (rdap.ts, ai-crawlers.ts for the normalizer).
 * Concurrency capped at 4 parallel RDAP queries; 10 minute per-domain cache.
 */

import { queryRdap, isUnsupportedTld, queryIpRdap, isPlausibleIp, type RdapResult, type IpRdapResult } from './rdap';
import { normalizeDomain } from './ai-crawlers';

const CACHE_TTL_MS = 10 * 60_000;
const CACHE_MAX = 300;
const MAX_DOMAINS = 10;
const MAX_PARALLEL = 4;
const rdapCache = new Map<string, { at: number; result: RdapResult }>();
const ipRdapCache = new Map<string, { at: number; result: IpRdapResult }>();

/** GET /api/check/rdap?ip=<address> : RIR registration data for one IP network. */
async function handleIpRdapCheck(ipRaw: string): Promise<Response> {
  const ip = ipRaw.trim();
  if (!isPlausibleIp(ip)) {
    return Response.json({ ok: false, error: 'Provide a valid IPv4 or IPv6 address.' }, { status: 400 });
  }
  const key = ip.toLowerCase();
  const hit = ipRdapCache.get(key);
  if (hit && Date.now() - hit.at < CACHE_TTL_MS) return Response.json({ ok: true, result: hit.result });

  const result = await queryIpRdap(ip);
  ipRdapCache.set(key, { at: Date.now(), result });
  if (ipRdapCache.size > CACHE_MAX) {
    const oldest = ipRdapCache.keys().next().value;
    if (oldest) ipRdapCache.delete(oldest);
  }
  return Response.json({ ok: true, result });
}

export async function handleRdapCheck(request: Request, _env: unknown): Promise<Response> {
  const url = new URL(request.url);

  const ipParam = url.searchParams.get('ip');
  if (ipParam) return handleIpRdapCheck(ipParam);

  const raw = url.searchParams.get('domains') || '';
  const domains: string[] = [];
  for (const part of raw.split(/[,\s]+/)) {
    if (!part) continue;
    const d = normalizeDomain(part);
    if (d && !domains.includes(d)) domains.push(d);
    if (domains.length >= MAX_DOMAINS) break;
  }
  if (domains.length === 0) {
    return Response.json({ ok: false, error: 'Provide 1 to 10 valid domains, comma or space separated.' }, { status: 400 });
  }

  const results: RdapResult[] = [];
  const queue = [...domains];
  const worker = async () => {
    while (queue.length) {
      const d = queue.shift()!;
      const hit = rdapCache.get(d);
      if (hit && Date.now() - hit.at < CACHE_TTL_MS) { results.push(hit.result); continue; }
      let result: RdapResult;
      if (await isUnsupportedTld(d)) {
        result = { domain: d, status: 'unsupported_tld', note: 'No RDAP server is published for this TLD in the IANA bootstrap: registry data is not available over RDAP.', sourceUrl: null, events: { registration: null, expiration: null, lastChanged: null }, registrar: { name: null, ianaId: null }, statuses: [], nameservers: [] };
      } else {
        result = await queryRdap(d);
        // Upgrade the honest ccTLD state when the answer carries no dates.
        if (result.status === 'ok' && !result.events.registration) {
          result = { ...result, status: 'date_redacted', note: result.note || 'The registry response carries no registration event: creation dates are withheld by policy for this TLD.' };
        }
      }
      rdapCache.set(d, { at: Date.now(), result });
      if (rdapCache.size > CACHE_MAX) {
        const oldest = rdapCache.keys().next().value;
        if (oldest) rdapCache.delete(oldest);
      }
      results.push(result);
    }
  };
  await Promise.all([worker(), worker(), worker(), worker()]);

  // Preserve the caller's domain order
  const ordered = domains.map((d) => results.find((r) => r.domain === d)!).filter(Boolean);
  return Response.json({ ok: true, count: ordered.length, results: ordered });
}
