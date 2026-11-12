import { readFileSync, writeFileSync } from 'node:fs';

// 1. Build the tool href set from tools.ts
const toolsSource = readFileSync('src/data/tools.ts', 'utf8');
const toolHrefs = new Set();
for (const m of toolsSource.matchAll(/href:\s*'([^']+)'/g)) toolHrefs.add(m[1]);

const monitoringHrefs = new Set(['/dmarc-monitoring/', '/dns-monitoring/']);
const botHrefs = new Set([
  '/amazonbot/', '/applebot-extended/', '/bytespider/', '/ccbot/', '/claudebot/',
  '/common-crawl-bot/', '/diffbot/', '/gemini-ai/', '/gptbot/', '/meta-ai/',
  '/perplexitybot/', '/applebot/', '/cohere-ai/',
]);

const pages = [
  'src/pages/dns/index.astro',
  'src/pages/dns-records/index.astro',
  'src/pages/email-authentication/index.astro',
  'src/pages/email-deliverability.astro',
  'src/pages/dns-security.astro',
  'src/pages/dns-providers.astro',
  'src/pages/ai-web-infrastructure.astro',
  'src/pages/ip-and-networking.astro',
  'src/pages/ssl-tls.astro',
  'src/pages/dns-error-messages.astro',
];

let totalFiles = 0;
let totalBadges = 0;

for (const page of pages) {
  let s = readFileSync(page, 'utf8');
  const lines = s.split('\n');
  let currentHref = '';
  let changed = false;

  for (let i = 0; i < lines.length; i++) {
    // Track href when we see it
    const hrefMatch = lines[i].match(/href:\s*'([^']+)'/);
    if (hrefMatch) currentHref = hrefMatch[1];

    // Also check for href on the same line as badge (single-line cards)
    const badgeMatch = lines[i].match(/badge:\s*'([^']+)'/);
    if (badgeMatch) {
      // If href is on the same line, use it
      const sameLineHref = lines[i].match(/href:\s*'([^']+)'/);
      if (sameLineHref) currentHref = sameLineHref[1];

      // Determine the correct badge
      let newBadge;
      if (botHrefs.has(currentHref)) {
        newBadge = 'AI Bot';
      } else if (monitoringHrefs.has(currentHref)) {
        newBadge = 'Monitoring';
      } else if (toolHrefs.has(currentHref)) {
        newBadge = 'Free Tool';
      } else {
        newBadge = 'Guide';
      }

      const oldBadge = badgeMatch[1];
      if (oldBadge !== newBadge) {
        lines[i] = lines[i].replace(`badge: '${oldBadge}'`, `badge: '${newBadge}'`);
        totalBadges++;
        changed = true;
        if (oldBadge !== newBadge) {
          console.log(`  ${page}: '${oldBadge}' -> '${newBadge}' (${currentHref})`);
        }
      }
    }
  }

  if (changed) {
    writeFileSync(page, lines.join('\n'));
    totalFiles++;
  }
}

console.log('\nFiles changed:', totalFiles, '| Badges updated:', totalBadges);
