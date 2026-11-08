/**
 * worker/checks/botfetch.ts
 *
 * Live HTTP response probe per AI bot user agent.
 * One-way import module: imported by worker/checks/ai-crawlers.ts. Imports
 * nothing from other worker modules.
 *
 * Why per-token probes exist: robots.txt is advisory and sits above the
 * network. A WAF or CDN (Cloudflare Bot Fight Mode, AI Crawl Control, an
 * ASN block) can answer 403, 429 or 503 to a fetch that robots.txt allows.
 * This module probes https://<domain>/ with each real crawler's user agent
 * and classifies the response.
 */

export type PurposeClass = 'training' | 'search' | 'user-fetch' | 'control';

export interface BotSpec {
  token: string;
  operator: string;
  purpose: PurposeClass;
  /** User-Agent string used for the live probe; empty for control tokens. */
  ua: string;
  /** Control tokens never fetch: they are robots.txt policy declarations. */
  fetches: boolean;
  /** Operator documentation URL, when the operator publishes one. */
  doc: string | null;
  /** How the operator says to verify real traffic. */
  verification: string;
}

export const PURPOSE_LABELS: Record<PurposeClass, string> = {
  training: 'Model Training',
  search: 'AI Search Index',
  'user-fetch': 'User-Initiated Fetch',
  control: 'Control Token Only',
};

const OPENAI_DOCS = 'https://platform.openai.com/docs/bots';
const ANTHROPIC_DOCS = 'https://docs.anthropic.com/en/docs/agents-and-tools/crawlers';
const GOOGLE_DOCS = 'https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers';
const APPLE_DOCS = 'https://support.apple.com/en-us/HT204684';
const PERPLEXITY_DOCS = 'https://docs.perplexity.ai/guides/bots';

/** The 17 tokens this tool reports, across the 4 purpose classes. */
export const AI_BOTS: BotSpec[] = [
  { token: 'GPTBot', operator: 'OpenAI', purpose: 'training', ua: 'GPTBot/1.0', fetches: true, doc: OPENAI_DOCS, verification: 'Reverse DNS on *.openai.com addresses per operator docs' },
  { token: 'OAI-SearchBot', operator: 'OpenAI', purpose: 'search', ua: 'OAI-SearchBot/1.0', fetches: true, doc: OPENAI_DOCS, verification: 'Reverse DNS on *.openai.com addresses per operator docs' },
  { token: 'ChatGPT-User', operator: 'OpenAI', purpose: 'user-fetch', ua: 'ChatGPT-User/1.0', fetches: true, doc: OPENAI_DOCS, verification: 'Reverse DNS on *.openai.com addresses per operator docs' },
  { token: 'ClaudeBot', operator: 'Anthropic', purpose: 'training', ua: 'ClaudeBot/1.0', fetches: true, doc: ANTHROPIC_DOCS, verification: 'Reverse DNS on *.anthropic.com addresses per operator docs' },
  { token: 'Claude-SearchBot', operator: 'Anthropic', purpose: 'search', ua: 'Claude-SearchBot/1.0', fetches: true, doc: ANTHROPIC_DOCS, verification: 'Reverse DNS on *.anthropic.com addresses per operator docs' },
  { token: 'Claude-User', operator: 'Anthropic', purpose: 'user-fetch', ua: 'Claude-User/1.0', fetches: true, doc: ANTHROPIC_DOCS, verification: 'Reverse DNS on *.anthropic.com addresses per operator docs' },
  { token: 'PerplexityBot', operator: 'Perplexity', purpose: 'search', ua: 'PerplexityBot/1.0', fetches: true, doc: PERPLEXITY_DOCS, verification: 'Reverse DNS on *.perplexity.ai addresses per operator docs' },
  { token: 'Perplexity-User', operator: 'Perplexity', purpose: 'user-fetch', ua: 'Perplexity-User/1.0', fetches: true, doc: PERPLEXITY_DOCS, verification: 'Reverse DNS on *.perplexity.ai addresses per operator docs' },
  { token: 'Google-Extended', operator: 'Google', purpose: 'control', ua: '', fetches: false, doc: GOOGLE_DOCS, verification: 'Control token: no crawler fetches under this name' },
  { token: 'Applebot-Extended', operator: 'Apple', purpose: 'control', ua: '', fetches: false, doc: APPLE_DOCS, verification: 'Control token: no crawler fetches under this name' },
  { token: 'CCBot', operator: 'Common Crawl', purpose: 'training', ua: 'CCBot/2.0', fetches: true, doc: 'https://commoncrawl.org/ccbot', verification: 'Operator documents respect for robots.txt; reverse DNS on *.commoncrawl.org' },
  { token: 'Bytespider', operator: 'ByteDance', purpose: 'training', ua: 'Bytespider', fetches: true, doc: null, verification: 'No public operator documentation or verification method' },
  { token: 'Amazonbot', operator: 'Amazon', purpose: 'training', ua: 'Amazonbot/1.0', fetches: true, doc: 'https://developer.amazon.com/support/amazonbot', verification: 'Reverse DNS on *.amazonbot.com addresses per operator docs' },
  { token: 'Meta-ExternalAgent', operator: 'Meta', purpose: 'training', ua: 'meta-externalagent/1.1', fetches: true, doc: 'https://developers.facebook.com/docs/sharing/webmasters/crawler', verification: 'Reverse DNS on *.fbsv.net or facebot naming per operator docs' },
  { token: 'cohere-ai', operator: 'Cohere', purpose: 'training', ua: 'cohere-ai', fetches: true, doc: null, verification: 'No public operator documentation or verification method' },
  { token: 'Diffbot', operator: 'Diffbot', purpose: 'training', ua: 'Mozilla/5.0 (compatible; Diffbot/2.1)', fetches: true, doc: 'https://docs.diffbot.com/', verification: 'Operator documents its crawler in its own docs; no published IP list' },
  { token: 'YouBot', operator: 'You.com', purpose: 'training', ua: 'YouBot (+http://y.com/bot)', fetches: true, doc: null, verification: 'No public operator documentation or verification method' },
];

export type HttpKind = 'ok' | 'blocked' | 'server-error' | 'inconclusive';

export interface ProbeResult {
  status: number | null;
  kind: HttpKind;
  note: string;
  ms: number;
}

const PROBE_TIMEOUT_MS = 8000;

/**
 * Probe https://<domain>/ with a given user agent. HEAD first, one GET
 * fallback when the server rejects HEAD or errors; the GET body is
 * cancelled immediately so the probe stays lightweight.
 */
export async function probeUrl(domain: string, ua: string): Promise<ProbeResult> {
  const started = Date.now();
  const finish = (status: number | null, kind: HttpKind, note: string): ProbeResult => ({ status, kind, note, ms: Date.now() - started });

  const attempt = async (method: 'HEAD' | 'GET'): Promise<Response> =>
    fetch('https://' + domain + '/', {
      method,
      signal: AbortSignal.timeout(PROBE_TIMEOUT_MS),
      headers: { 'user-agent': ua, accept: 'text/html' },
    });

  let res: Response;
  try {
    res = await attempt('HEAD');
    if (res.status === 405 || res.status >= 500) {
      // Some servers do not answer HEAD cleanly: one polite GET fallback.
      // The GET body is cancelled immediately so the probe stays lightweight.
      const getRes = await attempt('GET');
      await getRes.body?.cancel();
      res = getRes;
    }
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    return finish(null, 'inconclusive', 'fetch failed: ' + msg.slice(0, 60));
  }

  if (res.status >= 200 && res.status < 300) return finish(res.status, 'ok', 'fetched normally');
  if (res.status === 401 || res.status === 403 || res.status === 429 || res.status === 503) {
    return finish(res.status, 'blocked', 'edge or WAF refusal (challenge, rate limit, or bot rule)');
  }
  if (res.status >= 500) return finish(res.status, 'server-error', 'server error, not a bot-specific verdict');
  return finish(res.status, 'ok', 'reachable with status ' + res.status);
}

/** Probe for llms.txt presence: 200 with any body counts as present. */
export async function probeLlmsTxt(domain: string): Promise<{ present: boolean; status: number | null }> {
  try {
    const res = await fetch('https://' + domain + '/llms.txt', {
      method: 'GET',
      signal: AbortSignal.timeout(6000),
      headers: { 'user-agent': 'PromptDNS-AiCrawlerCheck/1.0 (+https://promptdns.com/ai-crawler-checker/)' },
    });
    await res.body?.cancel();
    return { present: res.status >= 200 && res.status < 300, status: res.status };
  } catch {
    return { present: false, status: null };
  }
}
