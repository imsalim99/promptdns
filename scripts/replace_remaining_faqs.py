"""FAQ replacement batch: 17 remaining tool pages with generic boilerplate FAQs.
Each page gets unique, result-state-derived questions per the audit 7.4 rules.
Also replaces the FAQPage JSON-LD schema to match visible text.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path("src/pages")

FAQS = {
    "ai-crawler-checker.astro": [
        ("Does blocking GPTBot remove my site from ChatGPT answers?",
         "Blocking GPTBot prevents OpenAI from crawling your content for training, but it does not immediately remove already-indexed content from ChatGPT responses. Search bots like OAI-SearchBot control search citations separately."),
        ("Is blocking AI crawlers bad for my SEO?",
         "Not necessarily. Blocking training bots (GPTBot, CCBot) preserves your content for search indexing while preventing AI model training. Blocking search bots (OAI-SearchBot, PerplexityBot) may reduce your visibility in AI-powered search answers."),
        ("Can AI crawlers bypass my robots.txt rules?",
         "Reputable AI companies respect robots.txt. However, there is no global enforcement mechanism, and some lesser-known crawlers may ignore it. Our checker reports which major AI crawlers are currently accessing your site."),
        ("How do I allow AI crawlers for search but block training?",
         "Use different user-agent rules: Allow OAI-SearchBot and PerplexityBot (search) while Disallow GPTBot and CCBot (training). Our checker shows you which crawlers are currently allowed or blocked."),
    ],
    "ai-readiness-checker.astro": [
        ("What does the AI readiness score actually measure?",
         "It checks seven technical signals: website DNS resolution, IPv6 support, DNSSEC, SPF, DMARC policy, AI crawler access via robots.txt, and llms.txt availability. Each check earns points toward a 100-point score."),
        ("Is a low AI readiness score bad for my regular SEO?",
         "Not directly. The score measures how accessible your site is to AI systems (crawlers, answer engines, training models). Regular SEO depends on different signals, though llms.txt and DNS security increasingly overlap."),
        ("How often should I check my AI readiness?",
         "After any robots.txt change, DNS modification, or hosting migration. Automated monitoring on paid plans checks every 6 hours."),
    ],
    "bimi-record-checker.astro": [
        ("Do I need a VMC certificate for BIMI?",
         "Yes, for Gmail and Apple Mail you need a Verified Mark Certificate (VMC) issued by a certificate authority like DigiCert or Entrust. Some providers accept Common Mark Certificates (CMC) which are cheaper."),
        ("Does BIMI work without DMARC?",
         "No. BIMI requires your domain to have DMARC enforced at p=quarantine or p=reject. p=none is not sufficient. This is why DMARC enforcement is a prerequisite for BIMI deployment."),
        ("Which email providers support BIMI?",
         "Gmail, Apple Mail (iOS 16+), and Yahoo Mail support BIMI. Microsoft Outlook does not currently support the BIMI standard. Adoption is growing but not universal."),
    ],
    "cidr-calculator.astro": [
        ("What is the difference between /24 and /16?",
         "/24 gives you 256 addresses (a typical small network). /16 gives you 65,536 addresses (a larger network or ISP allocation). The number after the slash is the count of leading 1-bits in the subnet mask."),
        ("How many usable hosts are in a /29?",
         "A /29 has 8 total addresses but only 6 usable hosts: 2 are reserved for the network identifier and the broadcast address. Our calculator shows usable hosts automatically."),
        ("Can I convert IPv4 CIDR to IPv6?",
         "Yes, an IPv4 /32 maps to an IPv6 /128 in the ::ffff: prefix range. Our IPv4-to-IPv6 converter handles this mapping."),
    ],
    "dkim-record-generator.astro": [
        ("What key size should I use for DKIM?",
         "2048-bit RSA is the current standard. 1024-bit keys are considered weak and are rejected by some receivers. Our generator defaults to 2048-bit."),
        ("Can I use the same DKIM key for multiple domains?",
         "Technically yes, but it is not recommended. Each domain should have its own DKIM key so that compromising one domain's key does not affect others."),
        ("Where do I publish the DKIM record?",
         "At your DNS provider as a TXT record at selector._domainkey.yourdomain.com. For example, if your selector is 'resend', publish at resend._domainkey.yourdomain.com."),
    ],
    "dmarc-record-generator.astro": [
        ("What is the difference between rua and ruf?",
         "rua receives aggregate reports (daily XML summaries of all DMARC evaluation results). ruf receives forensic reports (individual failure samples with full message content). Most providers only support rua."),
        ("Should I start with p=none or p=quarantine?",
         "Start with p=none to collect reports without affecting mail delivery. Read the aggregate reports to identify all legitimate senders, fix any that fail, then step to p=quarantine and finally p=reject."),
        ("Do I need DMARC on subdomains too?",
         "Not necessarily. Without an sp= tag, subdomains inherit the root domain's policy. Use sp= explicitly if you want different policies for subdomains."),
    ],
    "dns-leak-test.astro": [
        ("What is a DNS leak?",
         "A DNS leak happens when your DNS queries are sent to your ISP's resolver instead of your VPN's encrypted resolver, revealing which websites you visit to your internet provider."),
        ("How does the DNS leak test work?",
         "It generates unique subdomains and checks which resolvers respond. If resolvers outside your expected provider answer, your queries are leaking outside the tunnel."),
        ("Does a DNS leak affect my DNSSEC validation?",
         "No, DNSSEC validation is independent of which resolver handles your queries. A leak affects privacy, not integrity."),
    ],
    "dns-record-lookup.astro": [
        ("What record types can I look up?",
         "All major types: A, AAAA, CNAME, MX, NS, TXT, SOA, SRV, PTR, CAA, DNSKEY, and DS. Each returns full values and TTLs from live DNS-over-HTTPS queries."),
        ("Why do different tools show different results for the same domain?",
         "DNS results vary by resolver due to caching and TTL. Our tool queries Cloudflare, Google, and AliDNS directly. The propagation checker shows differences across all three side by side."),
        ("What does TTL mean in the results?",
         "TTL (Time To Live) is how long a resolver caches the record before re-querying the authoritative server. Lower TTLs mean faster propagation but more resolver load."),
    ],
    "email-header-analyzer.astro": [
        ("Are my email headers uploaded to a server?",
         "No. All parsing happens in your browser using JavaScript. Your email headers never leave your device."),
        ("What are Received headers and why are there so many?",
         "Each mail server that handled your message adds a Received header. Reading them bottom-to-top shows the delivery path from the sending server to your mailbox."),
        ("What does it mean when SPF or DKIM shows fail in the headers?",
         "It means the sending server did not pass that authentication check. If DMARC also fails, the mail may be spoofed. Legitimate mail can fail if forwarding breaks the original authentication."),
    ],
    "ipv4-to-ipv6-converter.astro": [
        ("What is the ::ffff: prefix in the result?",
         "It is the IPv4-mapped IPv6 address format. It represents an IPv4 address inside the IPv6 address space for dual-stack compatibility."),
        ("Can every IPv4 address be converted to IPv6?",
         "Yes. Every IPv4 address maps to a unique IPv6 address using the ::ffff:0:0/96 prefix range. The conversion is lossless and reversible."),
        ("Does converting to IPv6 make my site IPv6-accessible?",
         "No. You also need an AAAA DNS record and an IPv6-enabled server. The converter only translates the notation."),
    ],
    "llms-txt-generator.astro": [
        ("Does llms.txt improve my search rankings?",
         "Not directly for Google Search. llms.txt helps AI systems (ChatGPT, Claude, Perplexity) understand and cite your content. Google uses its own crawling and indexing independently."),
        ("Where do I upload the llms.txt file?",
         "At the root of your domain: https://yourdomain.com/llms.txt. It must be reachable at that exact path. Our generator creates the file content for you to upload."),
        ("Is llms.txt an official standard?",
         "It is a community proposal (llmstxt.org) that is gaining adoption by AI companies but is not an IETF standard. Major AI providers are beginning to check for it."),
    ],
    "mta-sts-checker.astro": [
        ("What is the difference between MTA-STS and DANE?",
         "MTA-STS uses a DNS TXT record and an HTTPS-hosted policy file to enforce TLS for SMTP. DANE uses DNSSEC-signed TLSA records. They solve the same problem differently; MTA-STS is more widely adopted."),
        ("Does MTA-STS work without DNSSEC?",
         "Yes. MTA-STS relies on HTTPS certificate validation for the policy file, not DNSSEC. This makes it easier to deploy than DANE, which requires DNSSEC."),
        ("What happens if my MTA-STS policy file is unreachable?",
         "Receiving servers fall back to their cached copy of your policy. If no cached copy exists, they skip MTA-STS enforcement and deliver normally."),
    ],
    "punycode-converter.astro": [
        ("What is punycode used for?",
         "Punycode encodes internationalized domain names (IDNs) using non-ASCII characters (like \u00e9, \u00fc, \u4e2d\u6587) into ASCII-compatible encoding that the DNS system can process."),
        ("Are punycode domains safe to click?",
         "Mostly yes, but attackers have used visually similar Unicode characters (homograph attacks) to imitate trusted domains. Always check the punycode form in your browser address bar."),
        ("Does my browser show punycode or Unicode?",
         "Modern browsers show Unicode for legitimate IDNs but switch to punycode display when the domain contains mixed character scripts that could be used for spoofing."),
    ],
    "robots-txt-checker.astro": [
        ("Does robots.txt prevent Google from indexing my page?",
         "Not directly. Disallow in robots.txt prevents crawling, but Google may still index the URL if other pages link to it. Use noindex meta tags to prevent indexing."),
        ("Can I use robots.txt to block AI crawlers?",
         "Yes. Use User-agent: GPTBot with Disallow: / to block OpenAI's training crawler. Our checker shows you which AI crawlers are currently allowed or blocked by your robots.txt."),
        ("What happens if my robots.txt has a syntax error?",
         "Most crawlers ignore malformed lines and process the valid ones. Our checker highlights syntax issues so you can fix them before they affect crawling."),
    ],
    "spf-flattener.astro": [
        ("Is SPF flattening safe for my email delivery?",
         "It can be, if monitored. Flattening replaces include: mechanisms with direct IP addresses, which stay under the 10-lookup limit. But if a provider changes their IPs, your flattened record becomes stale and legitimate mail breaks."),
        ("How often should I re-flatten my SPF record?",
         "Whenever your email providers change their sending infrastructure. Automated monitoring catches these changes; manual flattening requires you to check provider documentation regularly."),
        ("What is the alternative to SPF flattening?",
         "Move sending streams to dedicated subdomains (mail.yourdomain.com, billing.yourdomain.com) so each gets its own 10-lookup quota. This is more resilient than flattening but requires DNS and provider changes."),
    ],
    "spf-record-generator.astro": [
        ("What happens if I have two SPF records?",
         "RFC 7208 requires exactly one v=spf1 record per domain. Multiple records cause a permerror, which means receivers ignore your SPF entirely. Merge all senders into a single record."),
        ("What is the difference between ~all and -all?",
         "~all (softfail) marks unlisted senders as suspicious but delivers their mail. -all (hardfail) instructs receivers to reject unlisted senders. Use ~all until you are confident every legitimate sender is listed."),
        ("Do I need ip4: and ip6: mechanisms?",
         "Only if you send email from servers not covered by an include: mechanism. Most email services (Google Workspace, SendGrid) provide include: directives that already cover their sending IPs."),
    ],
    "tls-rpt-checker.astro": [
        ("What is TLS-RPT and do I need it?",
         "TLS-RPT (RFC 8460) lets receiving servers report TLS connection failures to you via email. It is required for MTA-STS deployment and helps you diagnose delivery issues."),
        ("Where do TLS-RPT reports come from?",
         "Major mailbox providers (Gmail, Microsoft) send daily JSON reports listing TLS connection outcomes for your domain. They arrive at the address in your _smtp._tls DNS record."),
    ],
}

def strip_html(s):
    return re.sub(r'<[^>]+>', '', s)

def schema_for(pairs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": strip_html(a)}}
            for q, a in pairs
        ],
    }

def details_html(pairs):
    parts = []
    for q, a in pairs:
        parts.append(
            '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
            f'<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">{q}'
            '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
            f'<p class="mt-3 text-sm leading-relaxed text-ink-dim">{a}</p></details>'
        )
    return '<div class="mt-3 grid gap-3">' + ''.join(parts) + '</div>'

changed = 0
for fname, pairs in FAQS.items():
    path = ROOT / fname
    if not path.exists():
        print(f"SKIP {fname} (not found)")
        continue
    txt = path.read_text(encoding="utf-8")

    # Replace FAQPage JSON-LD schema
    schema_start = txt.find('"@context": "https://schema.org"')
    schema_end = txt.find('}', txt.find('"mainEntity"'))
    if schema_start >= 0 and schema_end >= 0:
        # find the closing brace of the whole schema object
        depth = 0
        for i in range(schema_start, len(txt)):
            if txt[i] == '{': depth += 1
            elif txt[i] == '}':
                depth -= 1
                if depth == 0:
                    schema_end = i + 1
                    break
        old_schema = txt[schema_start:schema_end]
        new_schema = json.dumps(schema_for(pairs), indent=1)
        txt = txt[:schema_start] + new_schema + txt[schema_end:]
        did_schema = True
    else:
        did_schema = False

    # Replace the visible FAQ details block
    faq_match = re.search(
        r'(<div class="mt-3 grid gap-3"><details class=.*?</div>\s*</div>|<div class="mt-3 grid gap-3"><details class=.*?</details></div>)',
        txt, re.DOTALL
    )
    did_div = False
    if faq_match and "How accurate are the results?" in faq_match.group(0):
        txt = txt[:faq_match.start()] + details_html(pairs) + txt[faq_match.end():]
        did_div = True

    if did_schema or did_div:
        path.write_text(txt, encoding="utf-8")
        changed += 1
        print(f"OK {fname}: {len(pairs)} unique FAQs")
    else:
        print(f"FAIL {fname}: no FAQ block found")

print(f"\n{changed} pages updated")
