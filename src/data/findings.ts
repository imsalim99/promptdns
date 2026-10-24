/**
 * Shared finding definitions for the Result Contract.
 *
 * One entry per finding code a tool can emit. The texts here are the single
 * source of truth: they are rendered by ResultCard on tool pages and will be
 * reused verbatim by alerts and the dashboard when monitoring ships.
 *
 * Writing rules (owner standing rules):
 * - Plain hyphens only, never em dashes.
 * - No guaranteed verdicts about receiver behaviour; say what the record
 *   permits receivers to conclude, citing the RFC when a rule matters.
 * - Fix steps must be actions a user can actually take, in order.
 */

export type Severity = 'fail' | 'warn' | 'pass' | 'info';

export interface FindingDef {
  severity: Severity;
  title: string;
  why: string;
  fix: string[];
  guide?: { label: string; href: string };
}

/** Finding emitted by a tool, with an optional dynamic headline sentence. */
export interface PdnsFinding {
  code: string;
  detail?: string;
}

/** Structured result dispatched as `pdns:result` and rendered by ResultCard. */
export interface PdnsResult {
  tool: string;
  domain: string;
  verdict: Severity;
  verdictLine: string;
  findings: PdnsFinding[];
  related?: { label: string; href: string }[];
  /** Optional CTA label override (per audit CTA map, e.g. DMARC: "See who sends email as your domain"). */
  ctaLabel?: string;
}

export const FINDINGS: Record<string, FindingDef> = {
  /* ---------------- SPF Record Checker ---------------- */

  SPF_LOOKUP_OVER_LIMIT: {
    severity: 'fail',
    title: 'Too many DNS lookup terms',
    why: 'RFC 7208 caps SPF evaluation at 10 DNS lookup terms. When a receiver reaches the limit it stops evaluating and returns permerror, so the record stops protecting the domain at all: the failure is caused by the record\'s structure, not by any sender.',
    fix: [
      'Open the record at your DNS provider and review each include: entry. Remove any service you no longer send mail through.',
      'Check each remaining provider\'s current SPF guidance before assuming their records are unchanged.',
      'Publish the trimmed record and re-run this check: the count must be 10 or fewer before nested includes are even counted.',
      'Avoid automatic flattening unless you also monitor the result: flattened IP lists go stale when a provider changes its infrastructure.',
    ],
    guide: { label: 'SPF permerror: causes and fixes', href: '/spf-permerror/' },
  },

  SPF_LOOKUP_NEAR_LIMIT: {
    severity: 'warn',
    title: 'Close to the DNS lookup limit',
    why: 'The record is within the limit, but a single new include: from you or a provider can push it over. Once over, evaluation ends in permerror for every receiver.',
    fix: [
      'Remove include: entries for services you no longer use.',
      'Re-run this check after any email vendor change; vendors sometimes add lookups on their side.',
    ],
  },

  SPF_MULTIPLE_RECORDS: {
    severity: 'fail',
    title: 'Multiple SPF records',
    why: 'RFC 7208 requires exactly one v=spf1 record per domain. When multiple records exist, evaluation ends in permerror regardless of what the records say.',
    fix: [
      'Keep the single correct record and delete every other v=spf1 TXT record at your DNS provider.',
      'Merge any senders listed only in the deleted records into the one you keep.',
      'Re-run this check; it must find exactly one record.',
    ],
    guide: { label: 'SPF permerror: causes and fixes', href: '/spf-permerror/' },
  },

  SPF_SYNTAX_ERROR: {
    severity: 'fail',
    title: 'Unrecognized terms in the record',
    why: 'A term a receiver does not recognize ends evaluation with permerror. A single typo in one mechanism name can disable the whole policy.',
    fix: [
      'Check each unrecognized term for typos, for example incllude: instead of include:.',
      'Confirm the term is real SPF syntax from RFC 7208, not a provider instruction pasted into the record.',
      'Publish the corrected record and re-run this check.',
    ],
    guide: { label: 'SPF records explained', href: '/spf-record/' },
  },

  SPF_PTR_DEPRECATED: {
    severity: 'warn',
    title: 'Deprecated ptr mechanism',
    why: 'RFC 7208 deprecates ptr: it is slow, results differ across receivers, and most implementations no longer trust it.',
    fix: [
      'Remove the ptr mechanism from the record.',
      'Authorize those senders with include: or ip4: entries instead.',
    ],
  },

  SPF_NO_ALL: {
    severity: 'warn',
    title: 'No "all" mechanism',
    why: 'Without an all mechanism the record makes no assertion about unlisted senders: they evaluate as neutral. The record can still support DMARC, but on its own it restricts nobody.',
    fix: [
      'End the record with ~all (softfail) as the common safe default, or -all (hard fail) once every legitimate sender is listed.',
    ],
    guide: { label: 'Softfail vs hardfail: ~all vs -all', href: '/spf-softfail-vs-hardfail/' },
  },

  SPF_PLUS_ALL: {
    severity: 'fail',
    title: '+all authorizes everyone',
    why: '+all authorizes every host on the internet to send mail as your domain. It defeats the purpose of SPF entirely.',
    fix: [
      'Remove +all and end the record with ~all or -all instead.',
    ],
    guide: { label: 'Softfail vs hardfail: ~all vs -all', href: '/spf-softfail-vs-hardfail/' },
  },

  SPF_NOT_PUBLISHED: {
    severity: 'warn',
    title: 'No SPF record published',
    why: 'The domain publishes TXT records but none is an SPF policy. If the domain sends mail, receivers cannot use SPF to tell your mail from spoofed mail.',
    fix: [
      'If the domain sends email, publish one v=spf1 TXT record listing your sending services.',
      'If it never sends email, no SPF record is needed; publishing v=spf1 -all states that explicitly.',
    ],
  },

  SPF_NO_TXT: {
    severity: 'info',
    title: 'No TXT records returned',
    why: 'The resolver returned no TXT records at all. That can mean the domain publishes none, or that the query did not complete. This is inconclusive, not a fail.',
    fix: [
      'Verify the domain resolves at all: run the DNS Record Lookup tool with record type A.',
      'Retry this check; transient resolver failures are common.',
    ],
  },

  SPF_DNS_UNREACHABLE: {
    severity: 'info',
    title: 'DNS query did not complete',
    why: 'The DNS query could not be completed, so nothing is known about the domain\'s SPF. This is an inconclusive result, not a pass or fail.',
    fix: [
      'Retry the check; transient network issues are common.',
      'If it keeps failing, check your connection or try from another network.',
    ],
  },

  SPF_VALID: {
    severity: 'pass',
    title: 'Record is syntactically valid',
    why: 'The record\'s syntax is well-formed and its top-level lookup terms are within the evaluation limit.',
    fix: [
      'Syntax validity is not sender verification: to confirm a real sender passes, send a test message and read its Authentication-Results header.',
      'Re-run this check after any DNS or email vendor change.',
    ],
  },

  /* ---------------- DMARC Record Checker ---------------- */

  DMARC_NOT_PUBLISHED: {
    severity: 'fail',
    title: 'No DMARC record',
    why: 'Without a DMARC record, receiving servers have no policy from you, so spoofed mail using your domain is treated like any other mail. DMARC is also how you would find out who sends as your domain.',
    fix: [
      'Publish a DMARC record at your DNS provider: v=DMARC1; p=none; rua=mailto:you@yourdomain.com to start in monitoring mode.',
      'Stay in monitoring mode until aggregate reports show every legitimate sender passing SPF or DKIM alignment.',
      'Then step the policy to quarantine and finally reject.',
    ],
    guide: { label: 'DMARC explained', href: '/dmarc/' },
  },

  DMARC_SYNTAX_ERROR: {
    severity: 'fail',
    title: 'Errors in the DMARC record',
    why: 'A malformed or incomplete DMARC record can make receivers ignore the policy entirely, which leaves the domain unprotected.',
    fix: [
      'Fix each error listed above; most are typos or a missing required tag.',
      'The record must start with v=DMARC1 and must include a p= tag.',
      'Re-run this check after publishing the corrected record.',
    ],
    guide: { label: 'DMARC explained', href: '/dmarc/' },
  },

  DMARC_P_NONE: {
    severity: 'warn',
    title: 'Policy is monitoring only (p=none)',
    why: 'With p=none receivers take no action on failing mail: spoofed mail is still delivered. Monitoring mode is the correct start, but it is not protection.',
    fix: [
      'Read the aggregate reports (rua) until every legitimate sender passes SPF or DKIM alignment.',
      'Move to p=quarantine, optionally ramping with pct= (25, then 50, then 100).',
      'Finish with p=reject once the reports are clean.',
    ],
    guide: { label: 'DMARC explained', href: '/dmarc/' },
  },

  DMARC_NO_RUA: {
    severity: 'warn',
    title: 'No aggregate reporting address (rua)',
    why: 'Without rua= you receive no aggregate reports, so you cannot see who is sending as your domain or whether your legitimate mail passes. A policy without reports cannot be tuned safely.',
    fix: [
      'Add rua=mailto:you@yourdomain.com to the record.',
      'Confirm the destination mailbox (or report processor) accepts mail from mailbox providers.',
      'Re-run this check to confirm the tag parses.',
    ],
    guide: { label: 'DMARC explained', href: '/dmarc/' },
  },

  DMARC_UNKNOWN_TAG: {
    severity: 'warn',
    title: 'Unknown tags in the record',
    why: 'Tags receivers do not recognize are ignored, and an unknown tag is often a typo in a tag you meant to set.',
    fix: [
      'Check the spelling of each unknown tag against the DMARC tag list.',
      'Remove tags that are not valid DMARC syntax.',
    ],
  },

  DMARC_FULL_ENFORCEMENT: {
    severity: 'info',
    title: 'Full enforcement (p=reject with pct=100)',
    why: 'Every failing message is subject to rejection. That is the goal, but any legitimate sender not yet passing SPF or DKIM alignment will be lost with it.',
    fix: [
      'Watch aggregate reports for legitimate mail failing alignment.',
      'If legitimate mail is rejected, lower pct= temporarily instead of reverting the policy.',
    ],
  },

  DMARC_HEALTHY: {
    severity: 'pass',
    title: 'DMARC is configured with a policy and reporting',
    why: 'The record has a policy and a reporting address, so receivers act on failing mail and you can monitor what passes and fails.',
    fix: [
      'Keep reading the aggregate reports: enforcement is ongoing maintenance, not a one-time setting.',
      'Re-run this check after any email vendor change.',
    ],
  },

  DMARC_DNS_UNREACHABLE: {
    severity: 'info',
    title: 'DNS query did not complete',
    why: 'The DNS query could not be completed, so nothing is known about the domain\'s DMARC. This is an inconclusive result, not a pass or fail.',
    fix: [
      'Retry the check; transient network issues are common.',
      'If it keeps failing, check your connection or try from another network.',
    ],
  },

  /* ---------------- DKIM Record Checker ---------------- */

  DKIM_NOT_FOUND: {
    severity: 'warn',
    title: 'No DKIM key at this selector',
    why: 'This check looked up exactly one selector. DKIM keys live at selector._domainkey.yourdomain.com and every provider chooses its own selector names, so a missing key here does not prove the domain has no DKIM.',
    fix: [
      'Find the real selector: open a recent message sent by the domain and read the s= value in its DKIM-Signature header.',
      'Or check the provider\'s DKIM page: google (Workspace), selector1/selector2 (Microsoft 365), k1 (Mailchimp), s1/s2 (Zoho).',
      'If DKIM is genuinely not set up, enable it in the provider and publish the TXT record it gives you.',
    ],
    guide: { label: 'DKIM explained', href: '/dkim/' },
  },

  DKIM_WEAK_KEY: {
    severity: 'warn',
    title: 'Weak DKIM key (under 2048-bit)',
    why: 'RSA keys under 2048 bits are considered weak, and some receivers reject or distrust mail signed with 1024-bit keys. The size shown is estimated from the published key material.',
    fix: [
      'Generate a 2048-bit key in your email provider\'s DKIM settings.',
      'Publish the new record, and remove the old key only after the new one verifies.',
      'Re-run this check with the same selector.',
    ],
    guide: { label: 'DKIM explained', href: '/dkim/' },
  },

  DKIM_VALID: {
    severity: 'pass',
    title: 'DKIM key found and parsed',
    why: 'A public key was found at this selector and its properties parsed. The key size is estimated from the published key material.',
    fix: [
      'To confirm signing works end to end, send a message and check the DKIM verdict in its Authentication-Results header.',
      'Re-check after any key rotation.',
    ],
  },

  DKIM_DNS_UNREACHABLE: {
    severity: 'info',
    title: 'DNS query did not complete',
    why: 'The DNS query could not be completed, so nothing is known about this selector. This is an inconclusive result, not a pass or fail.',
    fix: [
      'Retry the check; transient network issues are common.',
      'If it keeps failing, check your connection or try from another network.',
    ],
  },

  /* ---------------- Shared: generic DNS failure ---------------- */

  DNS_QUERY_FAILED: {
    severity: 'info',
    title: 'DNS query did not complete',
    why: 'The DNS query could not be completed, so nothing is known about this domain. This is an inconclusive result, not a pass or fail.',
    fix: [
      'Retry the check; transient network issues are common.',
      'If it keeps failing, check your connection or try from another network.',
    ],
  },

  /* ---------------- DNS Propagation Checker ---------------- */

  PROP_PROPAGATED: {
    severity: 'pass',
    title: 'All resolvers agree',
    why: 'Every public resolver queried returns the same records for this type, so a recent change has spread to these resolvers.',
    fix: [
      'Local ISP and corporate resolvers can still hold older answers until the record\'s TTL expires; the TTL column shows each remaining cache time.',
      'Re-run this check after the longest TTL shown if you need every cache to be fresh.',
    ],
  },

  PROP_PROPAGATING: {
    severity: 'warn',
    title: 'Resolvers disagree',
    why: 'Some resolvers still serve cached old records while others serve the new ones. The wait is governed by the record\'s TTL as each resolver sees it, not by a fixed propagation time.',
    fix: [
      'Compare the Answer column in the table: resolvers showing old values will refresh when their cached TTL expires.',
      'Wait out the longest TTL shown, then re-run this check.',
      'For future changes, lower the TTL to 300 seconds a day before the change, then raise it back after.',
    ],
  },

  PROP_NO_ANSWERS: {
    severity: 'warn',
    title: 'No resolver returned records',
    why: 'This can mean the record genuinely does not exist at this name, or that the queries did not complete. It is not proof of either on its own.',
    fix: [
      'Confirm the record exists: run the DNS Record Lookup tool for the same name and type.',
      'Check the record name spelling, including any subdomain or underscore prefix.',
      'Retry this check; transient resolver failures are common.',
    ],
  },

  /* ---------------- Blacklist Checker ---------------- */

  BLACKLIST_LISTED: {
    severity: 'fail',
    title: 'Listed on one or more blocklists',
    why: 'Blocklist listings cause mail from the domain or IP to be spam-foldered or rejected by receiving systems that consult those lists.',
    fix: [
      'Open each listing list\'s own site and read the return code: it states the reason for the listing.',
      'Fix the root cause before requesting delisting; common causes are a compromised account, an open redirect, or a misconfigured server.',
      'Request delisting on each list\'s process, then re-run this check.',
    ],
    guide: { label: 'Spamhaus removal guide', href: '/remove-from-spamhaus-blocklist/' },
  },

  BLACKLIST_CLEAN: {
    severity: 'pass',
    title: 'No listings found',
    why: 'Every list this tool could query returned clean for the domain and IP entered.',
    fix: [
      'Lists marked "not checkable" refuse queries from public resolvers; verify those on the list\'s own website.',
      'Re-run this check periodically, and always after deliverability suddenly drops.',
    ],
  },

  /* ---------------- DNSSEC Checker ---------------- */

  DNSSEC_SIGNED: {
    severity: 'pass',
    title: 'Domain is signed (DS present)',
    why: 'A DS record at the parent zone completes the chain of trust, so validating resolvers can detect forged DNS answers for this domain.',
    fix: [
      'The risky moment is key rollover: DS and DNSKEY must stay in sync at the registrar and the zone.',
      'Re-run this check after any registrar or DNS provider change.',
    ],
  },

  DNSSEC_KEYS_NO_DS: {
    severity: 'warn',
    title: 'Zone is signed but no DS at the parent',
    why: 'The zone publishes DNSKEY records, but without a DS record at the parent zone, validating resolvers have no chain of trust and will not treat the zone as signed.',
    fix: [
      'Publish the DS record at your registrar (it is generated from the zone\'s KSK).',
      'Confirm at the registrar that DNSSEC is enabled for the domain, not just at the DNS provider.',
      'Re-run this check until the DS check passes.',
    ],
    guide: { label: 'What is DNSSEC', href: '/what-is-dnssec/' },
  },

  DNSSEC_UNSIGNED: {
    severity: 'warn',
    title: 'Domain is not signed',
    why: 'Without DNSSEC, a forged DNS answer (for example a fake MX or A record) cannot be detected by validating resolvers.',
    fix: [
      'Enable DNSSEC at your DNS provider first (Cloudflare makes this one click).',
      'Then add the DS record it gives you at your registrar.',
      'Re-run this check to confirm the chain of trust is complete.',
    ],
    guide: { label: 'What is DNSSEC', href: '/what-is-dnssec/' },
  },

  /* ---------------- TTL Checker ---------------- */

  TTL_FAST: {
    severity: 'pass',
    title: 'TTLs are migration-friendly',
    why: 'At least one record changes quickly and no record waits more than an hour, so DNS changes here spread without long stale-cache windows.',
    fix: [
      'For planned migrations, 300 seconds on the records you will change is the comfortable target.',
      'Raise TTLs back after the change to reduce resolver load.',
    ],
  },

  TTL_SLOW: {
    severity: 'warn',
    title: 'Long TTLs will slow changes',
    why: 'The lowest TTL on this domain is above an hour, so any change will keep serving old values from resolver caches for hours.',
    fix: [
      'A day before a planned change, lower the TTL of the records you will edit to 300 seconds.',
      'Make the change, verify propagation, then raise TTLs back.',
    ],
  },

  TTL_NO_RECORDS: {
    severity: 'warn',
    title: 'No records found',
    why: 'The resolver returned none of the common record types for this domain. The domain may not exist, or the queries may not have completed.',
    fix: [
      'Verify the domain resolves at all: run the DNS Record Lookup with type A.',
      'Retry this check; transient resolver failures are common.',
    ],
  },

  /* ---------------- Record Lookup (12 type pages) ---------------- */

  LOOKUP_FOUND: {
    severity: 'pass',
    title: 'Records found',
    why: 'The resolver returned the records shown in the table. Values are what this public resolver currently serves; the TTL column is each record\'s remaining cache lifetime.',
    fix: [
      'A lower-than-expected TTL means you are seeing a cached answer close to expiry, not the authoritative value.',
      'Re-run after changes and use the propagation checker to compare resolvers.',
    ],
  },

  LOOKUP_NONE: {
    severity: 'warn',
    title: 'No records of this type',
    why: 'The domain resolved, but has no records of this type published. For many record types (AAAA, CAA, TXT variants) that is a legitimate configuration, not an error.',
    fix: [
      'Confirm whether this record type is expected for this domain\'s setup.',
      'If it should exist, publish it at your DNS provider and re-check.',
    ],
  },

  LOOKUP_NXDOMAIN: {
    severity: 'fail',
    title: 'Domain does not exist',
    why: 'The resolver returned NXDOMAIN: no such domain exists in DNS at all.',
    fix: [
      'Check the spelling of the domain.',
      'If the domain should exist, verify its nameservers and registration.',
    ],
  },
};
