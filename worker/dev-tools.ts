/**
 * Owner-only dev tools. POST /api/dev/dmarc-seed sends a message claiming
 * From: dmarc-seed@promptdns.com to the owner's verified mailbox, so mailbox
 * providers generate an aggregate DMARC report the ingestion pipeline can
 * capture (the domain sends no real mail, so reports would otherwise be
 * sparse). Requires the owner session; never exposed publicly.
 */

import { EmailMessage } from 'cloudflare:email';
import { getUserBySession } from './auth';
import type { Env } from './index';

function json(data: unknown, status = 200): Response {
  return Response.json(data, { status });
}

function sameOrigin(request: Request): boolean {
  const origin = request.headers.get('Origin');
  if (!origin) return true;
  try {
    return new URL(origin).host === new URL(request.url).host;
  } catch {
    return false;
  }
}

interface DevEnv extends Env {
  OWNER_EMAIL?: string;
  SEND_EMAIL?: { send(message: unknown): Promise<void> };
}

export async function handleDmarcSeed(request: Request, env: DevEnv): Promise<Response> {
  if (request.method !== 'POST') return json({ ok: false, error: 'POST only.' }, 405);
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  if (!env.DB || !env.SEND_EMAIL || !env.OWNER_EMAIL) return json({ ok: false, error: 'Not configured.' }, 503);

  const user = await getUserBySession(env.DB, request);
  if (!user || user.email !== env.OWNER_EMAIL.trim().toLowerCase()) {
    return json({ ok: false, error: 'Owner only.' }, 403);
  }

  const raw = [
    'From: DMARC Seed <dmarc-seed@promptdns.com>',
    `To: ${env.OWNER_EMAIL}`,
    'Subject: DMARC report seed (automated test, ignore)',
    '',
    'This message was sent by the PromptDNS seed tool so mailbox providers include promptdns.com in their next aggregate DMARC report. It exercises the full report pipeline end to end.',
    '',
  ].join('\r\n');

  try {
    await env.SEND_EMAIL.send(new EmailMessage('dmarc-seed@promptdns.com', env.OWNER_EMAIL, raw));
  } catch (e) {
    return json({ ok: false, error: e instanceof Error ? e.message : 'Send failed.' }, 502);
  }
  return json({ ok: true });
}
