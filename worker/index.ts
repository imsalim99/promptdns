/**
 * PromptDNS Worker - API routes and canonical redirects for the static site.
 *
 * wrangler.toml sets run_worker_first = true, so every request passes through
 * this script: canonical 301 redirects (http -> https, extension-less page
 * paths -> trailing slash) and a guaranteed-clean /robots.txt are handled
 * here, /api/* routes run their handlers, and everything else falls through
 * to the asset layer (Astro build output, 404-page handling included).
 */

import { handleWaitlist, handleWaitlistVerify } from './waitlist';
import { handleMagicLink, handleVerify, handleMe, handleLogout, type AuthEnv } from './auth';
import { handleDomainsList, handleDomainsAdd, handleDomainsDelete, handleDomainsPause } from './domains';
import { handleRescan, runScheduled, handleAlertsList, handleAlertsRead, handleHistory } from './monitor';
import { handleDmarcEmail, handleDmarcQuery, handleDmarcMark, handleDmarcUpload } from './dmarc-ingest';
import { handleOverview } from './overview';
import { handleDmarcSeed } from './dev-tools';
import { handleAiCrawlerCheck } from './checks/ai-crawlers';
import { handleRobotsCheck } from './checks/robots-api';

interface Env {
  DB?: D1Database;
  ASSETS: { fetch(request: Request): Promise<Response> };
  SEND_EMAIL?: { send(message: unknown): Promise<void> };
  RESEND_API_KEY?: string;
}

export type { Env };

export default {
  async fetch(request: Request, env: Env & AuthEnv): Promise<Response> {
    try {
      return await handleFetch(request, env);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      console.error('Worker error:', msg);
      return Response.json({ ok: false, error: 'Worker error: ' + msg.slice(0, 200) }, { status: 500 });
    }
  },

  // Monitoring engine: re-scan every monitored domain every 6 hours
  // (crontab in wrangler.toml).
  async scheduled(_event: ScheduledController, env: Env & AuthEnv, ctx: ExecutionContext): Promise<void> {
    if (!env.DB) return;
    ctx.waitUntil(runScheduled(env));
  },

  // DMARC aggregate report ingestion: invoked by the Email Routing rule
  // for reports@promptdns.com (rule created in the Cloudflare dashboard).
  async email(message: ForwardableEmailMessage, env: Env & AuthEnv, _ctx: ExecutionContext): Promise<void> {
    await handleDmarcEmail(message, env);
  },
} satisfies ExportedHandler<Env & AuthEnv>;

async function handleFetch(request: Request, env: Env & AuthEnv): Promise<Response> {
  const url = new URL(request.url);
  const path = url.pathname;
  const method = request.method;

  // Canonical 301 redirects (GET and HEAD only): http -> https, and
  // extension-less page paths -> trailing slash. One hop combines both.
  if ((method === 'GET' || method === 'HEAD') && isRedirectCandidate(url)) {
    return permanentRedirect(url);
  }

  if (path === '/api/waitlist') return handleWaitlist(request, env);
  if (path === '/api/waitlist/verify') return handleWaitlistVerify(request, env);
  if (path === '/api/auth/magic-link') return handleMagicLink(request, env);
  if (path === '/api/auth/verify') return handleVerify(request, env);
  if (path === '/api/auth/me') return handleMe(request, env);
  if (path === '/api/auth/logout') return handleLogout(request, env);
  if (path === '/api/domains' && method === 'GET') return handleDomainsList(request, env);
  if (path === '/api/domains' && method === 'POST') return handleDomainsAdd(request, env);
  if (path === '/api/domains/delete') return handleDomainsDelete(request, env);
  if (path === '/api/domains/pause') return handleDomainsPause(request, env);
  if (path === '/api/domains/history') return handleHistory(request, env);
  if (path === '/api/overview') return handleOverview(request, env);
  if (path === '/api/domains/dmarc') return handleDmarcQuery(request, env);
  if (path === '/api/domains/dmarc/mark') return handleDmarcMark(request, env);
  if (path === '/api/domains/dmarc/upload' && method === 'POST') return handleDmarcUpload(request, env);
  if (path === '/api/dev/dmarc-seed') return handleDmarcSeed(request, env);
  if (path === '/api/domains/rescan') return handleRescan(request, env);
  if (path === '/api/alerts' && method === 'GET') return handleAlertsList(request, env);
  if (path === '/api/alerts/read') return handleAlertsRead(request, env);
  if (path === '/api/check/ai-crawlers' && method === 'GET') return handleAiCrawlerCheck(request, env);
  if (path === '/api/check/robots' && (method === 'GET' || method === 'POST')) return handleRobotsCheck(request, env);

  // /robots.txt is always our own file, never the Cloudflare managed block:
  // strip a managed section if the edge ever injects one, and pin the
  // content type for every user agent.
  if (path === '/robots.txt') {
    const asset = await env.ASSETS.fetch(request);
    const body = stripManagedRobots(await asset.text());
    return new Response(body, {
      status: 200,
      headers: {
        'content-type': 'text/plain; charset=utf-8',
        'cache-control': 'public, max-age=3600',
      },
    });
  }

  return env.ASSETS.fetch(request);
}

/** Local development hosts keep their scheme; production is always https. */
function isLocalHost(hostname: string): boolean {
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1' || hostname.endsWith('.localhost');
}

/**
 * True when this GET/HEAD request must be canonically redirected.
 * Extension-less page paths (e.g. /ttl-checker) need the trailing slash;
 * files (robots.txt, sitemap.xml, /_astro/* bundles, fonts, images) have a
 * dot in the last segment and are left alone, as are API and .well-known
 * paths. Any non-local http:// request redirects so https is always
 * canonical in production.
 */
function isRedirectCandidate(url: URL): boolean {
  if (url.protocol === 'http:' && !isLocalHost(url.hostname)) return true;
  const path = url.pathname;
  if (path.endsWith('/')) return false;
  if (path.startsWith('/api/') || path.startsWith('/_astro/') || path.startsWith('/.well-known/')) return false;
  const lastSegment = path.slice(path.lastIndexOf('/') + 1);
  return !lastSegment.includes('.');
}

/** 301 to the https trailing-slash form of the URL, preserving the query. */
function permanentRedirect(url: URL): Response {
  const target = new URL(url.toString());
  if (!isLocalHost(url.hostname)) target.protocol = 'https:';
  if (!target.pathname.endsWith('/')) target.pathname += '/';
  return new Response(null, {
    status: 301,
    headers: { location: target.toString() },
  });
}

/** Remove a Cloudflare managed robots.txt section if one is ever injected. */
function stripManagedRobots(body: string): string {
  const begin = body.indexOf('# BEGIN Cloudflare Managed content');
  const end = body.indexOf('# END Cloudflare Managed content');
  if (begin === -1 || end === -1 || end < begin) return body;
  return (body.slice(0, begin) + body.slice(end + '# END Cloudflare Managed content'.length)).replace(/^\s+/, '');
}
