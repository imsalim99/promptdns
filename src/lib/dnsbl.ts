/**
 * DNSBL / email blacklist checks via DoH.
 * Important honesty rule: several blocklists (Spamhaus, URIBL) refuse queries
 * from large public resolvers and URIBL returns 127.0.0.1 as a "blocked
 * query" marker, we surface those as "not checkable via public resolver"
 * instead of false "listed" results.
 */
import { lookup, RESOLVERS } from './doh';

export interface DnsblList {
  name: string;
  zone: string;
  scope: 'domain' | 'ip';
  note: string;
  blockedMarker?: string; // A-record value that means "query refused", not listed
}

export const DOMAIN_LISTS: DnsblList[] = [
  { name: 'SURBL Multi', zone: 'multi.surbl.org', scope: 'domain', note: 'Spam sites + abused registrars + malware' },
  { name: 'URIBL Multi', zone: 'multi.uribl.com', scope: 'domain', note: 'URI blocklist composite', blockedMarker: '127.0.0.1' },
  { name: 'URIBL Black', zone: 'black.uribl.com', scope: 'domain', note: 'Active spam sources', blockedMarker: '127.0.0.1' },
  { name: 'URIBL Grey', zone: 'grey.uribl.com', scope: 'domain', note: 'Mixed sources (watchlist)', blockedMarker: '127.0.0.1' },
  { name: 'Spamhaus DBL', zone: 'dbl.spamhaus.org', scope: 'domain', note: 'Domain Block List (spam + phishing + malware)' },
  { name: 'Spamrat Dyna', zone: 'dyna.spamrats.com', scope: 'domain', note: 'Dynamic/generic PTR space' },
  { name: 'PSBL', zone: 'psbl.surriel.com', scope: 'ip', note: 'Passive spam blocklist (friendly to public queries)' },
];

export const IP_LISTS: DnsblList[] = [
  { name: 'Spamhaus ZEN', zone: 'zen.spamhaus.org', scope: 'ip', note: 'SBL+XBL+PBL composite' },
  { name: 'Barracuda BBRB', zone: 'b.barracudacentral.org', scope: 'ip', note: 'Barracuda reputation' },
  { name: 'SpamCop', zone: 'bl.spamcop.net', scope: 'ip', note: 'Spamtrap-driven' },
  { name: 'SORBS Spam', zone: 'dnsbl.sorbs.net', scope: 'ip', note: 'SORBS composite' },
  { name: 'Spamrat Dyna', zone: 'dyna.spamrats.com', scope: 'ip', note: 'Dynamic IP space' },
  { name: 'PSBL', zone: 'psbl.surriel.com', scope: 'ip', note: 'Passive spam blocklist' },
];

export interface DnsblResult {
  list: string;
  zone: string;
  note: string;
  status: 'clear' | 'listed' | 'blocked' | 'error';
  detail: string;
}

export function reverseIp(ip: string): string {
  if (ip.includes(':')) {
    // IPv6: expand + nibble reverse
    const parts = ip.split('::');
    const head = parts[0] ? parts[0].split(':') : [];
    const tail = parts[1] ? parts[1].split(':') : [];
    const fill = new Array(8 - head.length - tail.length).fill('0');
    const full = [...head, ...fill, ...tail]
      .map((h) => h.padStart(4, '0'))
      .join('')
      .split('')
      .reverse()
      .join('.');
    return `${full}.ip6.arpa`;
  }
  return `${ip.split('.').reverse().join('.')}.in-addr.arpa`;
}

async function checkZone(query: string, list: DnsblList): Promise<DnsblResult> {
  const res = await lookup(`${query}.${list.zone}`, 'A', RESOLVERS[0]);
  const a = res.answers.find((x) => x.type === 1)?.data;

  if (res.ok && a) {
    if (list.blockedMarker && a === list.blockedMarker) {
      return { list: list.name, zone: list.zone, note: list.note, status: 'blocked', detail: 'This list refuses queries via public resolvers, check it on the list\u2019s own site.' };
    }
    if (a.startsWith('127.')) {
      return { list: list.name, zone: list.zone, note: list.note, status: 'listed', detail: `LISTED (returns ${a})` };
    }
    return { list: list.name, zone: list.zone, note: list.note, status: 'clear', detail: `Not listed (returns ${a})` };
  }
  if (res.status === 3) {
    return { list: list.name, zone: list.zone, note: list.note, status: 'clear', detail: 'Not listed (no record)' };
  }
  if (res.status === 2 || res.status === 5 || res.statusText === 'TIMEOUT') {
    return { list: list.name, zone: list.zone, note: list.note, status: 'blocked', detail: 'List refuses public-resolver queries (SERVFAIL/REFUSED), verify on the list\u2019s site.' };
  }
  return { list: list.name, zone: list.zone, note: list.note, status: 'error', detail: res.statusText };
}

export async function checkDomainBlacklists(domain: string, onProgress?: (m: string) => void): Promise<DnsblResult[]> {
  const out: DnsblResult[] = [];
  for (const list of DOMAIN_LISTS) {
    onProgress?.(`Checking ${list.name}…`);
    out.push(await checkZone(domain, list));
  }
  return out;
}

export async function checkIpBlacklists(ip: string, onProgress?: (m: string) => void): Promise<DnsblResult[]> {
  const rev = reverseIp(ip);
  const out: DnsblResult[] = [];
  for (const list of IP_LISTS) {
    onProgress?.(`Checking ${list.name}…`);
    out.push(await checkZone(rev, list));
  }
  return out;
}
