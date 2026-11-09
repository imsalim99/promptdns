/**
 * SPF parsing + flattening engine (client-side, DNS via DoH).
 */
import { lookup, RESOLVERS, type DohAnswer, type LookupResult } from './doh';

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

/* ---------------- Recursive evaluation tree (RFC 7208 section 4.6.4) ---------------- */

export interface SpfResolvedTerm {
  /** Domain whose record this term belongs to. */
  domain: string;
  depth: number;
  term: string;
  kind: string;
  countsLookup: boolean;
  /** Cumulative 1-based lookup index across all records, per RFC 7208 section 4.6.4. */
  lookupIndex: number | null;
  statusText: string | null;
  answerCount: number | null;
  /** NXDOMAIN or empty answer on a DNS-querying term (void lookup). */
  void: boolean;
  note: string;
}

export interface SpfTreeNode {
  domain: string;
  depth: number;
  /** How this record was reached: null for the root, otherwise the include:/redirect= term. */
  via: string | null;
  /** Lookup index of the include:/redirect= term that pulled this record in. */
  lookupIndex: number | null;
  record: string | null;
  txtRecordCount: number;
  note?: string;
}

export interface SpfResolution {
  tree: SpfTreeNode[];
  terms: SpfResolvedTerm[];
  totalLookups: number;
  voidLookups: number;
  /** Actual DoH queries spent (bounded by maxQueries). */
  queries: number;
  maxQueries: number;
  maxDepth: number;
  budgetExhausted: boolean;
  /** Domains publishing 2+ v=spf1 records (permerror per RFC 7208 section 3.2). */
  multipleRecordsDomains: string[];
  /** Include targets that have TXT but no v=spf1 record (permerror at evaluation). */
  noPolicyIncludes: string[];
}

/**
 * Recursively resolve an SPF policy the way a receiver would: follow every
 * include: and redirect= up to maxDepth levels, resolve a/mx/exists targets
 * to detect void lookups, and count every DNS-querying term against the
 * 10-lookup evaluation limit shared across all records in the chain.
 */
export async function resolveSpfRecord(rootDomain: string, maxDepth = 3, maxQueries = 15): Promise<SpfResolution> {
  const tree: SpfTreeNode[] = [];
  const terms: SpfResolvedTerm[] = [];
  const multipleRecordsDomains: string[] = [];
  const noPolicyIncludes: string[] = [];
  const visited = new Set<string>();
  let totalLookups = 0;
  let voidLookups = 0;
  let queries = 0;
  let budgetExhausted = false;

  const budgetLeft = () => queries < maxQueries;

  async function query(name: string, type: 'TXT' | 'A' | 'AAAA' | 'MX'): Promise<LookupResult | null> {
    if (!budgetLeft()) { budgetExhausted = true; return null; }
    queries++;
    return lookup(name, type, RESOLVERS[0]);
  }

  async function processRecord(domain: string, depth: number, via: string | null, viaIndex: number | null, pre?: LookupResult): Promise<void> {
    const node: SpfTreeNode = { domain, depth, via, lookupIndex: viaIndex, record: null, txtRecordCount: 0 };
    tree.push(node);
    if (depth > maxDepth) { node.note = 'include depth limit reached, not resolved'; return; }
    if (visited.has(domain)) { node.note = 'already evaluated (include loop)'; return; }
    visited.add(domain);

    let res = pre ?? null;
    if (!res) {
      res = await query(domain, 'TXT');
      if (!res) { node.note = 'query budget exhausted, not resolved'; return; }
    }
    const txts = txtRecords(res.answers);
    node.txtRecordCount = txts.length;
    const spfs = txts.filter((t) => /^v=spf1(\s|$)/i.test(t.trim()));
    if (spfs.length > 1) multipleRecordsDomains.push(domain);
    const rec = spfs[0] ?? null;
    node.record = rec;
    if (spfs.length > 1) node.note = 'multiple v=spf1 records, permerror per RFC 7208 section 3.2';
    if (!rec) {
      if (via) { node.note = 'TXT exists but no v=spf1 record, include would permerror'; noPolicyIncludes.push(domain); }
      else node.note = 'no v=spf1 record at this domain';
      return;
    }

    for (const term of rec.trim().split(/\s+/).slice(1)) {
      const t = term.toLowerCase();
      let counts = false;
      let target: { name: string; type: 'TXT' | 'A' | 'AAAA' | 'MX' } | null = null;
      let note = '';
      if (t.startsWith('include:')) {
        counts = true; target = { name: term.slice(8), type: 'TXT' };
        note = 'pulls in the SPF policy of ' + target.name;
      } else if (t === 'a' || t.startsWith('a:') || t.startsWith('a/')) {
        counts = true; target = { name: t.startsWith('a:') ? term.slice(2).split('/')[0] : domain, type: 'A' };
        note = 'matches the A/AAAA records of ' + target.name;
      } else if (t === 'mx' || t.startsWith('mx:') || t.startsWith('mx/')) {
        counts = true; target = { name: t.startsWith('mx:') ? term.slice(3).split('/')[0] : domain, type: 'MX' };
        note = 'matches the MX hosts of ' + target.name;
      } else if (t.startsWith('exists:')) {
        counts = true; target = { name: term.slice(7), type: 'A' };
        note = 'matches if the name resolves (macro domains evaluate against the sender IP)';
      } else if (t.startsWith('ptr')) {
        counts = true;
        note = 'deprecated (RFC 7208), reverse-DNS double lookup, resolution skipped';
      } else if (t.startsWith('redirect=')) {
        counts = true; target = { name: term.slice(9), type: 'TXT' };
        note = 'replaces evaluation with the policy of ' + target.name;
      } else if (t.startsWith('ip4:') || t.startsWith('ip6:')) {
        note = 'literal IP range, no DNS lookup';
      } else if (/^[-~+?]?all$/.test(t)) {
        note = 'default qualifier for unmatched senders';
      } else if (t.startsWith('exp=')) {
        note = 'explanation modifier, no lookup';
      } else {
        note = 'unrecognized term';
      }

      let idx: number | null = null;
      let st: string | null = null;
      let ac: number | null = null;
      let isVoid = false;
      if (counts) {
        totalLookups++;
        idx = totalLookups;
        if (target) {
          const r = await query(target.name, target.type);
          if (r) {
            st = r.statusText;
            ac = r.answers.length;
            let extra: LookupResult | null = null;
            if (target.type === 'A' && (r.status !== 0 || r.answers.length === 0) && budgetLeft()) {
              extra = await query(target.name, 'AAAA');
            }
            const primaryEmpty = r.status === 3 || r.answers.length === 0;
            const extraEmpty = !extra || extra.status === 3 || extra.answers.length === 0;
            isVoid = primaryEmpty && extraEmpty;
            if (isVoid) {
              voidLookups++;
              note += ' - VOID lookup: ' + (r.status === 3 ? 'NXDOMAIN' : 'no answers');
            }
            if (target.type === 'TXT' && !isVoid) {
              const childTxts = txtRecords(r.answers);
              const childSpfs = childTxts.filter((x) => /^v=spf1(\s|$)/i.test(x.trim()));
              if (!childSpfs.length) {
                noPolicyIncludes.push(target.name);
                note += ' - target has TXT but no v=spf1 record, include would permerror';
              } else {
                await processRecord(target.name, depth + 1, t.startsWith('include:') ? 'include' : 'redirect', idx, r);
              }
            }
          } else {
            st = 'SKIPPED (query budget)';
            note += ' - query budget exhausted, target not resolved';
          }
        }
      }
      terms.push({ domain, depth, term, kind: counts ? 'mechanism (DNS)' : 'term', countsLookup: counts, lookupIndex: idx, statusText: st, answerCount: ac, void: isVoid, note });
    }
  }

  await processRecord(rootDomain, 0, null, null);
  return { tree, terms, totalLookups, voidLookups, queries, maxQueries, maxDepth: maxDepth, budgetExhausted, multipleRecordsDomains, noPolicyIncludes };
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
