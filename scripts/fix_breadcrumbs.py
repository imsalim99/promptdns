# -*- coding: utf-8 -*-
"""Batch-fix breadcrumbs across ALL pages: assign proper hub hierarchy."""
import re, os, glob

# Map: slug -> [(label, href_or_None), ...] breadcrumb trail (last item = current page, no link)
# None href = current page (plain text)
B = lambda *items: [(x[0], x[1]) for x in items]

H = 'Home', '/'
D = 'DNS Guide', '/dns/'
RT = 'Record Types', '/dns-records/'
EA = 'Email Authentication', '/email-authentication/'
ED = 'Email Deliverability', '/email-deliverability/'
PG = 'Provider Guides', '/dns-providers/'
IP = 'IP & Networking', '/ip-and-networking/'
SL = 'SSL/TLS Guides', '/ssl-tls/'
TL = 'Tools', '/tools/'

def bc(*trail):
    """Build breadcrumb nav HTML from trail. Last item is plain text, others are links."""
    parts = []
    for i, (label, href) in enumerate(trail):
        if i < len(trail) - 1:
            parts.append(f'<a href="{href}" class="hover:text-accent">{label}</a>')
        else:
            parts.append(f'<span class="text-ink-dim">{label}</span>')
    sep = ' <span aria-hidden="true">/</span>\n      '
    inner = ('\n      ' + sep + '\n      ').join(parts) if len(parts) > 1 else parts[0]
    return ('<nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">\n      '
            + ('\n      ' + sep).join(parts) + '\n    </nav>')

# Actually simpler: build the nav directly
def make_nav(trail):
    parts = []
    for i, (label, href) in enumerate(trail):
        if i < len(trail) - 1:
            parts.append(f'<a href="{href}" class="hover:text-accent">{label}</a>')
        else:
            parts.append(f'<span class="text-ink-dim">{label}</span>')
    joiner = ' <span aria-hidden="true">/</span>\n      '
    inner = ('\n      ' + joiner).join(parts)
    return ('<nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">\n      '
            + ('\n      ' + joiner).join(parts) + '\n    </nav>')

BC = {}

def add(slug, label, *parents):
    trail = [H] + list(parents) + [(label, None)]
    BC[slug] = make_nav(trail)

# --- DNS Fundamentals ---
for s, l in [('what-is-dns','What Is DNS'),('how-dns-works','How DNS Works'),
             ('dns-propagation','DNS Propagation'),('flush-dns-cache','Flush DNS Cache')]:
    add(s, l, D)

# --- Record Type pillars ---
for t in ['a','aaaa','cname','txt','ns','soa','ptr','srv','caa','alias','ds','dnskey']:
    add(f'{t}-record', t + ' Record', D, RT)

# --- Record Type lookups ---
for t in ['a','aaaa','cname','mx','ns','txt','soa','ptr','srv','caa','ds','dnskey']:
    add(f'{t}-record-lookup', t + ' Record Lookup', D, RT)

# --- DNS Security cluster ---
for s, l in [('dns-hijacking','DNS Hijacking'),('dns-cache-poisoning','DNS Cache Poisoning'),
             ('dns-amplification-attack','DNS Amplification Attacks'),('dns-tunneling','DNS Tunneling'),
             ('dns-rebinding-explained','DNS Rebinding')]:
    add(s, l, D, ('DNS Security', '/dns-security/'))

add('dns-error-messages', 'DNS Error Messages', D)
add('what-is-dnssec', 'What Is DNSSEC', D)
add('dnssec-checker', 'DNSSEC Checker', D, TL)
add('enable-dnssec-cloudflare', 'Enable DNSSEC in Cloudflare', D)

# --- Email Auth ---
for s, l in [('spf-record','SPF Records'),('spf-record-syntax','SPF Syntax'),('spf-lookup-limit','SPF Lookup Limit'),
             ('dkim','DKIM'),('dkim-selector','DKIM Selectors'),('how-to-add-dkim-record','Add DKIM Record'),
             ('dmarc','DMARC'),('dmarc-record','DMARC Record Syntax'),('how-to-read-dmarc-reports','Read DMARC Reports'),
             ('bimi','BIMI'),('mta-sts','MTA-STS'),('list-unsubscribe-header','List-Unsubscribe Headers'),
             ('email-sending-reputation','Sender Reputation'),('how-to-warm-up-email-server','Warm Up Email Server'),
             ('dedicated-vs-shared-ip','Dedicated vs Shared IP'),('cold-email-deliverability','Cold Email Deliverability'),
             ('why-emails-go-to-spam','Why Emails Go to Spam'),('email-bounced-reasons','Why Emails Bounce'),
             ('imap-vs-smtp','IMAP vs SMTP'),('spf-record-generator','SPF Generator'),
             ('dkim-record-generator','DKIM Generator'),('dmarc-record-generator','DMARC Generator'),
             ('dmarc-report-analyzer','DMARC Report Analyzer')]:
    add(s, l, EA)
add('email-bounced-reasons', 'Why Emails Bounce', EA, ED)

# --- ESP matrix (42 pages) ---
ESPS = ['sendgrid','mailchimp','hubspot','zoho-mail','brevo','klaviyo','postmark','mailgun','mandrill',
        'salesforce','pipedrive','zendesk','freshdesk','atlassian','intercom','activecampaign',
        'constant-contact','mailerlite','getresponse','aweber','mailjet','moosend','campaign-monitor',
        'customer-io','sparkpost','amazon-ses','smtp2go','socketlabs','shopify-email','woocommerce',
        'bigcommerce','woodpecker','instantly','lemlist','reply-io','gmass','sendy','drip','dotdigital',
        'ongage','pepipost','mailer-send']
for slug in ESPS:
    add(f'spf-dkim-dmarc-{slug}', f'Setup for {slug}', EA, ('Service Setup Guides', '/email-authentication/'))

# --- Deliverability cluster ---
for s, l in [('email-deliverability','Email Deliverability'),
             ('get-off-barracuda-blocklist','Barracuda Removal'),
             ('remove-from-spamhaus-blocklist','Spamhaus Removal'),
             ('sorbs-delisting-guide','SORBS Delisting')]:
    add(s, l, ED)

# --- Provider playbooks ---
PROVIDERS = ['cloudflare','godaddy','namecheap','route53','azure-dns','google-cloud-dns','cpanel','plesk']
for p in PROVIDERS:
    add(f'manage-dns-in-{p}', f'Manage DNS in {p}', PG)
    add(f'{p}-change-nameservers', f'Change Nameservers in {p}', PG)
    add(f'{p}-dns-troubleshooting', f'{p} DNS Troubleshooting', PG)
for m in ['wix','squarespace','shopify','netlify']:
    add(f'manage-dns-in-{m}', f'Manage DNS in {m}', PG)
    add(f'{m}-connect-domain', f'Connect Domain to {m}', PG)
for c in ['cloudflare-dns-vs-google-dns','cloudflare-vs-route53']:
    add(c, c.replace('-',' ').title(), PG)

# --- IP & Networking ---
for s, l in [('nat-explained','NAT Explained'),('common-network-ports','Common Network Ports'),
             ('reserved-ip-ranges','Reserved IP Ranges'),('reverse-proxy-explained','Reverse Proxy'),
             ('dns-load-balancing','DNS Load Balancing'),('asn-explained','What Is an ASN'),
             ('static-vs-dynamic-ip','Static vs Dynamic IP'),('ipv4-vs-ipv6','IPv4 vs IPv6'),
             ('public-vs-private-ip','Public vs Private IP'),('what-is-a-cdn','What Is a CDN')]:
    add(s, l, IP)
add('ip-and-networking', 'IP & Networking Hub')

# --- SSL/TLS ---
for s, l in [('free-ssl-lets-encrypt',"Let's Encrypt"),('tls-versions-explained','TLS Versions'),
             ('hsts-explained','HSTS'),('mixed-content-fix','Mixed Content'),
             ('ssl-certificate-errors','Certificate Errors'),('certificate-authorities-explained','Certificate Authorities'),
             ('https-vs-dnssec','HTTPS vs DNSSEC'),('what-is-ssl-tls','What Is SSL/TLS')]:
    add(s, l, SL)
add('ssl-tls', 'SSL/TLS Guides Hub')

# --- AI cluster ---
for s, l in [('ai-crawlers-list','AI Crawlers List'),('how-to-block-ai-crawlers','Block AI Crawlers'),
             ('how-to-allow-ai-crawlers','Allow AI Crawlers'),('what-is-llms-txt','What Is llms.txt'),
             ('llms-txt-syntax','llms.txt Syntax'),('ai-readiness-guide','AI Readiness Guide'),
             ('robots-txt-guide','robots.txt Guide')]:
    add(s, l, ('AI Web Infrastructure', '/ai-crawlers-list/'))

# --- Tool pages (Home / Tools / Tool Name) ---
for s, l in [('dns-propagation-checker','DNS Propagation Checker'),('dns-record-lookup','DNS Record Lookup'),
             ('dns-speed-test','DNS Speed Test'),('ttl-checker','TTL Checker'),('dnssec-checker','DNSSEC Checker'),
             ('delegation-checker','Delegation Checker'),('glue-record-checker','Glue Record Checker'),
             ('wildcard-dns-tester','Wildcard DNS Tester'),('axfr-checker','AXFR Leak Checker'),
             ('dns-resolver-tester','Resolver Tester'),('dns-response-time-test','Response Time Test'),
             ('spf-record-checker','SPF Record Checker'),('spf-flattener','SPF Flattener'),
             ('dkim-record-checker','DKIM Record Checker'),('dmarc-record-checker','DMARC Record Checker'),
             ('blacklist-checker','Blacklist Checker'),('ip-reputation-checker','IP Reputation Checker'),
             ('smtp-tester','SMTP Preflight'),('email-header-analyzer','Email Header Analyzer'),
             ('bimi-record-checker','BIMI Checker'),('mta-sts-checker','MTA-STS Checker'),
             ('tls-rpt-checker','TLS-RPT Checker'),('autodiscover-checker','Autodiscover Checker'),
             ('my-ip','What Is My IP'),('ip-lookup','IP Lookup'),('reverse-ip-lookup','Reverse IP Lookup'),
             ('whois-lookup','WHOIS Lookup'),('domain-age-checker','Domain Age Checker'),
             ('nameserver-lookup','Nameserver Lookup'),('cidr-calculator','CIDR Calculator'),
             ('ipv4-to-ipv6-converter','IPv6 Converter'),('punycode-converter','Punycode Converter'),
             ('dns-leak-test','DNS Leak Test'),('ai-crawler-checker','AI Crawler Checker'),
             ('robots-txt-checker','robots.txt Checker'),('llms-txt-generator','llms.txt Generator'),
             ('ai-readiness-checker','AI Readiness Checker'),('ai-log-analyzer','AI Log Analyzer'),
             ('schema-validator','Schema Validator'),('agents-txt-checker','agents.txt Checker'),
             ('dns-error-messages','DNS Error Messages')]:
    add(s, l, TL)

# --- Operations ---
for s, l in [('dns-migration-checklist','DNS Migration Checklist'),('site-down-after-dns-change','Site Down After DNS Change'),
             ('email-not-working-after-dns-change','Email Stopped After DNS Change')]:
    add(s, l, D)

# --- Troubleshooting ---
for s, l in [('mx-record-not-working','MX Not Working'),('how-to-add-mx-record','Add MX Records'),
             ('how-to-add-dkim-record','Add DKIM Record'),('website-not-resolving','Website Not Resolving')]:
    add(s, l, D)

# ---------- APPLY ----------
patched = 0
for slug, nav_html in BC.items():
    path = f'src/pages/{slug}.astro'
    if not os.path.exists(path):
        print('SKIP (no file):', slug); continue
    s = open(path, encoding='utf-8').read()
    # find and replace the breadcrumb nav
    m = re.search(r'<nav class="[^"]*"[^>]*aria-label="Breadcrumb">.*?</nav>', s, re.S)
    if m:
        s = s[:m.start()] + nav_html + s[m.end():]
        open(path, 'w', encoding='utf-8').write(s)
        patched += 1
    else:
        print('NO BREADCRUMB FOUND:', slug)

print(f'Patched {patched} breadcrumbs')
