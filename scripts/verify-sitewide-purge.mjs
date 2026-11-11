import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(join(dir, e.name)) : e.name.endsWith('.html') ? [join(dir, e.name)] : []
  );
}

// These are the INTERNAL MAP SCAFFOLDING terms that must have 0 matches.
// Use word boundaries for short codes that could be substrings of legitimate English.
const patterns = [
  /\bmoney core\b/gi,
  /\btraffic core\b/gi,
  /\bCore A[:\s]/g,
  /\bCore B[:\s]/g,
  /\bCore C[:\s]/g,
  /\bCore D[:\s]/g,
  /\bOuter 1[:\s]/g,
  /\bOuter 2[:\s]/g,
  /\bOuter 3[:\s]/g,
  /\bMaster hub\b/gi,
  /\bCore Pillar\b/gi,
  /\bPillar Guide\b/gi,
  /\bDeliverability Pillar\b/gi,
  /\bSSL\/TLS Pillar\b/gi,
  /\bReverse DNS Pillar\b/gi,
  /\bDiagnostic Pillar\b/gi,
  /\bEntity Directory\b/gi,
  /\bentity reference profiles\b/gi,
  /\bDNS Security Cluster\b/gi,
  /\bMaster Reference Table\b/gi,
  /\bAnswerBlocks\b/gi,
  /\bauthentication hub\b/gi,
  /\bdeliverability hub\b/gi,
  /\bsecurity hub\b/gi,
  /\btypes hub\b/gi,
  /\bSSL\/TLS hub\b/gi,
  /\bUsers asking /g,
  /\bwhat does a stand for in dns\b/gi,
  /\bwhy private ip in public a record fails\b/gi,
  /\bDNS AAAA record full form\b/gi,
];

const files = walk('dist');
let total = 0;
for (const file of files) {
  const h = readFileSync(file, 'utf8');
  for (const p of patterns) {
    p.lastIndex = 0;
    const match = p.exec(h);
    if (match) {
      total++;
      const rel = file.replace(/\\/g, '/');
      console.log('MATCH:', JSON.stringify(match[0]), 'in', rel);
    }
  }
}
if (total === 0) {
  console.log('VERIFICATION PASSED: 0 matches across all ' + files.length + ' HTML files for all ' + patterns.length + ' patterns');
} else {
  console.log('VERIFICATION FAILED: ' + total + ' matches found');
  process.exit(1);
}
