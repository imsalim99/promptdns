import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';
import { isHeld } from './src/data/publish-queue.js';
import { execSync } from 'node:child_process';

/**
 * Build a map of file path -> last git commit ISO date.
 * One git invocation covers the whole repo; the result is cached for the build.
 * Falls back to an empty map (serialize omits lastmod) if git is unavailable.
 */
function buildGitDateMap() {
  try {
    const output = execSync('git log --format="%cI" --name-only', {
      encoding: 'utf-8',
      cwd: process.cwd(),
      maxBuffer: 20 * 1024 * 1024,
      timeout: 30000,
    });
    const dates = {};
    let currentDate = null;
    for (const line of output.split('\n')) {
      const trimmed = line.trim();
      if (/^\d{4}-\d{2}-\d{2}T/.test(trimmed)) {
        currentDate = trimmed;
      } else if (trimmed && currentDate) {
        // first sighting (newest commit) wins
        if (!dates[trimmed]) dates[trimmed] = currentDate;
      }
    }
    return dates;
  } catch {
    return {};
  }
}

const gitDates = buildGitDateMap();

/**
 * Map a sitemap URL path (/what-is-dns/) to its source file in src/pages/.
 * Handles both flat pages and subdirectory pages.
 */
function urlToSourceFile(urlPath) {
  const clean = urlPath.replace(/^\//, '').replace(/\/$/, '');
  if (!clean) return 'src/pages/index.astro';
  return 'src/pages/' + clean + '.astro';
}

export default defineConfig({
  site: 'https://promptdns.com',
  integrations: [
    sitemap({
      filter: (page) => !isHeld(new URL(page).pathname),
      serialize(item) {
        const sourceFile = urlToSourceFile(new URL(item.url).pathname);
        const gitDate = gitDates[sourceFile];
        if (gitDate) {
          // W3C datetime format for sitemaps: YYYY-MM-DDTHH:MM:SS+00:00
          item.lastmod = gitDate;
        }
        return item;
      },
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
});
