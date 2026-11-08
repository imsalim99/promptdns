/**
 * worker/checks/rdap.ts
 *
 * Shared RDAP module: IANA bootstrap resolution (RFC 9224), RDAP JSON
 * parsing (RFC 9083), and honest unsupported-TLD handling.
 * One-way imports only; imported by the /api/check/rdap endpoint and
 * later by the Phase 3 dashboard expiry monitor.
 */

const BOOTSTRAP_URL = 'https://data.iana.org/rdap/dns.json';
const BOOTSTRAP_TTL_MS = 24 * 3600 * 1000;
const RDAP_TIMEOUT_MS = 8000;

export interface RdapEvent { eventAction: string; eventDate: string }
export interface RdapEntityPublicId { type: string; identifier: string }

export interface RdapResult {
  domain: string;
  status: 'ok' | 'unsupported_tld' | 'date_redacted' | 'not_found' | 'error';
  /** Why a non-ok state happened, for direct display. */
  note: string;
  /** Authoritative RDAP endpoint that served the answer. */
  sourceUrl: string | null;
  events: { registration: string | null; expiration: string | null; lastChanged: string | null };
  registrar: { name: string | null; ianaId: string | null };
  statuses: string[];
  nameservers: string[];
}

interface BootstrapEntry { tld: string[]; url: string[] }
let bootstrapCache: { at: number; entries: BootstrapEntry[] } | null = null;

async function getBootstrap(): Promise<BootstrapEntry[]> {
  if (bootstrapCache && Date.now() - bootstrapCache.at < BOOTSTRAP_TTL_MS) return bootstrapCache.entries;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), RDAP_TIMEOUT_MS);
  try {
    const res = await fetch(BOOTSTRAP_URL, { signal: controller.signal });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const j = (await res.json()) as { services: [string[], string[]][] };
    const entries: BootstrapEntry[] = j.services.map(([tlds, urls]) => ({ tld: tlds, url: urls }));
    bootstrapCache = { at: Date.now(), entries };
    return entries;
  } finally {
    clearTimeout(timer);
  }
}

/** Longest-suffix match: a .co.uk domain resolves through the uk entry. */
function rdapBaseFor(domain: string, entries: BootstrapEntry[]): string | null {
  const labels = domain.split('.');
  for (let i = 0; i < labels.length; i++) {
    const suffix = labels.slice(i).join('.').toLowerCase();
    for (const e of entries) {
      if (e.tld.some((t) => t.toLowerCase() === suffix)) return e.url[0] ?? null;
    }
  }
  return null;
}

function stripDot(s: string): string {
  return s.replace(/\.$/, '');
}

/** Parse an RFC 9083 RDAP domain response into the fields we report. */
function parseRdapResponse(domain: string, j: any, sourceUrl: string): RdapResult {
  const events: RdapResult['events'] = { registration: null, expiration: null, lastChanged: null };
  for (const e of (j.events ?? []) as RdapEvent[]) {
    const action = String(e.eventAction ?? '').toLowerCase();
    if (action === 'registration' && !events.registration) events.registration = e.eventDate ?? null;
    else if (action === 'expiration' && !events.expiration) events.expiration = e.eventDate ?? null;
    else if ((action === 'last changed' || action === 'last update of rdap database') && !events.lastChanged) events.lastChanged = e.eventDate ?? null;
  }
  let registrarName: string | null = null;
  let registrarId: string | null = null;
  for (const ent of (j.entities ?? []) as any[]) {
    const roles: string[] = ent.roles ?? [];
    if (!roles.includes('registrar')) continue;
    for (const pid of (ent.publicIds ?? []) as RdapEntityPublicId[]) {
      if (/iana/i.test(pid.type ?? '') && !registrarId) registrarId = pid.identifier ?? null;
    }
    const vcard = ent.vcardArray;
    if (Array.isArray(vcard) && Array.isArray(vcard[1])) {
      for (const field of vcard[1]) {
        if (field[0] === 'fn' && typeof field[3] === 'string' && !registrarName) registrarName = field[3];
      }
    }
  }
  const statuses: string[] = (j.status ?? []).map(String);
  const nameservers: string[] = (j.nameservers ?? []).map((n: any) => n.ldhName).filter(Boolean).map(stripDot);
  const dateRedacted = !events.registration && statuses.some((s) => /redacted/i.test(s)) === false && (j.notes ?? []).length > 0;
  return {
    domain,
    status: 'ok',
    note: dateRedacted ? 'The registry response carries no registration event; this ccTLD withholds creation dates.' : '',
    sourceUrl,
    events,
    registrar: { name: registrarName, ianaId: registrarId },
    statuses,
    nameservers,
  };
}

/** Query RDAP for one domain with bootstrap resolution and rdap.org fallback. */
export async function queryRdap(domain: string): Promise<RdapResult> {
  let entries: BootstrapEntry[] = [];
  try {
    entries = await getBootstrap();
  } catch {
    entries = []; // bootstrap unreachable: fall straight through to rdap.org
  }
  const base = rdapBaseFor(domain, entries);
  const attempts: string[] = base
    ? [base.replace(/\/$/, '') + '/domain/' + domain, 'https://rdap.org/domain/' + domain]
    : ['https://rdap.org/domain/' + domain];

  let lastErr = 'unknown error';
  for (const url of attempts) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), RDAP_TIMEOUT_MS);
    try {
      const res = await fetch(url, {
        signal: controller.signal,
        headers: { accept: 'application/rdap+json, application/json' },
      });
      if (res.status === 404) {
        return { domain, status: 'not_found', note: 'The registry reports this domain as not found (unregistered or dropped).', sourceUrl: url, events: { registration: null, expiration: null, lastChanged: null }, registrar: { name: null, ianaId: null }, statuses: [], nameservers: [] };
      }
      if (!res.ok) { lastErr = 'HTTP ' + res.status + ' from ' + url; continue; }
      const j = await res.json();
      const parsed = parseRdapResponse(domain, j, url);
      if (!parsed.events.registration && parsed.statuses.length === 0 && (parsed.nameservers.length === 0)) {
        // Some registries answer 200 with an empty shell: treat as redacted.
        return { ...parsed, status: 'date_redacted', note: 'The registry returned no registration event: creation dates are withheld by policy for this TLD.' };
      }
      return parsed;
    } catch (e: unknown) {
      lastErr = e instanceof Error ? e.message : String(e);
    } finally {
      clearTimeout(timer);
    }
  }
  return { domain, status: 'error', note: 'RDAP lookup failed: ' + lastErr.slice(0, 120), sourceUrl: null, events: { registration: null, expiration: null, lastChanged: null }, registrar: { name: null, ianaId: null }, statuses: [], nameservers: [] };
}

/** True when a TLD is known to have no bootstrap entry (honest ccTLD state). */
export async function isUnsupportedTld(domain: string): Promise<boolean> {
  try {
    const entries = await getBootstrap();
    return rdapBaseFor(domain, entries) === null;
  } catch {
    return false;
  }
}
