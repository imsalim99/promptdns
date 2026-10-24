/** Single source of truth for the tool directory (navbar, footer, homepage, /tools/). */
export interface ToolEntry { name: string; href: string; desc: string }
export interface ToolCategory { id: string; cat: string; note: string; tools: ToolEntry[] }
export interface NavGroup { sub: string; tools: [string, string][] }
export interface NavColumn { heading: string; groups: NavGroup[] }

export const TOOL_CATEGORIES: ToolCategory[] = [
  {
    id: 'dns', cat: 'DNS Tools', note: 'Lookups, propagation, diagnostics, and resolver benchmarks',
    tools: [
      { name: 'DNS Propagation Checker', href: '/dns-propagation-checker/', desc: 'Query your record across independent public resolvers to see whether a change has fully spread or where old values are still cached.' },
      { name: 'DNS Record Lookup', href: '/dns-record-lookup/', desc: 'Fetch any record type, A through DNSKEY, with full values and TTLs, live over DNS-over-HTTPS.' },
      { name: 'DNS Speed Test', href: '/dns-speed-test/', desc: 'Benchmark Cloudflare, Google, and AliDNS from your own network with repeated lookups and a ranked winner.' },
      { name: 'TTL Checker', href: '/ttl-checker/', desc: "See every record's cache time at once: anything above 300 seconds is migration wait you can avoid." },
      { name: 'DNSSEC Checker', href: '/dnssec-checker/', desc: 'Verify the DS record at the parent and the zone\u2019s DNSKEYs, with algorithm strength.' },
      { name: 'Delegation Checker', href: '/delegation-checker/', desc: 'Check every nameserver: does it resolve, does it answer, is the zone consistent across the set.' },
      { name: 'Glue Record Checker', href: '/glue-record-checker/', desc: 'For nameservers inside your own domain, verify the parent publishes working glue A records.' },
      { name: 'Wildcard DNS Tester', href: '/wildcard-dns-tester/', desc: 'Probe random subdomains to detect wildcard records and see exactly what *.domain matches.' },
      { name: 'AXFR Leak Checker', href: '/axfr-checker/', desc: 'Audit zone-transfer exposure and get the one-command dig test for each authoritative server.' },
      { name: 'Resolver Tester', href: '/dns-resolver-tester/', desc: 'Query any DNS-over-HTTPS endpoint, preset or custom, with any record type and latency timing.' },
      { name: 'Response Time Test', href: '/dns-response-time-test/', desc: 'Measure how fast resolvers resolve your domain from scratch: fresh (cold) lookups versus cached ones, to diagnose slow authoritative DNS.' },
      { name: 'A Record Lookup', href: '/a-record-lookup/', desc: 'See the IPv4 addresses a domain points to, with TTLs, before and after migrations.' },
      { name: 'AAAA Record Lookup', href: '/aaaa-record-lookup/', desc: "Check any domain's IPv6 addresses to verify dual-stack setups and catch v6-only breakage." },
      { name: 'MX Record Lookup', href: '/mx-record-lookup/', desc: 'See which mail servers accept email for a domain, with priorities, before provider changes.' },
      { name: 'NS Record Lookup', href: '/ns-record-lookup/', desc: 'List the authoritative nameservers and compare against your DNS host\u2019s expected set.' },
      { name: 'TXT Record Lookup', href: '/txt-record-lookup/', desc: 'Every text record in one view: SPF, DKIM keys, DMARC, and verification tokens.' },
      { name: 'SOA Record Lookup', href: '/soa-record-lookup/', desc: 'Zone serial, refresh and expire timers, and the primary nameserver for any domain.' },
      { name: 'CNAME Record Lookup', href: '/cname-record-lookup/', desc: 'See the aliases any hostname points to; verify service integrations and CDN pointers.' },
      { name: 'PTR Record Lookup', href: '/ptr-record-lookup/', desc: 'Resolve an IP back to its hostname via reverse DNS, essential for mail server checks.' },
      { name: 'SRV Record Lookup', href: '/srv-record-lookup/', desc: 'Find service endpoints with priority, weight, and port for SIP, XMPP, and game servers.' },
      { name: 'CAA Record Lookup', href: '/caa-record-lookup/', desc: 'See which certificate authorities are authorized to issue TLS certificates for a domain.' },
      { name: 'DS Record Lookup', href: '/ds-record-lookup/', desc: 'Check the DNSSEC delegation signer at the parent; a stale DS breaks the whole zone.' },
      { name: 'DNSKEY Record Lookup', href: '/dnskey-record-lookup/', desc: 'Inspect a zone\u2019s DNSSEC public keys, KSK/ZSK flags, and algorithm strength.' },
    ],
  },
  {
    id: 'email', cat: 'Email Authentication', note: 'SPF, DKIM, DMARC, blocklists, and deliverability',
    tools: [
      { name: 'SPF Record Checker', href: '/spf-record-checker/', desc: 'Validate your SPF term by term: syntax errors, the all qualifier, and exactly how many of your 10 DNS lookups you\u2019re spending.' },
      { name: 'SPF Flattener', href: '/spf-flattener/', desc: 'Resolve every include: down to raw IPs and generate a flattened SPF that stays under the 10-lookup permerror limit.' },
      { name: 'SPF Generator', href: '/spf-record-generator/', desc: 'Pick your sending services and policy, and get a valid v=spf1 record with a live lookup count.' },
      { name: 'DKIM Record Checker', href: '/dkim-record-checker/', desc: 'Look up any selector\u2019s public key, verify key type and length, and catch weak 1024-bit keys.' },
      { name: 'DKIM Generator', href: '/dkim-record-generator/', desc: 'Generate a real 2048-bit RSA key pair in your browser: DNS record plus private key download. Keys never leave your device.' },
      { name: 'DMARC Record Checker', href: '/dmarc-record-checker/', desc: 'Check policy tags, alignment, and reporting configuration, graded A to F with plain-English fixes.' },
      { name: 'DMARC Generator', href: '/dmarc-record-generator/', desc: 'Configure policy, subdomain rules, pct, and reporting addresses; get a copy-paste-ready record.' },
      { name: 'DMARC Report Analyzer', href: '/dmarc-report-analyzer/', desc: 'Upload the XML or zip reports your mailbox receives and see senders, pass rates, and fixes.' },
      { name: 'Blacklist Checker', href: '/blacklist-checker/', desc: 'Check domain and sending IP against SURBL, URIBL, Spamhaus, Barracuda, SpamCop, SORBS and more, with honest per-list results.' },
      { name: 'IP Reputation Checker', href: '/ip-reputation-checker/', desc: 'Scan any IPv4 across the major blocklists in one pass, with reverse DNS included.' },
      { name: 'Email Header Analyzer', href: '/email-header-analyzer/', desc: 'Paste full headers to decode the Received chain, SPF/DKIM/DMARC verdicts, and delivery delays.' },
      { name: 'SMTP Preflight', href: '/smtp-tester/', desc: 'MX routing, PTR, SPF/DKIM/DMARC, and blacklist readiness for any sending domain.' },
      { name: 'BIMI Checker', href: '/bimi-record-checker/', desc: 'Verify your BIMI record: version, logo URL, and VMC certificate reference.' },
      { name: 'MTA-STS Checker', href: '/mta-sts-checker/', desc: 'Verify the _mta-sts TXT record and fetch the policy file to check mode and MX hosts.' },
      { name: 'TLS-RPT Checker', href: '/tls-rpt-checker/', desc: 'Check where providers send your TLS failure reports via the _smtp._tls record.' },
      { name: 'Autodiscover Checker', href: '/autodiscover-checker/', desc: 'Check the DNS records mail clients probe for automatic account setup.' },
    ],
  },
  {
    id: 'domain-ip', cat: 'Domain & IP', note: 'Your address, and everyone else\u2019s',
    tools: [
      { name: 'What Is My IP', href: '/my-ip/', desc: 'Your public IP with reverse DNS, ASN, ISP, and approximate location, resolved as the page loads.' },
      { name: 'IP Lookup', href: '/ip-lookup/', desc: 'Any IPv4 or IPv6 address: geolocation, network owner, ASN, and reverse DNS via our own DoH engine.' },
      { name: 'Reverse IP / PTR', href: '/reverse-ip-lookup/', desc: 'Resolve any IP to its hostname, then forward-confirm the match, in one step.' },
      { name: 'WHOIS / RDAP Lookup', href: '/whois-lookup/', desc: 'Registrar, creation and expiry dates, statuses, and nameservers via modern RDAP.' },
      { name: 'Domain Age Checker', href: '/domain-age-checker/', desc: 'Registry creation data with age computed in years, for vetting domains and competitors.' },
      { name: 'Nameserver Lookup', href: '/nameserver-lookup/', desc: 'Every NS record for a domain, each nameserver resolved to its IPv4 and IPv6 addresses.' },
      { name: 'CIDR Calculator', href: '/cidr-calculator/', desc: 'Subnet math instantly: network, range, mask, wildcard, broadcast, and usable host count.' },
      { name: 'IPv6 Converter', href: '/ipv4-to-ipv6-converter/', desc: 'Convert any IPv4 address to its IPv6-mapped, full, and 6to4 forms, computed locally.' },
      { name: 'Punycode Converter', href: '/punycode-converter/', desc: 'Translate internationalized domains between Unicode and xn-- ASCII form, both directions.' },
      { name: 'DNS Leak Test', href: '/dns-leak-test/', desc: 'Detect which DNS resolvers actually handle your queries, and whether your VPN\u2019s resolver leaks.' },
    ],
  },
  {
    id: 'ai', cat: 'AI & Web Infrastructure', note: 'The layer AI systems read',
    tools: [
      { name: 'AI Crawler Checker', href: '/ai-crawler-checker/', desc: 'Audit your robots.txt against 12 AI crawlers, GPTBot to PerplexityBot, and see exactly who\u2019s allowed or blocked.' },
      { name: 'robots.txt Checker', href: '/robots-txt-checker/', desc: 'Validate robots.txt line by line: syntax errors, unknown directives, and AI-bot verdicts.' },
      { name: 'llms.txt Generator', href: '/llms-txt-generator/', desc: 'Build a valid llms.txt, the markdown map that tells language models what your site is.' },
      { name: 'AI Readiness Checker', href: '/ai-readiness-checker/', desc: 'One score for machine-readability: DNS, DNSSEC, email auth, AI crawler access, and llms.txt.' },
      { name: 'AI Log Analyzer', href: '/ai-log-analyzer/', desc: 'Upload access logs and see which AI bots visit, how often, and what they fetch. Parsed locally.' },
      { name: 'Schema Validator', href: '/schema-validator/', desc: 'Fetch any page, extract its JSON-LD blocks, and validate the data machines depend on.' },
      { name: 'agents.txt Checker', href: '/agents-txt-checker/', desc: 'Verify the emerging agents.txt rules file for AI agents on any domain.' },
    ],
  },
];

export const TOTAL_TOOLS = TOOL_CATEGORIES.reduce((s, c) => s + c.tools.length, 0);

/** Curated navbar menu: sub-headed groups, top tools only, no scrolling. */
export const NAV_MENU: NavColumn[] = [
  {
    heading: 'DNS',
    groups: [
      { sub: 'Lookups & checks', tools: [['DNS Propagation Checker', '/dns-propagation-checker/'], ['DNS Record Lookup', '/dns-record-lookup/'], ['TTL Checker', '/ttl-checker/'], ['DNSSEC Checker', '/dnssec-checker/'], ['DNS Speed Test', '/dns-speed-test/']] },
      { sub: 'Delegation & zone', tools: [['Delegation Checker', '/delegation-checker/'], ['Glue Record Checker', '/glue-record-checker/'], ['Wildcard Tester', '/wildcard-dns-tester/'], ['AXFR Leak Checker', '/axfr-checker/']] },
    ],
  },
  {
    heading: 'Email',
    groups: [
      { sub: 'SPF & DKIM', tools: [['SPF Record Checker', '/spf-record-checker/'], ['SPF Flattener', '/spf-flattener/'], ['DKIM Record Checker', '/dkim-record-checker/'], ['DKIM Generator', '/dkim-record-generator/']] },
      { sub: 'DMARC', tools: [['DMARC Record Checker', '/dmarc-record-checker/'], ['DMARC Generator', '/dmarc-record-generator/'], ['Report Analyzer', '/dmarc-report-analyzer/'], ['Header Analyzer', '/email-header-analyzer/']] },
      { sub: 'Reputation', tools: [['Blacklist Checker', '/blacklist-checker/'], ['IP Reputation', '/ip-reputation-checker/'], ['SMTP Preflight', '/smtp-tester/']] },
    ],
  },
  {
    heading: 'Domain & IP',
    groups: [
      { sub: 'Identity', tools: [['What Is My IP', '/my-ip/'], ['IP Lookup', '/ip-lookup/'], ['WHOIS / RDAP', '/whois-lookup/'], ['Domain Age', '/domain-age-checker/']] },
      { sub: 'Utilities', tools: [['Nameserver Lookup', '/nameserver-lookup/'], ['CIDR Calculator', '/cidr-calculator/'], ['IPv6 Converter', '/ipv4-to-ipv6-converter/'], ['Punycode Converter', '/punycode-converter/']] },
    ],
  },
  {
    heading: 'AI',
    groups: [
      { sub: 'Access & policy', tools: [['AI Crawler Checker', '/ai-crawler-checker/'], ['robots.txt Checker', '/robots-txt-checker/'], ['agents.txt Checker', '/agents-txt-checker/']] },
      { sub: 'Visibility', tools: [['llms.txt Generator', '/llms-txt-generator/'], ['AI Readiness Score', '/ai-readiness-checker/'], ['AI Log Analyzer', '/ai-log-analyzer/'], ['Schema Validator', '/schema-validator/']] },
    ],
  },
];
