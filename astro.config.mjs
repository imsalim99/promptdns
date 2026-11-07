import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';
import { isHeld } from './src/data/publish-queue.js';
import { buildDatesFromGit, isShallowRepo } from './src/data/git-dates.lib.mjs';
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const MANIFEST = fileURLToPath(new URL('./src/data/git-dates.json', import.meta.url));

/**
 * Per-route content dates { route: { created, modified } }.
 *
 * Full clone: rebuild from git history and refresh the committed manifest so
 * it stays current for the next shallow build.
 * Shallow clone (Cloudflare Workers Builds): read the committed manifest
 * as-is, so dates can never collapse to the HEAD commit timestamp.
 * Falls back to an empty map (serialize omits lastmod) if both fail.
 */
function loadGitDates() {
  if (!isShallowRepo()) {
    try {
      const dates = buildDatesFromGit();
      if (Object.keys(dates).length > 0) {
        try {
          writeFileSync(MANIFEST, JSON.stringify(dates, null, 2) + '\n');
        } catch {
          /* manifest refresh is best-effort; the in-memory map is already good */
        }
        return dates;
      }
    } catch {
      /* fall through to the manifest */
    }
  }
  try {
    return JSON.parse(readFileSync(MANIFEST, 'utf8'));
  } catch {
    return {};
  }
}

const gitDates = loadGitDates();

/** '/what-is-dns/' -> '/what-is-dns/', '/' -> '/' (manifest keys are routes). */
function routeOf(urlPath) {
  const clean = String(urlPath).replace(/^\//, '').replace(/\/$/, '');
  return clean === '' ? '/' : '/' + clean + '/';
}

export default defineConfig({
  site: 'https://promptdns.com',
  integrations: [
    sitemap({
      // /app/ and /login/ are signed-in product surfaces (noindex, R0.18):
      // never listed in the sitemap regardless of the publish queue.
      filter: (page) => {
        const path = new URL(page).pathname;
        if (path === '/app/' || path === '/login/') return false;
        return !isHeld(path);
      },
      serialize(item) {
        const dates = gitDates[routeOf(new URL(item.url).pathname)];
        if (dates && dates.modified) {
          // W3C datetime format for sitemaps: YYYY-MM-DDTHH:MM:SS+00:00
          item.lastmod = dates.modified;
        }
        return item;
      },
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
});
