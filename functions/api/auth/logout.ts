// POST /api/auth/logout — clear session.
interface Env { DB: D1Database }

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  const cookie = request.headers.get('Cookie') ?? '';
  const m = cookie.match(/pdns_session=([^;\s]+)/);
  if (m) await env.DB.prepare('DELETE FROM sessions WHERE token = ?').bind(m[1]).run();
  return new Response(null, {
    status: 302,
    headers: { Location: '/', 'Set-Cookie': 'pdns_session=; Path=/; HttpOnly; Max-Age=0' },
  });
};
