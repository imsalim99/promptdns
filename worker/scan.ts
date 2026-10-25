/**
 * Server-side first scan (run when a domain is added).
 *
 * Mirrors the client-side homepage scanner (src/lib/scan.ts) and the
 * documented methodology page: same seven checks, same weights
 * (DMARC 25, SPF 20, Website 15, DKIM 15, MX 10, DNSSEC 10, NS 5 = 100),
 * same grade bands. Runs over DoH (Cloudflare JSON API) from the Worker.
 */

export interface ScanCheck {
  id: string;
  label: string;
  status: 'pass' | 'warn' | 'fail';
  value: string;
  earned: number;
  weight: number;
}

export interface ScanRecord { type: string; name: string; value: string }

export interface ScanResult {
  domain: string;
  score: number;
  grade: string;
  checks: ScanCheck[];
  records: ScanRecord[];
}

interface DohAnswer { name: string; type: number; TTL: number; data: string }
interface DohJson { Status: number; Answer?: DohAnswer[] }

const DOH = 'https://cloudflare-dns.com/dns-query';

async function doh(name: string, type: string): Promise<DohJson> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 6000);
  try {
    const res = await fetch(`${DOH}?name=${encodeURIComponent(name)}&type=${type}`, {
      headers: { accept: 'application/dns-json' },
      signal: controller.signal,
    });
    if (!res.ok) throw new Error(`DoH HTTP ${res.status}`);
    return (await res.json()) as DohJson;
  } finally {
    clearTimeout(timer);
  }
}

const answersOf = (r: DohJson) => r.Answer ?? [];
const txts = (r: DohJson) => answersOf(r).filter((a) => a.type === 16).map((a) => a.data.replace(/^"|"$/g, ''));

const SPF_LOOKUP_PREFIXES = ['include:', 'a:', 'a/', 'mx:', 'mx/', 'exists:', 'redirect='];
const isSpfLookupTerm = (t: string) => {
  const l = t.toLowerCase();
  return SPF_LOOKUP_PREFIXES.some((p) => l.startsWith(p)) || l === 'a' || l === 'mx';
};

const DKIM_SELECTORS = ['google', 'selector1', 'selector2', 'k1', 's1', 's2', 'default', 'mail', 'zoho'];

export async function scanDomainServer(domain: string): Promise<ScanResult> {
  const checks: ScanCheck[] = [];

  const records: ScanRecord[] = [];
  const addRecords = (type: string, name: string, answers: DohAnswer[], typeId: number) => {
    for (const a of answers.filter((x) => x.type === typeId)) {
      records.push({ type, name, value: a.data.replace(/^"|"$/g, '') });
    }
  };

  // Website DNS (15)
  let aRecords = 0;
  try {
    const [a, aaaa] = await Promise.all([doh(domain, 'A'), doh(domain, 'AAAA')]);
    aRecords = answersOf(a).filter((x) => x.type === 1).length + answersOf(aaaa).filter((x) => x.type === 28).length;
    addRecords('A', domain, answersOf(a), 1);
    addRecords('AAAA', domain, answersOf(aaaa), 28);
  } catch { /* treated as no records */ }
  checks.push({
    id: 'website', label: 'Website DNS', weight: 15,
    status: aRecords > 0 ? 'pass' : 'fail',
    value: aRecords > 0 ? `${aRecords} A/AAAA record(s)` : 'No A/AAAA records',
    earned: aRecords > 0 ? 15 : 0,
  });

  // Nameservers (5)
  let nsCount = 0;
  try {
    const nsRes = await doh(domain, 'NS');
    nsCount = answersOf(nsRes).filter((x) => x.type === 2).length;
    addRecords('NS', domain, answersOf(nsRes), 2);
  } catch { /* ignore */ }
  checks.push({
    id: 'ns', label: 'Nameservers', weight: 5,
    status: nsCount > 0 ? 'pass' : 'fail',
    value: nsCount > 0 ? `${nsCount} NS record(s)` : 'No NS records',
    earned: nsCount > 0 ? 5 : 0,
  });

  // Mail routing (10)
  let mxHosts: string[] = [];
  try {
    const mxRes = await doh(domain, 'MX');
    mxHosts = answersOf(mxRes).filter((x) => x.type === 15).map((x) => x.data.replace(/^\d+\s+/, ''));
    addRecords('MX', domain, answersOf(mxRes), 15);
  } catch { /* ignore */ }
  checks.push({
    id: 'mx', label: 'Mail Routing (MX)', weight: 10,
    status: mxHosts.length > 0 ? 'pass' : 'warn',
    value: mxHosts.length > 0 ? `${mxHosts.length} MX host(s)` : 'No MX records (ok if the domain never receives mail)',
    earned: mxHosts.length > 0 ? 10 : 0,
  });

  // SPF (20)
  let spf: string | null = null;
  let spfLookups = 0;
  try {
    const spfRes = await doh(domain, 'TXT');
    const spfRecords = txts(spfRes).filter((t) => t.toLowerCase().startsWith('v=spf1'));
    spf = spfRecords[0] ?? null;
    spfLookups = spf ? spf.trim().split(/\s+/).slice(1).filter(isSpfLookupTerm).length : 0;
    for (const t of spfRecords) records.push({ type: 'TXT', name: domain, value: t });
  } catch { /* ignore */ }
  const spfEarned = !spf ? 0 : spfLookups <= 10 ? 20 : 5;
  checks.push({
    id: 'spf', label: 'SPF', weight: 20,
    status: !spf ? 'fail' : spfLookups <= 10 ? 'pass' : 'warn',
    value: !spf ? 'No SPF record' : `${spfLookups}/10 lookup terms`,
    earned: spfEarned,
  });

  // DMARC (25)
  let policy: string | null = null;
  try {
    const dmarcRes = await doh(`_dmarc.${domain}`, 'TXT');
    const rec = txts(dmarcRes).find((t) => t.toLowerCase().startsWith('v=dmarc1'));
    policy = rec?.match(/p\s*=\s*(none|quarantine|reject)/i)?.[1]?.toLowerCase() ?? null;
    if (rec) records.push({ type: 'TXT', name: `_dmarc.${domain}`, value: rec });
  } catch { /* ignore */ }
  const dmarcEarned = policy === 'reject' ? 25 : policy === 'quarantine' ? 20 : policy === 'none' ? 10 : 0;
  checks.push({
    id: 'dmarc', label: 'DMARC', weight: 25,
    status: policy === 'reject' ? 'pass' : policy ? 'warn' : 'fail',
    value: policy ? `p=${policy}` : 'No DMARC record',
    earned: dmarcEarned,
  });

  // DKIM (15): common selectors; a miss here is not proof of absence
  let dkimFound: string | null = null;
  try {
    const probes = await Promise.allSettled(
      DKIM_SELECTORS.map(async (sel) => {
        const r = await doh(`${sel}._domainkey.${domain}`, 'TXT');
        const key = txts(r).find((t) => t.includes('p='));
        return key ? sel : null;
      }),
    );
    dkimFound = probes.map((p) => (p.status === 'fulfilled' ? p.value : null)).find(Boolean) ?? null;
  } catch { /* ignore */ }
  checks.push({
    id: 'dkim', label: 'DKIM', weight: 15,
    status: dkimFound ? 'pass' : 'warn',
    value: dkimFound ? `Selector "${dkimFound}" found` : 'No key under common selectors',
    earned: dkimFound ? 15 : 0,
  });

  // DNSSEC (10)
  let ds = 0;
  try {
    ds = answersOf(await doh(domain, 'DS')).filter((x) => x.type === 43).length;
  } catch { /* ignore */ }
  checks.push({
    id: 'dnssec', label: 'DNSSEC', weight: 10,
    status: ds > 0 ? 'pass' : 'warn',
    value: ds > 0 ? 'DS record present' : 'Not signed',
    earned: ds > 0 ? 10 : 0,
  });

  const earned = checks.reduce((s, c) => s + c.earned, 0);
  const score = Math.round(earned); // weights sum to 100
  const grade = score >= 90 ? 'A' : score >= 75 ? 'B' : score >= 60 ? 'C' : score >= 40 ? 'D' : 'F';
  return { domain, score, grade, checks, records };
}
