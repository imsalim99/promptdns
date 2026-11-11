import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(join(dir, e.name)) : (e.name.endsWith('.astro') || e.name.endsWith('.ts')) ? [join(dir, e.name)] : []
  );
}

const files = walk('src');
let count = 0;

const FIXES = [
  // ===== dns/index.astro =====
  [/badge: 'Protocol Comparison'/g, "badge: 'Comparison'"],
  [/badge: 'Reference Directory \(All 13 Types\)'/g, "badge: 'All DNS Records'"],
  [/badge: 'Reference Directory \(12 Providers\)'/g, "badge: 'Provider Guides'"],
  [/Flagship Live Diagnostic Tools/g, 'Live DNS Tools'],
  [/record reference directory/g, 'DNS record guides'],
  [/DNS Record Types reference directory/g, 'DNS Record Types guide'],

  // ===== ip-and-networking.astro =====
  [/badge: 'Protocol Comparison'/g, "badge: 'Comparison'"],
  [/protocol comparison/g, 'comparison guide'],

  // ===== ssl-tls.astro =====
  [/badge: 'Syntax Guide'/g, "badge: 'Guide'"],

  // ===== email-authentication/index.astro =====
  [/badge: 'ESP Playbook'/g, "badge: 'Setup Guide'"],
  [/badge: 'Rollout Playbook'/g, "badge: 'Step-by-Step'"],
  [/badge: 'Syntax Guide'/g, "badge: 'Guide'"],

  // ===== dns-error-messages.astro =====
  [/badge: 'Syntax Guide'/g, "badge: 'Guide'"],
  [/badge: 'OS Stub Timeout'/g, "badge: 'Error Fix'"],
  [/badge: 'Chromium Error'/g, "badge: 'Error Fix'"],
  [/badge: 'Chromium Error \(-105\)'/g, "badge: 'Error Fix'"],
  [/badge: 'Outage Recovery'/g, "badge: 'Error Fix'"],
  [/badge: 'Mail Recovery'/g, "badge: 'Error Fix'"],
  [/badge: 'Mail Routing'/g, "badge: 'Error Fix'"],
  [/badge: 'TLS & PKI'/g, "badge: 'Error Fix'"],
  [/badge: 'SPF RFC 7208'/g, "badge: 'Error Fix'"],
  [/badge: 'DKIM RFC 6376'/g, "badge: 'Error Fix'"],
  [/badge: 'SMTP Bounce'/g, "badge: 'Error Fix'"],
  [/badge: 'Free DoH Tool'/g, "badge: 'Free Tool'"],
  [/badge: 'Operations Guide'/g, "badge: 'Guide'"],

  // ===== email-deliverability.astro =====
  [/badge: 'Delisting Playbook'/g, "badge: 'Delisting Guide'"],
  [/badge: 'Rollout Playbook'/g, "badge: 'Step-by-Step'"],
  [/badge: 'Protocol Comparison'/g, "badge: 'Comparison'"],

  // ===== what-is-llms-txt.astro =====
  [/Curate Flagship Canonical URLs:/g, 'Choose Your Most Important Pages:'],
  [/flagship pages/g, 'key pages'],

  // ===== Component comments =====
  [/the ESP matrix - Koray document-template method, deep per-service data\)/g, 'shared template for email provider setup pages)'],
  [/Koray document-template method\./g, 'Shared template for DNS provider guide pages.'],
  [/Koray document-template method: one structure, deep per-type data\./g, 'Shared template for DNS record type pages.'],
  [/Used by the 12 record-lookup pages in the topical map\./g, 'Used by the 12 record-lookup pages.'],
  [/Deep editorial article layer for tool pages \(process, interpretation,\n \*  CLI method, errors, audience, FAQs\) - the Koray semantic-node content\./g, 'Editorial content section for tool pages.'],
  [/Deep editorial content for tool pages \(Koray semantic-node layer\)\./g, 'Editorial content for tool pages.'],
];

for (const file of files) {
  let s = readFileSync(file, 'utf8');
  const before = s;
  for (const [pattern, replacement] of FIXES) {
    s = s.replace(pattern, replacement);
  }
  // Clean up any leftover "Deep editorial" phrases
  s = s.replace(/Deep editorial article layer for tool pages \(process, interpretation,\s*\*\s*CLI method, errors, audience, FAQs\) - the Koray semantic-node content\./g, 'Editorial content section for tool pages.');
  s = s.replace(/Deep editorial content for tool pages \(Koray semantic-node layer\)\./g, 'Editorial content for tool pages.');
  // Catch any remaining Koray references
  s = s.replace(/Koray document-template method/g, 'Shared template');
  s = s.replace(/Koray semantic-node/g, 'Editorial');
  if (s !== before) {
    writeFileSync(file, s);
    count++;
    console.log('FIXED:', file.replace(/\\/g, '/'));
  }
}
console.log('\nTotal files changed:', count);
