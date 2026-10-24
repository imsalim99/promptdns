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
