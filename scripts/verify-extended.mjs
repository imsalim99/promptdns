import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(join(dir, e.name)) : e.name.endsWith('.html') ? [join(dir, e.name)] : []
  );
}

// Internal map scaffolding codes — use word boundaries so "Core DNS" (legitimate English)
// doesn't match as a false positive for "Core D" (internal code).
const patterns = [
  /\bProtocol Comparison\b/g,
  /\bReference Directory\b/g,
  /\bESP Playbook\b/g,
  /\bFlagship\b/g,
  /\bKoray\b/g,
  /\bsemantic-node\b/g,
  /\btopical map\b/g,
  /\bdocument-template\b/g,
  /\bRollout Playbook\b/g,
  /\bDelisting Playbook\b/g,
  /\bDeep editorial\b/g,
  /\bSyntax Guide\b/g,
  /\bMaster Reference Table\b/g,
  /\bCore Pillar\b/g,
  /\bPillar Guide\b/g,
  /\bEntity Directory\b/g,
  /\bentity reference profiles\b/g,
  /\bDNS Security Cluster\b/g,
  /\bmoney core\b/gi,
  /\btraffic core\b/gi,
  /\bCore A\b(?!\w)/g,
  /\bCore B\b(?!\w)/g,
  /\bCore C\b(?!\w)/g,
  /\bCore D\b(?!\w)(?!\s*NS)(?!\s*Record)(?!\s*Protocol)(?!\s*Concept)/g,
  /\bOuter 1\b(?!\w)/g,
  /\bOuter 2\b(?!\w)/g,
  /\bAnswerBlocks\b/g,
  /\bauthentication hub\b/gi,
  /\bdeliverability hub\b/gi,
  /\bsecurity hub\b/gi,
  /\bSSL\/TLS hub\b/gi,
  /\bDiagnostic Pillar\b/gi,
  /\bDeliverability Pillar\b/gi,
  /\bReverse DNS Pillar\b/gi,
  /\bSSL\/TLS Pillar\b/gi,
  /\bFlagship Live\b/g,
  /\bflagship pages\b/g,
  /\bCurate Flagship\b/g,
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
  console.log('EXTENDED VERIFICATION PASSED: 0 matches across all ' + files.length + ' HTML files for all ' + patterns.length + ' patterns');
} else {
  console.log('EXTENDED VERIFICATION FAILED: ' + total + ' matches found');
  process.exit(1);
}
