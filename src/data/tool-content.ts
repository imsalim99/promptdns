/** Deep editorial content for tool pages (Koray semantic-node layer).
 *  Each entry: process, interpret, cli, errors[3], who, faqs[5-6]. */
export interface ToolContent {
  title: string;
  process: string[];
  interpret: string[];
  cli: string;
  errors: [string, string][];
  who: string;
  faqs: [string, string][];
}

export const TOOL_CONTENT: Record<string, ToolContent> = {
  "ttl-checker": {
    title: "Understanding TTL values",
    process: [
      "The checker queries seven record families (A, AAAA, MX, NS, TXT, SOA, CAA) against a public resolver and reports the TTL still attached to each cached or authoritative answer. Every row is one live DNS response, exactly as resolvers worldwide would receive it.",
      "A TTL counts down from the value your zone publishes. A record with TTL 3600 shows 3600 on the first query after publication and smaller numbers as caches age, which is why the checker's numbers occasionally differ from your DNS panel.",
    ],
    interpret: [
      "3600 or higher: the record is treated as stable. Good for untouched infrastructure, painful for anything you plan to change.",
      "300 or lower: migration-ready. Changes appear globally in minutes because caches expire almost immediately.",
      "86400 on a record you might move: a full day of mixed traffic after any change. Lower it before, not after, the cutover.",
    ],
    cli: "dig example.com A +noall +answer   # the fourth column is the TTL",
    errors: [
      ["TTL shows 0","Your DNS host published a zero TTL: caching is disabled and your nameservers absorb every query. Raise it."],
      ["TTL differs between resolvers","Normal: each resolver's copy ages independently. The authoritative value is what your panel shows."],
      ["No answers for a type","The domain publishes no records of that family; the TTL check simply skips it."],
    ],
    who: "Anyone planning a migration, debugging why a change hasn't appeared, or inheriting a zone with mystery settings.",
    faqs: [
      ["Does lowering TTL speed up my site?","No. TTL affects how quickly changes spread, not resolution speed for visitors. Lower TTLs can even add slight lookup overhead."],
      ["Is a high TTL bad?","Not inherently: stable records with high TTLs resolve efficiently. It only becomes a problem when you need changes to appear fast."],
      ["How long before a TTL change takes effect?","The OLD TTL governs. If your record has TTL 86400, resolvers may hold the old value (and its old TTL) up to a day."],
      ["What TTL do CDNs use?","Typically 60-300 seconds, because their edge IPs rotate. Follow your CDN's published guidance."],
      ["Why did my TTL edit not apply yet?","Caches still serve the previously published TTL. The new TTL only governs answers fetched after caches expire."],
      ["Does TTL apply to MX records too?","Yes: every record type carries a TTL, which is why email migrations need the same pre-lowering treatment as websites."],
    ],
  },
  "dns-speed-test": {
    title: "How resolver benchmarking works",
    process: [
      "The test sends four identical A-record queries to each participating resolver over DNS-over-HTTPS and measures the full round-trip from your browser: connection, TLS, query, response. The average and the best (warm-cache) time are reported per resolver.",
      "Because every query starts from your own network, the numbers reflect your route to each resolver, not a global truth. Two users in different cities can see opposite rankings and both be correct.",
    ],
    interpret: [
      "Under 20 ms: excellent; you won't perceive any difference browsing.",
      "Differences under 10 ms between resolvers: statistically noise; pick on privacy and filtering features instead.",
      "One resolver far slower on every run: a routing problem on your network's path to it, or an overloaded node; retry later before drawing conclusions.",
      "Best time much lower than average: the first query paid a cold-connection cost. Warm performance is what daily browsing experiences.",
    ],
    cli: "dig @1.1.1.1 example.com +stats   # look at the 'Query time' line",
    errors: [
      ["All resolvers very slow","Your own connection is the bottleneck: run the test again on a different network before blaming resolvers."],
      ["A resolver times out entirely","Its DoH endpoint may be blocked on your network (some ISPs and firewalls filter 8.8.8.8 specifically)."],
      ["Results differ wildly between runs","Mobile networks and congested Wi-Fi add jitter; average over several sessions."],
    ],
    who: "Users choosing a system resolver, VPN users verifying performance, and network admins benchmarking provider changes.",
    faqs: [
      ["Does a faster DNS make downloads faster?","No: DNS only resolves names. Download speed depends on the connection to the actual server."],
      ["Is the fastest resolver the most private?","Not necessarily. Speed and privacy are separate choices; check each provider's logging policy."],
      ["Should I switch my router's DNS based on this?","You can, but enterprise setups often prefer their ISP or corporate resolver for filtering and local resolution."],
      ["Why is my first query always slower?","The TCP and TLS handshake to the DoH endpoint is paid once per connection; subsequent queries reuse it."],
      ["Do results differ on mobile data?","Yes, sometimes significantly: mobile carrier routing is a different path entirely."],
      ["How often should I re-test?","Only when something changes: a new ISP, a move, or a provider announcement. DNS speed is stable day to day."],
    ],
  },
  "dns-resolver-tester": {
    title: "Querying resolvers directly",
    process: [
      "The tester sends your exact query to the resolver you select as a standard DNS-over-HTTPS request and returns the raw answer set: every record with its name, TTL, and value, plus the round-trip time. Custom endpoints work the same way, as long as they speak the RFC 8484 JSON profile.",
      "This is the closest a browser can get to running dig by hand: you control both the question (name and type) and the party being asked.",
    ],
    interpret: [
      "An answer with a TTL means the resolver cached it from the authoritative source; TTL counts down from the zone's value.",
      "NOERROR with zero answers: the name exists but publishes no records of that type.",
      "NXDOMAIN: the name itself doesn't exist in the zone.",
      "SERVFAIL from one resolver while others answer: validation failure (often DNSSEC) or that resolver's upstream problem.",
    ],
    cli: "dig @1.1.1.1 example.com MX +noall +answer",
    errors: [
      ["Custom endpoint returns nothing","The endpoint must send CORS headers and speak the JSON DoH profile (name= and type= parameters, Accept: application/dns-json)."],
      ["CORS error in browser console","The resolver refuses browser-origin queries. Not all DoH servers allow web use."],
      ["Unexpected record values","You queried a caching resolver: it may serve a slightly older answer within TTL. Query the authoritative nameserver for the zone's current truth."],
    ],
    who: "Developers debugging DNS behavior, admins comparing provider answers, and anyone validating a custom DoH deployment.",
    faqs: [
      ["What is a DoH endpoint?","An HTTPS URL that accepts DNS queries and returns answers as JSON (or wire format). Cloudflare, Google, AliDNS, and NextDNS all publish one."],
      ["Can I test my own resolver?","Yes, if it exposes a DoH JSON endpoint with CORS enabled. Enter its URL in the custom field."],
      ["Why do different resolvers give different answers?","Caches at different ages, geo-routing (CDNs answer differently per region), and filtering policies all play a role."],
      ["Is this the same as nslookup?","Functionally yes for queries; the transport is HTTPS instead of port 53, which also means encrypted transit."],
      ["What does the TTL in the answer mean?","How long the resolver may keep serving that cached answer before re-asking the authoritative server."],
    ],
  },
  "dns-response-time-test": {
    title: "Reading resolver latency",
    process: [
      "Response time is measured the same way the speed test measures it: repeated DoH queries from your browser, timing each round trip. The distinction is emphasis: this view is about per-query latency behavior, including the cold-start penalty on the first connection.",
      "Each resolver is queried multiple times so the average smooths out single-packet jitter, and the best (minimum) time shows the steady-state performance your browsing actually experiences.",
    ],
    interpret: [
      "A high first query with fast repeats is normal: connection setup, not DNS slowness.",
      "Consistent latency above 100 ms to every resolver points at your network, not the providers.",
      "Comparing runs before and after changing your system resolver shows whether the switch actually mattered.",
    ],
    cli: "for i in 1 2 3 4; do dig @8.8.8.8 example.com +stats | grep 'Query time'; done",
    errors: [
      ["One resolver skipped or timed out","Its DoH endpoint is unreachable from your network path; retry on another connection."],
      ["Latency differs between the speed test and this one","Different moment, different network load. Treat anything under 30 ms as equivalent."],
    ],
    who: "Anyone tuning their network stack, comparing VPN providers' DNS, or validating that a resolver change helped.",
    faqs: [
      ["What is a good DNS response time?","Under 50 ms is typical for major providers; under 20 ms is excellent. Beyond 100 ms, investigate."],
      ["Does this test encrypt my queries?","Yes: all queries travel over DNS-over-HTTPS, so your network operator sees HTTPS traffic, not DNS."],
      ["Why measure from the browser?","Because that's where most real-world lookups happen: browsers route their own DoH, and this measures that exact path."],
    ],
  },
  "delegation-checker": {
    title: "What delegation health means",
    process: [
      "The checker lists every nameserver your domain's NS records declare, then resolves each server hostname to an IP address. A nameserver that cannot resolve is a delegation break in waiting: resolvers that pick it get SERVFAIL while others answer, producing intermittent, hard-to-reproduce failures.",
      "It also flags in-bailiwick hosts (nameservers inside your own domain, like ns1.example.com), which additionally require glue records at the parent zone.",
    ],
    interpret: [
      "All servers resolve: delegation is structurally healthy; follow up with content consistency checks.",
      "One server missing an IP: fix it before it rotates into a resolver's selection. Half-broken delegation is worse than fully broken because it hides.",
      "In-bailiwick without glue: the parent must publish glue A records, or that nameserver is unreachable by strict resolvers.",
    ],
    cli: "dig example.com NS +short && dig @ns1.example.com example.com SOA",
    errors: [
      ["NS host has no A record","Add the missing address record (or glue at the registrar), or remove that server from the NS set."],
      ["Intermittent SERVFAIL for some users","Classic lame or slow delegation: one nameserver in the set is dead or stale."],
      ["Registry NS differ from zone NS","Two sources of truth: align the registrar delegation with the zone's own NS records."],
    ],
    who: "Anyone who has changed DNS providers, moved hosting, or inherited a domain with mystery failures.",
    faqs: [
      ["How many nameservers should a domain have?","Two to four, all healthy. More servers only add reliability if each one actually answers."],
      ["What is lame delegation?","A nameserver listed as authoritative that doesn't actually serve the zone: users hit it at random and fail."],
      ["Do I need glue records?","Only when nameservers live inside the domain they serve (ns1.example.com for example.com)."],
      ["How often should I check delegation?","After any provider or registrar change, and whenever intermittent resolution failures appear."],
    ],
  },
  "glue-record-checker": {
    title: "Glue records and in-bailiwick delegation",
    process: [
      "The checker identifies which of your nameservers are in-bailiwick (hosted inside your own domain) and verifies each resolves to an address. For in-bailiwick servers, the parent zone (.com registry or your delegated subdomain) must publish glue A records, because a resolver cannot learn ns1.example.com's address without asking example.com's nameservers, which it can't reach without knowing ns1's address.",
    ],
    interpret: [
      "In-bailiwick and resolving: glue exists and works.",
      "In-bailiwick and not resolving: missing or broken glue at the parent; set it at the registrar.",
      "Out-of-bailiwick: glue is unnecessary; ordinary A records at the DNS host suffice.",
    ],
    cli: "dig @a.gtld-servers.net example.com NS   # the additional section shows registry glue",
    errors: [
      ["Nameserver resolves elsewhere but not via glue","Some resolvers accepted a normal A record; strict resolvers still fail. Publish proper registry glue."],
      ["Glue set at registrar but checker still fails","Delegation caches: registry NS changes take up to 48 hours to appear everywhere."],
    ],
    who: "Operators running their own nameservers under their own domain, and anyone moving off hosting-provider DNS.",
    faqs: [
      ["Are glue records set in my DNS panel?","No. For registry delegation, glue belongs at the registrar (who writes it into the parent zone)."],
      ["Do I need glue for ns1.example.net?","No: out-of-bailiwick nameservers resolve through normal DNS."],
      ["Can glue point to multiple IPs?","Yes: publish one glue record per address the nameserver answers on."],
    ],
  },
  "wildcard-dns-tester": {
    title: "Detecting wildcard records",
    process: [
      "The tester queries three randomly generated subdomains that no human could have created. If they resolve anyway, a wildcard record (*.domain) is matching everything; the returned addresses show what the wildcard points at. If they return NXDOMAIN, no wildcard exists.",
    ],
    interpret: [
      "Wildcard detected: every subdomain answers, including typos of your real hosts. Intentional for some platforms (vanity domains, catch-all landing pages); surprising when inherited from an old setup.",
      "No wildcard: only explicitly created records answer; typo subdomains simply fail.",
      "Mixed results across probes: rare partial wildcards or flaky infrastructure worth investigating.",
    ],
    cli: "dig random-xyz123.example.com A +short",
    errors: [
      ["Wildcard points at a parking IP","Inherited hosting state: replace or delete the *.record if you don't intend catch-all behavior."],
      ["Wildcard detected but I never made one","Check for a *.record in your zone (some hosts add them by default for 'all subdomains work' marketing)."],
    ],
    who: "Anyone auditing inherited zones, setting up multi-tenant subdomains, or verifying that catch-all behavior is deliberate.",
    faqs: [
      ["Are wildcard records bad?","Not inherently: they power multi-tenant apps and vanity URLs. They're a problem only when unintentional, because typos resolve and NXDOMAIN-based checks break."],
      ["Do wildcards cover existing records?","No: specific records win over the wildcard for their exact name."],
      ["Do wildcards work for email?","Technically yes, but wildcard MX is strongly discouraged: it invites typographical mail to unknown servers."],
    ],
  },
  "axfr-checker": {
    title: "Why open zone transfers matter",
    process: [
      "AXFR is the protocol DNS servers use to replicate an entire zone between themselves. If a nameserver allows AXFR to the whole internet, anyone can download every record in your zone: internal hostnames, mail infrastructure, staging servers. Browsers cannot open the TCP/53 sessions AXFR requires, so this audit enumerates your authoritative servers and produces the exact test command for each.",
    ],
    interpret: [
      "REFUSED or SERVFAIL in response to the dig command: correct; transfers are restricted.",
      "A full record listing: your zone leaks. Restrict allow-transfer to your secondaries' addresses immediately.",
      "No response at all: firewalled, which also prevents the attack, though REFUSED is the cleaner posture.",
    ],
    cli: "dig AXFR yourdomain.com @ns1.yourdomain.com   # REFUSED is the passing result",
    errors: [
      ["Transfer succeeds from one server","That server's allow-transfer is missing or set to any. Restrict it to your secondary IPs, or disable AXFR entirely if you have no secondaries."],
      ["Zone transfers were fine last year","Provider migrations sometimes reset ACLs; re-audit after any DNS infrastructure change."],
    ],
    who: "Server administrators, security auditors, and anyone who inherited a self-hosted DNS setup.",
    faqs: [
      ["Is AXFR always bad?","No: it's essential between your own primary and secondaries. The risk is allowing it to everyone."],
      ["What can an attacker do with my zone?","Map your infrastructure: internal hostnames, staging boxes, mail topology. It's reconnaissance gold."],
      ["Do managed DNS hosts allow AXFR?","Almost never by default; the risk mostly applies to self-hosted BIND/PowerDNS servers."],
    ],
  },
  "dnssec-checker": {
    title: "Reading the DNSSEC chain",
    process: [
      "The checker queries two record types that together prove DNSSEC is active: the DS record at the parent zone (the registrar-published voucher for your key) and the DNSKEY records in your zone (the public keys themselves). Both must be present and consistent for validating resolvers to trust your answers.",
    ],
    interpret: [
      "DS + DNSKEY present: the chain of trust is publishable; validation happens at resolvers worldwide.",
      "DNSKEY without DS: the zone signs but nobody can verify it; publish the DS at the registrar to activate.",
      "DS without DNSKEY: a broken or removed signing setup; resolvers will SERVFAIL the domain. Re-enable signing or remove the DS.",
      "Algorithm 13 or 15: modern, compact. Algorithm 8: acceptable. Anything else: plan a rotation.",
    ],
    cli: "dig example.com DS +short && dig example.com DNSKEY +short | wc -l",
    errors: [
      ["SERVFAIL everywhere after enabling DNSSEC","DS mismatch: the digest at the registrar doesn't match the zone's KSK. Compare the tuples field by field."],
      ["DS present but stale","Key rotation happened without updating the DS. Publish the new key's DS, wait, then retire the old."],
    ],
    who: "Anyone enabling DNSSEC, rotating keys, or diagnosing domain-wide resolution failures.",
    faqs: [
      ["Does DNSSEC slow my site down?","Marginally larger DNS responses, unnoticeable in practice. The security benefit outweighs it."],
      ["Can I have DNSSEC without a DS record?","Your zone signs but no resolver trusts it: an island. The DS is the activation step."],
      ["How do I know my DNSSEC is valid?","Resolve your domain through a validating resolver like Quad9; success without warnings means the chain works."],
    ],
  },
  "smtp-tester": {
    title: "The SMTP preflight model",
    process: [
      "Browsers cannot open raw SMTP sockets, so this preflight audits everything around the SMTP conversation: MX records that route mail to you, reverse DNS (PTR) on your mail host's IP, and the full authentication stack (SPF, DKIM, DMARC) that receivers check before accepting your outbound mail.",
      "Each check maps to a real SMTP failure mode: missing MX means delivery has no destination, missing PTR is a heavy spam signal, failed authentication gets your mail rejected by Gmail and Yahoo's 2024 requirements.",
    ],
    interpret: [
      "All four rows green: your domain is structurally ready to send and receive.",
      "MX green but PTR missing: set reverse DNS with your hosting provider for the mail server's IP.",
      "Auth rows failing: fix SPF/DKIM/DMARC first; they're free and instant compared to reputation repair.",
    ],
    cli: "openssl s_client -starttls smtp -connect mail.example.com:587   # then EHLO test",
    errors: [
      ["MX points at a host with no PTR","Set reverse DNS at the IP owner (cloud provider), matching the hostname the server announces."],
      ["SPF passes but DMARC fails","Alignment: the From domain differs from the authenticated domain. Configure the mail platform to send as your domain."],
    ],
    who: "Admins standing up mail servers, deliverability troubleshooters, and SaaS operators self-hosting notification mail.",
    faqs: [
      ["Does this test send any email?","No: it performs DNS-layer checks only. The terminal commands below run the actual socket conversation when you're ready."],
      ["Why does PTR matter so much?","Receivers do forward-confirmed reverse DNS: an IP without matching PTR is treated as unconfigured, which correlates strongly with spam."],
      ["What ports should my mail server expose?","25 for server-to-server inbound, 587 (STARTTLS) or 465 (implicit TLS) for user submission."],
    ],
  },
  "ip-reputation-checker": {
    title: "How IP blocklist checks work",
    process: [
      "DNS-based blocklists (DNSBLs) answer a simple question through DNS itself: reverse the IP, append the list's zone, and see whether an A record comes back. A 127.x.x.x answer means the IP carries that list's flag (spam source, proxy, dynamic space); NXDOMAIN means clean. The checker runs your IP against each list's zone over DoH and translates the codes.",
    ],
    interpret: [
      "Clean everywhere: your IP carries no blocklist penalties; deliverability problems lie elsewhere (authentication, content, reputation).",
      "Listed on one list: read that list's code page (each 127.x.octet means a specific reason), fix the root cause, then delist.",
      "'Not checkable' on Spamhaus/URIBL: those lists refuse public-resolver queries by policy to prevent abuse; verify on their own lookups before assuming clean.",
    ],
    cli: "dig 10.113.0.203.zen.spamhaus.org +short   # answers only when listed",
    errors: [
      ["Listed on SORBS for a clean server","SORBS aggregates aggressively; request delisting with evidence after confirming the IP isn't actually sending spam."],
      ["Newly assigned IP already listed","You inherited the previous tenant's reputation: delist and warm up gradually."],
    ],
    who: "Email server operators, deliverability troubleshooters, and anyone whose mail suddenly started bouncing or junk-folding.",
    faqs: [
      ["Can I check a domain here too?","Yes: the full Blacklist Checker handles domain-based lists (SURBL, DBL) alongside IP lists."],
      ["How fast do listings clear?","Delisting takes hours to days depending on the list's policy; some auto-expire if the behavior stops."],
      ["Why do lists differ?","Each blocklist has its own traps, sources, and policies; an IP can be clean on one and listed on another."],
    ],
  },
  "autodiscover-checker": {
    title: "How mail clients auto-configure",
    process: [
      "When a mail client learns only an email address, it probes predictable DNS names to fetch server settings: autodiscover.yourdomain.com (Microsoft clients), autoconfig.yourdomain.com (Thunderbird and friends), and an SRV record (_autodiscover._tcp) as fallback. This checker queries all three and reports what each returns.",
    ],
    interpret: [
      "CNAME or SRV present: clients can auto-discover server settings; user setup is one password entry.",
      "All missing: clients fall back to manual entry, which is where typos and support tickets breed.",
      "Autodiscover points at the wrong host: clients will try the wrong server and fail with confusing certificate errors.",
    ],
    cli: "dig autodiscover.example.com CNAME +short && dig _autodiscover._tcp.example.com SRV +short",
    errors: [
      ["Outlook prompts for settings repeatedly","Autodiscover is missing or points at a host without a valid certificate."],
      ["Autoconfig works on desktop but not mobile","Mobile clients lean on SRV records or mobileconfig profiles; publish the SRV too."],
    ],
    who: "IT admins deploying mail for teams, and anyone whose users keep asking 'what are the server settings?'",
    faqs: [
      ["Is autodiscover only for Microsoft?","The autodiscover name is Microsoft's; Thunderbird uses autoconfig, and SRV is the neutral fallback. Publishing all three covers every client."],
      ["Do I need these if I publish good docs?","Docs help, but auto-configuration removes an entire class of setup errors, especially for non-technical staff."],
    ],
  },
  "schema-validator": {
    title: "Why JSON-LD validation matters",
    process: [
      "Structured data (JSON-LD blocks embedded in pages) tells machines exactly what entities your content describes: organizations, products, articles, FAQs. The validator fetches the page, extracts every script[type=application/ld+json] block, and parses each as strict JSON: syntax errors here silently disable rich results and machine comprehension.",
    ],
    interpret: [
      "Valid JSON-LD with @type: the block parses; check the type list against what the page actually is.",
      "Invalid JSON: a trailing comma, unquoted key, or stray bracket is breaking that block; fix and revalidate.",
      "No JSON-LD found: the page either has none or ships it via microdata/RDFa (different syntaxes this validator doesn't read).",
    ],
    cli: "curl -s https://example.com | python -c \"import sys,json,re; [json.loads(b) for b in re.findall(r'<script type=.application/ld\\+json.>(.*?)</script>', sys.stdin.read(), re.S)]\"",
    errors: [
      ["Valid JSON but no rich results","Validity is necessary, not sufficient: Google also requires eligibility (content type, guidelines) and time to recrawl."],
      ["Multiple blocks with errors","Fix blocks one at a time; a single broken block doesn't usually break siblings, so validate each."],
    ],
    who: "SEO engineers implementing schema, developers debugging structured data, and AI-readiness auditors.",
    faqs: [
      ["Does valid schema guarantee rich results?","No: it makes you eligible. Google applies its own quality and policy filters on top."],
      ["JSON-LD vs microdata?","Same vocabulary (schema.org), different syntax. JSON-LD is Google's recommended format and the only one this validator parses."],
      ["Can schema help AI visibility?","Yes: unambiguous entity markup removes interpretation work for answer engines, which is part of AI readiness."],
    ],
  },
  "ai-log-analyzer": {
    title: "Reading AI crawlers in your logs",
    process: [
      "Server access logs record every request with its User-Agent string. The analyzer scans the uploaded log for all twelve documented AI crawler user-agents (GPTBot, ClaudeBot, PerplexityBot and friends), counts each bot's requests, and extracts the most-fetched paths: the ground truth of what AI systems actually read on your site, as opposed to what their docs claim.",
    ],
    interpret: [
      "GPTBot hammering /blog/: OpenAI is training on your content at scale.",
      "OAI-SearchBot + ChatGPT-User present: ChatGPT is retrieving your pages to answer user questions, the citation-friendly traffic.",
      "A bot fetching robots.txt and sitemap.xml repeatedly: it's (re)discovering your site; watch what follows.",
      "Zero AI bots in a large log: either they're blocked by robots/WAF, or your content isn't on their discovery path yet.",
    ],
    cli: "grep -iE 'gptbot|claudebot|perplexitybot' /var/log/nginx/access.log | awk '{print $7}' | sort | uniq -c | sort -rn",
    errors: [
      ["Huge log file stalls the browser","Split the file or analyze a recent slice; the parser streams line by line but browsers limit single-file reads."],
      ["Bot visits but paths all 404","The crawler is probing old URLs: check your redirects and sitemap freshness."],
    ],
    who: "Publishers deciding AI-access policy, SEO teams measuring AI visibility, and admins auditing unexpected crawl load.",
    faqs: [
      ["Does this upload my logs anywhere?","No: parsing happens in your browser with JavaScript. The file never leaves your machine."],
      ["What formats work?","Any line-based log containing the User-Agent string: nginx, Apache, CDN exports, cloud load-balancer logs."],
      ["Can I identify AI bots that fake their user-agent?","Not from user-agent alone; dedicated operators can spoof. Cross-check with reverse DNS on the source IPs for high-stakes decisions."],
    ],
  },
  "agents-txt-checker": {
    title: "The agents.txt convention",
    process: [
      "agents.txt is an emerging convention (distinct from robots.txt) for publishing machine-readable guidance to AI agents: what they may access, preferred endpoints, and contact points. The checker fetches https://yourdomain/agents.txt through the proxy chain and shows the raw content for review.",
    ],
    interpret: [
      "File found: read it as you would robots.txt; verify it says what you intend for agents.",
      "Not found: extremely common today, the convention is young. Publishing one positions you early, but don't expect universal consumption yet.",
      "HTML returned instead of plain text: the server is falling back to a 404 page; the file genuinely doesn't exist at the root.",
    ],
    cli: "curl -s https://example.com/agents.txt | head -20",
    errors: [
      ["Checker shows my homepage HTML","The server returns 200 with an HTML page for unknown paths (soft 404). Publish a real file or leave it absent."],
      ["Fetched via relay label","Your server didn't send CORS headers, so the proxy chain fetched it; content is identical."],
    ],
    who: "Early adopters of agent-facing infrastructure and teams auditing their machine-readable surface area.",
    faqs: [
      ["Is agents.txt a real standard?","Emerging and not universal. Unlike robots.txt, no major crawler documents support for it; treat it as forward-compatible infrastructure."],
      ["agents.txt vs llms.txt?","Different jobs: agents.txt addresses agent permissions/behavior; llms.txt is a content map for language models. Publishing both is coherent."],
    ],
  },
  "reverse-ip-lookup": {
    title: "Forward-confirmed reverse DNS",
    process: [
      "The lookup resolves your IP to a hostname via its PTR record (in the in-addr.arpa reverse zone), then immediately resolves that hostname forward to an address. When the forward answer matches the original IP, the pair is 'forward-confirmed': the strongest signal that the reverse DNS is real and deliberate rather than leftover defaults.",
    ],
    interpret: [
      "PTR exists and forward-confirms: correct configuration, required for mail-sending IPs and valued by reputation systems.",
      "PTR exists but doesn't confirm: often a shared host's generic name; acceptable for web servers, harmful for mail senders.",
      "No PTR: acceptable for consumer connections, a deliverability problem for anything that sends mail.",
    ],
    cli: "dig -x 8.8.8.8 +short && dig $(dig -x 8.8.8.8 +short) +short",
    errors: [
      ["PTR is a generic ISP name","Fine for browsing, bad for sending mail: set a matching hostname with your provider and align your mail server's HELO."],
      ["PTR changed by itself","Dynamic IP space: your provider reassigns addresses. Use a static IP for anything mail-related."],
    ],
    who: "Mail server operators, deliverability engineers, and admins documenting their infrastructure.",
    faqs: [
      ["Who controls PTR records?","The owner of the IP address block: your hosting provider or ISP, never your domain registrar."],
      ["Can one IP have several PTR records?","Technically possible, practically harmful: resolvers return them in unpredictable order, breaking forward confirmation."],
      ["Does PTR affect website SEO?","No: reverse DNS matters for mail and network diagnostics, not web rankings."],
    ],
  },
  "nameserver-lookup": {
    title: "What nameserver data tells you",
    process: [
      "The lookup queries your domain's NS records from a public resolver, then resolves every returned nameserver to both its IPv4 and IPv6 addresses. You get the complete delegation picture: which servers the internet believes are authoritative, and whether each is actually reachable.",
    ],
    interpret: [
      "The expected set, all resolving: delegation is correct.",
      "An unexpected set: the domain's delegation differs from what you thought (provider changed, domain moved, or someone edited the registrar).",
      "A nameserver with no addresses: a dead server in the set; see the Delegation Checker for the deeper diagnosis.",
    ],
    cli: "dig example.com NS +short && dig ns1.example.com A +short",
    errors: [
      ["Two different NS sets appear","Registry delegation and zone NS records disagree: align them at the registrar and the DNS host."],
      ["Old nameservers still listed after a move","Delegation caches for up to 48 hours; confirm the registry updated, then wait."],
    ],
    who: "Anyone who changed DNS providers, transferred a domain, or inherited unknown infrastructure.",
    faqs: [
      ["NS lookup vs WHOIS: same thing?","No: WHOIS shows registration data (registrar, dates); the NS lookup shows live delegation. Both matter after changes."],
      ["Should NS have IPv6?","Good practice: dual-stack nameservers resolve for v6-preferring resolvers without a fallback step."],
    ],
  },
  "domain-age-checker": {
    title: "Domain age from registry data",
    process: [
      "The checker queries the domain's RDAP record (the modern registry protocol) and extracts the registration event dates: creation, last change, and expiry. Age is computed from creation to today, in years and days.",
    ],
    interpret: [
      "Very young (days): a brand-new registration; treat external links from it with normal caution.",
      "Very old (decades): established registration history; the domain predates most of the modern web.",
      "Created long ago but expiring soon: check renewal status if this is your domain, or expect availability if it's one you're watching.",
    ],
    cli: "curl -s https://rdap.org/domain/example.com | grep -A3 eventAction",
    errors: [
      ["No data returned","Some registries and newer TLDs expose limited RDAP; try the registry's own WHOIS service."],
      ["Creation date changed recently","That happens after domain transfers between registrars, where some re-register the record; the original creation may live in historical WHOIS archives."],
    ],
    who: "Domain buyers vetting auction lots, SEO analysts assessing link sources, and admins auditing their own portfolio.",
    faqs: [
      ["Does domain age help SEO?","Age itself is a minor signal at best; the accumulated history (links, content, reputation) is what matters. Old and empty beats nothing, but not much."],
      ["Why does the age differ from WHOIS sites?","Some sites show the first-seen date in crawl archives; RDAP shows the registry's official creation date."],
      ["Can age be faked?","The registry record can't, but old domains can be 're-aged' by buying expired ones with history. Vet what happened on the domain, not just its birthday."],
    ],
  },
  "whois-lookup": {
    title: "Reading RDAP records",
    process: [
      "RDAP (Registration Data Access Protocol) is WHOIS's structured successor: the same registration data as machine-readable JSON. The lookup queries rdap.org, which routes to the authoritative registry for the domain's TLD, and flattens the response into human fields: registrar, events (created/changed/expires), statuses, and nameservers.",
    ],
    interpret: [
      "clientTransferProhibited: registrar lock, which protects against unauthorized transfers (good).",
      "pendingDelete / redemptionPeriod: the domain is expiring or expired; availability timing depends on the grace stages.",
      "autoRenewPeriod: the registry grace window after expiry, during which the registrant can still renew.",
    ],
    cli: "curl -s https://rdap.org/domain/example.com | python -m json.tool | head -40",
    errors: [
      ["Rate limited","RDAP servers throttle aggressive clients; wait a moment between lookups."],
      ["No registrar entity shown","Some registries redact registrar handles in RDAP for privacy-regulated TLDs."],
    ],
    who: "Domain buyers, security researchers checking registration dates, and admins auditing expiry status across a portfolio.",
    faqs: [
      ["Is RDAP the same as WHOIS?","Same data, modern protocol: structured JSON with standardized fields instead of free-text WHOIS responses. It's the official replacement."],
      ["Why is owner contact info hidden?","GDPR-era privacy: most registries redact registrant contacts. The registrar handle remains visible."],
      ["What does 'transfer lock' mean here?","The clientTransferProhibited status: the domain can't move registrars until unlocked, protecting against hijacking."],
    ],
  },
  "my-ip": {
    title: "What your public IP reveals",
    process: [
      "The page asks ipify for your public IP as seen from the internet, then enriches it: reverse DNS (PTR) resolved through our own DoH engine, ASN and organization from public IP intelligence, and approximate geographic location. Everything renders as the data arrives.",
    ],
    interpret: [
      "The IP itself is exact: it's literally the address your requests originate from.",
      "PTR often shows your ISP or host's naming; for mail servers this should match your announced hostname.",
      "Location is network-registered, not GPS: correct at country level, often city level, never street level.",
    ],
    cli: "curl -s https://api.ipify.org && echo && dig -x $(curl -s https://api.ipify.org) +short",
    errors: [
      ["IP shows a VPN exit address","Correct: that's your public identity while the tunnel is up. Compare with the tunnel off to see the difference."],
      ["IPv6 shown instead of IPv4","Your network prefers v6; both are valid answers depending on which protocol this page's requests used."],
    ],
    who: "Users verifying VPN state, admins checking outbound NAT addresses for firewall allowlists, and anyone configuring mail or API integrations.",
    faqs: [
      ["Why does my IP change?","Dynamic assignment: consumer connections re-lease addresses periodically. Static IPs are a paid upgrade with most ISPs."],
      ["Can two devices share one IP?","Yes: your router NATs the whole network behind one public address."],
      ["Is showing my IP dangerous?","Alone, no: every site you visit sees it. It gains power only when combined with other data."],
    ],
  },
  "ip-lookup": {
    title: "Reading IP intelligence",
    process: [
      "The lookup enriches any address with three independent data layers: PTR (resolved by our DoH engine from the actual reverse zone), registry routing data (ASN and organization), and geolocation estimates (ipwho.is). PTR and ASN are factual DNS/registry records; geolocation is an estimate.",
    ],
    interpret: [
      "ASN + organization: who operates the network the address lives in (an ISP, cloud provider, or enterprise).",
      "PTR: the hostname the address maps back to; often reveals the provider's naming scheme.",
      "City-level geolocation: an estimate mapped from the network's registration, not the device's position.",
    ],
    cli: "whois 8.8.8.8 | grep -E 'OrgName|NetRange' && dig -x 8.8.8.8 +short",
    errors: [
      ["Geolocation shows the wrong city","Expected behavior: geo databases map network registrations. The ASN and PTR are the reliable fields."],
      ["IP shows as 'reserved' or 'private'","Private ranges (192.168.x.x, 10.x.x.x) have no public records by design; look up your public IP instead."],
    ],
    who: "Analysts triaging log entries, mail admins checking sending infrastructure, and the perennial 'whose server is this?' question.",
    faqs: [
      ["Can geolocation find an exact address?","No, and services claiming street-level accuracy are guessing. Registry-level data (ASN, country) is solid; cities are estimates."],
      ["Why does the ASN matter?","It identifies the operating network, which determines reputation context: a residential ASN sending bulk mail looks very different from AWS."],
      ["Do IP details change?","The registry data changes when blocks are reassigned; PTR changes at the operator's whim; geo databases update on their own schedule."],
    ],
  },
};
