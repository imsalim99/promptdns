# PromptDNS — Page Inventory & Tool Status

Generated: Aug 2026 · Live site: https://promptdns.com · Local preview: `npm run preview` (or `npm run dev` for pages-only on :4321)

---

## 1. How to check ALL pages yourself (3 ways)

1. **Sitemap** — every public URL, always current:
   - Production: `https://promptdns.com/sitemap-0.xml`
   - Local: `http://localhost:4321/sitemap-0.xml`
2. **The /tools/ hub page** — all tools, categorized, with descriptions
3. **The link audit script** (checks every internal link on every page):
   ```bash
   npm run build && python scripts/link_audit.py
   ```

## 2. Tool status (56 total) — by dependency type

### A. Always work, anywhere (no external services) — 44 tools
Everything DNS-over-HTTPS based: 12 record lookups + all-in-one lookup, propagation
checker, DNS speed test, response-time test, TTL checker, DNSSEC checker, delegation
checker, glue checker, wildcard tester, AXFR checker, resolver tester, nameserver
lookup, SPF checker/flattener/generator, DKIM checker/**generator** (keys made
in-browser), DMARC checker/generator/**report analyzer** (upload-based, offline),
blacklist checker, IP reputation, SMTP preflight, header analyzer (paste-based),
CIDR calculator, IPv6 converter, punycode converter, AI readiness checker,
robots.txt/llms.txt generator (input-based parts).

### B. Depend on IP/geo services (status verified: UP) — 4 tools
- What Is My IP → api.ipify.org + ipwho.is + our DoH PTR ✓
- IP Lookup / Reverse IP / IP Reputation → ipwho.is + DoH ✓

### C. Depend on document proxies (fixed: now 4-way fallback) — 5 tools
- AI Crawler Checker, robots.txt Checker, agents.txt Checker, llms.txt Generator
  (fetch mode), Schema Validator
- Chain: direct → AllOrigins → CodeTabs → r.jina.ai
- **Aug 2026 incident:** AllOrigins returned 500 (sole proxy at the time) → these
  tools broke. Fixed with the fallback chain above; r.jina.ai verified working.
- These fetch THIRD-PARTY sites, so results also depend on the target site
  allowing automated fetches; error messages now distinguish "no file" vs "fetch blocked".

### D. Depend on registry/data services (verified: UP) — 3 tools
- WHOIS/RDAP Lookup + Domain Age → rdap.org ✓ (redirects to authoritative server)
- DNS Leak Test → bash.ws ✓ (third-party detector; may rate-limit)

## 3. Page inventory by section (158 pages)

| Section | Count | Examples |
|---|---|---|
| Homepage | 1 | `/` (hero scanner + full tool directory) |
| Tools hub | 1 | `/tools/` |
| Tool pages | 56 | See §2 and `/tools/` |
| Content hubs | 4 | `/dns/`, `/dns-records/`, `/email-authentication/` (+matrix), `/about/` |
| Fundamentals | 4 | what-is-dns, how-dns-works, dns-propagation, flush-dns-cache |
| Record-type pillars | 12 | a/aaaa/cname/txt/ns/soa/ptr/srv/caa/alias/ds/dnskey-record |
| Record-type lookups | 12 | `{type}-record-lookup` dedicated tool pages |
| Email auth guides | 15 | spf-record, dkim, dmarc, dmarc-record, bimi, mta-sts, spf-lookup-limit, dkim-selector, how-to-add-dkim-record, spf-record-syntax, how-to-add-mx-record, mx-record-not-working, how-to-read-dmarc-reports, why-emails-go-to-spam, doh-vs-dot |
| **ESP setup matrix** | **42** | `/spf-dkim-dmarc-{service}/` for SendGrid, Mailchimp, HubSpot, … |
| DNS security & ops | 5 | what-is-dnssec, ttl, cname-flattening, site-down-after-dns-change, doh-vs-dot |
| AI cluster | 6 | ai-crawlers-list, robots-txt-guide, what-is-llms-txt, llms-txt-syntax, ai-readiness-guide, block/allow-ai-crawlers |
| Blocklist removal | 3 | Spamhaus, Barracuda, SORBS |
| Company/legal | 5 | pricing, support, contact, privacy, terms |
| Misc | 1 | dnskey/sitemap/robots.txt (non-page files excluded from count) |

## 4. Deployment notes

- `git push` → Cloudflare Pages rebuilds (~2 min) → sitemap auto-updates
- Commit history: `main` = production · `saas-wip` branch = parked auth/dashboard work
- Un-pushed batches sit as local commits until you push

## 5. Known limitations (honest)

- Blacklist check: Spamhaus/URIBL refuse public-resolver queries → shown as
  "not checkable" rather than fake results
- DNS Leak Test depends on bash.ws availability
- Proxy tools depend on target sites not blocking automated fetches
- DMARC Report Analyzer is upload-only until the SaaS phase wires email ingestion
