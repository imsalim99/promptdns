/**
 * worker/checks/robots.ts
 *
 * RFC 9309 compliant robots.txt fetcher, parser and evaluator.
 * One-way import module: imported by worker/checks/ai-crawlers.ts and
 * (later) the dashboard monitors and /robots-txt-checker/. Imports nothing
 * from other worker modules.
 *
 * Semantics implemented:
 * - Fetch with up to 5 redirects (RFC 9309 section 2.3).
 * - 2xx: parse up to 500 KiB (RFC 9309 section 2.2).
 * - 4xx: unavailable, treat as allow-all for every crawler (section 2.3.1).
 * - 5xx or network failure: unreachable, inconclusive (treated by crawlers
 *   as a temporary disallow, never reported here as a real block).
 * - Groups: consecutive User-agent lines share one group; duplicate groups
 *   for the same token combine; the wildcard * group never merges with a
 *   named group; a named group always wins over * (section 2.2.1).
 * - Path matching: case-sensitive, * wildcard, $ end anchor, longest
 *   matching pattern by octet length wins, Allow wins a length tie
 *   (section 2.2.2). An empty Disallow value carries no restriction.
 */

export interface RobotsRule {
  type: 'allow' | 'disallow' | 'content-signal';
  path: string;
  raw: string;
  /** 1-based line number in the source file. */
  line: number;
}

export interface RobotsGroup {
  tokens: string[];
  rules: RobotsRule[];
}

export interface RobotsParseResult {
  groups: RobotsGroup[];
  sitemaps: string[];
  /** Cloudflare managed section markers detected in the raw body. */
  managed: boolean;
  /** Non-standard Content-Signal directives detected. */
  contentSignals: boolean;
  /** Syntax problems and structural notes (rules before UA, missing /, merged duplicates). */
  errors: string[];
  notes: string[];
  bytes: number;
  truncated: boolean;
}

export type FetchClass = 'ok' | 'unavailable-4xx' | 'unreachable-5xx' | 'error';

export interface RobotsFetch {
  status: number | null;
  classification: FetchClass;
  /** Raw body up to 500 KiB, null when not fetched. */
  body: string | null;
  finalUrl: string | null;
  redirects: number;
  note: string;
}

const MAX_BYTES = 500 * 1024;
const MAX_REDIRECTS = 5;
const FETCH_TIMEOUT_MS = 8000;

/** Fetch https://<domain>/robots.txt following up to 5 redirects. */
export async function fetchRobots(domain: string): Promise<RobotsFetch> {
  let url = 'https://' + domain + '/robots.txt';
  let redirects = 0;
  for (;;) {
    let res: Response;
    try {
      res = await fetch(url, {
        method: 'GET',
        redirect: 'manual',
        signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
        headers: { 'user-agent': 'PromptDNS-RobotsCheck/1.0 (+https://promptdns.com/robots-txt-checker/)' },
      });
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      return { status: null, classification: 'error', body: null, finalUrl: url, redirects, note: 'fetch failed: ' + msg.slice(0, 80) };
    }
    if (res.status >= 300 && res.status < 400) {
      const loc = res.headers.get('location');
      if (!loc || redirects >= MAX_REDIRECTS) {
        return { status: res.status, classification: 'error', body: null, finalUrl: url, redirects, note: 'redirect loop or missing Location header' };
      }
      try {
        url = new URL(loc, url).toString();
      } catch {
        return { status: res.status, classification: 'error', body: null, finalUrl: url, redirects, note: 'invalid redirect target' };
      }
      redirects++;
      continue;
    }
    if (res.status >= 200 && res.status < 300) {
      const buf = await res.arrayBuffer();
      const truncated = buf.byteLength > MAX_BYTES;
      const body = new TextDecoder('utf-8', { fatal: false }).decode(truncated ? buf.slice(0, MAX_BYTES) : buf);
      return { status: res.status, classification: 'ok', body, finalUrl: url, redirects, note: truncated ? 'body truncated at 500 KiB per RFC 9309' : '' };
    }
    if (res.status >= 400 && res.status < 500) {
      return { status: res.status, classification: 'unavailable-4xx', body: null, finalUrl: url, redirects, note: 'unavailable: RFC 9309 says treat as allow-all' };
    }
    return { status: res.status, classification: 'unreachable-5xx', body: null, finalUrl: url, redirects, note: 'unreachable: RFC 9309 says treat as temporary disallow' };
  }
}

/** Parse a robots.txt body into groups, sitemaps, CDN markers and syntax notes. */
export function parseRobots(raw: string): RobotsParseResult {
  const managed = raw.includes('# BEGIN Cloudflare Managed content');
  const result: RobotsParseResult = { groups: [], sitemaps: [], managed, contentSignals: false, errors: [], notes: [], bytes: raw.length, truncated: false };

  let pending: string[] = [];
  let current: RobotsGroup | null = null;

  const flushGroup = (): RobotsGroup | null => {
    if (pending.length === 0) return current;
    const tokens = pending.map((t) => t.trim()).filter((t) => t.length > 0);
    pending = [];
    if (tokens.length === 0) return current;
    for (const t of tokens) {
      if (t.includes('*') && t !== '*') {
        result.errors.push(`Wildcard inside User-agent token "${t}" (line ${result.errors.length + 1}): only a standalone * is a wildcard; this token is treated literally.`);
      }
    }
    // Merge duplicate groups carrying the exact same token set (RFC 9309
    // section 2.2.1: crawlers may combine). The wildcard group stays
    // separate from any named group.
    const key = tokens.map((t) => t.toLowerCase()).join(',');
    for (const g of result.groups) {
      if (g.tokens.map((t) => t.toLowerCase()).join(',') === key) {
        result.notes.push(`Duplicate groups for User-agent: ${g.tokens[0]} were merged (RFC 9309 section 2.2.1).`);
        current = g;
        return g;
      }
    }
    const g: RobotsGroup = { tokens, rules: [] };
    result.groups.push(g);
    current = g;
    return g;
  };

  const lines = raw.split(/\r\n|\n|\r/);
  for (let lineNo = 1; lineNo <= lines.length; lineNo++) {
    const rawLine = lines[lineNo - 1];
    // Detect Content-Signal anywhere (non-standard Cloudflare directive).
    if (!result.contentSignals && /^\s*content-signal\s*:/i.test(rawLine)) {
      result.contentSignals = true;
    }
    // Strip comments AFTER the managed marker check on the raw body.
    const hash = rawLine.indexOf('#');
    const line = (hash === -1 ? rawLine : rawLine.slice(0, hash)).trim();
    if (line.length === 0) continue;
    const colon = line.indexOf(':');
    if (colon === -1) {
      result.errors.push(`Line ${lineNo}: no colon, "${line.slice(0, 50)}". Crawlers ignore malformed lines.`);
      continue;
    }
    const field = line.slice(0, colon).trim().toLowerCase();
    const value = line.slice(colon + 1).trim();

    if (field === 'user-agent') {
      if (current && pending.length === 0) {
        // A User-agent line after rules starts a new group.
        current = null;
      }
      pending.push(value);
      continue;
    }
    if (field === 'sitemap') {
      result.sitemaps.push(value);
      continue;
    }
    if (field === 'allow' || field === 'disallow') {
      const g = flushGroup();
      if (!g) {
        result.errors.push(`Line ${lineNo}: ${field}: rule appears before any User-agent line and applies to no group.`);
        continue;
      }
      if (value && !value.startsWith('/') && !value.startsWith('*')) {
        result.errors.push(`Line ${lineNo}: ${field}: path "${value.slice(0, 40)}" does not start with / and may never match.`);
      }
      g.rules.push({ type: field as 'allow' | 'disallow', path: value, raw: line, line: lineNo });
      continue;
    }
    if (field === 'content-signal') {
      const g = flushGroup();
      if (!g) continue;
      g.rules.push({ type: 'content-signal', path: value, raw: line, line: lineNo });
      continue;
    }
    // Unknown fields (Crawl-delay, Clean-param, ...) are ignored.
  }
  flushGroup();
  return result;
}

/** Pattern to regex: * wildcard matches any sequence, $ anchors the end. */
function patternToRegex(pattern: string): RegExp | null {
  if (pattern.length === 0) return null;
  let out = '';
  for (const ch of pattern) {
    if (ch === '*') out += '[\\s\\S]*';
    else if (ch === '$') out += '$';
    else out += ch.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  try {
    return new RegExp('^' + out);
  } catch {
    return null;
  }
}

export interface TokenVerdict {
  verdict: 'allowed' | 'disallowed';
  /** Group whose rules decided the verdict: the named token or '*'. */
  matchedGroup: string | null;
  /** The winning rule line, e.g. "Allow: /" or "Disallow: /private/". */
  rule: string | null;
  note: string;
}

/**
 * Evaluate one token against parsed rules for the root path "/".
 * Longest matching pattern by octet length wins; Allow wins a tie.
 */
export function evaluateToken(parsed: RobotsParseResult, token: string, path = '/'): TokenVerdict {
  const lower = token.toLowerCase();
  const specific = parsed.groups.filter((g) => g.tokens.some((t) => t.toLowerCase() === lower));
  const wildcard = parsed.groups.filter((g) => g.tokens.includes('*'));
  const active = specific.length > 0 ? specific : wildcard;
  if (active.length === 0) {
    return { verdict: 'allowed', matchedGroup: null, rule: null, note: 'no group for this token: allowed by default' };
  }
  const matchedGroup = specific.length > 0 ? specific[0].tokens[0] : '*';
  let best: { rule: RobotsRule; len: number } | null = null;
  for (const g of active) {
    for (const rule of g.rules) {
      if (rule.type !== 'allow' && rule.type !== 'disallow') continue;
      // An empty Disallow value carries no restriction (RFC 9309).
      if (rule.type === 'disallow' && rule.path.length === 0) continue;
      const re = patternToRegex(rule.path);
      if (!re || !re.test(path)) continue;
      const len = rule.path.length;
      if (!best || len > best.len || (len === best.len && rule.type === 'allow' && best.rule.type === 'disallow')) {
        best = { rule, len };
      }
    }
  }
  if (!best) {
    return { verdict: 'allowed', matchedGroup, rule: null, note: 'no matching rule for / in group ' + matchedGroup };
  }
  return {
    verdict: best.rule.type === 'allow' ? 'allowed' : 'disallowed',
    matchedGroup,
    rule: best.rule.raw,
    note: 'inherited from User-agent: ' + matchedGroup,
  };
}
