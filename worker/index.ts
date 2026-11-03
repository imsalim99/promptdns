/**
 * PromptDNS Worker - API routes for the static site (Workers static assets).
 *
 * Static asset requests never reach this script (the asset layer answers
 * first); only non-asset paths like /api/* arrive here. Everything else
 * falls through to the asset layer, which serves the Astro 404 page.
 */

import { handleWaitlist, handleWaitlistVerify } from './waitlist';
import { handleMagicLink, handleVerify, handleMe, handleLogout, type AuthEnv } from './auth';
import { handleDomainsList, handleDomainsAdd, handleDomainsDelete, handleDomainsPause } from './domains';
import { handleRescan, runScheduled, handleAlertsList, handleAlertsRead, handleHistory } from './monitor';
import { handleDmarcEmail, handleDmarcQuery, handleDmarcMark, handleDmarcUpload } from './dmarc-ingest';
import { handleVerifyStart, handleVerifyCheck } from './verify';
import { handleRulesList, handleRulesCreate, handleRulesUpdate, handleRulesDelete, handleDigestSetting } from './rules';
import { handleOverview } from './overview';
import { handleDmarcSeed } from './dev-tools';

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
  async scheduled(_event: ScheduledEvent, env: Env & AuthEnv, ctx: ExecutionContext): Promise<void> {
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

    if (path === '/api/rules' && method === 'GET') return handleRulesList(request, env);
    if (path === '/api/rules' && method === 'POST') return handleRulesCreate(request, env);
    if (path === '/api/rules/update' && method === 'POST') return handleRulesUpdate(request, env);
    if (path === '/api/rules/delete' && method === 'POST') return handleRulesDelete(request, env);
    if (path === '/api/settings/digest' && method === 'POST') return handleDigestSetting(request, env);
    if (path === '/api/domains/verify/check' && method === 'POST') return handleVerifyCheck(request, env);
    if (path === '/api/dev/dmarc-seed') return handleDmarcSeed(request, env);
    if (path === '/api/domains/rescan') return handleRescan(request, env);
    if (path === '/api/alerts' && method === 'GET') return handleAlertsList(request, env);
    if (path === '/api/alerts/read') return handleAlertsRead(request, env);

    return env.ASSETS.fetch(request);
}
