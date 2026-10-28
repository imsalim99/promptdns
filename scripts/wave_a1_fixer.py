"""Wave A1 fixer: backfill 3 FAQs on the 19 pages whose structure lacks a grid anchor.
Adds FAQPage schema const where the page has none. Targeted per-page edits."""
import json
import pathlib
import re

PAGES = pathlib.Path('src/pages')

FAQS3 = {
  'how-to-add-dkim-record': [
    ('Where do I get my DKIM key?', 'From your sending service: Gmail, Microsoft 365, and ESPs generate the key pair and show you the public value to publish. The private key never leaves their system in hosted setups.'),
    ('Can I add DKIM without my ESP?', 'Only if you run your own mail server and generate the key pair yourself. Hosted ESPs own the private key and publish the selector for you to add.'),
    ('How do I test the record after adding it?', 'Send a message and read the DKIM result in its headers, or run the selector through our DKIM record checker before sending anything.'),
  ],
  'how-to-add-mx-record': [
    ('What priority should my MX records use?', 'Lower numbers are tried first. Use 10 for the primary and 20 or higher for backups; equal priorities split load instead of failing over.'),
    ('Can I have multiple MX records?', 'Yes, and it is the standard resilience pattern: two or three hosts at different priorities.'),
    ('How long before MX changes work?', 'As long as the old record TTL. Lower it to 300 seconds before the change, and the new routing applies within minutes.'),
  ],
  'how-to-allow-ai-crawlers': [
    ('Which AI crawlers should I allow?', 'The search-oriented ones whose citations you want: OAI-SearchBot for ChatGPT Search and PerplexityBot for Perplexity answers. Training crawlers are a separate, independent decision.'),
    ('Does allowing AI crawlers affect SEO?', 'No. AI crawler rules do not touch Googlebot or your rankings. Search visibility and AI visibility are independent switches.'),
    ('How do I allow some AI crawlers and block others?', 'One rule block per token: Disallow: / under User-agent: GPTBot blocks training while OAI-SearchBot stays allowed with no rule or an explicit Allow.'),
  ],
  'how-to-block-ai-crawlers': [
    ('Will blocking AI crawlers hurt my traffic?', 'Your Google rankings are unaffected. What changes is presence in AI answers, which is a business decision per vendor, not an SEO penalty.'),
    ('Which AI crawlers ignore robots.txt?', 'Bytespider is reported to ignore it at times. For that one, edge-level blocking by autonomous system is the enforcement that holds.'),
    ('Can I block AI crawlers in Cloudflare?', 'Yes: the managed AI scraper blocking control, or a custom WAF rule on the user-agent token or ASN, blocks at the edge before robots.txt is even read.'),
  ],
  'how-to-read-dmarc-reports': [
    ('How often do DMARC reports arrive?', 'Daily, one XML per provider per day. Gmail, Microsoft, and Yahoo each send their own, so volume scales with the providers your recipients use.'),
    ('Why do I get reports from providers I do not use?', 'The reports cover mail claiming to be your domain anywhere: spoofing attempts, forwarders, and recipients whose mailbox provider is that vendor.'),
    ('What should I do with unknown source IPs?', 'Reverse DNS them first: many are legitimate services you forgot. The ones that fail authentication and are unknown are your spoofing candidates.'),
  ],
  'llms-txt-syntax': [
    ('Is llms.txt a standard?', 'It is an emerging convention from llmstxt.org, widely adopted by AI-facing sites but not an IETF RFC. Treat it as a strong recommendation rather than a protocol.'),
    ('Where does llms.txt go?', 'At the root of your domain: https://yoursite.com/llms.txt, served like robots.txt, in Markdown format.'),
    ('Does llms.txt replace robots.txt?', 'No. robots.txt controls crawling; llms.txt curates content for the models that already read your site. They answer different questions.'),
  ],
  'mta-sts': [
    ('Does MTA-STS require DNSSEC?', 'No. MTA-STS is enforced through a DNS TXT record plus an HTTPS-hosted policy file with a valid certificate. DNSSEC is unrelated.'),
    ('What is the difference between testing and enforce mode?', 'Testing reports TLS failures without affecting delivery; enforce requires valid TLS and bouncing non-compliant senders. Start in testing, watch reports, then enforce.'),
    ('How long is the policy max_age?', 'You set it in seconds; 86400 (one day) suits testing, and 604800 (a week) is common for stable enforce-mode policies.'),
  ],
  'mx-record-not-working': [
    ('Why is my MX lookup empty?', 'Either no MX record exists at the name you checked, or the records were removed. Mail falls back to the A record, which usually fails delivery.'),
    ('Can MX point to a CNAME?', 'It should not: RFC 2181 section 10.3 prohibits MX targets pointing at CNAMEs. Point MX at an A or AAAA hostname.'),
    ('How do I test mail delivery after fixing MX?', 'Send from an external account and read the delivery headers, or run an SMTP-level check that walks the MX priorities end to end.'),
  ],
  'remove-from-spamhaus-blocklist': [
    ('How long does Spamhaus delisting take?', 'Approved SBL and XBL removals typically apply within the hour. Repeat listings after unresolved compromises re-lock quickly.'),
    ('Why does my IP keep getting relisted?', 'Persistent listings mean the underlying source is still sending: an open relay, a compromised account, or a misconfigured newsletter stack. Delisting without fixing the source loops forever.'),
    ('What is the difference between SBL and XBL?', 'SBL lists spam sources and Spamhaus observes them actively; XBL lists exploited machines found through botnet tracking. The fixes differ: content and behavior for SBL, malware cleanup for XBL.'),
  ],
  'robots-txt-guide': [
    ('Does robots.txt guarantee compliance?', 'No. It is a request that well-behaved crawlers honor. For agents that ignore it, enforce at the WAF or edge level instead.'),
    ('Where must robots.txt be served from?', 'The root of every hostname: https://yoursite.com/robots.txt. A file anywhere else is ignored.'),
    ('What happens with an empty robots.txt?', 'Crawlers assume everything is allowed. That is a valid posture; the file only matters when you want per-crawler or per-path rules.'),
  ],
  'site-down-after-dns-change': [
    ('How long until my site works after a DNS change?', 'As long as the old TTL: records edited after a 300-second TTL recover in minutes, while a 3600-second TTL can hold stale answers for an hour, and NS changes up to 48 hours.'),
    ('My site works on mobile but not desktop, why?', 'Different devices use different resolvers with different caches. The propagation checker shows which resolvers still serve the old answer.'),
    ('Should I lower TTL before the next change?', 'Yes: lower to 300 seconds at least 24 hours ahead, make the change, verify, then raise it back. It is the single habit that prevents most migration incidents.'),
  ],
  'sorbs-delisting-guide': [
    ('What is SORBS?', 'The Spam and Open Relay Blocking System, a blocklist family covering spam sources, dynamic IPs, and exploited hosts. Some mail admins weight it heavily.'),
    ('How long does SORBS delisting take?', 'Requests are processed manually and can take days. SORBS also asks for a donation consideration on some listing classes, unlike Spamhaus.'),
    ('Why was I listed without sending spam?', 'Dynamic IP ranges and shared hosts get listed because of other tenants or a past assignment. The fix is proving a static, clean source or moving to one.'),
  ],
  'spf-lookup-limit': [
    ('Do ip4 ranges count toward the limit?', 'No. ip4 and ip6 are answered from the record itself and cost zero lookups. Only include, a, mx, ptr, exists, and redirect consume the budget.'),
    ('What happens exactly at 11 lookups?', 'Evaluation stops and receivers return permerror: the record stops protecting the domain, and mail may fail authentication.'),
    ('Does the checker follow nested includes?', 'Our checker counts the top-level terms in your record and warns about nested includes, which consume additional lookups during real evaluation.'),
  ],
  'spf-record': [
    ('What is the difference between SPF and DKIM?', 'SPF authorizes the sending IP via the envelope; DKIM signs the message content cryptographically. DMARC ties both to the visible From domain.'),
    ('Does SPF cover my website?', 'No. SPF covers email only. Website protection is DNS, TLS, and your hosting stack.'),
    ('How many SPF records can I have?', 'Exactly one per name. Two v=spf1 records on the same domain is a permerror and receivers stop evaluating.'),
  ],
  'spf-record-syntax': [
    ('What does ~all mean in SPF?', 'Softfail: senders failing SPF are marked suspicious but not rejected. -all hardfails them. ~all is the safe choice while tuning; -all is the enforcement choice.'),
    ('Is +all ever correct?', 'No. Plus-pass on everything means any server on earth may send as your domain. It is always a misconfiguration.'),
    ('What is the difference between a mechanism and a modifier?', 'Mechanisms match the sending IP and decide the result; modifiers like redirect= and exp= change evaluation or provide explanations without matching.'),
  ],
  'ssl-tls': [
    ('Are SSL and TLS the same thing?', 'TLS is the modern successor to SSL; the names are used interchangeably but every current certificate actually uses TLS. SSL 3.0 and older are deprecated and insecure.'),
    ('Which TLS version should I run?', 'TLS 1.2 as the floor and TLS 1.3 as the default. TLS 1.0 and 1.1 fail modern compliance scans.'),
    ('How do I check my certificate?', 'Visit the site and inspect the certificate in the browser, or run our SSL checker for expiry, chain, and protocol details.'),
  ],
  'what-is-llms-txt': [
    ('Who reads llms.txt?', 'AI tools and agents that use it for curated context: it points models to your best pages in Markdown. Adoption is growing across AI products and agent frameworks.'),
    ('Does llms.txt improve AI citations?', 'It helps models find your canonical pages quickly, which improves the odds of accurate citations, but it is not a guarantee: content quality and crawler access still decide.'),
    ('Is llms.txt required?', 'No. It is a strong recommendation for AI-facing sites. Missing llms.txt is scored in our AI readiness check as a gap, not an error.'),
  ],
  'what-is-ttl-in-dns': [
    ('What TTL should I use?', '300 seconds while migrating, 3600 seconds for stable records. Critical mail records can sit at 3600 once behavior is predictable.'),
    ('Does low TTL hurt performance?', 'Slightly: more resolver queries and marginally slower answers for repeat visitors. The trade is faster change propagation.'),
    ('Where is TTL set?', 'Per record in your DNS host, with a default TTL in the SOA record for the zone. Our TTL checker shows the live value for every record.'),
  ],
  'why-emails-go-to-spam': [
    ('Does DMARC fix spam placement?', 'It removes the authentication reason for spam placement. Reputation, content, and engagement still matter, so DMARC is necessary but not sufficient.'),
    ('Can a blacklist listing send me to spam?', 'Yes, major filters weigh DNSBL listings. Check and delist first, then fix the behavior that caused the listing.'),
    ('How long does reputation recovery take?', 'Days to weeks of clean, authenticated, low-complaint volume. There is no instant reset switch; consistency is the mechanism.'),
  ],
}

applied = 0
for slug, faqs in FAQS3.items():
    p = PAGES / f'{slug}.astro'
    s = p.read_text(encoding='utf-8')
    if s.count('<details') >= 3:
        print('skip (already has):', slug)
        continue
    items = ''
    for q, a in faqs:
        items += (
            '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
            f'<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">{q}'
            '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
            f'<p class="mt-3 text-sm leading-relaxed text-ink-dim">{a}</p></details>'
        )
    section = (
        '<h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>\n'
        '      <div class="mt-3 grid gap-3">' + items + '</div>\n      '
    )
    anchor = s.find('<h2>Related</h2>')
    if anchor > 0:
        s = s[:anchor] + section + s[anchor:]
        how = 'before Related'
    else:
        bl = s.rfind('</BaseLayout>')
        dv = s.rfind('</div>', 0, bl)
        s = s[:dv] + section + s[dv:]
        how = 'before final div'
    if 'FAQPage' not in s:
        qjson = ',\n    '.join(
            "{ '@type': 'Question', name: " + json.dumps(q).replace('"', "'") + ', acceptedAnswer: { '
            + "'@type': 'Answer'" + ', text: ' + json.dumps(a).replace('"', "'") + ' } }'
            for q, a in faqs
        )
        const = (
            'const faqSchema = {\n'
            "  '@context': 'https://schema.org',\n"
            "  '@type': 'FAQPage',\n"
            '  mainEntity: [\n    ' + qjson + ',\n  ],\n};\n'
        )
        s = re.sub(r'^---\n', '---\n' + const, s, count=1)
        s = s.replace('<BaseLayout\n', '<BaseLayout\n  schema={[faqSchema]}\n', 1)
    p.write_text(s, encoding='utf-8')
    applied += 1
    print(f'{slug}: 3 FAQs ({how}), schema added')
print('applied:', applied)
