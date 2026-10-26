"""Waves 3+5: compact entity-dense descriptions on all tool pages + AI word audit.

Wave 3: Finds every tool page with a description paragraph >12 words between
</h1> and <ToolPanel, replaces it with a compact entity-dense version.

Wave 5: Scans all 257 built pages for blacklisted AI words and sentence
openers per Koray's methodology. Outputs a report.
"""
import pathlib, re, sys

PAGES = pathlib.Path("src/pages")
DIST = pathlib.Path("dist")

# ---------- Wave 3: entity-dense descriptions ----------

# Per-tool compact descriptions. Key = filename stem.
COMPACT = {
    "dns-propagation-checker": "Free DNS propagation checker: query A, AAAA, MX, TXT, CNAME across Cloudflare, Google and AliDNS resolvers.",
    "dns-record-lookup": "Free DNS record lookup: query any record type (A through DNSKEY) with full values and TTLs over DNS-over-HTTPS.",
    "dns-speed-test": "Free DNS speed test: benchmark resolver latency across Cloudflare, Google and AliDNS with repeated lookups.",
    "dnssec-checker": "Free DNSSEC checker: verify DS records, DNSKEY algorithms, and chain of trust for any domain.",
    "delegation-checker": "Free delegation checker: verify every nameserver resolves, answers, and stays consistent across the set.",
    "glue-record-checker": "Free glue record checker: verify parent glue A records for nameservers inside your own domain.",
    "wildcard-dns-tester": "Free wildcard DNS tester: probe random subdomains to detect wildcard records and their scope.",
    "axfr-checker": "Free AXFR leak checker: audit zone-transfer exposure and get the dig test for each authoritative server.",
    "dns-resolver-tester": "Free DNS resolver tester: query any DoH endpoint with any record type and latency timing.",
    "dns-response-time-test": "Free DNS response time test: measure cold vs cached resolution to diagnose slow authoritative DNS.",
    "a-record-lookup": "Free A record lookup: see IPv4 addresses and TTLs for any domain, before and after migrations.",
    "aaaa-record-lookup": "Free AAAA record lookup: verify IPv6 addresses and catch dual-stack breakage.",
    "mx-record-lookup": "Free MX record lookup: see mail server priorities and targets before provider changes.",
    "ns-record-lookup": "Free NS record lookup: list authoritative nameservers and compare against your DNS host.",
    "txt-record-lookup": "Free TXT record lookup: see SPF, DKIM, DMARC and verification tokens in one view.",
    "soa-record-lookup": "Free SOA record lookup: check zone serial, refresh, retry, expire and primary nameserver.",
    "cname-record-lookup": "Free CNAME lookup: see alias targets and verify CDN and service integrations.",
    "ptr-record-lookup": "Free PTR lookup: resolve IP to hostname via reverse DNS for mail server checks.",
    "srv-record-lookup": "Free SRV record lookup: find service endpoints with priority, weight and port.",
    "dnskey-record-lookup": "Free DNSKEY lookup: see zone signing keys and algorithm details for DNSSEC validation.",
    "ds-record-lookup": "Free DS record lookup: verify the delegation signer at the parent zone for DNSSEC.",
    "dnskey-record": "DNSKEY records explained: zone signing keys, algorithms, and DNSSEC key rollover.",
    "ds-record": "DS records explained: delegation signer records that anchor the DNSSEC chain of trust.",
    "caa-record": "CAA records explained: control which certificate authorities may issue certificates for your domain.",
    "spf-flattener": "Free SPF flattener: compress include: chains under the 10-lookup limit automatically.",
    "spf-record-generator": "Free SPF record generator: build correct v=spf1 records with include, ip4, ip6, mx and all mechanisms.",
    "dkim-record-generator": "Free DKIM record generator: create selector._domainkey TXT records with the right key size.",
    "dmarc-record-generator": "Free DMARC record generator: build v=DMARC1 records with p= policy, rua reporting and sp= subdomain policy.",
    "blacklist-checker": "Free blacklist checker: check domain and IP against SURBL, URIBL, SpamCop, Barracuda and more.",
    "dmarc-report-analyzer": "Free DMARC report analyzer: upload XML or ZIP aggregate reports, see source IPs, pass rates and dispositions.",
    "dmarc-record-checker": "Free DMARC checker: validate p= policy, rua reporting, alignment and subdomain sp= tags.",
    "dkim-record-checker": "Free DKIM checker: find selectors, verify key type and size, catch weak 1024-bit keys.",
    "spf-record-checker": "Free SPF checker: validate SPF syntax, count DNS lookups, find permerrors. No sign up.",
    "dnssec-checker": "Free DNSSEC checker: verify DS records, DNSKEY algorithms, and chain of trust.",
    "ttl-checker": "Free TTL checker: see every DNS record's cache time at once. Plan migrations, catch bloated caches.",
    "mta-sts-checker": "Free MTA-STS checker: verify MTA-STS policy records and TLS enforcement for inbound mail.",
    "tls-rpt-checker": "Free TLS-RPT checker: verify TLS reporting records and SMTP TLS failure reporting.",
    "bimi-record-checker": "Free BIMI checker: verify BIMI records, VMC certificates and logo requirements.",
    "email-header-analyzer": "Free email header analyzer: parse Received hops, SPF, DKIM, DMARC results from raw email headers.",
    "ai-crawler-checker": "Free AI crawler checker: test whether GPTBot, ClaudeBot, Google-Extended and other AI agents can access your site.",
    "ai-readiness-checker": "Free AI readiness checker: audit DNS, content and technical signals for AI search visibility.",
    "ai-log-analyzer": "Free AI log analyzer: identify AI crawler user agents in your server logs.",
    "llms-txt-generator": "Free llms.txt generator: create llms.txt files so AI systems can understand your content structure.",
    "robots-txt-checker": "Free robots.txt checker: parse directives, find errors, verify AI crawler access rules.",
    "agents-txt-checker": "Free agents.txt checker: verify agents.txt files for AI agent discovery and access control.",
    "schema-validator": "Free schema validator: check JSON-LD structured data for correctness and AI readability.",
    "cidr-calculator": "Free CIDR calculator: convert IP ranges, calculate subnets, usable hosts and broadcast addresses.",
    "ipv4-to-ipv6-converter": "Free IPv4 to IPv6 converter: convert dotted-decimal to hex IPv6 notations instantly.",
    "punycode-converter": "Free punycode converter: convert internationalized domain names between Unicode and punycode.",
    "domain-age-checker": "Free domain age checker: check registration date, age and WHOIS history for any domain.",
    "whois-lookup": "Free WHOIS lookup: check domain registration, expiry, nameservers and registrar details.",
    "my-ip": "Free IP checker: see your public IPv4 and IPv6 address instantly.",
    "ip-lookup": "Free IP lookup: get geolocation, ASN, ISP and reverse DNS for any IP address.",
    "reverse-ip-lookup": "Free reverse IP lookup: find all domains hosted on the same IP address.",
    "nameserver-lookup": "Free nameserver lookup: find authoritative and recursive nameservers for any domain.",
    "ip-reputation-checker": "Free IP reputation checker: check IP address against blocklists and reputation databases.",
    "smtp-tester": "Free SMTP tester: verify SMTP server connectivity, STARTTLS and authentication.",
    "dns-leak-test": "Free DNS leak test: detect DNS leaks and verify your resolver privacy.",
    "email-header-analyzer": "Free email header analyzer: parse full email headers for routing, SPF, DKIM and DMARC results.",
    "glue-record-checker": "Free glue record checker: verify glue records for in-bailiwick nameservers.",
}

desc_pattern = re.compile(
    r'(<p class="mt-4[^"]*text-lg[^"]*text-ink-dim[^"]*">)(.*?)(</p>\s*(?:<ToolPanel|<div class="mt-8))',
    re.DOTALL
)

count = 0
for f in sorted(PAGES.glob("*.astro")):
    stem = f.stem
    if stem not in COMPACT:
        continue
    txt = f.read_text(encoding="utf-8")
    m = desc_pattern.search(txt)
    if not m:
        continue
    existing = m.group(2).strip()
    # strip HTML tags to count words
    plain = re.sub(r'<[^>]+>', '', existing).strip()
    word_count = len(plain.split())
    new_desc = COMPACT[stem]
    if word_count <= 14:
        continue  # already compact
    # preserve HTML tags in new_desc if the old one had them
    if '<span' in existing or '<code' in existing:
        new_desc = f'<span class="font-mono text-sm">{new_desc}</span>'
    txt = txt[:m.start(2)] + new_desc + txt[m.end(2):]
    f.write_text(txt, encoding="utf-8")
    count += 1
    print(f"W3: {stem} ({word_count} -> {len(new_desc.split())} words)")

print(f"\nWave 3: {count} descriptions compacted")

# ---------- Wave 5: AI word blacklist audit ----------
BLACKLIST = [
    'delve', 'crucial', 'paramount', 'testament', 'tapestry', 'beacon',
    'realm', 'landscape', 'moreover', 'furthermore', 'notably',
    'it is worth noting', 'in conclusion', 'seamless', 'robust',
    'comprehensive guide', 'unlock', 'unleash', 'elevate', 'game-changer',
    'dive into', 'symphony', 'underscore', 'in today\'s digital',
    "whether you're a", 'not only', 'but also',
]
OPENERS = [
    'When it comes to', 'In today\'s digital', 'Understanding .* is essential',
]

hits = {}
for f in sorted(DIST.glob("**/index.html")):
    txt = f.read_text(encoding="utf-8")
    # strip tags for text-only scan
    plain = re.sub(r'<[^>]+>', ' ', txt).lower()
    rel = str(f.relative_to(DIST))
    for word in BLACKLIST:
        if word.lower() in plain:
            hits.setdefault(word, []).append(rel)

if hits:
    print(f"\nWave 5: AI word audit found {len(hits)} blacklisted terms:")
    for w, files in sorted(hits.items()):
        print(f"  '{w}': {len(files)} pages (e.g. {files[0]})")
else:
    print("\nWave 5: No blacklisted AI words found")

sys.exit(0)
