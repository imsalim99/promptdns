/**
 * Local end-to-end test of the DMARC ingestion path with real prod packages:
 * builds a Google-format raw email (gzipped XML attachment), runs it through
 * the REAL handleDmarcEmail with a mock D1, and asserts the stored rows.
 * Verifies everything except the live email-handler invocation itself.
 */
import { buildSync } from 'esbuild';
import { writeFileSync, mkdirSync } from 'node:fs';
import { gzipSync } from 'node:zlib';

mkdirSync('tmp', { recursive: true });

const bundle = buildSync({
  entryPoints: ['worker/dmarc-ingest.ts'],
  bundle: true,
  format: 'esm',
  platform: 'node',
  outfile: 'tmp/dmarc-ingest.test.mjs',
  external: ['cloudflare:email'],
  logLevel: 'silent',
});

const { handleDmarcEmail } = await import('../tmp/dmarc-ingest.test.mjs');

// Google-style XML
const now = Math.floor(Date.now() / 1000);
const xml = `<?xml version="1.0" encoding="UTF-8"?>
<feedback>
  <report_metadata>
    <org_name>google.com</org_name>
    <email>noreply-dmarc-support@google.com</email>
    <extra_contact_info>https://support.google.com/a/answer/2466580</extra_contact_info>
    <report_id>1750000000000000-test</report_id>
    <date_range><begin>${now - 86400}</begin><end>${now}</end></date_range>
  </report_metadata>
  <policy_published>
    <domain>promptdns.com</domain>
    <adkim>r</adkim><aspf>r</aspf><p>none</p><sp>none</sp><pct>100</pct>
  </policy_published>
  <record>
    <row>
      <source_ip>209.85.220.41</source_ip>
      <count>7</count>
      <policy_evaluated><disposition>none</disposition><dkim>pass</dkim><spf>pass</spf></policy_evaluated>
    </row>
    <identifiers><header_from>promptdns.com</header_from></identifiers>
  </record>
  <record>
    <row>
      <source_ip>203.0.113.99</source_ip>
      <count>2</count>
      <policy_evaluated><disposition>none</disposition><dkim>fail</dkim><spf>fail</spf></policy_evaluated>
    </row>
    <identifiers><header_from>promptdns.com</header_from></identifiers>
  </record>
</feedback>`;

const gz = gzipSync(Buffer.from(xml, 'utf8'));
const filename = `google.com!promptdns.com!${now - 86400}!${now}.gz`;
const b64 = gz.toString('base64');
// RFC 2045: base64 lines max 76 chars, like real mail
const b64wrapped = b64.replace(/(.{76})/g, '$1\r\n').trimEnd();

const rawEmail = [
  'From: Google <noreply-dmarc-support@google.com>',
  'To: reports@promptdns.com',
  'Subject: Report domain: promptdns.com Submitter: google.com Report-ID: 1750000000000000-test',
  'Date: Mon, 26 Oct 2026 12:00:00 +0000',
  'MIME-Version: 1.0',
  'Content-Type: multipart/mixed; boundary="000000000000fe1a2b0605c3d4e5"',
  '',
  '--000000000000fe1a2b0605c3d4e5',
  'Content-Type: text/plain; charset="UTF-8"',
  '',
  'Attachment: google.com!promptdns.com report.',
  '--000000000000fe1a2b0605c3d4e5',
  `Content-Type: application/gzip; name="${filename}"`,
  'Content-Disposition: attachment; filename="' + filename + '"',
  'Content-Transfer-Encoding: base64',
  'X-Attachment-Id: f_test123',
  '',
  b64wrapped,
  '--000000000000fe1a2b0605c3d4e5--',
  '',
].join('\r\n');

// Mock D1 capturing inserts
class MockStmt {
  constructor(db, sql) { this.db = db; this.sql = sql; this._binds = []; }
  bind(...args) { this._binds = args; return this; }
  async all() {
    if (/SELECT id FROM domains/.test(this.sql)) {
      return { results: [{ id: 42 }] }; // promptdns.com is monitored, id 42
    }
    return { results: [] };
  }
  async run() {
    const isReport = /INSERT OR IGNORE INTO dmarc_reports/.test(this.sql);
    if (isReport) {
      this.db.reports.push(this._binds);
      return { meta: { changes: 1, last_row_id: 1000 + this.db.reports.length } };
    }
    this.db.sources.push(this._binds);
    return { meta: { changes: 1 } };
  }
  async first() { return null; }
}
class MockD1 {
  constructor() { this.reports = []; this.sources = []; }
  prepare(sql) { return new MockStmt(this, sql); }
}

const db = new MockD1();
const rejects = [];
const message = {
  to: 'reports@promptdns.com',
  raw: new ReadableStream({
    start(c) {
      c.enqueue(new TextEncoder().encode(rawEmail));
      c.close();
    },
  }),
  setRejectReason(r) { rejects.push(r); },
};

await handleDmarcEmail(message, { DB: db });

console.log('reports stored:', db.reports.length);
console.log('sources stored:', db.sources.length);
if (db.reports.length) {
  const [domain_id, org, rid, begin, end, policy, total] = db.reports[0];
  console.log('  report:', { domain_id, org, rid, begin, end, policy, total });
}
db.sources.forEach((s, i) => console.log('  source', i, s));

const ok = db.reports.length === 1 && db.sources.length === 2
  && db.reports[0][2] === '1750000000000000-test'
  && db.reports[0][6] === 9
  && db.sources[0][1] === '209.85.220.41' && db.sources[0][3] === 7
  && db.sources[1][1] === '203.0.113.99';
console.log(ok ? '\nPASS: full pipeline works with prod packages' : '\nFAIL: pipeline broken');
process.exit(ok ? 0 : 1);
