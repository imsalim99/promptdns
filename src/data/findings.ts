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
};
