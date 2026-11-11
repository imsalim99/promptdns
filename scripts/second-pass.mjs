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
  [/badge: 'SSL\/TLS Pillar'/g, "badge: 'Security Guide'"],
  [/Master hub for SSL\/TLS and web security:/g, 'Complete technical reference for SSL/TLS and web security:'],
  [/covered in this hub by protocol mechanism/g, 'covered in this guide by protocol mechanism'],
  [/<!-- Section 1: Master Reference Table -->/g, '<!-- Section 1: Master Table -->'],
  [/<!-- Section 2: Guides & Pillars Grid -->/g, '<!-- Section 2: Guides Grid -->'],
  [/<!-- Section 1: 5 Pillars Master Table -->/g, '<!-- Section 1: 5 Filtering Gates Table -->'],
  [/Domain Name System hub covering/g, 'Domain Name System guide covering'],
  [/covered in this hub by technical scope/g, 'covered in this guide by technical scope'],
  [/essential pillar of modern/g, 'essential part of modern'],
  [/AI Crawler Access<\/a> hub, which connects/g, 'AI Crawler Access</a> guide, which connects'],
  [/email deliverability<\/a> hub shows/g, 'email deliverability</a> guide shows'],
  [/email deliverability<\/a> hub, which connect/g, 'email deliverability</a> guide, which connects'],
  [/Aligned breadcrumbs site-wide: Home \/ Hub \/ Page for guides, Home \/ Tools \/ Tool for tools\./g, 'Standardized three-level breadcrumb navigation across all documentation guides and tools.'],
  [/Deep editorial layer added to tool pages\./g, 'Added step-by-step result interpretation, command-line examples, and RFC reference tables to tool pages.'],
  [/DNS hub/g, 'DNS guide'],
  [/covered in this hub/g, 'covered in this guide'],
];

for (const file of files) {
  let s = readFileSync(file, 'utf8');
  const before = s;
  for (const [pattern, replacement] of FIXES) {
    s = s.replace(pattern, replacement);
  }
  if (s !== before) {
    writeFileSync(file, s);
    count++;
    console.log('FIXED:', file.replace(/\\/g, '/'));
  }
}
console.log('\nSecond pass files changed:', count);
