/**
 * CORS-aware text fetcher for cross-origin documents (robots.txt, llms.txt,
 * page metadata). Tries a direct fetch first; falls back to a free public CORS
 * relay. At deploy time we replace the relay with our own Cloudflare Worker.
 */
export interface ProxyResult {
  ok: boolean;
  text: string;
  via: 'direct' | 'relay' | 'failed';
  status: number;
}

const TIMEOUT = 12000;

async function timedFetch(url: string): Promise<Response> {
  const c = new AbortController();
  const t = setTimeout(() => c.abort(), TIMEOUT);
  try {
    return await fetch(url, { signal: c.signal, redirect: 'follow' });
  } finally {
    clearTimeout(t);
  }
}

export async function fetchText(url: string): Promise<ProxyResult> {
  // 1) direct (works when the target sends CORS headers)
  try {
    const res = await timedFetch(url);
    if (res.ok) {
      const text = await res.text();
      if (text) return { ok: true, text, via: 'direct', status: res.status };
    }
  } catch { /* fall through to relay */ }
  // 2) public relay
  try {
    const res = await timedFetch(`https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`);
    if (res.ok) {
      const text = await res.text();
      if (text) return { ok: true, text, via: 'relay', status: res.status };
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
