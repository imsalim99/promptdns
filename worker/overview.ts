/**
 * GET /api/overview - the Overview screen in one round trip:
 * domain count, open alerts, average latest score, and DMARC totals
 * (including the daily pass/fail series) across all of the user's domains.
 */

import { getUserBySession } from './auth';
import type { Env } from './index';

function json(data: unknown, status = 200): Response {
  return Response.json(data, { status });
}

export async function handleOverview(request: Request, env: Env): Promise<Response> {
  if (!env.DB) return json({ ok: false, error: 'Storage is not configured.' }, 503);
  const user = await getUserBySession(env.DB, request);
  if (!user) return json({ ok: false, error: 'Sign in first.' }, 401);
  const uid = user.id;

  const domainCount = await env.DB
    .prepare('SELECT COUNT(*) AS n FROM domains WHERE user_id = ?1')
    .bind(uid)
    .first<{ n: number }>();

  const alertsOpen = await env.DB
    .prepare("SELECT COUNT(*) AS n FROM alerts WHERE user_id = ?1 AND read_at IS NULL")
    .bind(uid)
    .first<{ n: number }>();

  const avg = await env.DB
    .prepare(
      `SELECT AVG(s.score) AS avgScore
         FROM snapshots s
         JOIN (SELECT domain_id, MAX(id) AS mid FROM snapshots
                WHERE domain_id IN (SELECT id FROM domains WHERE user_id = ?1)
                GROUP BY domain_id) latest ON latest.mid = s.id`,
    )
    .bind(uid)
    .first<{ avgScore: number | null }>();

  const dmarcTotals = await env.DB
    .prepare(
      `SELECT COUNT(DISTINCT r.id) AS reports,
              COALESCE(SUM(r.messages_total), 0) AS messages
         FROM dmarc_reports r
        WHERE r.domain_id IN (SELECT id FROM domains WHERE user_id = ?1)`,
    )
    .bind(uid)
    .first<{ reports: number; messages: number }>();

  const dmarcPass = await env.DB
    .prepare(
      `SELECT COALESCE(SUM(s.count), 0) AS total,
              COALESCE(SUM(CASE WHEN s.dmarc_result = 'pass' THEN s.count ELSE 0 END), 0) AS passing
         FROM dmarc_sources s
         JOIN dmarc_reports r ON r.id = s.report_ref
        WHERE r.domain_id IN (SELECT id FROM domains WHERE user_id = ?1)`,
    )
    .bind(uid)
    .first<{ total: number; passing: number }>();

  const daily = await env.DB
    .prepare(
      `SELECT r.date_end AS date,
              SUM(s.count) AS total,
              SUM(CASE WHEN s.dmarc_result = 'pass' THEN s.count ELSE 0 END) AS passing
         FROM dmarc_sources s
         JOIN dmarc_reports r ON r.id = s.report_ref
        WHERE r.domain_id IN (SELECT id FROM domains WHERE user_id = ?1) AND r.date_end IS NOT NULL
        GROUP BY r.date_end ORDER BY r.date_end DESC LIMIT 30`,
    )
    .bind(uid)
    .all<{ date: string; total: number; passing: number }>();

  const activity = await env.DB
    .prepare(
      `SELECT date(ran_at) AS date,
              COUNT(*) AS runs,
              ROUND(AVG(score)) AS avgScore
         FROM scan_runs
        WHERE domain_id IN (SELECT id FROM domains WHERE user_id = ?1) AND score IS NOT NULL
        GROUP BY date(ran_at) ORDER BY date DESC LIMIT 14`,
    )
    .bind(uid)
    .all<{ date: string; runs: number; avgScore: number }>();

  const total = dmarcPass?.total ?? 0;
  return json({
    ok: true,
    domains: domainCount?.n ?? 0,
    max: 3,
    alertsOpen: alertsOpen?.n ?? 0,
    avgScore: avg?.avgScore === null || avg?.avgScore === undefined ? null : Math.round(avg.avgScore),
    dmarc: {
      reports: dmarcTotals?.reports ?? 0,
      messages: dmarcTotals?.messages ?? 0,
      passRate: total > 0 ? Math.round(((dmarcPass?.passing ?? 0) / total) * 100) : null,
      daily: (daily.results ?? []).slice().reverse(),
    },
    activity: (activity.results ?? []).slice().reverse().map((a) => ({ date: a.date, runs: a.runs, avgScore: Math.round(a.avgScore) })),
  });
}
