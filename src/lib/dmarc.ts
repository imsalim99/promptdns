/**
 * DMARC record parsing + generation.
 */
export interface DmarcTag {
  tag: string;
  value: string;
  meaning: string;
}

export interface DmarcParse {
  found: boolean;
  record: string;
  policy: string;
  tags: DmarcTag[];
  errors: string[];
  warnings: string[];
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
}

const MEANINGS: Record<string, (v: string) => string> = {
  v: () => 'Protocol version, must be DMARC1.',
  p: (v) => `Policy for the domain: ${v === 'none' ? 'monitor only, no action on failures' : v === 'quarantine' ? 'failing mail goes to spam/quarantine' : 'failing mail is rejected'}.`,
  sp: (v) => `Policy for subdomains: ${v}.`,
  pct: (v) => `${v}% of failing mail receives the policy (roll-out knob).`,
  rua: (v) => `Aggregate reports are sent to ${v}.`,
  ruf: (v) => `Forensic (failure) reports are sent to ${v}.`,
  adkim: (v) => `DKIM alignment: ${v === 'r' ? 'relaxed (organizational domains must match)' : 'strict (exact match required)'}.`,
  aspf: (v) => `SPF alignment: ${v === 'r' ? 'relaxed (organizational domains must match)' : 'strict (exact match required)'}.`,
  fo: (v) => `Forensic reporting options: ${v}.`,
  rf: (v) => `Report format: ${v}.`,
  ri: (v) => `Report interval: ${v} seconds.`,
};

export function parseDmarc(record: string): DmarcParse {
  const tags: DmarcTag[] = [];
  const errors: string[] = [];
  const warnings: string[] = [];

  if (!/^v=DMARC1/i.test(record.trim())) {
    errors.push('Record must start with v=DMARC1.');
  }
  const parts = record.trim().split(';').map((s) => s.trim()).filter(Boolean);
  for (const part of parts) {
    const eq = part.indexOf('=');
    if (eq < 0) {
      errors.push(`Malformed tag "${part}" (missing =).`);
      continue;
    }
    const tag = part.slice(0, eq).trim().toLowerCase();
    const value = part.slice(eq + 1).trim();
    if (!MEANINGS[tag]) {
      warnings.push(`Unknown tag "${tag}", check spelling.`);
    }
    tags.push({ tag, value, meaning: MEANINGS[tag]?.(value) ?? 'Unknown tag.' });
  }

  const get = (t: string) => tags.find((x) => x.tag === t)?.value;
  const policy = (get('p') ?? '').toLowerCase();

  if (!get('p')) errors.push('Missing required p= tag (none, quarantine, or reject).');
  if (policy === 'none') warnings.push('p=none is monitoring-only, spoofed mail is still delivered. Plan a move to quarantine, then reject.');
  if (!get('rua')) warnings.push('No rua= tag, you receive no aggregate reports, so p=none gives you zero visibility.');
  if (policy === 'reject' && !get('rua')) warnings.push('Enforcement without reporting (rua) makes tuning impossible.');
  if (get('pct') === '100' && policy === 'reject') warnings.push('pct=100 with p=reject is full enforcement, make sure all legitimate senders pass first.');

  const hasRuA = Boolean(get('rua'));
  const grade: DmarcParse['grade'] =
    policy === 'reject' && hasRuA ? 'A'
    : policy === 'quarantine' && hasRuA ? 'B'
    : policy === 'none' && hasRuA ? 'C'
    : hasRuA ? 'D' : 'F';

  return { found: true, record, policy: policy || '(missing)', tags, errors, warnings, grade };
}

export interface DmarcGenOptions {
  policy: 'none' | 'quarantine' | 'reject';
  subdomainPolicy: '' | 'none' | 'quarantine' | 'reject';
  pct: number;
  rua: string;
  ruf: string;
  adkim: '' | 'r' | 's';
  aspf: '' | 'r' | 's';
}

export function generateDmarc(o: DmarcGenOptions): string {
  const parts = ['v=DMARC1', `p=${o.policy}`];
  if (o.subdomainPolicy) parts.push(`sp=${o.subdomainPolicy}`);
  if (o.pct !== 100) parts.push(`pct=${o.pct}`);
  if (o.rua.trim()) parts.push(`rua=mailto:${o.rua.trim().replace(/^mailto:/, '')}`);
  if (o.ruf.trim()) parts.push(`ruf=mailto:${o.ruf.trim().replace(/^mailto:/, '')}`);
  if (o.adkim) parts.push(`adkim=${o.adkim}`);
  if (o.aspf) parts.push(`aspf=${o.aspf}`);
  return parts.join('; ');
}
