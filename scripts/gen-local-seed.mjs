// Generates scripts/_seed_local.sql + scripts/_token.txt for local dashboard
// verification. Run: node scripts/gen-local-seed.mjs
import crypto from 'node:crypto';
import fs from 'node:fs';

const token = crypto.randomBytes(32).toString('hex');
const hash = crypto.createHash('sha256').update(token).digest('hex');

const checks1 = JSON.stringify([
  { id: 'spf', label: 'SPF', status: 'fail', value: 'v=spf1 include:_spf.google.com include:sendgrid.net include:mailchimp.com ~all', earned: 0, weight: 15 },
  { id: 'dmarc', label: 'DMARC', status: 'pass', value: 'v=DMARC1; p=quarantine; rua=mailto:rua@promptdns.com', earned: 25, weight: 25 },
  { id: 'dkim', label: 'DKIM', status: 'warn', value: 'No selector found at google._domainkey', earned: 8, weight: 15 },
  { id: 'dnssec', label: 'DNSSEC', status: 'fail', value: 'No DS record at parent', earned: 0, weight: 10 },
  { id: 'mx', label: 'MX', status: 'pass', value: '10 mx.example-ship.com', earned: 10, weight: 10 },
  { id: 'website', label: 'Website', status: 'pass', value: '200 OK', earned: 10, weight: 10 },
  { id: 'ns', label: 'Nameservers', status: 'pass', value: '2 nameservers', earned: 15, weight: 15 },
]);
const checks2 = JSON.stringify([
  { id: 'spf', label: 'SPF', status: 'pass', value: 'v=spf1 include:mailgun.org -all', earned: 15, weight: 15 },
  { id: 'dmarc', label: 'DMARC', status: 'pass', value: 'v=DMARC1; p=reject; rua=mailto:rua@promptdns.com', earned: 25, weight: 25 },
  { id: 'dkim', label: 'DKIM', status: 'pass', value: 'Selector k1 found', earned: 15, weight: 15 },
  { id: 'dnssec', label: 'DNSSEC', status: 'pass', value: 'DS record present', earned: 10, weight: 10 },
  { id: 'mx', label: 'MX', status: 'pass', value: '10 mxa.mailgun.org', earned: 10, weight: 10 },
  { id: 'website', label: 'Website', status: 'pass', value: '200 OK', earned: 10, weight: 10 },
  { id: 'ns', label: 'Nameservers', status: 'pass', value: '2 nameservers', earned: 15, weight: 15 },
]);

const q = (s) => s.replace(/'/g, "''");
let sql = "DELETE FROM dmarc_sources; DELETE FROM dmarc_reports; DELETE FROM dmarc_marks; DELETE FROM alerts; DELETE FROM scan_runs; DELETE FROM snapshots; DELETE FROM domains; DELETE FROM sessions; DELETE FROM users;\n";
sql += "INSERT INTO users (id, email) VALUES (1, 'owner@local.test');\n";
sql += `INSERT INTO sessions (user_id, token_hash, expires_at) VALUES (1, '${hash}', datetime('now','+30 days'));\n`;
sql += "INSERT INTO domains (id, user_id, domain, last_checked_at, paused) VALUES (1, 1, 'example-ship.com', datetime('now','-2 hours'), 0), (2, 1, 'acme-books.net', datetime('now','-3 hours'), 0);\n";
sql += `INSERT INTO snapshots (domain_id, score, grade, checks_json, checked_at) VALUES (1, 72, 'C', '${q(checks1)}', datetime('now','-2 hours')), (2, 100, 'A', '${q(checks2)}', datetime('now','-3 hours'));\n`;
sql += "INSERT INTO alerts (user_id, domain_id, severity, title, detail, created_at, read_at) VALUES (1, 1, 'critical', 'SPF record failed the lookup limit', 'The SPF record on example-ship.com evaluates to 11 DNS lookups. Receivers may ignore the policy entirely. Remove or flatten an include.', datetime('now','-4 hours'), NULL), (1, 1, 'warning', 'DKIM selector not found', 'No DKIM key was published for the checked selector on example-ship.com. Publishing one lets mail sign correctly.', datetime('now','-26 hours'), NULL), (1, 2, 'info', 'All checks passed', 'acme-books.net passed every check on the latest run.', datetime('now','-3 hours'), datetime('now','-1 hours'));\n";
sql += "INSERT INTO scan_runs (domain_id, outcome, score, changes, ran_at) VALUES (1, 'changed', 72, 1, datetime('now','-2 hours')), (1, 'same', 78, 0, datetime('now','-8 hours')), (1, 'same', 80, 0, datetime('now','-14 hours')), (2, 'same', 100, 0, datetime('now','-3 hours'));\n";
for (let d = 12; d >= 0; d--) {
  const total = 8000 + Math.round(Math.sin(d) * 2000 + d * 120);
  const passing = Math.round(total * Math.min(0.99, 0.86 + 0.01 * (12 - d)));
  const rid = 1000 + d;
  sql += `INSERT INTO dmarc_reports (id, domain_id, org_name, report_id, date_begin, date_end, messages_total, received_at) VALUES (${rid}, 1, 'google.com', 'r${d}', date('now','-${d + 1} days'), date('now','-${d} days'), ${total}, datetime('now','-${d} days'));\n`;
  sql += `INSERT INTO dmarc_sources (report_ref, source_ip, header_from, count, spf_result, dkim_result, dmarc_result, disposition) VALUES (${rid}, '209.85.220.41', 'example-ship.com', ${Math.round(total * 0.7)}, 'pass', 'pass', 'pass', 'none');\n`;
  sql += `INSERT INTO dmarc_sources (report_ref, source_ip, header_from, count, spf_result, dkim_result, dmarc_result, disposition) VALUES (${rid}, '167.89.123.58', 'mail.example-ship.com', ${Math.round(total * 0.18)}, 'pass', 'fail', 'pass', 'none');\n`;
  sql += `INSERT INTO dmarc_sources (report_ref, source_ip, header_from, count, spf_result, dkim_result, dmarc_result, disposition) VALUES (${rid}, '203.0.113.44', NULL, ${Math.round(total * 0.12)}, 'fail', 'fail', 'fail', 'reject');\n`;
}

fs.writeFileSync('scripts/_seed_local.sql', sql);
fs.writeFileSync('scripts/_token.txt', token);
console.log('seed + token written');
