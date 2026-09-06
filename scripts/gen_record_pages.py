# -*- coding: utf-8 -*-
"""Deep commercial-grade data for the 12 record-type pillars."""
import json

R = {}

R["a"] = {
 "type": "A", "title": "A Record: What It Is, How It Works, and How to Fix It",
 "description": "A records explained in depth: how IPv4 mapping works, anatomy, TTL strategy, round-robin behavior, common mistakes, and how to check yours live.",
 "intro": "The A record is DNS's most fundamental answer: it maps a hostname to the IPv4 address of the server that hosts it. Every website visit, API call, and ping starts with someone, somewhere, reading an A record.",
 "deepDive": [
  "When a resolver asks your nameserver for example.com, the A record is the reply that says '203.0.113.10'. That single line is the difference between a name that works and a name that goes nowhere. Everything else in your zone, mail routing, security signatures, verification tokens, exists in service of the traffic that the A record directs.",
  "One hostname can hold multiple A records, each pointing at a different address. Resolvers return all of them and clients typically pick the first, a behavior called round-robin DNS. It distributes load across servers, but be clear about what it is not: round-robin has no health checking, so a dead server keeps receiving its share of connections until you remove the record. For real failover you need a load balancer (one A record pointing at the balancer's IP) or a DNS provider with health-checked failover.",
  "TTL strategy matters more with A records than with almost anything else in your zone, because A records change when servers do. A 24-hour TTL is efficient for a stable site, but it converts every migration into a day of split traffic. The professional pattern: drop the TTL to 300 seconds a full day before any planned change, make the change, confirm propagation, then raise the TTL back."
 ],
 "example": "example.com.   3600  IN  A  203.0.113.10\nwww            3600  IN  A  203.0.113.10\napi            300   IN  A  198.51.100.7",
 "anatomy": [
  ["example.com.", "The owner name. The bare apex is often written @ in provider UIs."],
  ["3600", "TTL in seconds: how long resolvers worldwide may cache this answer."],
  ["IN", "The class, short for Internet. Always IN in practice."],
  ["A", "The record type. Exactly one IPv4 address follows."],
  ["203.0.113.10", "The address. Must be a literal IPv4, not a hostname."]
 ],
 "uses": [
  "Pointing your apex and www at your web server or CDN",
  "Pointing subdomains (api, shop, staging) at individual servers",
  "Round-robin distribution across several identical servers",
  "Migration cutover: change one address and traffic follows"
 ],
 "steps": [
  ["Look it up", "Run your domain through the PromptDNS A record lookup. You should see the address you expect, with its TTL."],
  ["Compare apex and www", "Check both names. If only one exists, part of your audience gets errors depending on how they type your domain."],
  ["Verify propagation after changes", "Run the propagation checker: when every resolver returns the new address, the change is fully live."],
  ["Confirm the server answers", "DNS only points; it does not serve. If DNS is right but the site is down, the problem is on the server or firewall."]
 ],
 "mistakes": [
  "Keeping an old server's IP after a migration; lower the TTL first, then cut over, then decommission",
  "Assuming apex and www are the same record; they are two separate entries that both need to exist (or one should redirect to the other)",
  "Using multiple A records as failover; round-robin happily sends traffic to a dead server",
  "Pointing an A record at an address behind a home router with a changing IP; that scenario needs dynamic DNS"
 ],
 "faqs": [
  ["Can an A record point to a domain name?", "No. A records point to literal IPv4 addresses only. If you want name-to-name pointing, that is a CNAME record."],
  ["How many A records can one name have?", "As many as you like, and resolvers return them all. Multiple records mean round-robin distribution, not redundancy."],
  ["Why do I see the old IP after changing my A record?", "Caches. Resolvers keep the previous answer until its TTL expires. Check the propagation checker and flush your local cache."],
  ["Do I need an A record if I use a CDN?", "Yes in some form: either an A record at the CDN's edge IPs, or a CNAME/ALIAS to the CDN hostname. Follow your CDN's DNS instructions."]
 ],
 "related": [["AAAA records (IPv6)", "/aaaa-record/"], ["CNAME vs A records", "/cname-record/"], ["TTL explained", "/what-is-ttl-in-dns/"]]
}

R["aaaa"] = {
 "type": "AAAA", "title": "AAAA Record: IPv6 DNS Explained",
 "description": "AAAA records explained in depth: IPv6 mapping, dual-stack best practice, common v6-only failure modes, and how to verify yours.",
 "intro": "The AAAA record does what the A record does, but for IPv6: it maps a hostname to a 128-bit address. As IPv4 space runs dry, AAAA is how a dual-stack site stays reachable for the growing share of users on IPv6-preferred networks.",
 "deepDive": [
  "IPv6 addresses are eight groups of four hexadecimal digits, and DNS carries them in AAAA records exactly as IPv4 rides in A records. A hostname can have both record types at once, and should: that dual-stack setup lets each client pick the protocol it prefers, usually IPv6 when a route exists.",
  "The failure mode unique to AAAA is asymmetric reachability. If you publish an AAAA record but the server's IPv6 path is broken (no route, firewalled port 443, or a tunnel that intermittently drops), IPv6-capable visitors experience timeouts while everyone else sees a perfect site. The bug hides from whoever tests on IPv4. Always test both protocols after publishing: load the site over a v6 proxy or a lookup tool that shows both record types.",
  "Adoption is past the point of optionality: major mobile carriers run IPv6-preferred networks, and Google's stats have long shown a third or more of client connections arriving over v6. For a new deployment, configuring AAAA from day one is cheaper than retrofitting it."
 ],
 "example": "example.com.  3600  IN  AAAA  2606:2800:220:1:248:1893:25c8:1946",
 "anatomy": [
  ["AAAA", "The record type (read as 'quad-A'). One IPv6 address follows."],
  ["2606:2800:...", "The address: eight colon-separated hexadecimal groups, often compressed with :: for runs of zeros."],
  ["3600", "TTL in seconds, cached by resolvers like any other record."]
 ],
 "uses": [
  "Serving your site over IPv6 alongside IPv4 (dual stack)",
  "IPv6-only infrastructure and services",
  "Meeting requirements of v6-preferred mobile carriers and enterprise networks"
 ],
 "steps": [
  ["Confirm your server has IPv6", "Your host assigns a v6 address; it must be bound to the interface and listening on ports 80/443."],
  ["Open the firewall", "An open v4 rule does nothing for v6. Allow inbound 80/443 on the v6 address explicitly."],
  ["Publish the AAAA record", "Add it beside your A record in the DNS panel, TTL 3600."],
  ["Test both protocols", "Load the site from a v6 connection and run our record lookup filtered to AAAA to confirm what the world sees."]
 ],
 "mistakes": [
  "Publishing AAAA before the server actually answers on v6; every v6 visitor times out",
  "Firewalling only IPv4; v6 traffic silently dropped",
  "Typos in compressed notation; one wrong colon changes the address entirely",
  "Treating v6 as optional while a growing share of mobile traffic prefers it"
 ],
 "faqs": [
  ["Do I need AAAA if I have an A record?", "The site works without it, but IPv6-preferred clients then fall back to IPv4. For new deployments, publish both."],
  ["Can one hostname have A and AAAA records together?", "Yes, and it should. That is exactly what dual-stack means."],
  ["Why does my site work for some users and not others?", "Classic asymmetric IPv6 breakage: the AAAA record exists but the v6 path is dead. Test over both protocols."],
  ["Is AAAA slower than A?", "No. Latency depends on routing, not record type, and v6 paths are often shorter."]
 ],
 "related": [["A records", "/a-record/"], ["Check AAAA records live", "/dns-record-lookup/"]]
}

R["cname"] = {
 "type": "CNAME", "title": "CNAME Record: Canonical Names Explained",
 "description": "CNAME records explained in depth: aliasing, the apex restriction, flattening, chaining risks, and how to audit your aliases.",
 "intro": "A CNAME record aliases one hostname to another. Instead of saying 'www lives at this IP', it says 'www is whatever example.com is', so one change at the target updates every alias that follows it.",
 "deepDive": [
  "CNAME stands for Canonical Name, and the mechanics are exactly that: the alias is not an answer, it is a pointer to the canonical (real) name. When a resolver chasing www hits the CNAME, it restarts the lookup against the target and returns that answer, with a note that it arrived via alias. The client never notices unless it inspects the chain.",
  "The famous restriction: a CNAME cannot coexist with other records at the same name, which bans it from the zone apex, because the apex must carry SOA and NS records to be a zone at all. Providers paper over this with ALIAS/ANAME pseudo-records or CNAME flattening, where the provider resolves the target server-side and publishes the resulting A record. Functionally similar, but the mechanisms differ enough to matter during debugging.",
  "CNAME chains (alias to alias to target) multiply lookup latency and failure surface, and some resolvers cap the chase. Keep chains one hop deep, point at stable targets, and remember that a CNAME imports the target's availability: if the target stops resolving, every alias under it breaks with it."
 ],
 "example": "www.example.com.  3600  IN  CNAME  example.com.\ndocs                3600  IN  CNAME  yourname.getgridea.pages.hosted.",
 "anatomy": [
  ["www.example.com.", "The alias: the name users actually type or that services verify."],
  ["CNAME", "The record type. A canonical hostname follows, never an IP."],
  ["example.com.", "The target. The alias inherits whatever A/AAAA answers this name has."]
 ],
 "uses": [
  "Pointing subdomains at hosted services: CDNs, GitHub Pages, helpdesks, landing page hosts",
  "Keeping www automatically in sync with the apex",
  "Managing many vanity hostnames that must always match one moving target"
 ],
 "steps": [
  ["Identify the target", "Your service's DNS setup page gives you the exact hostname to point at. Copy it verbatim."],
  ["Create the CNAME", "In your DNS panel, host 'www' (or the subdomain), type CNAME, value the target hostname."],
  ["Watch propagation", "CNAME changes respect TTL like everything else; confirm with the propagation checker."],
  ["Verify the full chain", "The lookup tool shows the alias resolving through to a final address; if the chain dead-ends, the target moved."]
 ],
 "mistakes": [
  "Placing a CNAME at the apex; it is technically illegal and most providers reject it (use ALIAS/flattening)",
  "Pointing a CNAME at an IP address; that is an A record's job",
  "Long alias chains that add latency and break when an intermediate hop moves",
  "Forgetting that a CNAME at a name blocks all other record types at that same name, including TXT verification records on that subdomain"
 ],
 "faqs": [
  ["Why can't I use CNAME at the root domain?", "The apex must hold SOA and NS records, and CNAME cannot coexist with any other record type. Use ALIAS/ANAME or a provider that flattens."],
  ["Does a CNAME redirect traffic?", "No. It aliases DNS resolution, not HTTP. Visitors still see the original hostname; changing the visible URL is an HTTP redirect."],
  ["Can a CNAME point to another domain I don't own?", "Yes, and that is exactly how SaaS DNS verification works. The trade-off is you inherit their availability."],
  ["What is CNAME flattening?", "A provider feature that resolves the CNAME target server-side and answers with plain A records, making CNAME-style pointing legal at the apex."]
 ],
 "related": [["ALIAS/ANAME records", "/alias-record/"], ["CNAME flattening explained", "/cname-flattening/"], ["A records", "/a-record/"]]
}

R["txt"] = {
 "type": "TXT", "title": "TXT Record: The Workhorse of Modern DNS",
 "description": "TXT records explained in depth: the 255-character rule, SPF/DKIM/DMARC carriage, domain verification, and the mistakes that break email.",
 "intro": "TXT records attach arbitrary text to a DNS name, which sounds trivial until you realize they carry the entire email-authentication stack, domain-ownership proofs for hundreds of services, and assorted machine-to-machine config.",
 "deepDive": [
  "Structurally, a TXT record is one or more quoted strings, each capped at 255 characters. Longer payloads, like DKIM public keys, are split into multiple strings that receivers concatenate in order. Providers usually handle the splitting; hand-editing zone files is where quoting bugs creep in.",
  "The workhorse role: SPF lives at the apex as v=spf1..., DKIM public keys live at selector._domainkey subdomains, DMARC policy lives at _dmarc, and service verifications use their own prefixed names like _google-site-verify or _amazonses. This namespacing is why one domain can carry dozens of TXT records without collision, and it also means deleting a 'random string' record during cleanup can silently break email or a service integration months later.",
  "SPF has a strict one-record rule: a name with two v=spf1 TXT strings evaluates to permerror, which receivers treat as no SPF at all. If two teams each added 'their' SPF, both are broken. The fix is always to merge mechanisms into one record, then re-check the 10-lookup budget."
 ],
 "example": "example.com.              IN  TXT  \"v=spf1 include:_spf.google.com include:sendgrid.net ~all\"\n_google-site-verify.  3600  IN  TXT  \"verification-token-here\"\ndefault._domainkey.   3600  IN  TXT  \"v=DKIM1; k=rsa; p=MIIBIjANBgkq...\"",
 "anatomy": [
  ["TXT", "The record type. One or more quoted strings follow."],
  ["\"v=spf1 ...\"", "The payload. v= prefixes mark machine-readable dialects: SPF, DKIM, DMARC."],
  ["_dmarc / selector._domainkey", "Prefixed subdomains namespace TXT records per protocol or service."]
 ],
 "uses": [
  "SPF, DKIM public keys, and DMARC policy: the email-authentication stack",
  "Domain ownership verification for Google, Microsoft, AWS, Stripe, and hundreds more",
  "Machine-readable config: site verification, security policies like MTA-STS and TLS-RPT pointers"
 ],
 "steps": [
  ["Find what exists", "A TXT lookup on your domain lists every record; the v= prefixes tell you which protocol each serves."],
  ["Check for duplicates", "One v=spf1 per name, always. Two means both are broken."],
  ["Mind the 255 rule", "Long values must split into quoted strings; our tools display the joined value receivers see."],
  ["Verify before deleting", "Never remove an unexplained TXT record; it is probably a verification or authentication key something depends on."]
 ],
 "mistakes": [
  "Two SPF records on one name: permerror, receivers ignore SPF entirely",
  "Unquoted or mis-escaped strings that break parsing silently",
  "Forgetting string splitting for keys longer than 255 characters",
  "Cleanup sprees that delete verification records nobody could explain"
 ],
 "faqs": [
  ["How long can a TXT record be?", "Each quoted string is capped at 255 characters, but a record can hold multiple strings that get concatenated, which is how long DKIM keys fit."],
  ["Can I have multiple TXT records on one name?", "Yes for different purposes, no for SPF: exactly one v=spf1 record per name is valid."],
  ["Why did adding SPF break my email?", "Most commonly a second v=spf1 record appeared, or the new include pushed past the 10-lookup limit. The SPF checker pinpoints both."],
  ["Do TXT records affect website speed?", "No. They are only fetched by the systems that need them: mail servers and verification services."]
 ],
 "related": [["SPF records", "/spf-record/"], ["DKIM explained", "/dkim/"], ["DMARC record syntax", "/dmarc-record/"]]
}

R["ns"] = {
 "type": "NS", "title": "NS Record: Nameservers and Delegation",
 "description": "NS records explained in depth: registry vs zone NS, lame delegation, transfer mechanics, and how to audit who really serves your DNS.",
 "intro": "NS records declare which nameservers are authoritative for a name. They are the load-bearing wall of delegation: get them wrong and your entire zone, website and email included, stops answering.",
 "deepDive": [
  "There are two places NS records live, and confusing them causes most delegation incidents. The parent zone (.com registry) holds the delegation NS set you configure through your registrar. Your own zone also publishes NS records at its apex. When the two sets disagree, part of the internet asks servers that no longer hold your data, a state called lame delegation that shows up as intermittent SERVFAIL for a subset of users.",
  "Changing DNS providers is therefore an ordered procedure, not a toggle: add the zone at the new provider first, verify it answers identically, then change the delegation at the registrar, then wait out the full TTL window (up to 48 hours, because registry delegations cache) before decommissioning the old servers. Reversing any of those steps creates an interval where some resolvers have nowhere valid to ask.",
  "NS records also delegate subdomains. Pointing dev.example.com at a different provider's nameservers lets teams run their own zone without touching yours. The same correctness rules apply: the parent (you) must publish delegation matching what the child zone serves, glue records included when the child's nameservers live inside the delegated name."
 ],
 "example": "example.com.  86400  IN  NS  ns1.cloudflare.com.\nexample.com.  86400  IN  NS  ns2.cloudflare.com.",
 "anatomy": [
  ["NS", "The record type: an authoritative nameserver hostname follows."],
  ["86400", "Delegation TTLs are long by design; registry-side caching makes NS changes slow."],
  ["ns1.cloudflare.com.", "The nameserver. It must itself resolve to an A/AAAA record (glue, when hosted under the delegated name)."]
 ],
 "uses": [
  "Delegating your domain to its DNS host (Cloudflare, Route 53, registrar DNS)",
  "Delegating subdomains to other providers or teams",
  "Verifying that a registrar transfer or provider switch actually completed"
 ],
 "steps": [
  ["Look up the delegation", "An NS query on your domain shows what resolvers consider authoritative."],
  ["Compare with the zone", "Your DNS provider's panel lists the NS set it publishes. Both sets must match exactly."],
  ["Test the servers directly", "Querying each nameserver for your apex A record proves each one answers, not just the first."],
  ["After any switch, wait out the window", "Keep the old provider answering for 48 hours before cancelling it."]
 ],
 "mistakes": [
  "Changing NS records inside the old provider's panel and expecting the world to follow; the registry only hears your registrar",
  "Mismatched sets between registry and zone, producing lame delegation and intermittent failures",
  "Cancelling the old DNS plan the day after a switch, before long delegation TTLs expire",
  "Four or more nameservers 'for reliability' without monitoring: slow or dead ones hurt more than fewer fast ones"
 ],
 "faqs": [
  ["Where do I change my nameservers?", "At your registrar. The registrar tells the registry, and the registry's delegation is what resolvers follow."],
  ["Why do NS changes take up to 48 hours?", "Registry delegations cache with long TTLs, independent of your zone's own records."],
  ["What is lame delegation?", "The parent points at nameservers that don't authoritatively answer for your zone. Users see random SERVFAIL."],
  ["Do more nameservers mean more reliability?", "Only if they are all healthy. A dead nameserver in the set adds latency and failure cases."]
 ],
 "related": [["How DNS resolution works", "/how-dns-works/"], ["SOA records (zone metadata)", "/soa-record/"]]
}

R["soa"] = {
 "type": "SOA", "title": "SOA Record: Start of Authority Explained",
 "description": "SOA records explained in depth: serial number discipline, refresh/retry/expire timers, negative caching, and transfer debugging.",
 "intro": "The SOA record is your zone's ID card and maintenance schedule in one: who runs it, its version number, and the timers secondaries use to stay synchronized. Every zone has exactly one, and it encodes more operational meaning than any other record.",
 "deepDive": [
  "Two fields identify the zone: MNAME, the primary master nameserver, and RNAME, the responsible person's email written with a dot where the @ belongs. Nobody mails RNAME anymore, but tooling reads it, and it dates forgotten zones fascinatingly.",
  "The serial number is the change counter. Secondaries compare serials to detect changes; a serial that fails to increase means your 'saved' edit propagates to exactly nowhere. The conventional format YYYYMMDDnn (date plus two-digit revision) keeps numbers monotonic and self-documenting. If a serial goes backwards, the standard recovery is jumping far forward, since secondaries only move up.",
  "The four timers orchestrate secondary synchronization: refresh (how often secondaries poll for a new serial), retry (poll cadence after failure), expire (when secondaries give up and stop serving the zone), and minimum (the negative-caching TTL, how long resolvers may remember that a name doesn't exist). Defaults vary by software, and they are usually fine; they matter when zones are large, transfers are slow, or you are debugging why a secondary went rogue."
 ],
 "example": "example.com.  3600  IN  SOA  ns1.example.com. hostmaster.example.com. (\n                  2026082201 ; serial (YYYYMMDDnn)\n                  7200       ; refresh\n                  3600       ; retry\n                  1209600    ; expire\n                  3600 )     ; negative-cache minimum",
 "anatomy": [
  ["MNAME", "The primary master nameserver for the zone."],
  ["RNAME", "Admin contact, first dot read as @."],
  ["serial", "Version counter; must increase on every change or secondaries ignore the update."],
  ["refresh", "Seconds between secondary polls for a new serial."],
  ["retry / expire", "Retry cadence after a failed refresh, and when a secondary drops the zone entirely."],
  ["minimum", "Negative-caching TTL for NXDOMAIN answers."]
 ],
 "uses": [
  "Zone transfer synchronization between primary and secondary servers",
  "Debugging stale secondaries (the serial did not increase)",
  "Tuning how long 'name does not exist' answers cache"
 ],
 "steps": [
  ["Read your SOA", "An SOA lookup shows the current serial and timers; providers auto-manage serials on panel edits."],
  ["After any change, watch the serial", "It must increase. If you edit zone files by hand, this is the one field you must never forget."],
  ["Check secondaries serve the same serial", "A mismatch means a transfer problem, not a caching problem."],
  ["Use negative caching deliberately", "A 3600 minimum softens load from non-existent names without hiding new subdomains for long."]
 ],
 "mistakes": [
  "Hand edits that forget to bump the serial, silently blocking replication",
  "Writing RNAME with an @ instead of a dot",
  "Expecting registrar-level changes to respect zone timers; delegation TTLs run on their own clock",
  "Aggressively low refresh values hammering the primary for no benefit"
 ],
 "faqs": [
  ["What happens if the SOA serial doesn't increase?", "Secondaries conclude nothing changed and keep serving the old zone. Your edit exists only on the primary."],
  ["What is negative caching?", "Resolvers remembering NXDOMAIN answers for 'minimum' seconds, so repeated lookups of dead names don't hit your servers."],
  ["Who manages the serial?", "DNS panels increment it automatically. Only hand-maintained zone files put the burden on you."],
  ["Can a zone have two SOA records?", "No. Exactly one SOA at the apex is mandatory and standard."]
 ],
 "related": [["NS records", "/ns-record/"], ["DNS propagation explained", "/dns-propagation/"]]
}

R["ptr"] = {
 "type": "PTR", "title": "PTR Record: Reverse DNS Explained",
 "description": "PTR records explained in depth: the in-addr.arpa zone, who controls reverse DNS, forward-confirmed matching, and the email reputation connection.",
 "intro": "A PTR record answers the reverse question: given an IP, which hostname? Forward DNS maps names to addresses; PTR maps addresses back to names, in special reverse zones that most people never see until email starts bouncing.",
 "deepDive": [
  "Reverse DNS lives in the in-addr.arpa zone (ip6.arpa for IPv6), built by reversing the IP's octets. The address 203.0.113.10 becomes 10.113.0.203.in-addr.arpa, and its PTR record names the host. Because reverse zones are delegated alongside the IP space, control sits with whoever owns the address block: your hosting provider or ISP, not your domain registrar.",
  "That ownership detail is the number-one confusion. You cannot create a PTR record for 198.51.100.5 in your domain's DNS panel; there is no such zone there. Cloud providers expose reverse-DNS settings on the instance or reserved-IP level, and dedicated-server hosts often require a matching forward record before accepting the change.",
  "Mail is where PTR earns its reputation. Receiving servers run forward-confirmed reverse DNS: resolve the connecting IP's PTR, then resolve that hostname forward, and require the original IP in the answer. A missing or mismatched PTR is treated as a strong spam signal by most receivers, and several major providers reject outright. For any server that sends mail, set the PTR to the HELO hostname and make its A record point back to the same address."
 ],
 "example": "10.113.0.203.in-addr.arpa.  3600  IN  PTR  mail.example.com.",
 "anatomy": [
  ["in-addr.arpa", "The reverse zone: the IP's octets reversed, plus this suffix."],
  ["PTR", "The record type: a hostname follows."],
  ["mail.example.com.", "The name the IP resolves back to; ideally one that resolves forward to the same IP."]
 ],
 "uses": [
  "Email deliverability: sending IPs need forward-confirmed reverse DNS",
  "Readable logs and abuse reports: IPs become names",
  "Network diagnostics and identifying who operates an address"
 ],
 "steps": [
  ["Check the current PTR", "Our IP lookup resolves reverse DNS for any address, including yours."],
  ["Set it at the IP owner", "In your cloud provider's panel (EC2 Elastic IP, VPS settings) or via your host's support."],
  ["Point the hostname forward", "The PTR target's A record must resolve back to the same IP, or matching fails."],
  ["Match HELO", "Configure your mail server to announce the same hostname in HELO/EHLO."]
 ],
 "mistakes": [
  "Trying to set PTR in the domain's DNS panel; the reverse zone belongs to the IP owner",
  "PTR pointing at a generic provider hostname that doesn't forward-resolve back",
  "HELO announcing a name that doesn't match the PTR",
  "Ignoring PTR until mail starts landing in spam or bouncing with policy errors"
 ],
 "faqs": [
  ["Who controls my PTR record?", "Whoever owns the IP space: your hosting provider or ISP. Domain registrars have no say."],
  ["Why does reverse DNS matter for email?", "Receivers verify the connecting IP has a matching forward-confirmed PTR; absence is scored as spammy."],
  ["Can one IP have multiple PTR records?", "Technically possible, practically harmful: unpredictable which answer a receiver gets. Configure exactly one."],
  ["How do I check reverse DNS?", "The PromptDNS IP lookup resolves the PTR for any address, plus ASN and network owner."]
 ],
 "related": [["MX records (receiving mail)", "/mx-record/"], ["IP Lookup tool", "/ip-lookup/"]]
}

R["srv"] = {
 "type": "SRV", "title": "SRV Record: Locating Services with DNS",
 "description": "SRV records explained in depth: the _service._proto naming scheme, priority and weight mechanics, and real deployments from SIP to Minecraft.",
 "intro": "SRV records answer 'where is this service?' rather than 'where is this server?'. They carry priority, weight, and port alongside the target host, letting clients discover and load-balance a specific protocol on your domain.",
 "deepDive": [
  "The owner name is a strict two-part prefix: underscored service, underscored protocol, then your domain. _sip._tcp.example.com says 'the SIP service over TCP on this domain'. The convention looks alien next to plain hostnames, but it is what every SRV-aware client searches for, character for character.",
  "Priority and weight work together. Priority is a hard order: clients try lower numbers first, exactly like MX. Among targets of equal priority, weight distributes connections proportionally, a 60/40 split for two servers both at priority 10. The port rides in the record itself, so the service can live on a non-standard port without clients hardcoding anything.",
  "In practice you meet SRV in three worlds: VoIP and XMPP, where handsets and clients discover the server from the domain alone; Active Directory, where domain-joined machines locate Kerberos and LDAP via _kerberos._tcp and friends; and gaming, where a single SRV lets players connect with play.example.com while the real server sits on a hidden host and port. The target must resolve via A/AAAA; pointing SRV at a CNAME is technically tolerated but pointless."
 ],
 "example": "_sip._tcp.example.com.   3600  IN  SRV  10 60 5060 sip1.example.com.\n_sip._tcp.example.com.   3600  IN  SRV  10 40 5060 sip2.example.com.\n_minecraft._tcp.example. 3600  IN  SRV  0  5 25565 play.example.com.",
 "anatomy": [
  ["_sip._tcp", "Service and protocol prefix; both underscored, both mandatory."],
  ["priority", "Lower tried first; equal priorities share traffic by weight."],
  ["weight", "Relative share among same-priority targets (0-65535)."],
  ["5060", "The port the service listens on."],
  ["sip1.example.com.", "Target hostname; must have an A/AAAA record."]
 ],
 "uses": [
  "SIP/VoIP provisioning and XMPP server discovery",
  "Active Directory service location",
  "Game server aliases (Minecraft and friends)",
  "Any client that supports DNS-based service discovery"
 ],
 "steps": [
  ["Confirm the prefix", "Get the exact _service._proto string from your software's docs; one wrong character makes it invisible."],
  ["Create the record", "Host field gets the prefix, then priority, weight, port, and target in your panel's SRV fields."],
  ["Resolve the target", "Verify the target hostname has an A record; SRV does not chase CNAME chains helpfully."],
  ["Test with a client", "Or run an SRV lookup here to see exactly what clients discover."]
 ],
 "mistakes": [
  "Missing the leading underscores in the prefix",
  "Target without an A/AAAA record",
  "Confusing weight with priority when the goal is ordering, not distribution",
  "Expecting browsers to use SRV; they famously do not"
 ],
 "faqs": [
  ["Do browsers use SRV records?", "No. Mainstream browsers skip SRV for websites; it exists for protocols and clients built to query it."],
  ["How do priority and weight differ?", "Priority orders groups absolutely; weight splits load within one priority level."],
  ["Why underscores in the name?", "They prevent collisions with real hostnames a human might create."],
  ["Can SRV point to a different domain?", "Yes. Cross-domain targets are common for hosted services."]
 ],
 "related": [["MX records: mail's specialized cousin", "/mx-record/"], ["Check SRV records", "/dns-record-lookup/"]]
}

R["caa"] = {
 "type": "CAA", "title": "CAA Record: Controlling Certificate Issuance",
 "description": "CAA records explained in depth: issue vs issuewild, iodef incident reporting, Let's Encrypt and vendor domains, and rollout mistakes.",
 "intro": "A CAA record tells certificate authorities which of them are allowed to issue TLS certificates for your domain. It is a one-line record that closes the door on misissuance by every CA you don't explicitly trust.",
 "deepDive": [
  "The mechanics are cooperative but effective: before issuing, a CA checks your CAA set, and policy forbids issuing unless one of its issuance domains appears. Since 2017 the check is mandatory across the industry, so a tight CAA set genuinely constrains who can mint certificates for your names.",
  "Two tags do the permitting. issue authorizes normal certificates and, unless overridden, wildcards too; issuewild independently governs wildcard issuance. Point them at the CA's documented issuance domain, not the marketing website: Let's Encrypt is letsencrypt.org, DigiCert is digicert.com, and each vendor documents the exact string. A third tag, iodef, is optional reporting: give a mailto or http endpoint and participating CAs will tell you when someone attempts an issuance your policy forbids, which is exactly the signal you want.",
  "CAA inherits down your tree: a record at the apex applies to every subdomain unless a closer name overrides it. That enables per-team policies (a separate CA for *.dev) but also surprises: tightening the apex while a subdomain relies on another CA breaks its renewals. Roll out by listing every CA currently issuing for you first, confirming renewals, then trimming."
 ],
 "example": "example.com.  3600  IN  CAA  0 issue \"letsencrypt.org\"\nexample.com.  3600  IN  CAA  0 issuewild \";\"\nexample.com.  3600  IN  CAA  0 iodef \"mailto:security@example.com\"",
 "anatomy": [
  ["0", "The flags byte; 128 marks the record as critical, which non-understanding CAs must obey by refusing."],
  ["issue", "Tag permitting issuance by the named CA."],
  ["issuewild", "Wildcard-specific permission; absent, it inherits issue."],
  ["\"letsencrypt.org\"", "The CA's issuance domain, exactly as its documentation specifies."],
  ["iodef", "Where violation attempts get reported."]
 ],
 "uses": [
  "Locking issuance to your actual CA or CAs",
  "Separate wildcard policy from name policy",
  "Getting alerted on out-of-policy issuance attempts",
  "Certificate-control compliance requirements"
 ],
 "steps": [
  ["Inventory your CAs", "Check current certificates (crt.sh or your inventory) for who issues for your domain today."],
  ["Publish permissive CAA first", "One issue record per CA in use, so renewals continue uninterrupted."],
  ["Add iodef reporting", "A security mailbox that someone actually monitors."],
  ["Tighten gradually", "Remove CAs you no longer use, verify with the record lookup, and watch renewals for a full cycle."]
 ],
 "mistakes": [
  "Using the CA's brand domain instead of the documented issuance domain",
  "Forgetting issuewild inherits from issue and accidentally permitting or blocking wildcards",
  "Tightening the apex while a subdomain's certificates come from another CA",
  "Syntax slips (missing quotes, wrong tag) invalidating the whole set"
 ],
 "faqs": [
  ["What happens with no CAA records?", "Any public CA may issue for your domain. CAA is the opt-in restriction layer."],
  ["Does CAA stop attackers issuing fraudulently?", "It constrains compliant CAs. Combined with monitoring (crt.sh, Cert Spotter) it shrinks the misissuance surface."],
  ["Can I have CAA for multiple CAs?", "Yes, one issue record per CA, all treated as permitted."],
  ["Why did my renewal fail after adding CAA?", "The issuing CA's domain is missing or misspelled in your set. Check its docs for the exact string."]
 ],
 "related": [["TXT records", "/txt-record/"], ["Check CAA records", "/dns-record-lookup/"]]
}

R["alias"] = {
 "type": "ALIAS/ANAME", "title": "ALIAS/ANAME Records: CNAME Behavior at the Apex",
 "description": "ALIAS/ANAME records explained in depth: the apex problem, provider implementations, flattening modes, and when not to use them.",
 "intro": "You cannot put a CNAME at your zone's apex, but nearly every modern host wants exactly that. ALIAS and ANAME records are the industry's answer: provider-resolved pseudo-records that give apex domains CNAME ergonomics while answering as legal A records.",
 "deepDive": [
  "The restriction they work around is old and absolute: the apex must carry SOA and NS records, and CNAME cannot share a name with anything. So ALIAS/ANAME moves the resolution server-side. Your provider periodically (or per-query) resolves the target hostname and publishes the resulting addresses as ordinary A/AAAA records. The internet sees a perfectly legal apex; you get follow-the-target behavior.",
  "Implementations differ in a way that matters operationally. Flatten-on-query resolves at request time: always fresh, slightly slower, dependent on the provider's resolvers. Flatten-on-publish resolves when you save and caches for the TTL: faster, but stale if the target changes quickly. Cloudflare flattens automatically for any apex CNAME; DNSimple and Route 53 offer explicit ALIAS records; some hosts implement nothing. The feature belongs to the DNS host, which means the zone must live where you configure it.",
  "Short TTLs are the honest companion to ALIAS: the synthesized answer is only as current as your refresh interval, so a 300-second TTL is typical. And remember what ALIAS cannot carry: it resolves to addresses, so anything the target publishes besides A/AAAA (like its own TXT-based verification) does not teleport to your apex."
 ],
 "example": "example.com.  300  IN  ALIAS  target-service.net.\n; Cloudflare style: create a normal CNAME at the apex; flattening is automatic.",
 "anatomy": [
  ["ALIAS / ANAME", "Provider-specific pseudo-types, not standards-track. Portable meaning, non-portable mechanics."],
  ["target-service.net.", "The origin hostname the provider resolves for you."],
  ["300", "Short TTL so the synthesized A answers track a moving target."]
 ],
 "uses": [
  "Pointing the apex at CDNs, load balancers, and PaaS hosts that hand you a hostname",
  "Escaping hardcoded origin IPs that break when the provider rotates them"
 ],
 "steps": [
  ["Confirm provider support", "Look for ALIAS, ANAME, or apex CNAME flattening in your DNS host's docs."],
  ["Get the target hostname", "From your CDN or platform's domain setup instructions."],
  ["Create the record at the apex", "Using the provider's ALIAS/ANAME flow, or a CNAME if it flattens automatically."],
  ["Verify what the world sees", "An A lookup on your apex should return the provider-synthesized addresses."]
 ],
 "mistakes": [
  "Expecting ALIAS to work after moving DNS elsewhere; it is a host feature, not a record you can export",
  "Long TTLs defeating the freshness the record exists to provide",
  "Assuming TXT verification on the target transfers to your apex; it does not",
  "Confusing ALIAS with HTTP redirects; this is resolution-level, URLs do not change"
 ],
 "faqs": [
  ["Is ALIAS a real DNS record type?", "No. It is synthesized by your provider into A/AAAA answers. That is why portability is limited."],
  ["What is the difference from CNAME flattening?", "Mostly naming and where resolution happens (on publish vs on query). Behavior at the apex is equivalent."],
  ["Why is my ALIAS TTL low?", "The synthesized answers must track the target; caching them long defeats the purpose."],
  ["Can I use ALIAS for www too?", "You can, but www has no SOA/NS conflict, so a plain CNAME is the standard choice there."]
 ],
 "related": [["CNAME records", "/cname-record/"], ["CNAME flattening explained", "/cname-flattening/"]]
}

R["ds"] = {
 "type": "DS", "title": "DS Record: The DNSSEC Chain of Trust",
 "description": "DS records explained in depth: key tags, algorithms, digests, activation and rollover procedure, and the SERVFAIL outage class they cause.",
 "intro": "The DS record is the link in DNSSEC's chain of trust: published in the parent zone, it vouches for the child zone's key so validators can verify every signed answer below. It is also the record whose stale copy can take an entire domain offline with SERVFAIL.",
 "deepDive": [
  "DNSSEC works by chains. Your zone signs its records with private keys and publishes the public halves as DNSKEY records. But a key you publish yourself proves nothing; something the verifier already trusts must vouch for it. That voucher is the DS record: a digest of your key-signing key, placed one level up. Validating resolvers walk root to TLD to your domain, checking each link's signature against the DS above it. Any break, and the safe response is to fail: not 'wrong answer' but 'no answer', domain-wide.",
  "That severity explains the operational fear around DS. The classic outage: a provider rotates its DNSSEC keys, your registrar still publishes the DS of the old key, and every validating resolver on earth returns SERVFAIL for your domain. The fix discipline is strict ordering: when rotating, publish the DS for the new key first, let it propagate, then retire the old key. When disabling DNSSEC, delete the DS and wait before dropping signatures.",
  "The record itself packs four values: the key tag (a shorthand for which DNSKEY), the algorithm number (8 RSA/SHA-256, 13 ECDSA P-256, 15 Ed25519), the digest type (2 SHA-256), and the digest itself. Providers and registrars that integrate well surface a copy-paste tuple; when copying by hand, whitespace or truncation in the digest is the usual killer."
 ],
 "example": "example.com.  3600  IN  DS  2371 13 2 1F987CC6583B6E1FD8C7F2D6BCB6A9C4C6B6A9C4C6B6A9C4C6B6A9C4",
 "anatomy": [
  ["2371", "Key tag identifying which DNSKEY this digest matches."],
  ["13", "Algorithm: 8 RSA/SHA-256, 13 ECDSA P-256, 15 Ed25519."],
  ["2", "Digest type; 2 is SHA-256."],
  ["(hash)", "The digest of the child's key. One bad character breaks validation."]
 ],
 "uses": [
  "Activating DNSSEC at your registrar once your zone signs",
  "Key rollovers, in the safe order",
  "Root-causing domain-wide SERVFAIL incidents"
 ],
 "steps": [
  ["Enable signing at your DNS host", "Cloudflare and major hosts toggle DNSSEC and display the DS tuple to publish."],
  ["Publish the DS at the registrar", "Copy all four fields exactly; this is the chain link."],
  ["Wait, then validate", "After propagation, a DS lookup should return your record, and validators (Quad9, Cloudflare) should resolve your domain normally."],
  ["Rotate in order", "New key's DS first, propagate, then remove the old key."]
 ],
 "mistakes": [
  "Rotating keys without updating the DS: domain-wide SERVFAIL",
  "Truncated or whitespace-corrupted digests when copying manually",
  "Deleting the DS while signatures still exist, or vice versa",
  "Assuming DNSSEC validation failures show a nice error; users see timeouts and SERVFAIL"
 ],
 "faqs": [
  ["What is a DS record for?", "It links a child zone's DNSSEC key to the parent zone, letting validators build an unbroken chain of trust from the root."],
  ["Where is the DS record published?", "In the parent zone, configured through your registrar."],
  ["Why did my whole site go down after a DNSSEC change?", "A broken chain, usually a stale DS after key rotation. Validators must refuse, so the domain SERVFAILs."],
  ["Is DNSSEC worth enabling?", "It defeats cache-poisoning and answer tampering. With a well-integrated host and registrar it is a toggle; the danger zone is manual key handling."]
 ],
 "related": [["DNSKEY records", "/dnskey-record/"], ["What is DNSSEC", "/what-is-dnssec/"]]
}

R["dnskey"] = {
 "type": "DNSKEY", "title": "DNSKEY Records: DNSSEC's Public Keys",
 "description": "DNSKEY records explained in depth: flags and the KSK/ZSK split, algorithm choices, rollover strategies, and validator expectations.",
 "intro": "DNSKEY records publish the public halves of your zone's DNSSEC signing keys. Validators fetch them, match the key-signing key against the parent's DS record, and use the zone-signing key to verify the signatures on everything else.",
 "deepDive": [
  "Two roles, two keys, in any properly run zone. The key-signing key (KSK, flags 257) exists to sign the DNSKEY record set itself and is the key whose digest appears in the parent's DS. The zone-signing key (ZSK, flags 256) signs the everyday records. Splitting duties limits how often the operationally-risky KSK changes, while the ZSK can rotate freely.",
  "Algorithms are a live compatibility question. RSA/SHA-256 (8) is the universal default; ECDSA P-256 (13) delivers equivalent security with far smaller records, which matters because big DNSSEC responses need to fit in packets; Ed25519 (15) is modern but still unevenly validated. Whatever you choose, the algorithm here must match what the DS record in the parent declares.",
  "Rollover is where DNSKEY knowledge pays for itself. The two standard methods are pre-publish (introduce the new key, wait, switch signing, wait, retire the old) and double-signing (sign with both during the transition). Both exist to keep the chain unbroken for resolvers at every point in the TTL window; skipping the waits is how zones SERVFAIL themselves."
 ],
 "example": "example.com.  3600  IN  DNSKEY  257 3 13 ( base64-KSK... )\nexample.com.  3600  IN  DNSKEY  256 3 13 ( base64-ZSK... )",
 "anatomy": [
  ["257 / 256", "Flags: 257 marks the KSK (matches the parent's DS), 256 the ZSK."],
  ["3", "Protocol field; fixed at 3."],
  ["13", "Algorithm: 8 RSA/SHA-256, 13 ECDSA P-256, 15 Ed25519."],
  ["(key)", "The base64 public key material."]
 ],
 "uses": [
  "Completing the DNSSEC validation chain (KSK to DS, ZSK to records)",
  "Key rollovers without breaking validators",
  "Auditing that the registrar-published keys match the zone's"
 ],
 "steps": [
  ["Inspect the key set", "A DNSKEY lookup on your domain shows flags and algorithms at a glance."],
  ["Match KSK to DS", "The 257-flagged key's tag should correspond to the DS at the parent; mismatch means a broken chain."],
  ["Prefer algorithm 13", "Unless you have legacy constraints, ECDSA keeps responses small and validation fast."],
  ["Rotate with waits", "Follow pre-publish or double-sign timing; the waits are the safety."]
 ],
 "mistakes": [
  "Retiring a KSK whose digest the parent still references",
  "Swapping flags so the DS-matching key signs records instead",
  "1024-bit RSA keys: weak and inflated; prefer algorithm 13 or 15",
  "Rollovers without waiting out TTLs at each phase"
 ],
 "faqs": [
  ["What is the difference between KSK and ZSK?", "The KSK signs the key set and matches the parent's DS; the ZSK signs the zone's records. Separation limits risky KSK changes."],
  ["Do I ever edit DNSKEY records by hand?", "Almost never. Signing software and DNS providers manage them; your job is publishing the DS and not breaking rotation order."],
  ["Which algorithm should I use?", "ECDSA P-256 (13) for new deployments: strong, compact, widely validated."],
  ["Can DNSSEC work without a DS at the parent?", "As an island that validators won't trust. The chain from the root is the point."]
 ],
 "related": [["DS records", "/ds-record/"], ["What is DNSSEC", "/what-is-dnssec/"]]
}

import os
for slug, d in R.items():
    t = d["type"]
    d["faqs"] = d["faqs"] + [
      (f"How do I check {t} records after changing them?", "Run the record lookup filtered to the type just changed: it shows live values straight from a public resolver. Then confirm worldwide agreement with the propagation checker."),
      (f"What TTL should {t} records use?", "3600 seconds (one hour) is the sensible default. Drop to 300 a full day before planned changes so cutover is quick, then raise it back afterwards."),
    ]
    page = "---\nimport RecordTypeTemplate from '../components/RecordTypeTemplate.astro';\nconst data = " + json.dumps(d, ensure_ascii=False, indent=1) + ";\n---\n<RecordTypeTemplate data={data} />\n"
    open(f'src/pages/{slug}-record.astro', 'w', encoding='utf-8').write(page)
    print('wrote', f'src/pages/{slug}-record.astro')
