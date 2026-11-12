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
  // ===== Tier 1a: AnswerBlock in GEO guide =====
  [/Front-Load a Self-Contained AnswerBlock in the First 30% of the Page:/g,
   'Front-Load a Self-Contained Answer in the First 30% of the Page:'],

  // ===== Tier 1b: Query Fan-Out + brand consensus in hub card =====
  [/desc: 'How RAG and Query Fan-Out work, the Princeton KDD 2024 9-method benchmark, SSR HTML requirements, and brand consensus\.'/g,
   "desc: 'How RAG retrieval works, the Princeton KDD 2024 9-method benchmark, SSR HTML requirements, and third-party corroboration.'"],

  // ===== Tier 1c: entity disambiguation + Summary sections in code tags =====
  [/Supplies Server-Side Rendered HTML, <code>Summary sections<\/code>, native tables, and entity disambiguation \(<code>sameAs<\/code>\)/g,
   'Supplies Server-Side Rendered HTML, structured summaries, native tables, and JSON-LD structured data (<code>sameAs</code>)'],

  // ===== Tier 1d: Master reference hub =====
  [/desc: 'Master reference hub covering/g, "desc: 'Complete guide to"],

  // ===== Tier 1e: (Master Table) in TOC links =====
  [/Protocol Overview \(Master Table\)/g, 'Protocol Overview'],

  // ===== Tier 1f: Master ESP DNS Configuration Matrix =====
  [/Master ESP DNS Configuration Matrix: All 44 Email Platforms Compared/g,
   'ESP DNS Configuration: All 44 Email Platforms Compared'],

  // ===== Tier 1g: Master Generative =====
  [/description="Master Generative Engine Optimization \(GEO\)/g,
   'description="Complete guide to Generative Engine Optimization (GEO)'],

  // ===== Tier 1h: Master email =====
  [/title: 'Master email deliverability'/g, "title: 'Email deliverability guide'"],

  // ===== Tier 1i: Master robots =====
  [/description="Master robots\.txt syntax/g, 'description="Complete robots\.txt syntax'],

  // ===== Tier 1j: Master cheat =====
  [/desc: 'Master cheat sheet for/g, "desc: 'Complete cheat sheet for"],

  // ===== Tier 1k: Playbook badges =====
  [/badge: 'Migration Playbook'/g, "badge: 'Migration Guide'"],
  [/badge: 'Outreach Playbook'/g, "badge: 'Outreach Guide'"],

  // ===== Tier 1l: head-to-head + Fourteen playbooks =====
  [/Fourteen playbooks and head-to-head comparisons cover/g, 'Fourteen guides and comparisons cover'],

  // ===== Tier 2: unusual badges =====
  [/badge: '7-Check Composite'/g, "badge: 'Free Audit'"],
  [/badge: 'RFC 9309 Validator'/g, "badge: 'Free Tool'"],
  [/badge: 'Agent Spec Tool'/g, "badge: 'Free Tool'"],
  [/badge: 'JSON-LD Auditor'/g, "badge: 'Free Tool'"],
  [/badge: 'Authoritative Benchmark'/g, "badge: 'Free Tool'"],
  [/badge: 'Resolver Benchmark'/g, "badge: 'Benchmark'"],
  [/badge: 'Actionable Checklist'/g, "badge: 'Checklist'"],
  [/badge: '2026 Mandate'/g, "badge: '2026 Update'"],
  [/badge: 'RFC 8058 Standard'/g, "badge: 'Guide'"],
  [/badge: 'RFC 6376 Spec'/g, "badge: 'Guide'"],
  [/badge: 'RFC 7208 Limit'/g, "badge: 'Guide'"],
  [/badge: 'Diagnostic Tutorial'/g, "badge: 'Tutorial'"],
  [/badge: 'Bot Comparison'/g, "badge: 'Comparison'"],
  [/badge: 'Bot IP Verifier'/g, "badge: 'Free Tool'"],
  [/badge: 'Local Log Parser'/g, "badge: 'Free Tool'"],
  [/badge: 'Amazon · Alexa & Rufus'/g, "badge: 'AI Bot'"],

  // ===== Tier 3: Master Table HTML comments =====
  [/<!-- Section 1: Master Table -->/g, '<!-- Section 1: Overview Table -->'],
  [/<!-- Section 1: 6 Layers Master Table -->/g, '<!-- Section 1: Overview Table -->'],
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
