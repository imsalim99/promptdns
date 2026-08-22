/**
 * SPF parsing + flattening engine (client-side, DNS via DoH).
 */
import { lookup, RESOLVERS, type DohAnswer } from './doh';

export interface SpfTerm {
  term: string;
  kind: 'mechanism' | 'modifier' | 'unknown';
  countsLookup: boolean;
  note: string;
}

export interface SpfParse {
  found: boolean;
  record: string;
  allQualifier: string;
  lookupCount: number;
  terms: SpfTerm[];
  errors: string[];
  warnings: string[];
}

const LOOKUP_MECHS = ['include:', 'a', 'mx', 'exists:', 'redirect='];

export function txtRecords(answers: DohAnswer[]): string[] {
  // DoH returns each TXT string quoted; join chunks per record
  const chunks = answers.filter((x) => x.type === 16).map((x) => x.data.replace(/^"|"$/g, ''));
  const out: string[] = [];
  let cur = '';
  for (const c of chunks) {
    cur += c;
    out.push(cur);
    cur = '';
  }
  return out;
}

export async function fetchSpf(domain: string): Promise<{ found: boolean; record: string; txtCount: number }> {
  const res = await lookup(domain, 'TXT', RESOLVERS[0]);
  const txts = txtRecords(res.answers).filter((t) => t.toLowerCase().startsWith('v=spf1'));
  return { found: txts.length > 0, record: txts[0] ?? '', txtCount: txts.length };
}

export function parseSpf(record: string): SpfParse {
  const errors: string[] = [];
  const warnings: string[] = [];
  const terms: SpfTerm[] = [];
  let lookupCount = 0;
  let allQualifier = '(none)';

  const parts = record.trim().split(/\s+/).slice(1); // drop v=spf1
  for (const term of parts) {
    const t = term.toLowerCase();
    if (term === 'all') {
      allQualifier = '+';
      terms.push({ term, kind: 'mechanism', countsLookup: false, note: 'Matches everything (default allow with +).' });
    } else if (/^[-~+?]all$/.test(t)) {
      allQualifier = term[0];
      const meaning: Record<string, string> = {
        '-': 'Hard fail, unlisted senders are rejected.',
        '~': 'Soft fail, accepted but marked (spam-folder risk).',
        '+': 'Pass, unlisted senders allowed.',
        '?': 'Neutral, no assertion.',
      };
      terms.push({ term, kind: 'mechanism', countsLookup: false, note: meaning[term[0]] ?? '' });
    } else if (t.startsWith('ip4:') || t.startsWith('ip6:')) {
      terms.push({ term, kind: 'mechanism', countsLookup: false, note: 'Literal IP, no DNS lookup needed.' });
    } else if (t.startsWith('include:')) {
      lookupCount++;
      terms.push({ term, kind: 'mechanism', countsLookup: true, note: 'Pulls in another domain\u2019s SPF (1 lookup).' });
    } else if (t === 'a' || t.startsWith('a:') || t.startsWith('a/')) {
      lookupCount++;
      terms.push({ term, kind: 'mechanism', countsLookup: true, note: 'Matches the domain\u2019s A/AAAA records (1 lookup).' });
    } else if (t === 'mx' || t.startsWith('mx:') || t.startsWith('mx/')) {
      lookupCount++;
      terms.push({ term, kind: 'mechanism', countsLookup: true, note: 'Matches the domain\u2019s MX hosts (1 lookup).' });
    } else if (t.startsWith('exists:')) {
      lookupCount++;
      terms.push({ term, kind: 'mechanism', countsLookup: true, note: 'Matches if the domain resolves (1 lookup).' });
    } else if (t.startsWith('ptr')) {
      warnings.push('ptr mechanism is deprecated (RFC 7208) and slow, remove it.');
      terms.push({ term, kind: 'mechanism', countsLookup: false, note: 'Deprecated.' });
    } else if (t.startsWith('redirect=')) {
      lookupCount++;
      terms.push({ term, kind: 'modifier', countsLookup: true, note: 'Redirects evaluation to another domain (1 lookup).' });
    } else if (t.startsWith('exp=')) {
      terms.push({ term, kind: 'modifier', countsLookup: false, note: 'Explanation string modifier.' });
    } else {
      errors.push(`Unrecognized term: ${term}`);
      terms.push({ term, kind: 'unknown', countsLookup: false, note: 'Not valid SPF syntax.' });
    }
  }

  if (allQualifier === '(none)') warnings.push('No "all" mechanism, your record is open-ended (defaults to neutral). Add ~all or -all.');
  if (lookupCount > 10) errors.push(`SPF uses ${lookupCount} DNS lookups, the hard limit is 10 (permerror). Flatten the record.`);
  else if (lookupCount > 8) warnings.push(`${lookupCount}/10 DNS lookups used, close to the limit. Consider flattening.`);

  return { found: true, record, allQualifier, lookupCount, terms, errors, warnings };
}

/* ---------------- Flattening ---------------- */

export interface FlattenResult {
  input: string;
  flattened: string;
  ips: string[];
  lookupsBefore: number;
  domainsIncluded: string[];
  warnings: string[];
}

const MAX_DEPTH = 6;

function extractIpsFromTxt(txts: string[]): { ip4: string[]; ip6: string[] } {
  const ip4: string[] = [];
  const ip6: string[] = [];
  for (const t of txts) {
    if (!t.toLowerCase().startsWith('v=spf1')) continue;
    for (const term of t.split(/\s+/)) {
      if (term.toLowerCase().startsWith('ip4:')) ip4.push(term.slice(4));
      if (term.toLowerCase().startsWith('ip6:')) ip6.push(term.slice(4));
    }
  }
  return { ip4, ip6 };
}

export async function flattenSpf(
  domain: string,
  onProgress?: (msg: string) => void,
): Promise<FlattenResult> {
  const ips = new Set<string>();
  const domainsIncluded: string[] = [];
  const warnings: string[] = [];
  let lookups = 0;

  async function walk(dom: string, depth: number): Promise<void> {
    if (depth > MAX_DEPTH) {
      warnings.push(`Stopped at ${dom}: include depth exceeds ${MAX_DEPTH}.`);
      return;
    }
    onProgress?.(`Resolving SPF of ${dom}…`);
    const res = await lookup(dom, 'TXT', RESOLVERS[0]);
    const spf = txtRecords(res.answers).find((t) => t.toLowerCase().startsWith('v=spf1'));
    if (!spf) {
      warnings.push(`${dom} has no SPF record (include is a permerror).`);
      return;
    }
    domainsIncluded.push(dom);
    const { ip4, ip6 } = extractIpsFromTxt([spf]);
    ip4.forEach((x) => ips.add(`ip4:${x}`));
    ip6.forEach((x) => ips.add(`ip6:${x}`));

    for (const term of spf.split(/\s+/).slice(1)) {
      const t = term.toLowerCase();
      if (t.startsWith('include:')) {
        lookups++;
        await walk(term.slice(8), depth + 1);
      } else if (t === 'a' || t.startsWith('a:') || t.startsWith('a/')) {
        lookups++;
        const target = t.startsWith('a:') ? term.slice(2) : t.startsWith('a/') ? dom : dom;
        const a = await lookup(target, 'A', RESOLVERS[0]);
        const aaaa = await lookup(target, 'AAAA', RESOLVERS[0]);
        a.answers.filter((x) => x.type === 1).forEach((x) => ips.add(`ip4:${x.data}`));
        aaaa.answers.filter((x) => x.type === 28).forEach((x) => ips.add(`ip6:${x.data}`));
      } else if (t === 'mx' || t.startsWith('mx:') || t.startsWith('mx/')) {
        lookups++;
        const target = t.startsWith('mx:') ? term.slice(3) : dom;
        const mx = await lookup(target, 'MX', RESOLVERS[0]);
        for (const r of mx.answers.filter((x) => x.type === 15)) {
          const host = r.data.replace(/^\d+\s+/, '').replace(/\.$/, '');
          const a = await lookup(host, 'A', RESOLVERS[0]);
          a.answers.filter((x) => x.type === 1).forEach((x) => ips.add(`ip4:${x.data}`));
        }
      } else if (t.startsWith('redirect=')) {
        lookups++;
        await walk(term.slice(9), depth + 1);
      }
    }
  }

  await walk(domain, 0);

  const all = [...ips].sort((a, b) => a.slice(4).localeCompare(b.slice(4), undefined, { numeric: true }));
  const allQualifier = 'unknown';
  const flattened = `v=spf1 ${all.join(' ')} -all`;
  if (!all.length) warnings.push('No IP addresses were found to flatten.');
  return { input: domain, flattened, ips: all, lookupsBefore: lookups, domainsIncluded, warnings };
}
