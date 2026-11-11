import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(join(dir, e.name)) : (e.name.endsWith('.astro') || e.name.endsWith('.ts')) ? [join(dir, e.name)] : []
  );
}

const files = walk('src');
let totalFiles = 0;

const REPLACEMENTS = [
  // ===== Category 2: Pillar badges → technical labels =====
  [/badge: 'Pillar Guide'/g, "badge: 'Protocol Standard'"],
  [/badge: 'Core Pillar'/g, "badge: 'Core Specification'"],
  [/badge: 'Deliverability Pillar'/g, "badge: 'Configuration Guide'"],
  [/badge: 'Reverse DNS Pillar'/g, "badge: 'Record Reference'"],
  [/badge: 'Diagnostic Pillar'/g, "badge: 'Troubleshooting Guide'"],
  [/badge: 'Security Pillar'/g, "badge: 'Security Guide'"],
  [/badge: 'Record Pillar'/g, "badge: 'Record Reference'"],
  [/badge: 'Reference Directory'/g, "badge: 'Reference Index'"],
  [/badge: 'Master Directory'/g, "badge: 'Reference Index'"],
  [/badge: 'Troubleshooting Pillar'/g, "badge: 'Troubleshooting Guide'"],

  // ===== Category 2: Pillar/Hub in visible text =====
  [/How the 5 Pillars of Email Deliverability Work Together \(Master Reference Table\)/g, 'How the 5 Filtering Gates of Email Deliverability Work Together'],
  [/How the 5 Pillars of Email Deliverability Work Together/g, 'How the 5 Filtering Gates of Email Deliverability Work Together'],
  [/The 5 pillars combine authentication, IP reputation, infrastructure, list hygiene, and engagement\./g, 'The 5 sequential filtering gates combine authentication, IP reputation, infrastructure, list hygiene, and engagement.'],
  [/The 5 pillars of email deliverability/g, 'The 5 filtering gates of email deliverability'],
  [/5 pillars of email deliverability/g, '5 filtering gates of email deliverability'],
  [/Deliverability Pillar<\/th>/g, 'Filtering Gate</th>'],
  [/The 3 pillars combine/g, 'The 3 foundational signals combine'],
  [/the 3 pillars combine/g, 'the 3 foundational signals combine'],

  // ===== Category 2: Master hub → technical reference =====
  [/Master hub for AI crawler access \(AI web infrastructure\):/g, 'Complete technical reference for AI crawler access:'],
  [/Master hub for AI web infrastructure:/g, 'Complete technical reference for AI crawler access:'],
  [/Master hub for DNS provider playbooks:/g, 'Complete setup and troubleshooting guides for DNS providers:'],
  [/Master hub for email deliverability:/g, 'Complete technical reference for email deliverability:'],
  [/Master hub for DNS security:/g, 'Complete technical reference for DNS security:'],
  [/Master hub for email authentication:/g, 'Complete technical reference for email authentication:'],
  [/Master hub for IP and networking infrastructure:/g, 'Complete technical reference for IP and networking:'],

  // ===== Category 2: Navigate this hub → natural navigation =====
  [/Navigate this hub across three directories:/g, 'Explore the guides in three sections:'],
  [/Navigate this hub across four directories:/g, 'Explore the guides in four sections:'],
  [/Navigate this hub by diagnostic task:/g, 'Explore the guides by diagnostic task:'],

  // ===== Category 2: Entity Directory / entity reference =====
  [/AI Crawler &amp; Bot Entity Directory/g, 'AI Crawler &amp; Bot Profiles'],
  [/AI Crawler &amp; Bot Entity Directory \(14 Bot Profiles and Comparisons\)/g, 'AI Crawler &amp; Bot Profiles (14 Bots Compared)'],
  [/Individual AI Crawler and Bot Entity Directory \(14 Bot Profiles and Comparisons\)/g, 'Individual AI Crawler and Bot Profiles (14 Bots Compared)'],
  [/Individual AI Crawler and Bot Entity Directory/g, 'Individual AI Crawler and Bot Profiles'],
  [/Entity Directory/g, 'Bot Profiles'],
  [/entity reference profiles/g, 'technical reference profiles'],
  [/Fourteen entity reference profiles/g, 'Fourteen technical reference profiles'],
  [/10 pillar and implementation guides/g, '10 implementation guides'],

  // ===== Category 2: DNS Security Cluster =====
  [/DNS Security Cluster/g, 'Related DNS Security Guides'],
  [/Every attack type and its defense, cross-referenced/g, 'Explore related DNS attack vectors and cryptographic defenses'],

  // ===== Category 2: "hub" in link anchor text =====
  [/Email deliverability hub →/g, 'Email deliverability guide →'],
  [/Email authentication hub →/g, 'Email authentication guide →'],
  [/SSL\/TLS hub →/g, 'SSL\/TLS guide →'],
  [/DNS security hub →/g, 'DNS security guide →'],
  [/Email deliverability hub/g, 'Email deliverability guide'],
  [/Email authentication hub/g, 'Email authentication guide'],
  [/DNS providers hub/g, 'DNS provider guides'],
  [/SSL\/TLS hub/g, 'SSL\/TLS guide'],
  [/DNS security hub/g, 'DNS security guide'],
  [/resource hub on/g, 'guide on'],

  // ===== Category 3: Master Reference Table =====
  [/ \(Master Reference Table\)/g, ''],
  [/Master Reference Table: /g, ''],

  // ===== Category 3: entity jargon =====
  [/for entity extraction/g, 'for search engines and AI parsers'],
  [/entity disambiguation \(sameAs\)/g, 'JSON-LD structured data'],
  [/Supplies Server-Side Rendered HTML, AnswerBlocks, native tables, and entity disambiguation \(sameAs\)/g, 'Supplies server-side rendered HTML, clear summary sections, semantic tables, and JSON-LD structured data'],
  [/AnswerBlocks/g, 'Summary sections'],

  // ===== Category 4: Raw query stuffing =====
  [/Users asking what is an a record and what does a stand for in dns discover that the letter 'A' stands for 'Address' \(IANA Type 1, RFC 1035\), making it the foundational resource record for/g, "The letter 'A' in an A record stands for 'Address' (IANA Type 1, RFC 1035), making it the foundational resource record for"],
  [/Examining why private ip in public a record fails reveals that routers discard/g, 'Publishing an RFC 1918 private IP address inside a public A record fails for external visitors because internet routers discard'],
  [/representing the official DNS AAAA record full form/g, ''],
  [/Engineers examining /g, 'Inspecting '],
  [/Engineers exploring /g, 'Exploring '],
  [/Administrators asking /g, 'Administrators who ask '],
  [/System administrators investigating /g, 'System administrators who investigate '],
  [/Operators asking /g, 'Operators who ask '],
  [/Developers asking /g, 'Developers who ask '],
  [/discover that /g, 'find that '],
  [/reveals that /g, 'shows that '],
  [/Examining why /g, 'Understanding why '],
];

for (const file of files) {
  let s = readFileSync(file, 'utf8');
  const before = s;
  for (const [pattern, replacement] of REPLACEMENTS) {
    s = s.replace(pattern, replacement);
  }
  if (s !== before) {
    writeFileSync(file, s);
    totalFiles++;
    console.log('FIXED:', file.replace(/\\/g, '/'));
  }
}
console.log('\nTotal files changed:', totalFiles);
