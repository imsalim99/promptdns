-- PromptDNS SaaS schema (Cloudflare D1 / SQLite)
-- Dashboard → Storage & Databases → D1 → create database "promptdns"
-- → Console (paste this file) → Run.

CREATE TABLE IF NOT EXISTS magic_tokens (
  token      TEXT PRIMARY KEY,
  email      TEXT NOT NULL,
  expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id         TEXT PRIMARY KEY,
  email      TEXT UNIQUE NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sessions (
  token      TEXT PRIMARY KEY,
  user_id    TEXT NOT NULL,
  expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS domains (
  id       TEXT PRIMARY KEY,
  user_id  TEXT NOT NULL,
  name     TEXT NOT NULL,
  added_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_domains_user ON domains(user_id);

CREATE TABLE IF NOT EXISTS dmarc_reports (
  id          TEXT PRIMARY KEY,
  domain_id   TEXT NOT NULL,
  org_name    TEXT,
  total_msgs  INTEGER NOT NULL DEFAULT 0,
  pass_count  INTEGER NOT NULL DEFAULT 0,
  raw_json    TEXT,
  received_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS alerts (
  id         TEXT PRIMARY KEY,
  domain_id  TEXT NOT NULL,
  kind       TEXT NOT NULL,
  message    TEXT NOT NULL,
  severity   TEXT NOT NULL DEFAULT 'info',
  is_read    INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_alerts_domain ON alerts(domain_id);

CREATE TABLE IF NOT EXISTS plan_state (
  user_id     TEXT PRIMARY KEY,
  plan        TEXT NOT NULL DEFAULT 'free',
  ls_order_id TEXT,
  updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
