/**
 * PromptDNS Domain Security Scanner, hero widget logic.
 * Real checks, all client-side via DoH (no backend, nothing stored).
 */
import { lookup, RESOLVERS, normalizeDomain, type DohAnswer } from './doh';

export type CheckStatus = 'pass' | 'warn' | 'fail' | 'unknown';

export interface ScanCheck {
  id: string;
  label: string;
  status: CheckStatus;
  value: string;
  detail: string;
  weight: number;
  earned: number;
}

export interface ScanReport {
  domain: string;
  score: number;
  grade: string;
  checks: ScanCheck[];
}

const DKIM_SELECTORS = [
  'google._domainkey', 'default._domainkey', 'selector1._domainkey', 'selector2._domainkey',
  'k1._domainkey', 's1._domainkey', 's2._domainkey', 'mail._domainkey',
  'zoho._domainkey', 'protonmail._domainkey', 'mandrill._domainkey', 'everlytickey1._domainkey',
];

function txtJoin(answers: DohAnswer[]): string[] {
  // DoH returns chunked TXT strings quoted; join adjacent chunks per record name+TTL group
  const out: string[] = [];
  let cur = '';
  for (const a of answers) {
    const chunk = a.data.replace(/^"|"$/g, '');
    if (cur) cur += chunk;
    else cur = chunk;
    // Heuristic: a record ends when the string looks complete (ends with " or space-term)
    if (a.data.endsWith('"') && !a.data.startsWith('" "')) {
      out.push(cur);
      cur = '';
    }
  }
  if (cur) out.push(cur);
  return out;
}

export async function scanDomain(
  rawDomain: string,
  onStage?: (stageIndex: number, label: string) => void,
): Promise<ScanReport> {
  const domain = normalizeDomain(rawDomain);
  const r = RESOLVERS[0];
  const checks: ScanCheck[] = [];

  // ---- Stage 1: website DNS ----
  onStage?.(0, 'Resolving website records…');
  const [a, aaaa] = await Promise.all([lookup(domain, 'A', r), lookup(domain, 'AAAA', r)]);
  const ips = a.answers.filter((x) => x.type === 1).map((x) => x.data);
  const ipv6 = aaaa.answers.filter((x) => x.type === 28).map((x) => x.data);
  checks.push({
    id: 'website', label: 'Website DNS', weight: 15,
    status: ips.length ? 'pass' : 'fail',
    earned: ips.length ? 15 : 0,
    value: ips.length ? `${ips.length} A record${ips.length > 1 ? 's' : ''}${ipv6.length ? ' + IPv6' : ''}` : 'No A record',
    detail: ips.length ? `Points to ${ips.join(', ')}${ipv6.length ? ` (and ${ipv6[0]} via IPv6)` : ''}.` : 'The domain has no A record, so it does not resolve to a website.',
  });

  const ns = await lookup(domain, 'NS', r);
  const nameservers = ns.answers.filter((x) => x.type === 2).map((x) => x.data);
  checks.push({
    id: 'ns', label: 'Nameservers', weight: 5,
    status: nameservers.length >= 2 ? 'pass' : nameservers.length ? 'warn' : 'fail',
    earned: nameservers.length >= 2 ? 5 : nameservers.length ? 3 : 0,
    value: nameservers.length ? `${nameservers.length} nameservers` : 'None found',
    detail: nameservers.length ? nameservers.slice(0, 3).join(', ') : 'No NS records returned, delegation may be broken.',
  });

  // ---- Stage 2: email ----
  onStage?.(1, 'Checking email authentication…');
  const mx = await lookup(domain, 'MX', r);
  const mxHosts = mx.answers.filter((x) => x.type === 15).map((x) => x.data);
  checks.push({
    id: 'mx', label: 'Mail Routing (MX)', weight: 10,
    status: mxHosts.length ? 'pass' : 'warn',
    earned: mxHosts.length ? 10 : 3,
    value: mxHosts.length ? `${mxHosts.length} MX record${mxHosts.length > 1 ? 's' : ''}` : 'No MX records',
    detail: mxHosts.length
      ? `Mail is routed via ${mxHosts.slice(0, 2).join(', ')}${mxHosts.length > 2 ? ` (+${mxHosts.length - 2} more)` : ''}.`
      : 'No MX records: this domain cannot receive email (fine for web-only domains).',
  });

  const txt = await lookup(domain, 'TXT', r);
  const txts = txtJoin(txt.answers.filter((x) => x.type === 16));
  const spf = txts.find((t) => t.toLowerCase().startsWith('v=spf1'));
  let spfLookups = 0;
  if (spf) {
    spfLookups = (spf.match(/(include:|redirect=|exists:|\ba\b|\bmx\b(?!=))/gi) ?? []).length;
  }
  checks.push({
    id: 'spf', label: 'SPF', weight: 20,
    status: !spf ? 'fail' : spfLookups > 10 ? 'warn' : 'pass',
    earned: !spf ? 0 : spfLookups > 10 ? 12 : 20,
    value: spf ? (spfLookups > 10 ? `Over lookup limit (${spfLookups})` : `Valid (${spfLookups} lookups)`) : 'Missing',
    detail: spf
      ? `${spf.slice(0, 90)}${spf.length > 90 ? '…' : ''}, ${spfLookups > 10 ? 'exceeds the 10-DNS-lookup limit (permerror). Flatten it.' : 'within the 10-lookup limit.'}`
      : 'No SPF record: receivers cannot verify which servers may send as this domain. Gmail/Yahoo require SPF.',
  });

  const dmarcTxt = await lookup(`_dmarc.${domain}`, 'TXT', r);
  const dmarc = txtJoin(dmarcTxt.answers.filter((x) => x.type === 16)).find((t) => t.toLowerCase().startsWith('v=dmarc1'));
  const policy = dmarc?.match(/\bp=(none|quarantine|reject)/i)?.[1]?.toLowerCase();
  const dmarcEarned = !dmarc ? 0 : policy === 'reject' ? 25 : policy === 'quarantine' ? 20 : policy === 'none' ? 10 : 15;
  checks.push({
    id: 'dmarc', label: 'DMARC', weight: 25,
    status: !dmarc ? 'fail' : policy === 'reject' || policy === 'quarantine' ? 'pass' : 'warn',
    earned: dmarcEarned,
    value: dmarc ? `Policy: p=${policy ?? 'unknown'}` : 'Missing',
    detail: dmarc
      ? (policy === 'none'
          ? 'DMARC is in monitoring mode (p=none), spoofed mail is still delivered. Move toward quarantine/reject.'
          : `Enforcement active (p=${policy}). Spoofed mail is ${policy === 'reject' ? 'rejected' : 'quarantined'}.`)
      : 'No DMARC record: anyone can spoof this domain and mailbox providers have no policy to act on.',
  });

  let dkimFound = '';
  for (let i = 0; i < DKIM_SELECTORS.length && !dkimFound; i += 4) {
    const batch = DKIM_SELECTORS.slice(i, i + 4);
    const results = await Promise.all(batch.map((sel) => lookup(`${sel}.${domain}`, 'TXT', r)));
    for (let j = 0; j < results.length; j++) {
      if (results[j].ok && results[j].answers.some((x) => x.type === 16 && x.data.includes('p='))) {
        dkimFound = batch[j];
        break;
      }
    }
  }
  checks.push({
    id: 'dkim', label: 'DKIM', weight: 15,
    status: dkimFound ? 'pass' : 'warn',
    earned: dkimFound ? 15 : 5,
    value: dkimFound ? `Found (${dkimFound.replace('._domainkey', '')})` : 'Not detected',
    detail: dkimFound
      ? `A DKIM public key exists at ${dkimFound}.${domain}.`
      : 'No DKIM key found on common selectors. If you send email, publish keys for your ESP\u2019s selectors.',
  });

  // ---- Stage 3: DNSSEC ----
  onStage?.(2, 'Verifying DNSSEC…');
  const ds = await lookup(domain, 'DS', r);
  const dnssecOn = ds.ok && ds.answers.length > 0;
  checks.push({
    id: 'dnssec', label: 'DNSSEC', weight: 10,
    status: dnssecOn ? 'pass' : 'warn',
    earned: dnssecOn ? 10 : 3,
    value: dnssecOn ? 'Signed' : 'Not signed',
    detail: dnssecOn
      ? 'The zone publishes DS records, responses are cryptographically verifiable.'
      : 'No DS record at the parent zone: responses can be tampered with in transit (cache poisoning).',
  });

  // ---- Stage 4: score ----
  onStage?.(3, 'Scoring…');
  const totalWeight = checks.reduce((s, c) => s + c.weight, 0);
  const earned = checks.reduce((s, c) => s + c.earned, 0);
  const score = Math.round((earned / totalWeight) * 100);
  const grade = score >= 90 ? 'A' : score >= 75 ? 'B' : score >= 60 ? 'C' : score >= 40 ? 'D' : 'F';
  return { domain, score, grade, checks };
}
