/**
 * PromptDNS Worker - API routes for the static site (Workers static assets).
 *
 * Static asset requests never reach this script (the asset layer answers
 * first); only non-asset paths like /api/* arrive here. Everything else
 * falls through to the asset layer, which serves the Astro 404 page.
 */

import { handleWaitlist } from './waitlist';
import { handleMagicLink, handleVerify, handleMe, handleLogout, type AuthEnv } from './auth';
import { handleDomainsList, handleDomainsAdd, handleDomainsDelete } from './domains';

interface Env {
  DB?: D1Database;
  ASSETS: { fetch(request: Request): Promise<Response> };
}

export type { Env };

export default {
  async fetch(request: Request, env: Env & AuthEnv): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    if (path === '/api/waitlist') return handleWaitlist(request, env);
    if (path === '/api/auth/magic-link') return handleMagicLink(request, env);
    if (path === '/api/auth/verify') return handleVerify(request, env);
    if (path === '/api/auth/me') return handleMe(request, env);
    if (path === '/api/auth/logout') return handleLogout(request, env);
    if (path === '/api/domains' && method === 'GET') return handleDomainsList(request, env);
    if (path === '/api/domains' && method === 'POST') return handleDomainsAdd(request, env);
    if (path === '/api/domains/delete') return handleDomainsDelete(request, env);

    return env.ASSETS.fetch(request);
  },
} satisfies ExportedHandler<Env & AuthEnv>;
