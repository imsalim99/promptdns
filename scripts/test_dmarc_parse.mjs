/* Sanity test for the DMARC aggregate XML extraction logic (same pattern as worker/dmarc-ingest.ts). */
import { XMLParser } from 'fast-xml-parser';

const SAMPLE = `<?xml version="1.0"?>
<feedback>
  <report_metadata>
    <org_name>google.com</org_name>
    <email>noreply-dmarc-support@google.com</email>
    <report_id>1234567890</report_id>
    <date_range><begin>1761388800</begin><end>1761475199</end></date_range>
  </report_metadata>
  <policy_published>
    <domain>promptdns.com</domain>
    <p>none</p>
  </policy_published>
  <record>
    <row>
      <source_ip>209.85.222.201</source_ip>
      <count>120</count>
      <policy_evaluated>
        <disposition>none</disposition>
        <dkim>pass</dkim>
        <spf>pass</spf>
      </policy_evaluated>
    </row>
    <identifiers><header_from>promptdns.com</header_from></identifiers>
    <auth_results>
      <dkim><domain>promptdns.com</domain><result>pass</result></dkim>
      <spf><domain>promptdns.com</domain><result>pass</result></spf>
    </auth_results>
  </record>
  <record>
    <row>
      <source_ip>203.0.113.7</source_ip>
      <count>5</count>
      <policy_evaluated>
        <disposition>none</disposition>
        <dkim>fail</dkim>
        <spf>fail</spf>
      </policy_evaluated>
    </row>
    <identifiers><header_from>promptdns.com</header_from></identifiers>
    <auth_results>
      <spf><domain>spammy.example</domain><result>fail</result></spf>
    </auth_results>
  </record>
</feedback>`;

const parser = new XMLParser({ ignoreAttributes: true });
const doc = parser.parse(SAMPLE);
const fb = doc.feedback;
const meta = fb.report_metadata ?? {};
const published = fb.policy_published ?? {};
const recordsRaw = Array.isArray(fb.record) ? fb.record : fb.record ? [fb.record] : [];
const toIso = (e) => (e ? new Date(Number(e) * 1000).toISOString().slice(0, 10) : null);

const rows = recordsRaw.map((rec) => {
  const row = rec.row ?? {};
  const ev = row.policy_evaluated ?? {};
  const spf = String(ev.spf ?? '?');
  const dkim = String(ev.dkim ?? '?');
  return {
    ip: String(row.source_ip ?? '?'),
    count: Number(row.count ?? 0),
    disposition: String(ev.disposition ?? '?'),
    spf,
    dkim,
    dmarc: spf === 'pass' || dkim === 'pass' ? 'pass' : 'fail',
    header_from: String(rec.identifiers?.header_from ?? '?'),
  };
});

const result = {
  domain: String(published.domain ?? '').toLowerCase(),
  org: String(meta.org_name ?? 'unknown'),
  reportId: String(meta.report_id ?? ''),
  begin: toIso(meta.date_range?.begin),
  end: toIso(meta.date_range?.end),
  policyP: String(published.p ?? ''),
  records: rows,
};

console.log(JSON.stringify(result, null, 1));

const assert = (cond, msg) => { if (!cond) { console.error('FAIL:', msg); process.exit(1); } };
assert(result.domain === 'promptdns.com', 'domain');
assert(result.org === 'google.com', 'org');
assert(result.reportId === '1234567890', 'report id');
assert(result.begin === '2025-10-25', 'begin date');
assert(result.policyP === 'none', 'policy');
assert(result.records.length === 2, 'record count');
assert(result.records[0].dmarc === 'pass' && result.records[1].dmarc === 'fail', 'dmarc verdicts');
assert(result.records[1].count === 5, 'count');
console.log('ALL PARSER ASSERTIONS PASS');
