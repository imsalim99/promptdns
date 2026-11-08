/**
 * worker/checks/asn.ts
 *
 * Shared ASN lookup module: Team Cymru DoH TXT + RIPEstat + IANA reserved
 * classification. One-way imports only; imported by /api/check/asn and
 * later by the Phase 3 dashboard.
 */

export interface AsnResult {
  query: string;
  resolvedIp: string | null;
  status: 'ok' | 'private_asn' | 'reserved_asn' | 'documentation_asn' | 'error';
  note: string;
  asn: number | null;
  asnFormat: '16-bit' | '32-bit' | null;
  holder: string | null;
  country: string | null;
  rir: string | null;
  bgpPrefix: string | null;
  announcedPrefixes: { prefix: string; type: 'IPv4' | 'IPv6' }[];
  rpkiStatus: string | null;
  sources: string[];
  checkedAt: string;
}

// IANA reserved / private / documentation ASN classification (RFC 6793, 6996, 5398, 7300, 7607)
function classifyAsn(n: number): string | null {
  if (n === 0) return 'reserved_asn';
  if (n === 23456) return 'reserved_asn'; // AS_TRANS
  if (n >= 64496 && n <= 64511) return 'documentation_asn'; // RFC 5398
  if (n >= 64512 && n <= 65534) return 'private_asn'; // RFC 6996
  if (n === 65535) return 'reserved_asn';
  if (n >= 65536 && n <= 65551) return 'documentation_asn'; // RFC 5398 32-bit
  if (n >= 65552 && n <= 131071) return 'reserved_asn'; // IANA
  if (n >= 4200000000 && n <= 4294967294) return 'private_asn'; // RFC 6996 32-bit
  if (n === 4294967295) return 'reserved_asn';
  return null;
}

async function cymruOrigin(ip: string): Promise<{ asn: number; prefix: string; country: string; rir: string; date: string } | null> {
  try {
    let name: string;
    if (ip.includes(':')) {
      const expanded = expandV6(ip);
      if (!expanded) return null;
      name = expanded.split('').reverse().join('.') + '.origin6.asn.cymru.com';
    } else {
      name = ip.split('.').reverse().join('.') + '.origin.asn.cymru.com';
    }
    const res = await fetch(`https://cloudflare-dns.com/dns-query?name=${encodeURIComponent(name)}&type=TXT`, {
      headers: { Accept: 'application/dns-json' },
      signal: AbortSignal.timeout(6000),
    });
    const j: any = await res.json();
    const txt = j.Answer?.find((a: any) => a.type === 16)?.data?.replace(/^"|"$/g, '');
    if (!txt) return null;
    const firstLine = txt.split('\n')[0].trim();
    const f = firstLine.split('|').map((s: string) => s.trim());
    if (!f[0]) return null;
    return { asn: Number(f[0]), prefix: f[1] ?? '', country: f[2] ?? '', rir: f[3] ?? '', date: f[4] ?? '' };
  } catch { return null; }
}

async function cymruAsnName(asn: number): Promise<string | null> {
  try {
    const res = await fetch(`https://cloudflare-dns.com/dns-query?name=AS${asn}.asn.cymru.com&type=TXT`, {
      headers: { Accept: 'application/dns-json' },
      signal: AbortSignal.timeout(6000),
    });
    const j: any = await res.json();
    const txt = j.Answer?.find((a: any) => a.type === 16)?.data?.replace(/^"|"$/g, '');
    if (!txt) return null;
    const f = txt.split('|').map((s: string) => s.trim());
    return f[4] ?? null;
  } catch { return null; }
}

async function ripestat(endpoint: string): Promise<any | null> {
  try {
    const res = await fetch(`https://stat.ripe.net/data/${endpoint}`, {
      headers: { Accept: 'application/json' },
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) return null;
    const j: any = await res.json();
    return j.data ?? null;
  } catch { return null; }
}

async function resolveDomain(domain: string): Promise<string | null> {
  try {
    const res = await fetch(`https://cloudflare-dns.com/dns-query?name=${encodeURIComponent(domain)}&type=A`, {
      headers: { Accept: 'application/dns-json' },
      signal: AbortSignal.timeout(6000),
    });
    const j: any = await res.json();
    return j.Answer?.find((a: any) => a.type === 1)?.data ?? null;
  } catch { return null; }
}

function expandV6(addr: string): string | null {
  try {
    const url = new URL('http://[' + addr + ']');
    const groups = url.hostname.split(':');
    if (groups.length !== 8) return null;
    return groups.map((g) => g.padStart(4, '0')).join('').toLowerCase();
  } catch { return null; }
}

export async function asnLookup(query: string): Promise<AsnResult> {
  const checkedAt = new Date().toISOString();
  const sources: string[] = [];
  let resolvedIp: string | null = null;
  let asn: number | null = null;
  let bgpPrefix: string | null = null;
  let country: string | null = null;
  let rir: string | null = null;
  let holder: string | null = null;

  // Try parsing as ASN
  const asnMatch = query.match(/^(?:AS)?(\d{1,10})$/i);
  if (asnMatch) {
    asn = Number(asnMatch[1]);
    const classification = classifyAsn(asn);
    if (classification) {
      return { query, resolvedIp: null, status: classification as any, note: `ASN ${asn} is classified as ${classification.replace('_', ' ')} per IANA registry rules.`, asn, asnFormat: asn > 65535 ? '32-bit' : '16-bit', holder: null, country: null, rir: null, bgpPrefix: null, announcedPrefixes: [], rpkiStatus: null, sources: ['IANA ASN registry classification'], checkedAt };
    }
    sources.push('Team Cymru AS{n}.asn.cymru.com TXT');
    holder = await cymruAsnName(asn);
  } else {
    // Try parsing as IP or domain
    let ip: string | null = null;
    if (/^\d{1,3}(\.\d{1,3}){3}$/.test(query)) {
      ip = query;
    } else if (query.includes(':')) {
      ip = query;
    } else if (query.includes('.')) {
      ip = await resolveDomain(query);
      if (!ip) return { query, resolvedIp: null, status: 'error', note: `Could not resolve ${query} to an IP address.`, asn: null, asnFormat: null, holder: null, country: null, rir: null, bgpPrefix: null, announcedPrefixes: [], rpkiStatus: null, sources: [], checkedAt };
      resolvedIp = ip;
    }
    if (!ip) return { query, resolvedIp: null, status: 'error', note: 'Could not parse the input as an ASN, IP, prefix, or domain.', asn: null, asnFormat: null, holder: null, country: null, rir: null, bgpPrefix: null, announcedPrefixes: [], rpkiStatus: null, sources: [], checkedAt };
    resolvedIp = ip;
    sources.push('Team Cymru origin.asn.cymru.com TXT');
    const origin = await cymruOrigin(ip);
    if (!origin) return { query, resolvedIp: ip, status: 'error', note: `No ASN origin found for ${ip}.`, asn: null, asnFormat: null, holder: null, country: null, rir: null, bgpPrefix: null, announcedPrefixes: [], rpkiStatus: null, sources, checkedAt };
    asn = origin.asn;
    bgpPrefix = origin.prefix;
    country = origin.country;
    rir = origin.rir;
    holder = await cymruAsnName(asn);
  }

  // RIPEstat enrichment
  const asOverview = await ripestat(`as-overview/data.json?resource=AS${asn}`);
  if (asOverview) {
    sources.push('RIPEstat as-overview');
    if (asOverview.holder && !holder) holder = asOverview.holder;
    if (asOverview.type) { /* "autonomous system" */ }
  }

  const prefixes = await ripestat(`announced-prefixes/data.json?resource=AS${asn}`);
  const announcedPrefixes: { prefix: string; type: 'IPv4' | 'IPv6' }[] = [];
  if (prefixes?.prefixes) {
    sources.push('RIPEstat announced-prefixes');
    for (const p of (prefixes.prefixes as any[]).slice(0, 30)) {
      announcedPrefixes.push({ prefix: p.prefix, type: p.prefix.includes(':') ? 'IPv6' : 'IPv4' });
    }
  }

  // RPKI validation for the queried prefix or the first announced prefix
  let rpkiStatus: string | null = null;
  const rpkiTarget = bgpPrefix || announcedPrefixes[0]?.prefix;
  if (rpkiTarget) {
    const rpki = await ripestat(`rpki-validation/data.json?resource=AS${asn}&prefix=${encodeURIComponent(rpkiTarget)}`);
    if (rpki) {
      sources.push('RIPEstat rpki-validation');
      rpkiStatus = rpki.validating_roas?.length > 0
        ? (rpki.validating_roas[0].validity === 'valid' ? 'valid' : rpki.validating_roas[0].validity === 'invalid' ? 'invalid' : 'not-found')
        : 'not-found';
    }
  }

  const classification = classifyAsn(asn);
  const status = classification ? (classification as any) : 'ok';
  const note = classification ? `ASN ${asn} is classified as ${classification.replace(/_/g, ' ')} per IANA registry rules.` : '';

  return {
    query, resolvedIp, status, note,
    asn, asnFormat: asn > 65535 ? '32-bit' : '16-bit',
    holder, country, rir, bgpPrefix, announcedPrefixes, rpkiStatus,
    sources: [...new Set(sources)], checkedAt,
  };
}
