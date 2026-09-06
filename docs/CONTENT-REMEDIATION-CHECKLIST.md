# Content Remediation Checklist — TOP PRIORITY (execute after Phase 3)

Status at capture: user manual audit found systematic thin content, missing FAQs,
missing Koray document conventions, and a CSS width bug (CSS fixed same day; the
rest is backlog). Do not start Phase 3 content batches until each item below has
an owner-checkmark. This file is the contract.

## 0. Global Koray document standard (apply to EVERY page)

Every page must have ALL of the following before it counts as "done":
- [ ] **6–8 FAQ accordions** (shared FaqAccordion component) + FAQPage JSON-LD
- [ ] **At least one table** (syntax, comparison, codes, or checklist data)
- [ ] **At least one visual** (SVG diagram in brand style, or annotated example block)
- [ ] **Ordered process section** (numbered steps with verification)
- [ ] **TOC / jump links** for any page over 1,200 words
- [ ] **Contextual internal links** (minimum 3: one up to hub, one lateral, one tool)
- [ ] **Last-updated stamp** on money pages
- [ ] Word-count floor by role: tool pages ≥700 · guides ≥900 · pillars ≥1,400 ·
      comparisons ≥1,200 · ESP/provider pages ≥1,100
- [ ] Zero un-linked orphan blocks; every claim actionable via an embedded tool or linked guide

## 1. Tool pages — article layer missing entirely (tool + 1 line only)
Each needs the full ToolArticle treatment (process / interpret results / CLI
equivalent / common errors / who needs it / 6–8 FAQs):
- [ ] /dns-propagation-checker/ (has some content, needs FAQ accordion + depth)
- [ ] /dns-record-lookup/ (needs per-type interpretation section)
- [ ] /spf-record-checker/ (has partial content; needs 6–8 FAQs + CLI)
- [ ] /spf-flattener/ (needs depth pass)
- [ ] /spf-record-generator/ (needs depth pass)
- [ ] /dkim-record-checker/ (needs 6–8 FAQs)
- [ ] /dkim-record-generator/ (needs depth pass)
- [ ] /dmarc-record-checker/ (needs 6–8 FAQs)
- [ ] /dmarc-record-generator/ (needs depth pass)
- [ ] /dmarc-report-analyzer/ (needs depth pass)
- [ ] /blacklist-checker/ (needs 6–8 FAQs + interpretation)
- [ ] /email-header-analyzer/ (needs depth pass)
- [ ] /bimi-record-checker/ (needs depth + FAQs)
- [ ] /mta-sts-checker/ (needs depth + FAQs)
- [ ] /tls-rpt-checker/ (needs depth + FAQs)
- [ ] /cidr-calculator/ (needs depth: how subnetting works + worked examples)
- [ ] /ipv4-to-ipv6-converter/ (needs depth + FAQs)
- [ ] /punycode-converter/ (needs depth + FAQs)
- [ ] /dns-leak-test/ (needs depth pass)
- [ ] /ai-crawler-checker/ (needs 6–8 FAQs + interpretation depth)
- [ ] /robots-txt-checker/ (needs 6–8 FAQs)
- [ ] /llms-txt-generator/ (needs depth pass)
- [ ] /ai-readiness-checker/ (needs 6–8 FAQs)

## 2. Tool pages — article layer present but verify
These 21 have ToolArticle content (fixed CSS width bug): TTL, speed, resolver
tester, response-time, delegation, glue, wildcard, AXFR, DNSSEC, SMTP, IP rep,
autodiscover, schema, AI-log, agents.txt, reverse-IP, nameserver, domain-age,
WHOIS, my-ip, ip-lookup.
- [ ] Re-review each for depth ≥700 words after CSS fix
- [ ] Ensure diagrams added where the concept is visual (delegation chain,
      DNSSEC chain of trust, blocklist query flow)

## 3. Core guides — thin (need expansion to ≥900 words + tables + visuals + 6–8 FAQs)
- [ ] /what-is-dns/
- [ ] /how-dns-works/
- [ ] /mx-record/
- [ ] /dns-propagation/
- [ ] /spf-record/
- [ ] /dkim/
- [ ] /dmarc/
- [ ] /bimi/
- [ ] /mta-sts/
- [ ] /dns-records/ hub enrichment
- [ ] /email-authentication/ hub enrichment
- [ ] /dns-providers/ hub enrichment

## 4. Comparison pages — still thin
- [ ] /cloudflare-dns-vs-google-dns/ (add use-case scenarios, pricing detail,
      migration walkthrough, decision flow diagram)
- [ ] /cloudflare-vs-route53/ (same treatment)

## 5. Provider playbooks (34 pages) — FAQs present, body thin
- [ ] Expand every manage/NS/troubleshooting page: add real panel-flow detail,
      a records-cheatsheet table per provider, screenshots (to be captured),
      and 2–3 unique provider facts (pricing notes, limits, history)

## 6. ESP matrix (42 pages) — verify against standard
- [ ] Spot-check 10 against §0; expand any under 1,100 words

## 7. Koray visual semantic framework (site-wide additions)
- [ ] Build reusable SVG diagram library (10+ diagrams: resolution, DNSSEC chain,
      DMARC decision tree, SPF evaluation, blocklist query, TTL lifecycle,
      delegation tree, wildcard matching, autodiscover probing, DKIM signing)
- [ ] Embed diagrams across all guide + tool pages (≥1 per page)
- [ ] Add TableOfContents component to pillars/comparisons
- [ ] Author entity pages + bylines on all guides (E-E-A-T)

## 8. Acceptance protocol
After remediation: user manual re-audit pass on a 15-page random sample.
Only after user sign-off does the batch ship.
