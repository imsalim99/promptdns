/**
 * Owner-only dev tools. POST /api/dev/dmarc-seed sends a message claiming
 * From: dmarc-seed@promptdns.com to the owner's verified mailbox, so mailbox
 * providers generate an aggregate DMARC report the ingestion pipeline can
 * capture (the domain sends no real mail, so reports would otherwise be
 * sparse). Requires the owner session; never exposed publicly.
 */

import { EmailMessage } from 'cloudflare:email';
import { gzipSync } from 'fflate';
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

/**
 * POST /api/dev/dmarc-test sends a synthetic Google-format aggregate report
 * (gzipped XML attachment) to reports@promptdns.com. Exercises the full
 * ingestion pipeline live: send_email -> Email Routing -> email handler -> D1.
 * Owner-gated like the seed tool; report_id is timestamped so it never collides.
 */
export async function handleDmarcTest(request: Request, env: DevEnv): Promise<Response> {
  if (request.method !== 'POST') return json({ ok: false, error: 'POST only.' }, 405);
  if (!sameOrigin(request)) return json({ ok: false, error: 'Cross-origin request rejected.' }, 403);
  if (!env.DB || !env.SEND_EMAIL) return json({ ok: false, error: 'Not configured.' }, 503);

  const user = await getUserBySession(env.DB, request);
  if (!user || user.email !== env.OWNER_EMAIL?.trim().toLowerCase()) {
    return json({ ok: false, error: 'Owner only.' }, 403);
  }

  const now = Math.floor(Date.now() / 1000);
  const begin = now - 86400;
  const end = now;
  const reportId = `pdns-selftest-${now}`;
  const xml = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<feedback>',
    '  <report_metadata>',
    '    <org_name>google.com</org_name>',
    '    <email>noreply-dmarc-support@google.com</email>',
    `    <report_id>${reportId}</report_id>`,
    `    <date_range><begin>${begin}</begin><end>${end}</end></date_range>`,
    '  </report_metadata>',
    '  <policy_published>',
    '    <domain>promptdns.com</domain>',
    '    <adkim>r</adkim><aspf>r</aspf><p>none</p><sp>none</sp><pct>100</pct>',
    '  </policy_published>',
    '  <record>',
    '    <row>',
    '      <source_ip>209.85.220.41</source_ip>',
    '      <count>3</count>',
    '      <policy_evaluated><disposition>none</disposition><dkim>pass</dkim><spf>pass</spf></policy_evaluated>',
    '    </row>',
    '    <identifiers><header_from>promptdns.com</header_from></identifiers>',
    '  </record>',
    '</feedback>',
  ].join('\r\n');

  const gz = gzipSync(new TextEncoder().encode(xml));
  let binary = '';
  for (const b of gz) binary += String.fromCharCode(b);
  const b64 = btoa(binary);
  const filename = `google.com!promptdns.com!${begin}!${end}.gz`;

  const raw = [
    'From: DMARC Self Test <dmarc-test@promptdns.com>',
    'To: reports@promptdns.com',
    'Subject: Synthetic DMARC aggregate report (self test)',
    'MIME-Version: 1.0',
    'Content-Type: multipart/mixed; boundary="PDNSSELfTEST"',
    '',
    '--PDNSSELfTEST',
    'Content-Type: text/plain; charset=utf-8',
    '',
    'Synthetic test report from the PromptDNS dev tool. Safe to ignore.',
    '--PDNSSELfTEST',
    `Content-Type: application/gzip; name="${filename}"`,
    'Content-Transfer-Encoding: base64',
    `Content-Disposition: attachment; filename="${filename}"`,
    '',
    b64,
    '--PDNSSELfTEST--',
    '',
  ].join('\r\n');

  try {
    await env.SEND_EMAIL.send(new EmailMessage('dmarc-test@promptdns.com', 'reports@promptdns.com', raw));
  } catch (e) {
    return json({ ok: false, error: e instanceof Error ? e.message : 'Send failed.' }, 502);
  }
  return json({ ok: true, reportId });
}
