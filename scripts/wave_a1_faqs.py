"""WAVE A1: FAQ backfill + hub AnswerBlocks. Read pages, inject unique FAQs
(reaching 3+ per page, with FAQPage schema parity where a schema const exists),
and add AnswerBlocks to the 7 hub pages missing one. Read+write targeted edits.
"""
import json
import pathlib
import re

PAGES = pathlib.Path('src/pages')

# 3 fresh FAQs for every page currently at 0
FAQS3 = {
  'ai-crawlers-list': [
    ('What is an AI crawler?', 'An AI crawler is a bot that fetches web pages to train or power AI systems: GPTBot collects training data for GPT models, OAI-SearchBot indexes for ChatGPT Search, and ClaudeBot does both for Claude.'),
    ('Which AI crawlers should I block?', 'Decide per vendor: allow the search crawlers whose citations you want (OAI-SearchBot, PerplexityBot) and decide training access separately (GPTBot, ClaudeBot, CCBot). Bytespider is the one commonly blocked at the firewall level.'),
    ('How do I check if an AI crawler visited my site?', 'Match the user-agent token in your server logs against reverse DNS on the fetching IP. Our AI crawler checker reads your published rules the way each bot would.'),
  ],
  'ai-readiness-guide': [
    ('What does the AI readiness score measure?', 'Seven technical signals: website DNS resolution, IPv6 support, DNSSEC, SPF, DMARC policy, AI crawler access via robots.txt, and llms.txt availability, each weighted toward a 100-point score.'),
    ('What is a good AI readiness score?', 'Anything above 90 means your domain resolves cleanly, authenticates mail, and is readable by the major AI crawlers. The most common gaps are missing DNSSEC and no published llms.txt.'),
    ('How often should I re-check AI readiness?', 'After any DNS, robots.txt, or hosting change. The checks run live in your browser, so re-running is free and takes seconds.'),
  ],
  'ai-web-infrastructure': [
    ('What is AI web infrastructure?', 'The layer of DNS records, crawling policy, and content signals that decides whether AI systems can read, cite, and trust your site: robots.txt rules per crawler, llms.txt, authentication records, and resolver health.'),
    ('Why do AI crawlers matter for my site?', 'AI answer engines crawl the web to build their indexes and training sets. If your policy blocks them, your content is absent from their answers; if your DNS is broken, they cannot verify you at all.'),
    ('How do I make my site AI-ready?', 'Publish explicit per-crawler rules in robots.txt, add llms.txt, keep SPF, DKIM, and DMARC aligned, and sign the zone with DNSSEC. The AI readiness checker scores all of it in one pass.'),
  ],
  'bimi': [
    ('Does BIMI improve deliverability?', 'Indirectly at best. BIMI displays your logo; it is the reward for DMARC enforcement, not a deliverability control. The reputation gains come from DMARC itself.'),
    ('Do I need a trademark for BIMI?', 'Yes for Gmail: a Verified Mark Certificate requires a registered trademark. Some providers accept a Common Mark Certificate with lighter requirements.'),
    ('Which providers support BIMI?', 'Gmail, Apple Mail on recent versions, Yahoo, and Fastmail display BIMI logos. Support requires the DNS record, the SVG, and a valid certificate.'),
  ],
  'dkim': [
    ('Does DKIM encrypt email?', 'No. DKIM signs the message so receivers can verify it was not altered. Encryption of the transport is a separate TLS mechanism.'),
    ('What happens if my DKIM key is revoked?', 'Mail signed with that selector fails verification. That is why rotation publishes the new selector first and retires the old one only after signing moves.'),
    ('Can I have multiple DKIM records?', 'Yes, under different selectors. Each selector is its own DNS name, and mail carries the selector it was signed with.'),
  ],
  'dmarc-alignment': [
    ('What is the difference between relaxed and strict alignment?', 'Relaxed (the default) compares organizational domains: mail.example.com aligns with example.com. Strict requires an exact match. Most domains should stay relaxed.'),
    ('Why does my email fail alignment when SPF passes?', 'SPF validates the envelope sender, and DMARC compares that domain with the visible From header. Forwarding and third-party senders change the envelope, breaking alignment while SPF itself passes.'),
    ('Does DMARC require both SPF and DKIM to pass?', 'No. DMARC passes when either SPF or DKIM passes AND the passing protocol aligns with the From header domain. Using both is redundancy, not a requirement.'),
  ],
  'dmarc-monitoring': [
    ('What does DMARC monitoring do?', 'It collects the aggregate reports mailbox providers already send you, parses the XML, and shows every source sending mail as your domain with its SPF, DKIM, and DMARC results.'),
    ('Do I need to change my DNS to use it?', 'Only to add or update your DMARC record with a rua address that points at the collection service. No records move; no mail flow changes.'),
    ('Is DMARC monitoring free?', 'The analyzer tool is free forever. Continuous collection and alerts are part of the early-access monitoring product.'),
  ],
  'dmarc-record': [
    ('Where do I publish the DMARC record?', 'As a TXT record at _dmarc.yourdomain.com in your authoritative DNS host. Most providers accept the name as _dmarc when you enter it at the root.'),
    ('Can I have multiple DMARC records?', 'No. Exactly one record at _dmarc is valid; multiple records make receivers ignore DMARC entirely. Merge everything into one.'),
    ('How long until DMARC takes effect?', 'The record propagates in minutes, but receivers cache policies, so expect 24 to 48 hours before the policy is applied everywhere.'),
  ],
  'dns-monitoring': [
    ('What does DNS monitoring check?', 'The records that break sites when they drift: A, AAAA, MX, NS, SPF, DKIM, DMARC, and DNSSEC, re-checked on a fixed schedule against their last known values.'),
    ('How often are domains re-checked?', 'Every 6 hours in the current early-access build, with an email alert when any monitored record changes.'),
    ('What happens when a record changes?', 'You get an alert with the old and new values, so a vendor-side change or an unauthorized edit surfaces in hours instead of after the outage.'),
  ],
  'dns-providers': [
    ('Which DNS provider should I choose?', 'Judge on four things: anycast coverage, API and automation support, DNSSEC handling, and how fast record changes go live. Our provider playbooks compare the majors on exactly those.'),
    ('Can I move DNS without moving my registrar?', 'Yes. Changing nameservers at the registrar repoints DNS hosting while ownership stays put. This is the standard way to move DNS.'),
    ('How do I know who my DNS host is?', 'Look up your NS records: the nameservers your registrar delegated to are your DNS host. Our nameserver lookup shows them instantly.'),
  ],
  'doh-vs-dot': [
    ('Which is faster, DoH or DoT?', 'On the wire they are comparable; DoT runs on port 853 as a dedicated protocol while DoH rides port 443. Real-world differences come from the resolver, not the transport.'),
    ('Does DoH hide DNS from my ISP?', 'Yes: the query is encrypted to the resolver, so the ISP sees the connection but not the names. The resolver operator still sees the queries.'),
    ('Is DoQ replacing both?', 'DNS-over-QUIC (RFC 9250) is the newer transport with lower connection setup cost, but adoption is earlier. All three encrypt; they differ in port and framing.'),
  ],
  'email-deliverability': [
    ('What improves email deliverability fastest?', 'Authenticate first: aligned SPF, DKIM, and an enforced DMARC policy fix the majority of avoidable spam placement. Reputation and content matter after authentication is solid.'),
    ('Does DMARC affect deliverability?', 'Yes, positively when enforced: receivers trust authenticated domains, and p=reject stops spoofed mail from poisoning your reputation.'),
    ('How do I test deliverability?', 'Send to a seed account and read the headers: our email header analyzer shows the authentication results and spam verdicts a mailbox applies.'),
  ],
  'enable-dnssec-cloudflare': [
    ('Does Cloudflare DNSSEC cost anything?', 'No. DNSSEC signing is included on all plans, and Cloudflare can publish the DS record to supported registrars in one click.'),
    ('How long does DNSSEC activation take?', 'Signing is near-instant on Cloudflare; the DS record at the registrar propagates within minutes to hours. Validation goes green once the chain is visible.'),
    ('What if my registrar does not support DS records?', 'Then the chain of trust cannot complete and DNSSEC stays inactive for that domain. Move DNS delegation to a registrar that publishes DS records, or host DNS with the registrar that does.'),
  ],
  'flush-dns-cache': [
    ('How often should I flush DNS?', 'Only when diagnosing or right after a record change. Routine flushing wastes time because the cache self-expires at each record TTL.'),
    ('Does flushing DNS delete history?', 'No. It clears only cached name resolutions, not browsing history, cookies, or saved passwords.'),
    ('Why do websites still fail after flushing?', 'The failure is probably not caching: verify the domain resolves with a record lookup, then check the resolver itself with the propagation checker.'),
  ],
  'get-off-barracuda-blocklist': [
    ('How long does Barracuda delisting take?', 'Usually within an hour of an approved request, and the block decays naturally in days if the sending behavior stops.'),
    ('Why did my IP get listed?', 'Barracuda reacts to spam-trap hits, complaint rates, and sudden volume from new IPs. A new server sending cold email is the classic trigger.'),
    ('Can I prevent future listings?', 'Authenticate with SPF, DKIM, and enforced DMARC, warm new IPs slowly, and keep complaint rates low. Listings follow behavior, not luck.'),
  ],
  'how-dns-works': [
    ('What are the four servers in a DNS lookup?', 'The recursive resolver, the root nameserver layer, the TLD nameserver for the extension, and the authoritative nameserver that holds the zone. Each answers with a referral to the next.'),
    ('Does DNS use TCP or UDP?', 'Both: UDP port 53 for normal queries, TCP port 53 for truncated responses and zone transfers, plus encrypted DoH and DoT transports.'),
    ('What is DNS caching?', 'Every answer carries a TTL that each layer may cache: the browser, the operating system, and the resolver. Caching is why changes propagate gradually.'),
  ],
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

# 1 extra FAQ for pages currently at 2
FAQS1 = {
  'arc-seal-explained': ('Is ARC widely supported by mailbox providers?', 'Gmail and Microsoft evaluate ARC chains; many smaller providers do not yet. Treat ARC as additive authentication, not a replacement for SPF and DKIM.'),
  'bimi-record': ('How long does BIMI setup take end to end?', 'The DNS record and SVG are minutes; the VMC certificate is the long pole, with trademark validation and issuance typically taking weeks.'),
  'bimi-vmc': ('Can I use a CMC instead of a VMC?', 'A Common Mark Certificate is accepted by some providers with lighter trademark verification. Gmail requires the full VMC, so check your target inboxes first.'),
  'dkim-canonicalization': ('Does canonicalization affect which headers are signed?', 'No. The h= list chooses which headers are signed; canonicalization only normalizes whitespace and folding before hashing so transit modifications do not break verification.'),
  'dkim-key-length': ('How do I rotate from 1024-bit to 2048-bit safely?', 'Publish the new 2048-bit key under a second selector, switch signing to it, verify inbound checks pass, then remove the old selector. Never delete the old record first.'),
  'dkim-not-signing': ('Can multiple ESPs sign the same domain with different selectors?', 'Yes, and it is the normal pattern: each ESP publishes its own selector and signs with its own key. Verification is per selector.'),
  'dkim-vs-dmarc': ('Why can mail pass DKIM and still fail DMARC?', 'DKIM passed cryptographically, but its d= domain did not align with the visible From header, so DMARC could not credit it. Alignment, not validity, is the DMARC test.'),
  'dmarc-aggregate-reports': ('Can I send aggregate reports to multiple addresses?', 'Yes: rua accepts a comma-separated list of mailto URIs, though large providers cap the number per record. Two addresses is the common pattern.'),
  'dmarc-enforcement-roadmap': ('What if legitimate mail fails after moving to reject?', 'Drop pct to a lower value or step back to quarantine while you fix the failing source, then re-advance. The aggregate reports show exactly which source failed.'),
  'dmarc-forensic-reports': ('Are forensic reports a privacy risk?', 'Yes, and that is why almost no major provider sends them: they carry message content to a third party. Aggregate reports give you the same source data without content.'),
  'dmarc-pct-tag': ('Does pct apply to reports too?', 'No. Reports cover every message regardless of pct; the tag only throttles how much failing mail receives the enforcement action.'),
  'dmarc-policies': ('How do I test p=quarantine before p=reject?', 'Use pct: start at pct=25 so a quarter of failing mail is quarantined, watch the aggregate reports for legitimate failures, then step up.'),
  'dmarc-subdomain-policy': ('What about subdomains I do not control?', 'You cannot force compliance on delegations you handed out, but sp=reject at your domain stops non-existent subdomains being used for spoofing.'),
  'dmarc-vs-spf-vs-dkim': ('Which protocol should I deploy first?', 'SPF first as the cheapest baseline, DKIM second because it survives forwarding, then DMARC to enforce and report. That order is the standard rollout.'),
  'how-to-create-dmarc-record': ('Should I start at p=none or p=quarantine?', 'Start at p=none with rua reporting: two weeks of aggregate reports tell you which legitimate senders exist before any enforcement decision.'),
  'mta-sts-record': ('How often is the MTA-STS policy refreshed?', 'Receivers cache the policy for its max_age, re-fetching it at expiry. Changes therefore take up to one max_age cycle to reach every sender.'),
  'multiple-dkim-selectors': ('Do multiple selectors increase lookup count?', 'No: DKIM lookups happen at mail time for the selector in the signature, not during SPF evaluation, so selectors do not touch the SPF 10-lookup budget.'),
  'spf-flattening': ('Does flattening remove the need for DKIM?', 'No. Flattening fixes the SPF lookup limit; DKIM still covers forwarding and alignment. Flattening without monitoring risks silent staleness.'),
  'spf-record-too-long': ('Is there a tool to check both limits at once?', 'Yes: our SPF record checker reports the lookup count and total length together, so you see both limits in one run.'),
  'spf-temperror': ('Can I retry a message that hit TempError myself?', 'Yes: resending after a few minutes usually succeeds because the resolver or nameserver recovered. Persistent TempError means a nameserver problem, not a record problem.'),
  'spf-vs-dmarc': ('Why does my mail pass SPF and still fail DMARC?', 'Because SPF validated the envelope domain, which did not align with the visible From header. DMARC tests alignment; SPF alone cannot provide it.'),
  'tls-rpt-record': ('Can TLS-RPT and DMARC reporting share an address?', 'Yes: both accept mailto URIs and the report formats identify themselves. A dedicated address keeps volume separation cleaner.'),
  'tls-rpt': ('Which providers send TLS reports?', 'Gmail and Microsoft are the major senders today. The reports arrive daily as JSON summaries of successful and failed TLS connections to your MX hosts.'),
}

ANSWERS = {
  'ai-web-infrastructure': 'AI web infrastructure is the layer of DNS records, crawler policy, and content signals that decides whether AI systems can read, cite, and trust your site. It spans per-crawler robots.txt rules, llms.txt, mail authentication, and resolver health.',
  'dmarc-monitoring': 'DMARC monitoring is the continuous collection and analysis of the aggregate reports mailbox providers already send, turning raw XML into a live list of every source sending mail as your domain with its authentication results.',
  'dns-monitoring': 'DNS monitoring is the continuous re-checking of a domain\u2019s records against their last known values, so a vendor-side change or unauthorized edit surfaces in hours instead of after the outage.',
  'dns-providers': 'DNS providers are the services that answer queries for your domain: they host the records, run the nameservers, and decide how fast changes go live. The registrar and the DNS host are two different roles.',
  'email-deliverability': 'Email deliverability is the measure of whether your mail reaches the inbox instead of spam, driven by authentication (SPF, DKIM, DMARC), sender reputation, and recipient engagement.',
  'ip-and-networking': 'IP and networking is the layer beneath DNS: how addresses are allocated and routed, how ports move traffic, and how networks talk to each other. Every DNS answer ends in an IP connection.',
  'ssl-tls': 'SSL and TLS are the cryptographic protocols that encrypt connections between browsers and servers. Modern certificates use TLS; the handshake, chain of trust, and versions decide whether visitors see a padlock or a warning.',
}

applied_faq, applied_answer = 0, []
for slug, faqs in FAQS3.items():
    p = PAGES / f'{slug}.astro'
    if not p.exists():
        print('MISSING:', slug); continue
    s = p.read_text(encoding='utf-8')
    items = ''
    for q, a in faqs:
        items += (
            '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
            f'<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">{q}'
            '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
            f'<p class="mt-3 text-sm leading-relaxed text-ink-dim">{a}</p></details>'
        )
    last = s.rfind('</details>')
    if last > 0:
        s = s[:last + len('</details>')] + items + s[last + len('</details>'):]
        how = 'appended to grid'
    else:
        # new FAQ section before the closing of the article or the tool-links footer paragraph
        anchor = s.rfind('<p class="mt-8 text-xs text-ink-faint">')
        section = (
            '<h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>\n'
            '      <div class="mt-3 grid gap-3">' + items + '</div>\n      '
        )
        if anchor > 0:
            s = s[:anchor] + section + s[anchor:]
        else:
            art = s.rfind('</article>')
            if art > 0:
                s = s[:art] + section + s[art:]
            else:
                print('NO ANCHOR:', slug); continue
        how = 'new section'
    # FAQPage schema parity: extend an existing faqSchema/faq const if present
    sm = re.search(r"(const (?:faqSchema|faq) = \{.*?mainEntity: \[)(.*?)(\],?)", s, re.S)
    if sm:
        qjson = ', '.join(
            "{ '@type': 'Question', name: " + json.dumps(q).replace('"', "'") + ', acceptedAnswer: { ' + "'@type': 'Answer'" + ', text: ' + json.dumps(a).replace('"', "'") + ' } }'
            for q, a in faqs
        )
        s = s[:sm.end(1)] + sm.group(2).rstrip().rstrip(',') + ', ' + qjson + sm.group(2)[-1:] + sm.group(3)[1:] + s[sm.end(3):]
    p.write_text(s, encoding='utf-8')
    applied_faq += 1
    print(f'FAQs {how}: {slug} (+{len(faqs)})')

for slug, answer in ANSWERS.items():
    p = PAGES / f'{slug}.astro'
    s = p.read_text(encoding='utf-8')
    if 'data-vs="answer"' in s:
        continue
    m = re.search(r'(</h1>\n)', s)
    if not m:
        print('NO H1:', slug); continue
    block = '\n    <div class="pd-answer" data-vs="answer">\n      <p class="text-lg leading-relaxed text-ink-dim">' + answer + '</p>\n    </div>'
    s = s[:m.end(1)] + block + s[m.end(1):]
    p.write_text(s, encoding='utf-8')
    applied_answer.append(slug)
print('AnswerBlocks added:', applied_answer)
