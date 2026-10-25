-- PromptDNS D1 schema v1 (prod + staging identical)
-- Lean on purpose: only tables a shipped feature uses. Auth, domains,
-- snapshots, alerts and DMARC tables are added in later versions when
-- those features ship (never paste unreviewed schema into production).

CREATE TABLE IF NOT EXISTS waitlist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL,
  domain TEXT,
  source TEXT,
  -- SHA-256 of the submitter IP, used only for flood limiting, never exposed
  ip_hash TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(email)
);

-- v2: accounts and sign-in (magic link). Tokens are stored hashed (SHA-256);
-- the raw token exists only in the email link / cookie.

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  created_at TEXT DEFAULT (datetime('now')),
  last_login_at TEXT
);

CREATE TABLE IF NOT EXISTS auth_tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id),
  token_hash TEXT NOT NULL UNIQUE,
  purpose TEXT NOT NULL DEFAULT 'magic_link',
  expires_at TEXT NOT NULL,
  used_at TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id),
  token_hash TEXT NOT NULL UNIQUE,
  expires_at TEXT DEFAULT (datetime('now', '+30 days')),
  created_at TEXT DEFAULT (datetime('now')),
  last_seen_at TEXT
);

-- Generic per-key hourly counters (hashed IP + action), shared by auth and
-- (later) other endpoints.
CREATE TABLE IF NOT EXISTS rate_limits (
  key TEXT PRIMARY KEY,
  count INTEGER NOT NULL DEFAULT 0,
  window_start TEXT NOT NULL DEFAULT (datetime('now'))
);

-- v3: monitored domains + scan snapshots (taken at add-time now; scheduled
-- re-checks arrive with the monitoring engine, which reuses this table).

CREATE TABLE IF NOT EXISTS domains (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id),
  domain TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(user_id, domain)
);

CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  domain_id INTEGER NOT NULL REFERENCES domains(id),
  score INTEGER,
  grade TEXT,
  checks_json TEXT NOT NULL,
  checked_at TEXT DEFAULT (datetime('now'))
);

-- v4: monitoring engine. Snapshots are stored only when checks change
-- (snapshot-on-change); alerts are created from scan diffs. fail_count
-- guards against false "domain vanished" alerts during transient DoH
-- outages: two consecutive unresolvable runs are required before alerting.

CREATE TABLE IF NOT EXISTS alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id),
  domain_id INTEGER NOT NULL REFERENCES domains(id),
  severity TEXT NOT NULL,
  title TEXT NOT NULL,
  detail TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  read_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_snapshots_domain ON snapshots(domain_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id, id DESC);

ALTER TABLE domains ADD COLUMN last_checked_at TEXT;
ALTER TABLE domains ADD COLUMN fail_count INTEGER NOT NULL DEFAULT 0;
