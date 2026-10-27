/**
 * Drip-release queue (spec section 9: paced publishing).
 *
 * Maps a page path to its publishOn date. Pages in the queue:
 *  - carry `noindex, nofollow` until their date passes (BaseLayout),
 *  - are excluded from the sitemap until their date passes (astro.config),
 *  - flip to fully public automatically on the first build after the date
 *    (the daily deploy workflow re-runs the build every day).
 *
 * Dates are staggered in small randomized-feeling batches; drop new rows here
 * when adding drip content. Remove rows once published (or keep for history).
 */
export const PUBLISH_QUEUE = {
  '/gptbot/': '2026-11-04',
  '/claudebot/': '2026-11-06',
  '/google-extended/': '2026-11-08',
  '/perplexitybot/': '2026-11-10',
  '/oai-searchbot/': '2026-11-12',
  '/ccbot/': '2026-11-14',
  '/bytespider/': '2026-11-17',
  '/does-blocking-ai-crawlers-hurt-seo/': '2026-11-19',
  '/ai-crawler-verification/': '2026-11-21',
  '/block-ai-crawlers-cloudflare/': '2026-11-24',
  '/gptbot-vs-claudebot/': '2026-11-26',
  '/dns-server-not-responding/': '2026-11-28',
  '/dns-probe-finished-nxdomain/': '2026-12-01',
  '/err-name-not-resolved/': '2026-12-03',
  '/registrar-vs-dns-hosting/': '2026-12-05',
  '/check-spf-dkim-dmarc-dig/': '2026-12-08',
};

/** True when the given path is held back from indexing on the given date. */
export function isHeld(path, today = new Date()) {
  const date = PUBLISH_QUEUE[path];
  if (!date) return false;
  return new Date(date + 'T23:59:59Z') > today;
}
