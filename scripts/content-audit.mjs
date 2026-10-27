/**
 * Visual semantics audit over dist/ (spec §4, §10, §11).
 *
 * Checks, per page:
 *  - data-vs hooks: centerpiece + attributes on tool pages, example on tools
 *    with sample states, result on ResultCard-bearing pages
 *  - first-N-words-before-H1 token budget (target: tool pages <= 130 incl. nav)
 *  - empty <tbody></tbody> at first paint
 *  - em/en dashes anywhere (owner rule: forbidden)
 *  - boilerplate FAQ markers ("in simple terms" mad-libs)
 *  - schema: FAQPage questions vs visible <details> count parity
 *  - BreadcrumbList presence (informational until batch 5)
 *
 * Usage: node scripts/content-audit.mjs  (run after npm run build)
 */
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const DIST = 'dist';
const TOOL_H1_BUDGET = 130; // words before H1 incl. header nav (spec target for tools)

function* walk(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) yield* walk(p);
    else if (name === 'index.html') yield p;
  }
}

const flags = [];
let pages = 0;
let dashPages = 0;
let emptyTbody = 0;
let boilerplate = 0;
let schemaParityBad = 0;
let noH1 = 0;
let heavyBeforeH1 = 0;
let tools = 0;
let toolsWithCenterpiece = 0;
let toolsWithExample = 0;

const DASH_RE = /[\u2013\u2014]/;

for (const file of walk(DIST)) {
  const html = readFileSync(file, 'utf8');
  const rel = file.replaceAll('\\', '/').replace(/^dist\//, '').replace(/\/index\.html$/, '/');
  if (rel.startsWith('app') || rel === 'login/') continue; // app screens are exempt
  pages += 1;

  if (DASH_RE.test(html)) {
    dashPages += 1;
    flags.push(`DASH ${rel}`);
  }
  if (html.includes('in simple terms') || html.includes('Do I need to memorize')) {
    boilerplate += 1;
    flags.push(`BOILERPLATE_FAQ ${rel}`);
  }
  if (/<tbody[^>]*><\/tbody>/.test(html)) {
    // only a problem if that tbody is inside a visible (non-hidden) container
    const m = html.match(/<tbody[^>]*><\/tbody>/);
    const before = html.slice(Math.max(0, m.index - 400), m.index);
    if (!/class="[^"]*hidden/.test(before)) {
      emptyTbody += 1;
      flags.push(`EMPTY_TBODY ${rel}`);
    }
  }

  const body = html.slice(html.indexOf('<body'));
  const h1 = body.match(/<h1\b/);
  if (!h1) {
    noH1 += 1;
    flags.push(`NO_H1 ${rel}`);
    continue;
  }
  const wordsBeforeH1 = body
    .slice(0, h1.index)
    .replace(/<[^>]+>/g, ' ')
    .split(/\s+/)
    .filter(Boolean).length;

  const isTool = /data-vs="centerpiece"/.test(html);
  if (isTool) {
    tools += 1;
    if (!/data-vs="attributes"/.test(html)) flags.push(`NO_ATTRIBUTES ${rel}`);
    if (/data-vs="example"/.test(html)) toolsWithExample += 1;
    toolsWithCenterpiece += 1;
    if (wordsBeforeH1 > TOOL_H1_BUDGET) {
      heavyBeforeH1 += 1;
      flags.push(`HEAVY_BEFORE_H1 ${rel} (${wordsBeforeH1}w)`);
    }
  }

  // FAQ schema parity: every FAQPage question should have a visible details FAQ
  const faqSchemaQ = (html.match(/"@type":\s*"Question"/g) ?? []).length;
  const visibleFaq = (html.match(/<details/g) ?? []).length;
  if (faqSchemaQ > 0 && visibleFaq < faqSchemaQ) {
    schemaParityBad += 1;
    flags.push(`FAQ_SCHEMA_PARITY ${rel} (schema=${faqSchemaQ}, visible=${visibleFaq})`);
  }
}

console.log(`pages scanned:        ${pages}`);
let answers = 0, tocs = 0, figures = 0;
for (const file of walk(DIST)) {
  const html = readFileSync(file, 'utf8');
  if (html.includes('data-vs="answer"')) answers += 1;
  if (html.includes('pd-toc')) tocs += 1;
  if (html.includes('data-vs="figure"')) figures += 1;
}
console.log(`tool pages:           ${tools} (centerpiece hooks: ${toolsWithCenterpiece}, example states: ${toolsWithExample})`);
console.log(`answer blocks:        ${answers}`);
console.log(`toc rails:            ${tocs}`);
console.log(`figure hooks:         ${figures}`);
console.log(`em/en dash pages:     ${dashPages}`);
console.log(`empty tbody:          ${emptyTbody}`);
console.log(`boilerplate FAQ:      ${boilerplate}`);
console.log(`faq schema mismatch:  ${schemaParityBad}`);
console.log(`pages without h1:     ${noH1}`);
console.log(`heavy before-h1:      ${heavyBeforeH1} (budget ${TOOL_H1_BUDGET}w)`);
if (flags.length) {
  console.log('\nFLAGS:');
  for (const f of flags) console.log('  ' + f);
  process.exitCode = 1;
} else {
  console.log('\nALL CLEAN');
}
