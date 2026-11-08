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

/* ------------------------------------------------------------------ */
/* IP network RDAP (RFC 9083 ip object).                               */
/* rdap.org 403-blocks Cloudflare Worker egress, so the authoritative  */
/* RIR server is resolved from the IANA RFC 9224 ipv4/ipv6 bootstrap   */
/* files with CIDR range matching; rdap.org remains a dev fallback.    */
/* ------------------------------------------------------------------ */

export interface IpRdapResult {
  query: string;
  status: 'ok' | 'not_found' | 'error';
  note: string;
  /** Authoritative RIR endpoint that served the final answer. */
  sourceUrl: string | null;
  handle: string | null;
  netName: string | null;
  netType: string | null;
  country: string | null;
  startAddress: string | null;
  endAddress: string | null;
  events: { registration: string | null; lastChanged: string | null };
  org: string | null;
  abuseEmail: string | null;
  statuses: string[];
}

/** Loose IP shape check: dotted quad, or something bracket-parseable as IPv6. */
export function isPlausibleIp(s: string): boolean {
  if (/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/.test(s)) {
    return s.split('.').every((o) => Number(o) <= 255);
  }
  if (!s.includes(':')) return false;
  try {
    const host = new URL('http://[' + s + ']/').hostname;
    return host.includes(':');
  } catch {
    return false;
  }
}

function vcardField(vcard: unknown, key: string): string | null {
  if (!Array.isArray(vcard) || !Array.isArray(vcard[1])) return null;
  for (const field of vcard[1] as unknown[][]) {
    if (field[0] === key && typeof field[3] === 'string') return field[3];
  }
  return null;
}

/* --- IANA IP address bootstrap (RFC 9224 ipv4.json / ipv6.json) ------ */
/* rdap.org 403-blocks Cloudflare Worker egress, so we resolve the       */
/* authoritative RIR server ourselves via CIDR range matching and keep   */
/* rdap.org only as a local-dev fallback.                                */

interface IpBootstrapEntry { prefixes: string[]; urls: string[] }
const IP_BOOTSTRAP_TTL_MS = 24 * 3600 * 1000;
const ipBootstrapCache: { v4: { at: number; entries: IpBootstrapEntry[] } | null; v6: { at: number; entries: IpBootstrapEntry[] } | null } = { v4: null, v6: null };

/** Fetch and cache one family's bootstrap file; each family gets its own timer. */
async function getIpBootstrap(family: 'v4' | 'v6'): Promise<IpBootstrapEntry[]> {
  const cached = ipBootstrapCache[family];
  if (cached && Date.now() - cached.at < IP_BOOTSTRAP_TTL_MS) return cached.entries;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), RDAP_TIMEOUT_MS);
  try {
    const res = await fetch('https://data.iana.org/rdap/' + family + '.json', { signal: controller.signal });
    if (!res.ok) throw new Error('bootstrap HTTP ' + res.status);
    const j = (await res.json()) as { services: [string[], string[]][] };
    const entries: IpBootstrapEntry[] = j.services.map(([prefixes, urls]) => ({ prefixes, urls }));
    ipBootstrapCache[family] = { at: Date.now(), entries };
    return entries;
  } finally {
    clearTimeout(timer);
  }
}

function v4ToInt(ip: string): number {
  const [a, b, c, d] = ip.split('.').map(Number);
  return ((a << 24) | (b << 16) | (c << 8) | d) >>> 0;
}

/** IPv6 to BigInt; returns null for anything not 8 clean hex groups. */
function v6ToBigInt(ip: string): bigint | null {
  const s = ip.toLowerCase().split('%')[0];
  let groups: string[];
  if (s.includes('::')) {
    const [l, r] = s.split('::');
    const head = l ? l.split(':') : [];
    const tail = r ? r.split(':') : [];
    const missing = 8 - head.length - tail.length;
    if (missing < 1) return null;
    groups = [...head, ...Array<string>(missing).fill('0'), ...tail];
  } else {
    groups = s.split(':');
    if (groups.length !== 8) return null;
  }
  let out = 0n;
  for (const g of groups) {
    if (!/^[0-9a-f]{1,4}$/.test(g)) return null;
    out = (out << 16n) | BigInt(parseInt(g, 16));
  }
  return out;
}

/** True when the CIDR prefix contains the query address. */
function cidrMatch(prefix: string, ip: string): boolean {
  const slash = prefix.indexOf('/');
  if (slash === -1) return false;
  const base = prefix.slice(0, slash);
  const len = Number(prefix.slice(slash + 1));
  if (!Number.isFinite(len)) return false;
  if (base.includes(':')) {
    const b = v6ToBigInt(base);
    const q = v6ToBigInt(ip);
    if (b === null || q === null || len < 0 || len > 128) return false;
    const shift = BigInt(128 - len);
    return (b >> shift) === (q >> shift);
  }
  if (!/^(\d{1,3}\.){3}\d{1,3}$/.test(base) || len < 0 || len > 32) return false;
  const b = v4ToInt(base);
  const q = v4ToInt(ip);
  const mask = len === 0 ? 0 : (0xFFFFFFFF << (32 - len)) >>> 0;
  return (b & mask) === (q & mask);
}

/** Query RDAP for one IP network: IANA bootstrap resolution, rdap.org fallback. */
export async function queryIpRdap(ip: string): Promise<IpRdapResult> {
  const attempts: string[] = [];
  try {
    const table = await getIpBootstrap(ip.includes(':') ? 'v6' : 'v4');
    const entry = table.find((e) => e.prefixes.some((p) => cidrMatch(p, ip)));
    if (entry?.urls[0]) attempts.push(entry.urls[0].replace(/\/$/, '') + '/ip/' + encodeURIComponent(ip));
  } catch {
    // bootstrap unreachable: fall straight through to rdap.org
  }
  attempts.push('https://rdap.org/ip/' + encodeURIComponent(ip));

  let lastErr = 'unknown error';
  let firstErr: string | null = null;
  for (const url of attempts) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), RDAP_TIMEOUT_MS);
    try {
      const res = await fetch(url, {
        signal: controller.signal,
        redirect: 'follow',
        headers: { accept: 'application/rdap+json, application/json' },
      });
      const servedBy = res.url && res.url !== url ? res.url : url;
      if (res.status === 404) {
        return { query: ip, status: 'not_found', note: 'No RIR network object covers this address in RDAP.', sourceUrl: servedBy, handle: null, netName: null, netType: null, country: null, startAddress: null, endAddress: null, events: { registration: null, lastChanged: null }, org: null, abuseEmail: null, statuses: [] };
      }
      if (!res.ok) {
        lastErr = 'HTTP ' + res.status + ' from ' + servedBy.slice(0, 80);
        if (!firstErr) firstErr = lastErr;
        continue;
      }
      const j: any = await res.json();
      const events: IpRdapResult['events'] = { registration: null, lastChanged: null };
      for (const e of (j.events ?? []) as RdapEvent[]) {
        const action = String(e.eventAction ?? '').toLowerCase();
        if (action === 'registration' && !events.registration) events.registration = e.eventDate ?? null;
        else if ((action === 'last changed' || action === 'last update of rdap database') && !events.lastChanged) events.lastChanged = e.eventDate ?? null;
      }
      let org: string | null = null;
      let abuseEmail: string | null = null;
      for (const ent of (j.entities ?? []) as any[]) {
        const roles: string[] = ent.roles ?? [];
        const fn = vcardField(ent.vcardArray, 'fn');
        if (roles.includes('registrant') && fn && !org) org = fn;
        if (roles.includes('abuse')) {
          const email = vcardField(ent.vcardArray, 'email');
          if (email && !abuseEmail) abuseEmail = email;
        }
      }
      // Some RIRs put the network name only on the top-level object.
      if (!org) org = vcardField(j.vcardArray, 'fn');
      return {
        query: ip,
        status: 'ok',
        note: '',
        sourceUrl: servedBy,
        handle: j.handle ? String(j.handle) : null,
        netName: j.name ? String(j.name) : null,
        netType: j.type ? String(j.type) : null,
        country: j.country ? String(j.country) : null,
        startAddress: j.startAddress ? String(j.startAddress) : null,
        endAddress: j.endAddress ? String(j.endAddress) : null,
        events,
        org,
        abuseEmail,
        statuses: (j.status ?? []).map(String),
      };
    } catch (e: unknown) {
      lastErr = e instanceof Error ? e.message : String(e);
      if (!firstErr) firstErr = lastErr;
    } finally {
      clearTimeout(timer);
    }
  }
  return { query: ip, status: 'error', note: 'RDAP lookup failed: ' + (firstErr ?? lastErr).slice(0, 120), sourceUrl: null, handle: null, netName: null, netType: null, country: null, startAddress: null, endAddress: null, events: { registration: null, lastChanged: null }, org: null, abuseEmail: null, statuses: [] };
}
