/**
 * Per-route content dates from git history.
 *
 * One `git log --name-only` pass covers the whole repo. Iterating newest to
 * oldest: the FIRST sighting of a page file is its last content change
 * (modified); the LAST sighting is the commit that added it (created).
 * Layout-only commits never touch page files, so per-page dates are naturally
 * immune to shell and component changes.
 *
 * Consumers:
 *  - scripts/gen_git_dates.mjs (full local clone, writes the manifest)
 *  - astro.config.mjs (full clone: rebuild + refresh manifest; shallow clone:
 *    read the committed manifest so dates never collapse to HEAD)
 *  - src/layouts/BaseLayout.astro (imports the committed JSON directly)
 */
import { execSync } from 'node:child_process';

/** True when this checkout has truncated git history (Workers Builds does). */
export function isShallowRepo() {
  try {
    return execSync('git rev-parse --is-shallow-repository', { encoding: 'utf8' }).trim() === 'true';
  } catch {
    return true; // no git available: behave like a shallow checkout
  }
}

/**
 * Map a path under src/pages/ to its site route.
 * 'index.astro' -> '/', 'foo.astro' -> '/foo/', 'a/b/index.md' -> '/a/b/'.
 * Returns null for dynamic routes, which cannot map to a single URL.
 */
export function fileToRoute(rel) {
  let p = String(rel).replace(/\\/g, '/').replace(/^src\/pages\//, '').replace(/\.(astro|md|markdown|html)$/i, '');
  if (p.startsWith('[')) return null;
  p = p.replace(/(^|\/)index$/i, '');
  return '/' + p + (p === '' ? '' : '/');
}

/**
 * Build { route: { created, modified } } from git history.
 * Dates are full ISO commit timestamps (W3C datetime, sitemap-safe).
 */
export function buildDatesFromGit() {
  const out = {};
  let output = '';
  try {
    output = execSync('git log --format=%cI --name-only', {
      encoding: 'utf8',
      maxBuffer: 64 * 1024 * 1024,
      timeout: 60000,
      cwd: process.cwd(),
    });
  } catch {
    return out;
  }
  let current = null;
  for (const raw of output.split('\n')) {
    const line = raw.trim();
    if (!line) continue;
    if (/^\d{4}-\d{2}-\d{2}T/.test(line)) {
      current = line;
      continue;
    }
    if (!current || !line.startsWith('src/pages/')) continue;
    const route = fileToRoute(line);
    if (!route) continue;
    if (!out[route]) out[route] = { created: current, modified: current };
    else out[route].created = current;
  }
  return out;
}
