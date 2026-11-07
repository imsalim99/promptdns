/**
 * Regenerate src/data/git-dates.json from full local git history.
 * Run after any content commit whose dates should propagate:
 *
 *   node scripts/gen_git_dates.mjs
 *
 * The manifest is deterministic (sorted at write time by JSON key order of
 * the build pass; re-running on the same history yields identical bytes for
 * unchanged routes) and is committed so Cloudflare Workers Builds' shallow
 * clone can serve true per-page dates instead of collapsing to HEAD.
 */
import { writeFileSync } from 'node:fs';
import { buildDatesFromGit, isShallowRepo } from '../src/data/git-dates.lib.mjs';

if (isShallowRepo()) {
  console.error('Shallow repository detected: run this inside a full clone (local checkout).');
  process.exit(1);
}

const dates = buildDatesFromGit();
const manifest = new URL('../src/data/git-dates.json', import.meta.url);
writeFileSync(manifest, JSON.stringify(dates, null, 2) + '\n');
console.log('git-dates.json written:', Object.keys(dates).length, 'routes');
