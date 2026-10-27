/**
 * Per-tool attribute badges with review evidence (Visual Semantics spec §2.1, §4).
 *
 * Every badge must be TRUE for that specific tool. The `evidence` field names the
 * concrete mechanism (which lib the page imports, where queries go) so claims can
 * be audited. ToolPanel resolves the slug from the URL and renders this list.
 *
 * Mechanics, classified from the actual imports:
 * - doh:    page imports src/lib/doh.ts; queries go browser -> public DoH resolvers
 * - proxy:  page imports src/lib/proxy.ts; cross-origin text fetched from the
 *           browser, falling back through public CORS proxies (allorigins,
 *           codetabs, r.jina.ai). NOT purely client-side: badge says what is true.
 * - api:    browser calls a public third-party API (ipinfo, bash.ws) directly
 * - local:  no network call at all (parsers, generators, calculators)
 */

export interface Badge {
  label: string;
  evidence: string;
}

const FREE: Badge = {
  label: '100% Free · No Sign Up',
  evidence: 'No auth on any tool route; paid plans are badged Coming soon on /pricing/.',
};

const DOH_LIVE: Badge = {
  label: '⚡ Instant Live Query',
  evidence: 'Page imports lib/doh; queries public DoH resolvers (Cloudflare 1.1.1.1, Google 8.8.8.8, AliDNS 223.5.5.5) directly from the browser at request time.',
};
const DOH_PRIVACY: Badge = {
  label: '🛡️ Client-Side · Zero Logs',
  evidence: 'DNS queries go browser to public resolver; no PromptDNS server sits in the lookup path and nothing is stored.',
};
const PROXY_LIVE: Badge = {
  label: '⚡ Live Fetch',
  evidence: 'Page imports lib/proxy; the target file is fetched live, direct where CORS allows, otherwise relayed via public CORS proxies.',
};
const PROXY_PRIVACY: Badge = {
  label: '🛡️ Nothing Stored',
  evidence: 'Fetch may relay via public CORS proxies (third parties could see the requested URL); PromptDNS servers log and store nothing.',
};
const API_LIVE: Badge = {
  label: '⚡ Live Query',
  evidence: 'Browser calls the public third-party API directly at request time.',
};
const API_PRIVACY: Badge = {
  label: '🛡️ Zero Logs',
  evidence: 'API call goes browser to provider; PromptDNS servers are not in the path and store nothing.',
};
const LOCAL_LIVE_PARSER: Badge = {
  label: '⚡ Instant Local Parser',
  evidence: 'Parsing happens entirely in the page JavaScript; no network call is made.',
};
const LOCAL_LIVE_BUILDER: Badge = {
  label: '⚡ Instant Builder',
  evidence: 'Generation happens entirely in the page JavaScript; no network call is made.',
};
const LOCAL_LIVE_CALC: Badge = {
  label: '⚡ Instant Calculator',
  evidence: 'Calculation happens entirely in the page JavaScript; no network call is made.',
};
const LOCAL_PRIVACY: Badge = {
  label: '🛡️ Runs in Your Browser · No Uploads',
  evidence: 'Input never leaves the browser: no upload endpoint exists for this tool.',
};
const CALC_PRIVACY: Badge = {
  label: '🛡️ Runs in Your Browser',
  evidence: 'Calculation is local; no network call is made.',
};

export const DEFAULT_ATTRIBUTES: Badge[] = [
  FREE,
  DOH_LIVE,
  DOH_PRIVACY,
  { label: 'DNS-over-HTTPS', evidence: 'Lookups run over DoH (RFC 8484) from the browser.' },
];

export const TOOL_ATTRIBUTES: Record<string, Badge[]> = {
  // --- DNS & email-auth lookup tools: browser DoH ---
  ...Object.fromEntries(
    [
      'spf-record-checker', 'dmarc-record-checker', 'dkim-record-checker', 'dns-record-lookup',
      'dns-resolver-tester', 'dns-response-time-test', 'dns-speed-test', 'dnssec-checker',
      'delegation-checker', 'glue-record-checker', 'nameserver-lookup', 'reverse-ip-lookup',
      'smtp-tester', 'spf-flattener', 'tls-rpt-checker', 'ttl-checker', 'wildcard-dns-tester',
      'autodiscover-checker', 'axfr-checker', 'bimi-record-checker', 'blacklist-checker',
    ].map((slug) => [slug, [FREE, DOH_LIVE, DOH_PRIVACY, { label: 'DNS-over-HTTPS', evidence: 'Lookups run over DoH (RFC 8484) from the browser.' }]]),
  ),
  'ip-reputation-checker': [
    FREE,
    DOH_LIVE,
    DOH_PRIVACY,
    { label: 'DNSBL over DoH', evidence: 'Blacklist checks query DNSBL zones over DoH (lib/dnsbl); IP metadata via a public API (lib/ipinfo).' },
  ],

  // --- HTTP fetch tools via lib/proxy (public CORS proxy fallback) ---
  'robots-txt-checker': [FREE, PROXY_LIVE, PROXY_PRIVACY, { label: 'robots.txt Parser', evidence: 'Fetches the live robots.txt and parses syntax locally; direct where CORS allows, else via public CORS proxies (lib/proxy).' }],
  'agents-txt-checker': [FREE, PROXY_LIVE, PROXY_PRIVACY, { label: 'agents.txt Parser', evidence: 'Fetches the live agents.txt and parses it locally; direct where CORS allows, else via public CORS proxies (lib/proxy).' }],
  'ai-crawler-checker': [FREE, PROXY_LIVE, PROXY_PRIVACY, { label: 'Robots + Crawler IPs', evidence: 'Fetches robots.txt via lib/proxy and verifies crawler IPs via lib/doh.' }],
  'ai-readiness-checker': [
    FREE,
    PROXY_LIVE,
    PROXY_PRIVACY,
    { label: 'Live HTTP + DNS', evidence: 'Fetches robots.txt and llms.txt via lib/proxy and runs DNS lookups via lib/doh; nothing stored.' },
  ],
  'mta-sts-checker': [
    FREE,
    PROXY_LIVE,
    PROXY_PRIVACY,
    { label: 'HTTPS Policy Fetch', evidence: 'MX records via DoH (lib/doh); the MTA-STS policy file via lib/proxy from https://mta-sts.<domain>/.' },
  ],
  'whois-lookup': [
    FREE,
    { label: '⚡ Live RDAP Query', evidence: 'Queries the registry RDAP endpoint live from the browser (lib/proxy direct fetch; RDAP sends CORS headers).' },
    PROXY_PRIVACY,
    { label: 'Live RDAP (RFC 7480)', evidence: 'RDAP/HTTP; no port-43 whois socket.' },
  ],
  'domain-age-checker': [
    FREE,
    { label: '⚡ Live RDAP Query', evidence: 'Queries registry RDAP for creation dates live from the browser (lib/proxy direct fetch).' },
    PROXY_PRIVACY,
    { label: 'Live RDAP (RFC 7480)', evidence: 'RDAP/HTTP; no port-43 whois socket.' },
  ],

  // --- Public API tools ---
  'my-ip': [
    FREE,
    API_LIVE,
    API_PRIVACY,
    { label: 'Live IP Detection', evidence: 'Browser calls a public IP-echo API; PromptDNS stores nothing.' },
  ],
  'dns-leak-test': [
    FREE,
    API_LIVE,
    API_PRIVACY,
    { label: 'Live Resolver Probe', evidence: 'Browser issues unique DNS queries and reports which resolvers answer, via the bash.ws test API; results are not stored.' },
  ],
  'ip-lookup': [
    FREE,
    API_LIVE,
    API_PRIVACY,
    { label: 'Public IP API', evidence: 'IP metadata from a public API (lib/ipinfo) called from the browser.' },
  ],

  // --- Local parsers: no network call ---
  'email-header-analyzer': [FREE, LOCAL_LIVE_PARSER, LOCAL_PRIVACY, { label: 'RFC 5322 Parser', evidence: 'Parses RFC 5322 header blocks locally in the page.' }],
  'dmarc-report-analyzer': [FREE, LOCAL_LIVE_PARSER, LOCAL_PRIVACY, { label: 'Local XML Parser', evidence: 'Unzips and parses DMARC aggregate XML entirely in the browser.' }],
  'ai-log-analyzer': [FREE, LOCAL_LIVE_PARSER, LOCAL_PRIVACY, { label: 'Local Log Parser', evidence: 'Parses pasted server log lines locally; no upload endpoint.' }],
  'schema-validator': [FREE, LOCAL_LIVE_PARSER, LOCAL_PRIVACY, { label: 'Local Schema Parser', evidence: 'Validates pasted JSON locally; an optional URL fetch (lib/proxy) exists for remote schemas.' }],
  'spf-lookup-limit': [FREE, LOCAL_LIVE_PARSER, LOCAL_PRIVACY, { label: 'RFC 7208 Audit', evidence: 'Counts DNS-querying mechanisms against the RFC 7208 limit of 10, locally.'}],

  // --- Local builders: no network call ---
  'spf-record-generator': [FREE, LOCAL_LIVE_BUILDER, LOCAL_PRIVACY, { label: 'RFC 7208 Builder', evidence: 'Builds v=spf1 records locally from your inputs.' }],
  'dkim-record-generator': [FREE, LOCAL_LIVE_BUILDER, LOCAL_PRIVACY, { label: 'RSA Key Builder', evidence: 'Generates the DKIM keypair locally via WebCrypto; the private key never leaves the browser.' }],
  'dmarc-record-generator': [FREE, LOCAL_LIVE_BUILDER, LOCAL_PRIVACY, { label: 'RFC 7489 Builder', evidence: 'Builds v=DMARC1 records locally from your inputs.' }],
  'llms-txt-generator': [FREE, LOCAL_LIVE_BUILDER, LOCAL_PRIVACY, { label: 'llmstxt.org Spec', evidence: 'Generates llms.txt per the llmstxt.org markdown spec, locally; an optional URL check exists via lib/proxy.' }],

  // --- Local calculators: no network call ---
  'cidr-calculator': [FREE, LOCAL_LIVE_CALC, CALC_PRIVACY, { label: 'Local Calculator', evidence: 'IPv4/IPv6 math runs locally.' }],
  'ipv4-to-ipv6-converter': [FREE, LOCAL_LIVE_CALC, CALC_PRIVACY, { label: 'Local Converter', evidence: 'Address conversion runs locally.' }],
  'punycode-converter': [FREE, LOCAL_LIVE_CALC, CALC_PRIVACY, { label: 'Local Converter', evidence: 'Punycode/IDN conversion runs locally.' }],
};

/** 1-click preset pills. Empty array hides the pill row (no text input to fill). */
export const DEFAULT_PRESETS = ['cloudflare.com', 'google.com', 'github.com'];

export const TOOL_PRESETS: Record<string, string[]> = {
  // textarea/file tools: no domain input to fill
  'email-header-analyzer': [],
  'dmarc-report-analyzer': [],
  'llms-txt-generator': [],
  'schema-validator': [],
  'ai-log-analyzer': [],
  // no input at all
  'my-ip': [],
  'dns-leak-test': [],
  // IP / IDN inputs
  'cidr-calculator': ['192.168.1.0/24', '10.0.0.1', '2001:db8::/32'],
  'ipv4-to-ipv6-converter': ['8.8.8.8', '192.168.1.1', '2606:4700:4700::1111'],
  'punycode-converter': ['münchen.de', 'bücher.de', 'пример.рф'],
};
