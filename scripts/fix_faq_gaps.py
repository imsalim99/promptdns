# -*- coding: utf-8 -*-
"""Add 6+ FAQ accordions to every page that has fewer than 4."""
import re, os, json, glob

# FAQ banks by topic pattern
def generic_dns_faqs(topic):
    return [
        (f"How do I check {topic} after making changes?", "Run the record lookup to see live values from a public resolver, then confirm worldwide agreement with the propagation checker. Both tools run in your browser with no signup."),
        (f"What TTL should I use for {topic}?", "3600 seconds (1 hour) is the sensible default for stable records. Drop to 300 seconds a full day before planned changes so cutover is quick, then raise it back afterwards."),
        (f"Can I manage {topic} without a DNS provider?", "You need a DNS host to publish records. Free options like Cloudflare DNS handle the authoritative side; your registrar just delegates to them."),
        (f"Why do my {topic} changes not appear immediately?", "Resolver caches serve old answers until each record's TTL expires. This is by design and is called propagation. Lower TTLs before planned changes to minimize the window."),
        (f"Is {topic} related to my website's SEO?", "Indirectly: broken DNS means an unreachable site, which destroys rankings. Correct DNS records also affect email deliverability, which impacts user trust signals."),
        (f"Do I need technical knowledge to manage {topic}?", "The basics are straightforward with the right tools. Our guides include step-by-step processes with screenshots, and every tool on this site runs in your browser with no configuration required."),
    ]

def checker_faqs(tool, what):
    return [
        (f"Is the {tool} really free?", f"Yes: every tool on PromptDNS is free forever, with no account, no limits, and no trial timers. The {what} runs entirely in your browser."),
        (f"How accurate are the results?", f"The {what} queries public DNS-over-HTTPS resolvers (Cloudflare, Google, Quad9) in real time. Results reflect what those resolvers actually serve, which is the same data the wider internet receives."),
        (f"Do you store the domains I look up?", f"No. Lookups happen client-side in your browser. Domains are not sent to our servers, stored, or logged. See the privacy policy for details."),
        (f"Can I use this tool for client work?", "Yes: the tools are free for commercial use. Agencies on the Business plan can also generate white-label automated reports."),
        (f"How often should I run this check?", f"After any DNS or infrastructure change, and periodically (weekly or monthly) as part of routine health monitoring. The paid plans automate this."),
        (f"What if the results look wrong?", f"Compare with a second tool or dig from a terminal. If results differ between tools, one may be showing a cached answer: the propagation checker reveals which resolvers disagree."),
    ]

def guide_faqs(topic):
    return [
        (f"What is {topic} in simple terms?", "Think of it as the rulebook that a specific part of the internet follows. Every page in this section explains one rule, why it exists, and how to follow it correctly."),
        ("Do I need to memorize all of this?", "No: bookmark this page and the related tools. The goal is understanding what to check and when, not memorizing syntax."),
        ("How long does it take to implement?", "Most configurations take 5-15 minutes in your DNS panel. The verification (using our tools) takes another 2 minutes."),
        ("What happens if I get it wrong?", "Depends on the setting: some errors cause immediate visible failures, others silently degrade deliverability or security. Every guide includes the symptoms to watch for."),
        ("Is this the same across all DNS providers?", "The underlying protocol is identical; the dashboard layout and terminology differ. Our provider playbooks cover the exact flow for Cloudflare, GoDaddy, Namecheap, Route 53, and others."),
        ("Where can I get help if I'm stuck?","Each guide links to the relevant free tool so you can verify your work. The support page lists email channels for questions the guides don't cover."),
    ]

def hub_faqs(topic):
    return [
        (f"What is the {topic} section?", f"It's a curated collection of guides and tools focused on {topic.lower()}, organized from fundamentals to advanced configurations."),
        ("Are all these pages free?", "Yes: every guide and tool on PromptDNS is free forever, with no account and no limits."),
        ("How do I navigate this section?","Start with the first card and follow the internal links. Each page connects to related topics so you naturally build understanding."),
        ("How often is this content updated?","Money pages are reviewed and refreshed every 90 days. New guides are added weekly as the topical map expands."),
        ("Can I suggest a topic that's missing?","Yes: email hello@promptdns.com with your suggestion. We prioritize based on search demand and user feedback."),
        ("Is this content written by experts?","Every page follows a documented editorial standard: verified processes, tool-verified instructions, and regular reviews. See the About page for details."),
    ]

# Map slugs to FAQ content
FAQ_MAP = {}

# Tool pages -> checker FAQs
tool_checks = {
    'ttl-checker': ('TTL Checker', 'TTL analysis'),
    'dns-speed-test': ('DNS Speed Test', 'resolver benchmark'),
    'dns-resolver-tester': ('DNS Resolver Tester', 'resolver query'),
    'dns-response-time-test': ('Response Time Test', 'latency measurement'),
    'dnssec-checker': ('DNSSEC Checker', 'DNSSEC validation'),
    'delegation-checker': ('Delegation Checker', 'delegation audit'),
    'glue-record-checker': ('Glue Record Checker', 'glue record audit'),
    'wildcard-dns-tester': ('Wildcard DNS Tester', 'wildcard probe'),
    'axfr-checker': ('AXFR Leak Checker', 'zone transfer audit'),
    'dns-leak-test': ('DNS Leak Test', 'DNS leak detection'),
    'smtp-tester': ('SMTP Preflight', 'SMTP preflight check'),
    'ip-reputation-checker': ('IP Reputation Checker', 'IP reputation scan'),
    'schema-validator': ('Schema Validator', 'structured data validation'),
    'ai-log-analyzer': ('AI Log Analyzer', 'AI crawler log analysis'),
}
for slug, (tool, what) in tool_checks.items():
    FAQ_MAP[slug] = checker_faqs(tool, what)

# Checker pages (email tools)
email_tools = {
    'spf-record-checker': ('SPF Record Checker', 'SPF validation'),
    'spf-flattener': ('SPF Flattener', 'SPF flattening'),
    'dkim-record-checker': ('DKIM Record Checker', 'DKIM validation'),
    'dmarc-record-checker': ('DMARC Record Checker', 'DMARC validation'),
    'dmarc-record-generator': ('DMARC Record Generator', 'DMARC record generation'),
    'dmarc-report-analyzer': ('DMARC Report Analyzer', 'DMARC report analysis'),
    'blacklist-checker': ('Blacklist Checker', 'blocklist scan'),
    'bimi-record-checker': ('BIMI Record Checker', 'BIMI validation'),
    'mta-sts-checker': ('MTA-STS Checker', 'MTA-STS validation'),
    'tls-rpt-checker': ('TLS-RPT Checker', 'TLS-RPT validation'),
    'spf-record-generator': ('SPF Generator', 'SPF record generation'),
    'dkim-record-generator': ('DKIM Generator', 'DKIM key generation'),
}
for slug, (tool, what) in email_tools.items():
    if slug not in FAQ_MAP:
        FAQ_MAP[slug] = checker_faqs(tool, what)

# Other tool pages
for slug, (tool, what) in {
    'ai-crawler-checker': ('AI Crawler Checker', 'AI crawler audit'),
    'llms-txt-generator': ('llms.txt Generator', 'llms.txt generation'),
    'ai-readiness-checker': ('AI Readiness Checker', 'AI readiness audit'),
    'email-header-analyzer': ('Email Header Analyzer', 'email header analysis'),
    'dns-record-lookup': ('DNS Record Lookup', 'DNS record lookup'),
    'dns-propagation-checker': ('DNS Propagation Checker', 'propagation check'),
    'whois-lookup': ('WHOIS Lookup', 'RDAP lookup'),
    'domain-age-checker': ('Domain Age Checker', 'domain age check'),
    'nameserver-lookup': ('Nameserver Lookup', 'nameserver lookup'),
    'reverse-ip-lookup': ('Reverse IP Lookup', 'reverse IP lookup'),
    'my-ip': ('What Is My IP', 'IP discovery'),
    'ip-lookup': ('IP Lookup', 'IP lookup'),
    'cidr-calculator': ('CIDR Calculator', 'subnet calculation'),
    'ipv4-to-ipv6-converter': ('IPv6 Converter', 'IPv6 conversion'),
    'punycode-converter': ('Punycode Converter', 'IDN conversion'),
    'dns-leak-test': ('DNS Leak Test', 'DNS leak detection'),
    'agents-txt-checker': ('agents.txt Checker', 'agents.txt validation'),
    'robots-txt-checker': ('robots.txt Checker', 'robots.txt validation'),
}.items():
    if slug not in FAQ_MAP:
        FAQ_MAP[slug] = checker_faqs(tool, what)

# Hub pages
for slug, topic in [
    ('dns', 'DNS'), ('dns-records', 'DNS record types'), ('dns-providers', 'DNS providers'),
    ('dns-security', 'DNS security'), ('email-authentication', 'email authentication'),
    ('email-deliverability', 'email deliverability'), ('ip-and-networking', 'IP and networking'),
    ('ssl-tls', 'SSL/TLS'), ('ai-web-infrastructure', 'AI web infrastructure'),
]:
    if slug not in FAQ_MAP:
        FAQ_MAP[slug] = hub_faqs(topic)

# Guide pages -> guide FAQs
guides = [
    'spf-record', 'dkim', 'dmarc', 'dmarc-record', 'bimi', 'mta-sts',
    'spf-record-syntax', 'spf-lookup-limit', 'dkim-selector',
    'how-to-add-dkim-record', 'how-to-add-mx-record', 'mx-record-not-working',
    'how-to-read-dmarc-reports', 'what-is-ttl-in-dns', 'doh-vs-dot',
    'cname-flattening', 'mx-record', 'dns-propagation', 'what-is-dns',
    'how-dns-works', 'flush-dns-cache', 'what-is-dnssec', 'https-vs-dnssec',
    'what-is-ssl-tls', 'free-ssl-lets-encrypt', 'tls-versions-explained',
    'hsts-explained', 'mixed-content-fix', 'ssl-certificate-errors',
    'certificate-authorities-explained', 'ipv4-vs-ipv6', 'public-vs-private-ip',
    'nat-explained', 'asn-explained', 'static-vs-dynamic-ip', 'what-is-a-cdn',
    'reverse-proxy-explained', 'dns-load-balancing', 'common-network-ports',
    'reserved-ip-ranges', 'cname-flattening', 'domain-age-seo',
    'remove-from-spamhaus-blocklist', 'get-off-barracuda-blocklist',
    'sorbs-delisting-guide', 'site-down-after-dns-change',
    'enable-dnssec-cloudflare', 'ai-crawlers-list', 'robots-txt-guide',
    'what-is-llms-txt', 'llms-txt-syntax', 'ai-readiness-guide',
    'how-to-block-ai-crawlers', 'how-to-allow-ai-crawlers',
]
for slug in guides:
    topic = slug.replace('-', ' ')
    if slug not in FAQ_MAP:
        FAQ_MAP[slug] = guide_faqs(topic)

# ip-and-networking hub already has 6 FAQs, skip
if 'ip-and-networking' in FAQ_MAP:
    del FAQ_MAP['ip-and-networking']
if 'ai-web-infrastructure' in FAQ_MAP:
    del FAQ_MAP['ai-web-infrastructure']
if 'tools' in FAQ_MAP:
    del FAQ_MAP['tools']

# ---------- INJECT ----------
patched = 0
for slug, faqs in FAQ_MAP.items():
    path = f'src/pages/{slug}.astro'
    if not os.path.exists(path):
        continue
    s = open(path, encoding='utf-8').read()
    # Count existing accordions
    existing = len(re.findall(r'<details class="group', s))
    if existing >= 4:
        continue  # already has enough

    # Build the FAQ accordion HTML
    faq_html = '<div class="mt-3 grid gap-3">' + ''.join(
        '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
        '<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">' + q +
        '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
        '<p class="mt-3 text-sm leading-relaxed text-ink-dim">' + a + '</p></details>' for q, a in faqs) + '</div>'

    # Build the section
    block = ('\n      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>\n'
             '      ' + faq_html + '\n')

    # Also build FAQPage schema
    faq_schema = json.dumps({
        '@context': 'https://schema.org', '@type': 'FAQPage',
        'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]
    }, ensure_ascii=False, indent=1)

    # Insert before "Related" section or before the closing div
    if 'Related' in s:
        # Find the Related h2 and insert before it
        idx = s.find('Related')
        if idx > 0:
            # Find the start of the h2 line
            h2_start = s.rfind('<h2', 0, idx)
            if h2_start > 0:
                s = s[:h2_start] + block + s[h2_start:]
                inserted = True
            else:
                inserted = False
        else:
            inserted = False
    else:
        # Insert before the closing div
        idx = s.rfind('    </div>\n  </div>\n</BaseLayout>')
        if idx > 0:
            s = s[:idx] + block + s[idx:]
            inserted = True
        else:
            inserted = False

    # Add schema if the page doesn't already have FAQPage
    if 'FAQPage' not in s and inserted:
        # Insert the schema import + const
        fm_start = s.find('---\n') + 4
        fm_end = s.find('---', fm_start)
        old_fm = s[fm_start:fm_end]
        # Add faq const
        faq_line = '\nconst faqSchema = ' + faq_schema + '\n'
        new_fm = old_fm + faq_line
        s = s[:fm_start] + new_fm + s[fm_end:]
        # Add schema to BaseLayout
        s = s.replace('schema={[', 'schema={[faqSchema, ', 1) if 'schema={[[' in s else s
        if 'schema=' not in s:
            s = s.replace('>', '  schema={[faqSchema]}\n>', 1) if 'schema=' not in s else s

    open(path, 'w', encoding='utf-8').write(s)
    patched += 1
    print('patched:', slug, f'({existing} -> {existing + len(faqs)} FAQs)')

print(f'\nTotal patched: {patched}')
