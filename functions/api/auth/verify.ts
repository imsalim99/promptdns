// GET /api/auth/verify?token=... — consume magic token, set session cookie, redirect to dashboard.
interface Env { DB: D1Database }

export const onRequestGet: PagesFunction<Env> = async ({ request, env }) => {
  const token = new URL(request.url).searchParams.get('token') ?? '';
  const row = await env.DB.prepare('SELECT email, expires_at FROM magic_tokens WHERE token = ?')
    .bind(token)
    .first<{ email: string; expires_at: string }>();

  if (!row || new Date(row.expires_at) < new Date()) {
    return new Response('This sign-in link is invalid or expired. Request a new one.', { status: 400 });
  }
  await env.DB.prepare('DELETE FROM magic_tokens WHERE token = ?').bind(token).run();

  // Create user if first login
  await env.DB.prepare('INSERT OR IGNORE INTO users (id, email) VALUES (?, ?)')
    .bind(crypto.randomUUID(), row.email)
    .run();
  const user = await env.DB.prepare('SELECT id FROM users WHERE email = ?')
    .bind(row.email)
    .first<{ id: string }>();

  const session = crypto.randomUUID() + crypto.randomUUID().replace(/-/g, '');
  const expires = new Date(Date.now() + 30 * 24 * 3600 * 1000).toISOString();
  await env.DB.prepare('INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)')
    .bind(session, user!.id, expires)
    .run();

  return new Response(null, {
    status: 302,
    headers: {
      Location: '/dashboard/',
      'Set-Cookie': `pdns_session=${session}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${30 * 24 * 3600}`,
    },
  });
};
