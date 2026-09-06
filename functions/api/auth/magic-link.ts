// POST /api/auth/magic-link — issue a login link.
// With RESEND_API_KEY set: emails the link. Without (dev): returns it in the response.
interface Env {
  DB: D1Database;
  RESEND_API_KEY?: string;
}

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  const { email } = (await request.json()) as { email?: string };
  if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return Response.json({ error: 'Enter a valid email address.' }, { status: 400 });
  }
  const token = crypto.randomUUID() + crypto.randomUUID().replace(/-/g, '');
  const expires = new Date(Date.now() + 15 * 60 * 1000).toISOString();
  await env.DB.prepare('INSERT INTO magic_tokens (token, email, expires_at) VALUES (?, ?, ?)')
    .bind(token, email.toLowerCase(), expires)
    .run();

  const url = new URL(request.url);
  const link = `${url.origin}/api/auth/verify?token=${token}`;

  if (env.RESEND_API_KEY) {
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: 'PromptDNS <login@promptdns.com>',
        to: email,
        subject: 'Your PromptDNS sign-in link',
        html: `<p>Click to sign in to PromptDNS:</p><p><a href="${link}">Sign in</a></p><p>This link expires in 15 minutes. If you didn't request it, ignore this email.</p>`,
      }),
    });
    return Response.json({ sent: true });
  }
  // Dev mode: no email provider configured — surface the link directly.
  return Response.json({ sent: false, link, note: 'Dev mode: set RESEND_API_KEY to email links.' });
};
