/**
 * PromptDNS shared DoH (DNS-over-HTTPS) lookup engine.
 * Powers all 54 tools. Client-side only, zero backend, zero API keys.
 *
 * JSON DoH endpoints used (all send CORS headers, free, no rate-limit issues
 * for normal use because queries run from each visitor's browser):
 *  - Cloudflare  https://cloudflare-dns.com/dns-query  (Accept: application/dns-json)
 *  - Google      https://dns.google/resolve
 *  - AliDNS      https://dns.alidns.com/resolve
 */

export type RecordType =
  | 'A' | 'AAAA' | 'CNAME' | 'MX' | 'TXT' | 'NS' | 'SOA'
  | 'PTR' | 'SRV' | 'CAA' | 'DS' | 'DNSKEY';

export interface DohAnswer {
  name: string;
  type: number;
  TTL: number;
  data: string;
}

export interface DohResponse {
  Status: number; // 0=NOERROR, 3=NXDOMAIN
  Answer?: DohAnswer[];
  Authority?: DohAnswer[];
}

export interface Resolver {
  id: string;
  name: string;
  url: (name: string, type: RecordType) => string;
  /** Cloudflare requires the JSON Accept header; Google and AliDNS /resolve are plain JSON */
  acceptHeader?: string;
}

export const RESOLVERS: Resolver[] = [
  {
    id: 'cloudflare',
    name: 'Cloudflare 1.1.1.1',
    url: (n, t) => `https://cloudflare-dns.com/dns-query?name=${encodeURIComponent(n)}&type=${t}`,
    acceptHeader: 'application/dns-json',
  },
  {
    id: 'google',
    name: 'Google 8.8.8.8',
    url: (n, t) => `https://dns.google/resolve?name=${encodeURIComponent(n)}&type=${t}`,
  },
  {
    id: 'alidns',
    name: 'AliDNS 223.5.5.5',
    url: (n, t) => `https://dns.alidns.com/resolve?name=${encodeURIComponent(n)}&type=${t}`,
  },
];

export const DEFAULT_RESOLVER = RESOLVERS[0];

const TIMEOUT_MS = 8000;

async function fetchDoh(resolver: Resolver, name: string, type: RecordType): Promise<DohResponse> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(resolver.url(name, type), {
      headers: resolver.acceptHeader ? { Accept: resolver.acceptHeader } : {},
      signal: controller.signal,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as DohResponse;
  } finally {
    clearTimeout(timer);
  }
}

export interface LookupResult {
  resolver: string;
  ok: boolean;
  status: number;
  statusText: string;
  answers: DohAnswer[];
  ms: number;
}

const STATUS_TEXT: Record<number, string> = {
  0: 'NOERROR',
  1: 'FORMERR',
  2: 'SERVFAIL',
  3: 'NXDOMAIN',
  5: 'REFUSED',
};

/** Single lookup against one resolver. */
export async function lookup(
  name: string,
  type: RecordType,
  resolver: Resolver = DEFAULT_RESOLVER,
): Promise<LookupResult> {
  const t0 = performance.now();
  try {
    const json = await fetchDoh(resolver, name, type);
    return {
      resolver: resolver.name,
      ok: json.Status === 0,
      status: json.Status,
      statusText: STATUS_TEXT[json.Status] ?? `STATUS ${json.Status}`,
      answers: json.Answer ?? [],
      ms: Math.round(performance.now() - t0),
    };
  } catch (e) {
    return {
      resolver: resolver.name,
      ok: false,
      status: -1,
      statusText: e instanceof Error && e.name === 'AbortError' ? 'TIMEOUT' : 'NETWORK ERROR',
      answers: [],
      ms: Math.round(performance.now() - t0),
    };
  }
}

export interface PropagationResult extends LookupResult {
  answerKey: string;
}

function answerKey(answers: DohAnswer[]): string {
  return answers
    .map((a) => a.data)
    .sort()
    .join('|');
}

/** Query all resolvers in parallel for propagation checking. */
export async function propagationCheck(
  name: string,
  type: RecordType,
  resolvers: Resolver[] = RESOLVERS,
): Promise<{ results: PropagationResult[]; agreeRatio: number; propagated: boolean }> {
  const results = await Promise.all(
    resolvers.map(async (r) => {
      const base = await lookup(name, type, r);
      return { ...base, answerKey: answerKey(base.answers) };
    }),
  );
  const successKeys = results.filter((r) => r.ok).map((r) => r.answerKey);
  const counts = new Map<string, number>();
  for (const k of successKeys) counts.set(k, (counts.get(k) ?? 0) + 1);
  const dominant = Math.max(0, ...counts.values());
  const agreeRatio = successKeys.length ? dominant / successKeys.length : 0;
  return { results, agreeRatio, propagated: agreeRatio >= 0.99 && successKeys.length === resolvers.length };
}

/** Human summary of answers for table display. */
export function summarize(answers: DohAnswer[], limit = 4): string {
  if (!answers.length) return 'n/a';
  const shown = answers.slice(0, limit).map((a) => a.data);
  return shown.length < answers.length ? `${shown.join(', ')} (+${answers.length - shown.length} more)` : shown.join(', ');
}

export const RECORD_TYPES: { value: RecordType; label: string }[] = [
  { value: 'A', label: 'A (IPv4 address)' },
  { value: 'AAAA', label: 'AAAA (IPv6 address)' },
  { value: 'CNAME', label: 'CNAME (alias)' },
  { value: 'MX', label: 'MX (mail server)' },
  { value: 'TXT', label: 'TXT (text/SPF/verification)' },
  { value: 'NS', label: 'NS (nameserver)' },
  { value: 'SOA', label: 'SOA (start of authority)' },
  { value: 'PTR', label: 'PTR (reverse DNS)' },
  { value: 'SRV', label: 'SRV (service)' },
  { value: 'CAA', label: 'CAA (certificate authority)' },
  { value: 'DS', label: 'DS (DNSSEC delegation)' },
  { value: 'DNSKEY', label: 'DNSKEY (DNSSEC key)' },
];

export function normalizeDomain(input: string): string {
  return input
    .trim()
    .replace(/^https?:\/\//, '')
    .replace(/\/.*$/, '')
    .replace(/\.$/, '')
    .toLowerCase();
}
