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
