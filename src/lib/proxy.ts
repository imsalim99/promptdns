/**
 * CORS-aware text fetcher for cross-origin documents (robots.txt, llms.txt,
 * page metadata). Strategy: try direct fetch (target may send CORS headers),
 * then fall back through multiple public proxies so one outage never breaks
 * the tools. r.jina.ai output carries a metadata header which we strip.
 */
export interface ProxyResult {
  ok: boolean;
  text: string;
  via: 'direct' | 'allorigins' | 'codetabs' | 'jina' | 'failed';
  status: number;
}

const TIMEOUT = 12000;

async function timedFetch(url: string, headers: Record<string, string> = {}): Promise<Response> {
  const c = new AbortController();
  const t = setTimeout(() => c.abort(), TIMEOUT);
  try {
    return await fetch(url, { signal: c.signal, redirect: 'follow', headers });
  } finally {
    clearTimeout(t);
  }
}

/** Remove r.jina.ai's metadata header ("Markdown Content:" preamble). */
function stripJinaHeader(text: string): string {
  const marker = 'Markdown Content:';
  const idx = text.indexOf(marker);
  return idx >= 0 ? text.slice(idx + marker.length).replace(/^\s+/, '') : text;
}

export async function fetchText(url: string): Promise<ProxyResult> {
  // 1) direct (works when the target sends CORS headers)
  try {
    const res = await timedFetch(url);
    if (res.ok) {
      const text = await res.text();
      if (text) return { ok: true, text, via: 'direct', status: res.status };
    }
  } catch { /* try proxies */ }

  // 2) AllOrigins raw
  try {
    const res = await timedFetch(`https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`);
    if (res.ok) {
      const text = await res.text();
      if (text) return { ok: true, text, via: 'allorigins', status: res.status };
    }
  } catch { /* next */ }

  // 3) CodeTabs
  try {
    const res = await timedFetch(`https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(url)}`);
    if (res.ok) {
      const text = await res.text();
      if (text) return { ok: true, text, via: 'codetabs', status: res.status };
    }
  } catch { /* next */ }

  // 4) r.jina.ai (most reliable free option currently; strip its header)
  try {
    const res = await timedFetch(`https://r.jina.ai/${url}`);
    if (res.ok) {
      const text = stripJinaHeader(await res.text());
      if (text) return { ok: true, text, via: 'jina', status: res.status };
    }
    return { ok: false, text: '', via: 'failed', status: res.status };
  } catch {
    return { ok: false, text: '', via: 'failed', status: 0 };
  }
}

export function normalizeSite(input: string): string {
  let s = input.trim();
  if (!/^https?:\/\//i.test(s)) s = `https://${s}`;
  return s.replace(/\/+$/, '');
}

export function hostOf(input: string): string {
  return normalizeSite(input).replace(/^https?:\/\//i, '').split('/')[0].toLowerCase();
}
