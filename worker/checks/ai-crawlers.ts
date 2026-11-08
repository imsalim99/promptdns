/**
 * worker/checks/ai-crawlers.ts
 *
 * Orchestrator for the AI crawler access check and the read-only JSON
 * endpoint behind /ai-crawler-checker/.
 * GET /api/check/ai-crawlers?domain=<domain>
 *
 * One-way imports only: robots.ts and botfetch.ts never import this file.
 * Nothing is stored: results are per-request with a short in-memory cache
 * to keep repeated scans polite to the target domain.
 */

import { fetchRobots, parseRobots, evaluateToken, type RobotsParseResult } from './robots';
import { AI_BOTS, PURPOSE_LABELS, probeUrl, probeLlmsTxt, type BotSpec } from './botfetch';

export interface BotReport {
  token: string;
  operator: string;
  purpose: string;
  purposeLabel: string;
  fetches: boolean;
  doc: string | null;
  verification: string;
  robots: {
    verdict: 'allowed' | 'disallowed';
    matchedGroup: string | null;
    rule: string | null;
    note: string;
  };
  http: { status: number | null; kind: string; note: string; ms: number } | null;
  /** Combined verdict: allowed, disallowed, blocked, token, inconclusive. */
  verdict: 'allowed' | 'disallowed' | 'blocked' | 'token' | 'inconclusive';
  notes: string[];
}

export interface AiCrawlerReport {
  ok: true;
  domain: string;
  checkedAt: string;
  robots: {
    status: number | null;
    classification: string;
    note: string;
    finalUrl: string | null;
    managed: boolean;
    contentSignals: boolean;
    sitemaps: string[];
    groupCount: number;
    bytes: number;
  };
  llmsTxt: { present: boolean; status: number | null };
  bots: BotReport[];
  counts: { allowed: number; disallowed: number; blocked: number; token: number; inconclusive: number };
  durationMs: number;
}

const DOMAIN_RE = /^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$/;
const CACHE_TTL_MS = 120_000;
const CACHE_MAX = 50;
const cache = new Map<string, { at: number; report: AiCrawlerReport }>();

export function normalizeDomain(input: string): string | null {
  let d = String(input || '').trim().toLowerCase();
  d = d.replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0].split('?')[0].split('#')[0];
  if (d.endsWith('.')) d = d.slice(0, -1);
  if (!DOMAIN_RE.test(d)) return null;
  return d;
}

async function buildReport(domain: string): Promise<AiCrawlerReport> {
  const started = Date.now();
  const fetched = await fetchRobots(domain);
  let parsed: RobotsParseResult | null = null;
  if (fetched.body !== null) parsed = parseRobots(fetched.body);
  const llms = await probeLlmsTxt(domain);

  const specs: BotSpec[] = AI_BOTS;
  const probes = await Promise.all(
    specs.filter((b) => b.fetches).map((b) => probeUrl(domain, b.ua))
  );
  const probeByToken = new Map<string, Awaited<ReturnType<typeof probeUrl>>>();
  let i = 0;
  for (const b of specs) if (b.fetches) probeByToken.set(b.token, probes[i++]);

  const bots: BotReport[] = specs.map((b) => {
    const notes: string[] = [];
    let robotsVerdict: BotReport['robots'];
    if (fetched.classification === 'ok' && parsed) {
      const v = evaluateToken(parsed, b.token);
      robotsVerdict = { verdict: v.verdict, matchedGroup: v.matchedGroup, rule: v.rule, note: v.note };
    } else if (fetched.classification === 'unavailable-4xx') {
      robotsVerdict = { verdict: 'allowed', matchedGroup: null, rule: null, note: 'robots.txt unavailable (4xx): RFC 9309 treats every crawler as allowed' };
    } else {
      robotsVerdict = { verdict: 'allowed', matchedGroup: null, rule: null, note: 'robots.txt unreachable: verdict inconclusive, no real rules observed' };
    }
    if (parsed && parsed.managed) notes.push('Cloudflare managed robots.txt section detected: its rules sit in front of your own');
    if (parsed && parsed.contentSignals) notes.push('Content-Signal directives detected (non-standard)');
    if (llms.present) notes.push('/llms.txt present');

    const probe = b.fetches ? probeByToken.get(b.token) : undefined;
    const http = probe ? { status: probe.status, kind: probe.kind, note: probe.note, ms: probe.ms } : null;

    let verdict: BotReport['verdict'];
    if (!b.fetches) {
      verdict = robotsVerdict.verdict === 'disallowed' ? 'disallowed' : 'token';
    } else if (probe && (probe.kind === 'inconclusive' || probe.kind === 'server-error')) {
      verdict = 'inconclusive';
      if (probe.kind === 'server-error') notes.push('5xx on / : server error, not a bot-specific verdict');
    } else if (robotsVerdict.verdict === 'disallowed') {
      verdict = 'disallowed';
    } else if (probe && probe.kind === 'blocked') {
      verdict = 'blocked';
      notes.push('robots.txt allows this token but the edge refused the fetch');
    } else {
      verdict = 'allowed';
    }
    return {
      token: b.token,
      operator: b.operator,
      purpose: b.purpose,
      purposeLabel: PURPOSE_LABELS[b.purpose],
      fetches: b.fetches,
      doc: b.doc,
      verification: b.verification,
      robots: robotsVerdict,
      http,
      verdict,
      notes,
    };
  });

  const counts = { allowed: 0, disallowed: 0, blocked: 0, token: 0, inconclusive: 0 };
  for (const b of bots) counts[b.verdict]++;

  return {
    ok: true,
    domain,
    checkedAt: new Date().toISOString(),
    robots: {
      status: fetched.status,
      classification: fetched.classification,
      note: fetched.note,
      finalUrl: fetched.finalUrl,
      managed: parsed ? parsed.managed : false,
      contentSignals: parsed ? parsed.contentSignals : false,
      sitemaps: parsed ? parsed.sitemaps.slice(0, 10) : [],
      groupCount: parsed ? parsed.groups.length : 0,
      bytes: parsed ? parsed.bytes : 0,
    },
    llmsTxt: llms,
    bots,
    counts,
    durationMs: Date.now() - started,
  };
}

export async function handleAiCrawlerCheck(request: Request, _env: unknown): Promise<Response> {
  const url = new URL(request.url);
  const domain = normalizeDomain(url.searchParams.get('domain') || '');
  if (!domain) {
    return Response.json({ ok: false, error: 'Provide a valid domain, e.g. example.com.' }, { status: 400 });
  }
  const hit = cache.get(domain);
  if (hit && Date.now() - hit.at < CACHE_TTL_MS) {
    return Response.json(hit.report);
  }
  const report = await buildReport(domain);
  cache.set(domain, { at: Date.now(), report });
  if (cache.size > CACHE_MAX) {
    const oldest = cache.keys().next().value;
    if (oldest) cache.delete(oldest);
  }
  return Response.json(report);
}
