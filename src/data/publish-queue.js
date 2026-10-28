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
  // Publishing rule (2026-10-28): no noindex-holding of linked pages - Googlebot
  // deprioritizes noindex'd URLs and recrawl lags for weeks after the hold lifts.
  // Diverse batches ship index,follow immediately; only large programmatic
  // batches (record leaves, ESP long tail) get paced, in weekly deploy waves.
  // Reuse this queue with future dates only if bulk staging is ever needed again.
};

/** True when the given path is held back from indexing on the given date. */
export function isHeld(path, today = new Date()) {
  const date = PUBLISH_QUEUE[path];
  if (!date) return false;
  return new Date(date + 'T23:59:59Z') > today;
}
