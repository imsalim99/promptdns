// GET /api/domains — list monitored domains. POST — add one. Auth: session cookie.
interface Env { DB: D1Database }

async function userId(request: Request, env: Env): Promise<string | null> {
  const m = (request.headers.get('Cookie') ?? '').match(/pdns_session=([^;\s]+)/);
  if (!m) return null;
  const row = await env.DB.prepare(
    'SELECT user_id FROM sessions WHERE token = ? AND expires_at > datetime(\'now\')'
  ).bind(m[1]).first<{ user_id: string }>();
  return row?.user_id ?? null;
}

export const onRequestGet: PagesFunction<Env> = async ({ request, env }) => {
  const uid = await userId(request, env);
  if (!uid) return Response.json({ error: 'Not signed in' }, { status: 401 });
  const { results } = await env.DB.prepare(
    'SELECT name, added_at FROM domains WHERE user_id = ? ORDER BY added_at DESC'
  ).bind(uid).all<{ name: string; added_at: string }>();
  return Response.json({ domains: results ?? [] });
};

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  const uid = await userId(request, env);
  if (!uid) return Response.json({ error: 'Not signed in' }, { status: 401 });
  const { name } = (await request.json()) as { name?: string };
  const domain = (name ?? '').trim().toLowerCase().replace(/^https?:\/\//, '').replace(/\/.*$/, '').replace(/\.$/, '');
  if (!domain.includes('.')) return Response.json({ error: 'Enter a valid domain.' }, { status: 400 });
  try {
    await env.DB.prepare('INSERT INTO domains (id, user_id, name) VALUES (?, ?, ?)')
      .bind(crypto.randomUUID(), uid, domain)
      .run();
  } catch {
    return Response.json({ error: 'That domain is already being monitored.' }, { status: 409 });
  }
  return Response.json({ ok: true, name: domain });
};

export const onRequestDelete: PagesFunction<Env> = async ({ request, env }) => {
  const uid = await userId(request, env);
  if (!uid) return Response.json({ error: 'Not signed in' }, { status: 401 });
  const { name } = (await request.json()) as { name?: string };
  const domain = (name ?? '').trim().toLowerCase();
  if (!domain.includes('.')) return Response.json({ error: 'Enter a valid domain.' }, { status: 400 });
  await env.DB.prepare('DELETE FROM domains WHERE user_id = ? AND name = ?')
    .bind(uid, domain)
    .run();
  return Response.json({ ok: true });
};
