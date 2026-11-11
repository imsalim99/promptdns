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
  // Stiff protocol labels → Guide
  [/badge: 'Protocol Standard'/g, "badge: 'Guide'"],
  [/badge: 'Core Specification'/g, "badge: 'Guide'"],
  [/badge: 'Core Concept'/g, "badge: 'Guide'"],
  [/badge: 'Core Mechanism'/g, "badge: 'Guide'"],
  [/badge: 'Security Standard'/g, "badge: 'Guide'"],
  [/badge: 'Syntax Reference'/g, "badge: 'Syntax Guide'"],
  [/badge: 'Configuration Guide'/g, "badge: 'Guide'"],
  [/badge: 'Security Guide'/g, "badge: 'Guide'"],
  [/badge: 'Troubleshooting Guide'/g, "badge: 'Error Fix'"],
  [/badge: 'Operations Guide'/g, "badge: 'Guide'"],
  [/badge: 'Transport Reference'/g, "badge: 'Guide'"],
  [/badge: 'Bounce Reference'/g, "badge: 'Bounce Guide'"],
  [/badge: 'Audit Guide'/g, "badge: 'Guide'"],
  [/badge: 'Technical Guide'/g, "badge: 'Guide'"],
  [/badge: 'SEO Analysis'/g, "badge: 'Guide'"],
  [/badge: 'Setup Guide'/g, "badge: 'Guide'"],
  [/badge: 'Reference Index'/g, "badge: 'Error Fix'"],
  [/badge: 'Core DNS Reference'/g, "badge: 'DNS Record'"],
  [/badge: 'Concepts Guide'/g, "badge: 'Guide'"],
  [/badge: 'Comparison Guide'/g, "badge: 'Comparison'"],
  [/badge: 'Audit Guide'/g, "badge: 'Guide'"],
  [/badge: 'Head-to-Head'/g, "badge: 'Comparison'"],
  [/badge: 'Layer Comparison'/g, "badge: 'Comparison'"],
  [/badge: 'Architecture Comparison'/g, "badge: 'Comparison'"],
  [/badge: 'Master Comparison'/g, "badge: 'Comparison'"],
  [/badge: 'Auth Stack'/g, "badge: 'Guide'"],
  [/badge: 'Transport Encryption'/g, "badge: 'Guide'"],
  [/badge: 'Transport Security'/g, "badge: 'Guide'"],
  [/badge: 'Email TLS Policy'/g, "badge: 'Guide'"],
  [/badge: 'Encrypted DNS'/g, "badge: 'Guide'"],
  [/badge: 'Encrypted DNS Ports'/g, "badge: 'Guide'"],
  [/badge: 'PKI Architecture'/g, "badge: 'Guide'"],
  [/badge: 'DNS Cryptography'/g, "badge: 'Guide'"],
  [/badge: 'BGP Security'/g, "badge: 'Guide'"],
  [/badge: 'Routing Protocol'/g, "badge: 'Guide'"],
  [/badge: 'Server Architecture'/g, "badge: 'Guide'"],
  [/badge: 'Router Mechanics'/g, "badge: 'Guide'"],
  [/badge: 'Apex Routing'/g, "badge: 'Guide'"],
  [/badge: 'Apex Routing'/g, "badge: 'Guide'"],
  [/badge: 'SMTP & Mail Ports'/g, "badge: 'Guide'"],
  [/badge: 'Threat Guide'/g, "badge: 'Guide'"],
  [/badge: 'Security Header'/g, "badge: 'Guide'"],
  [/badge: 'Brand Certificates'/g, "badge: 'Guide'"],
  [/badge: 'Certificate Guide'/g, "badge: 'Guide'"],
  [/badge: 'HTTPS Repair'/g, "badge: 'Guide'"],
  [/badge: 'Traffic Steering'/g, "badge: 'Guide'"],
  [/badge: 'Edge Performance'/g, "badge: 'Guide'"],
  [/badge: 'BGP & Routing Guide'/g, "badge: 'Guide'"],
  [/badge: 'TLS Reporting'/g, "badge: 'TLS-RPT Guide'"],
  [/badge: 'Email TLS Policy'/g, "badge: 'TLS-RPT Guide'"],
  [/badge: 'Encrypted DNS Ports'/g, "badge: 'Guide'"],
  [/badge: 'Forwarding Standard'/g, "badge: 'Guide'"],
  [/badge: 'EU Directive'/g, "badge: 'Compliance'"],

  // Record Reference → DNS Record (these are DNS record cards)
  [/badge: 'Record Reference'/g, "badge: 'DNS Record'"],

  // ===== email-deliverability: 5 Filtering Gates → 5 Key Factors =====
  [/5 Filtering Gates/g, '5 Key Factors'],
  [/5 filtering gates/g, '5 key factors'],
  [/5 sequential filtering gates/g, '5 key factors'],
  [/Filtering Gate<\/th>/g, 'Key Factor</th>'],
  [/the 5 key factors combine/g, 'the 5 key factors combine'],

  // ===== ai-web-infrastructure: bot cards → AI Bot =====
  [/badge: 'OpenAI · Training'/g, "badge: 'AI Bot'"],
  [/badge: 'OpenAI · AI Search'/g, "badge: 'AI Bot'"],
  [/badge: 'Anthropic · Training'/g, "badge: 'AI Bot'"],
  [/badge: 'Perplexity · AI Search'/g, "badge: 'AI Bot'"],
  [/badge: 'Google · Control Token'/g, "badge: 'AI Bot'"],
  [/badge: 'Apple · Control Token'/g, "badge: 'AI Bot'"],
  [/badge: 'Meta · Training & RAG'/g, "badge: 'AI Bot'"],
  [/badge: 'Common Crawl · Dataset'/g, "badge: 'AI Bot'"],
  [/badge: 'ByteDance · Scraper'/g, "badge: 'AI Bot'"],
  [/badge: 'Diffbot · Knowledge Graph'/g, "badge: 'AI Bot'"],
  [/badge: 'Cohere · Enterprise AI'/g, "badge: 'AI Bot'"],
  [/badge: 'You.com · AI Search'/g, "badge: 'AI Bot'"],
  [/badge: 'Perplexity · AI Search'/g, "badge: 'AI Bot'"],
  [/badge: 'Common Crawl · Dataset'/g, "badge: 'AI Bot'"],
  [/badge: 'Flagship AI Tool'/g, "badge: 'Free Tool'"],

  // ===== ai-web-infrastructure: technical reference profiles → bot guides =====
  [/Fourteen technical reference profiles document/g, 'Fourteen bot guides cover'],
  [/technical reference profiles/g, 'bot guides'],

  // ===== section comments =====
  [/<!-- Section 2: Guides Grid -->/g, '<!-- Section 2: Guides -->'],
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
console.log('\nTotal files changed:', count);
