# -*- coding: utf-8 -*-
"""Phase 3 batch 3: remaining topical map pages - security, ops, troubleshooting, deliverability depth."""
import json

def build_page(slug, title, desc, h1, intro, body, faqs, related):
    faq_const = ("const faqSchema = " + json.dumps(
        {'@context': 'https://schema.org', '@type': 'FAQPage',
         'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]},
        ensure_ascii=False, indent=1) + "\n") if faqs else ""
    faq_line = "  schema={[faqSchema]}\n" if faqs else ""
    sec = ""
    for h2, html in body:
        sec += '      <h2 class="font-display mt-10 text-xl font-semibold text-ink">' + h2 + '</h2>\n      ' + html + '\n'
    faq_html = '<div class="mt-3 grid gap-3">' + ''.join(
        '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
        '<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">' + q +
        '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
        '<p class="mt-3 text-sm leading-relaxed text-ink-dim">' + a + '</p></details>' for q, a in faqs) + '</div>' if faqs else ''
    rel = '<ul class="mt-3 grid gap-2">' + ''.join(
        '<li><a href="' + href + '" class="text-accent hover:text-accent-soft">' + label + ' →</a></li>' for label, href in related) + '</ul>'
    doc = (
        "---\nimport BaseLayout from '../layouts/BaseLayout.astro';\n" + faq_const + "---\n"
        "<BaseLayout\n  title=\"" + title + " | PromptDNS\"\n  description=\"" + desc + "\"\n" + faq_line + ">\n"
        '  <div class="mx-auto max-w-3xl px-4 py-12">\n'
        '    <nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">\n'
        '      <a href="/" class="hover:text-accent">Home</a> <span aria-hidden="true">/</span>\n'
        '      <span class="text-ink-dim">' + h1 + '</span>\n'
        '    </nav>\n'
        '    <h1 class="font-display text-3xl font-bold tracking-tight text-ink sm:text-4xl">' + h1 + '</h1>\n'
        '    <p class="mt-5 text-lg leading-relaxed text-ink-dim">' + intro + '</p>\n'
        '    <div class="rich-text mt-8">\n' + sec +
        ('      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>\n'
         '      ' + faq_html + '\n') if faqs else ''
    )
    # rebuild cleanly to avoid conditional-in-expression issues
    parts = [
        "---\nimport BaseLayout from '../layouts/BaseLayout.astro';\n" + faq_const + "---\n",
        "<BaseLayout\n  title=\"" + title + " | PromptDNS\"\n  description=\"" + desc + "\"\n" + faq_line + ">\n",
        '  <div class="mx-auto max-w-3xl px-4 py-12">\n',
        '    <nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">\n',
        '      <a href="/" class="hover:text-accent">Home</a> <span aria-hidden="true">/</span>\n',
        '      <span class="text-ink-dim">' + h1 + '</span>\n',
        '    </nav>\n',
        '    <h1 class="font-display text-3xl font-bold tracking-tight text-ink sm:text-4xl">' + h1 + '</h1>\n',
        '    <p class="mt-5 text-lg leading-relaxed text-ink-dim">' + intro + '</p>\n',
        '    <div class="rich-text mt-8">\n',
    ]
    for h2, html in body:
        parts.append('      <h2 class="font-display mt-10 text-xl font-semibold text-ink">' + h2 + '</h2>\n      ' + html + '\n')
    if faqs:
        parts.append('      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>\n')
        parts.append('      <div class="mt-3 grid gap-3">' + ''.join(
            '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
            '<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">' + q +
            '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
            '<p class="mt-3 text-sm leading-relaxed text-ink-dim">' + a + '</p></details>' for q, a in faqs) + '</div>\n')
    parts.append('      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Related</h2>\n')
    parts.append('      <ul class="mt-3 grid gap-2">' + ''.join(
        '<li><a href="' + href + '" class="text-accent hover:text-accent-soft">' + label + ' →</a></li>' for label, href in related) + '</ul>\n')
    parts.append('    </div>\n  </div>\n</BaseLayout>\n')
    open('src/pages/' + slug + '.astro', 'w', encoding='utf-8').write(''.join(parts))

N = 0

def T(label, rows):
    _ = label  # unused header

    trs = ''.join('<tr>' + ''.join('<td class="text-sm text-ink-dim">' + c + '</td>' for c in r) + '</tr>' for r in rows)
    return '<div class="overflow-x-auto rounded-xl border border-line bg-panel/60"><table class="pdns-table"><tbody>' + trs + '</tbody></table></div>'

def L(items):
    return '<ul class="list-disc space-y-1.5 pl-5">' + ''.join('<li class="leading-relaxed">' + x + '</li>' for x in items) + '</ul>'

# ===== SECURITY PAGES =====

build_page('dns-hijacking',
 'DNS Hijacking: How Attacks Work and How to Stop Them',
 'DNS hijacking explained: the attack types (registrar hijack, MITM, cache poisoning), real examples, and the layered defense that stops each one.',
 'DNS Hijacking: How Attacks Work and How to Stop Them',
 "DNS hijacking redirects your domain's traffic by manipulating DNS answers. The victim never sees your server. This is one of the most damaging attacks because it is invisible to users and can persist for hours or days.",
 [
  ("The three attack vectors", L([
    '<strong class="text-ink">Registrar hijack:</strong> the attacker gains access to your registrar account (via phishing, credential stuffing, or a registrar breach) and changes your nameservers or A records to point at their infrastructure. This is the most damaging form because it is authoritative.',
    '<strong class="text-ink">On-path (MITM):</strong> the attacker intercepts unencrypted DNS queries between the user and the resolver and forges answers. Defeated by DNSSEC (authentication) and DoH/DoT (encryption).',
    '<strong class="text-ink">Cache poisoning:</strong> the attacker injects forged records into a resolver\u2019s cache. Defeated by DNSSEC and randomizing source ports/query IDs.',
   ])),
  ("Real attack scenarios", L([
    'A crypto exchange\u2019s DNS is hijacked; users visit a pixel-perfect clone, enter credentials, and lose funds.',
    'A government registrar is compromised; hundreds of domains redirect to a censorship page simultaneously.',
    'A router\u2019s DNS settings are changed via a vulnerability; every device on the network resolves to an attacker-controlled resolver.',
   ])),
  ("The layered defense", L([
    '<strong class="text-ink">DNSSEC:</strong> makes forged answers cryptographically detectable. Enable it at your <a href="/what-is-dnssec/">DNS host and registrar</a>.',
    '<strong class="text-ink">Registrar security:</strong> two-factor authentication, registry lock, transfer authorization codes stored securely.',
    '<strong class="text-ink">Monitoring:</strong> alert on any record change, especially nameservers and A records. Our <a href="/dns-propagation-checker/">propagation checker</a> detects mismatches.',
    '<strong class="text-ink">CAA records:</strong> prevent attackers from issuing certificates for your domain even if they control DNS.',
    '<strong class="text-ink">DoH/DoT:</strong> encrypt DNS queries so on-path attackers cannot read or forge them.',
   ])),
 ],
 [
  ["How do I know if my DNS has been hijacked?","Check your domain with the DNS record lookup and propagation checker: if different resolvers return different answers, or the IP is one you don\u2019t recognize, investigate immediately. Check your registrar\u2019s audit log for unauthorized changes."],
  ["Can DNS hijacking be reversed?","Yes, but it takes time: fix the root cause (regain registrar access, remove the poisoned record), then wait for caches to expire. DNSSEC-enabled zones recover faster because resolvers reject the forged answers automatically."],
  ["Does my DNS provider protect against hijacking?","Reputable providers (Cloudflare, Route 53) implement strong internal controls, but the registrar account is the soft target. Enable every security feature they offer."],
  ["What is the difference between DNS hijacking and DNS spoofing?","They overlap. Spoofing is the technique (forging answers); hijacking is the outcome (traffic redirected). Cache poisoning is a spoofing method; registrar compromise is a hijacking method."],
  ["Should I use a DNS provider with registry lock?","Yes for high-value domains. Registry lock requires human verification at the registry level before any nameserver change, adding a layer beyond registrar security."],
  ["Does my hosting provider protect DNS too?","Only if they host your DNS. If your nameservers point at Cloudflare or Route 53, your hosting provider\u2019s security is irrelevant to DNS attacks."],
 ],
 [("What is DNSSEC","/what-is-dnssec/"), ["CAA records","/caa-record/"], ("DNS propagation checker","/dns-propagation-checker/"), ("Homepage security scanner","/")],
)
N += 1

build_page('dns-cache-poisoning',
 'DNS Cache Poisoning (Spoofing) Explained',
 'DNS cache poisoning explained: how attackers inject fake records into resolver caches, the Kaminsky attack that changed everything, and how DNSSEC and port randomization stop it.',
 'DNS Cache Poisoning Explained',
 "DNS cache poisoning injects a forged answer into a resolver's cache. Until the TTL expires, every user of that resolver receives the attacker's IP instead of yours: no warning, no error, just the wrong destination.",
 [
  ("How the attack works",
   '<ol class="list-decimal space-y-1.5 pl-5"><li>The attacker triggers a lookup for target.com at a vulnerable resolver.</li><li>Before the authoritative server answers, the attacker floods the resolver with forged responses.</li><li>If a forged response matches the query (correct transaction ID, source port, and question), the resolver accepts and caches it.</li><li>Every subsequent user of that resolver gets the attacker\u2019s IP for target.com until the TTL expires.</li></ol>'),
  ("The Kaminsky vulnerability (2008)",
   '<p>Dan Kaminsky demonstrated that by querying random subdomains (a1.target.com, a2.target.com...) an attacker could generate enough guessing attempts to reliably poison the parent domain\u2019s cache. The industry response was source port randomization (16 extra bits of entropy) and the acceleration of DNSSEC deployment.</p>'),
  ("The defenses, ranked",
   '<ol class="list-decimal space-y-1.5 pl-5"><li><strong class="text-ink">DNSSEC:</strong> cryptographically signs answers, making forgery detectable regardless of guessing.</li><li><strong class="text-ink">Source port randomization:</strong> makes blind spoofing exponentially harder (already standard).</li><li><strong class="text-ink">0x20 encoding:</strong> randomizes query case for additional entropy.</li><li><strong class="text-ink">DoH/DoT:</strong> encrypts queries, preventing on-path injection entirely.</li></ol>'),
 ],
 [
  ["Can cache poisoning happen over HTTPS?","Not to the DNS resolution itself if you use DoH/DoT. But the resolved connection then depends on TLS for its own protection: both layers together are the full defense."],
  ["How do I know if my resolver has been poisoned?","Compare answers across multiple resolvers with the propagation checker. A single resolver returning a different IP for the same domain is a red flag."],
  ["Does my DNS provider protect against poisoning?","Major providers (Cloudflare, Google, Route 53) implement port randomization and DNSSEC validation. Self-hosted BIND servers need explicit configuration."],
  ["What is the difference between poisoning and hijacking?","Poisoning targets the resolver\u2019s cache (temporary, until TTL). Hijacking changes the authoritative data (persists until fixed). Both redirect traffic."],
  ["Can I prevent someone from poisoning my domain specifically?","DNSSEC is the only complete answer: it makes your zone\u2019s answers cryptographically verifiable so forgeries are rejected."],
  ["Is cache poisoning still a threat in 2026?","Less so against major providers, but self-hosted DNS, IoT devices, and legacy resolvers remain vulnerable. DNSSEC is the belt-and-suspenders answer."],
 ],
 [("What is DNSSEC","/what-is-dnssec/"), ("DNS hijacking","/dns-hijacking/"), ("DoH vs DoT","/doh-vs-dot/")],
)
N += 1

build_page('dns-amplification-attack',
 'DNS Amplification Attacks Explained',
 'DNS amplification attacks explained: how open resolvers are weaponized for DDoS, why the amplification factor matters, and how to prevent your server from being used.',
 'DNS Amplification Attacks Explained',
 "A DNS amplification attack turns small queries into massive floods: the attacker sends a 60-byte query to an open DNS resolver, which responds with a 4000-byte answer directed at the victim. The amplification factor can exceed 50x.",
 [
  ("How it works",
   '<ol class="list-decimal space-y-1.5 pl-5"><li>The attacker spoofs the victim\u2019s IP as the source of a DNS query.</li><li>The query asks for a large response (ANY type, or a DNSSEC-signed zone with big records).</li><li>The open resolver sends the large response to the victim\u2019s (spoofed) IP.</li><li>Thousands of resolvers respond simultaneously: the victim\u2019s bandwidth is overwhelmed.</li></ol>'),
  ("What makes a resolver 'open'",
   '<p>A resolver that answers queries from any source IP (not just its own customers) is open. Malicious actors scan the internet for open resolvers and compile lists for attacks. If you run your own DNS server, recursion must be restricted to your own network.</p>'),
  ("Preventing your server from being weaponized",
   '<ul class="list-disc space-y-1.5 pl-5"><li>Disable recursion for non-local clients (BIND: <code>allow-recursion { localhost; };</code>).</li><li>Do not respond to ANY queries (drop or return NOTIMP).</li><li>Use response rate limiting (RRL) to throttle identical responses.</li><li>If you use managed DNS (Cloudflare, Route 53), this is handled for you.</li></ul>'),
 ],
 [
  ["Am I responsible if my resolver is used in an attack?","Potentially, yes: operators of open resolvers used in DDoS attacks can face legal pressure and blocklisting. Close the recursion or face the consequences."],
  ["What is the amplification factor?","The ratio of response size to query size. DNSSEC-signed zones with large keys can amplify 50x or more, making them preferred weapons."],
  ["Does DNSSEC make amplification worse?","Yes, larger signed responses amplify more. But the answer is rate limiting and response filtering, not abandoning DNSSEC."],
  ["Can Cloudflare or Route 53 be used for amplification?","No: they restrict recursion to customers and implement response rate limiting at global scale."],
  ["How do I test if my resolver is open?","Use an open resolver scanner (like the Shadowserver Foundation\u2019s) or try querying it from an external network."],
  ["Does this affect my website?","Only if you self-host DNS. If you use a managed provider, this is their problem, not yours."],
 ],
 [("DNS security hub","/what-is-dnssec/"), ("NS records","/ns-record/"), ("How DNS works","/how-dns-works/")],
)
N += 1

build_page('dns-tunneling',
 'DNS Tunneling: Data Exfiltration Through Port 53',
 'DNS tunneling explained: how attackers encode stolen data inside DNS queries to bypass firewalls, and how to detect and prevent it.',
 'DNS Tunneling: Data Exfiltration Through Port 53',
 "DNS tunneling encodes arbitrary data inside DNS queries and responses. Because almost every network allows DNS traffic to pass, it becomes a covert channel for data exfiltration, command-and-control communication, and firewall bypass.",
 [
  ("How it works",
   '<ol class="list-decimal space-y-1.5 pl-5"><li>The attacker controls the authoritative nameserver for a domain (like tunnel.attacker.com).</li><li>Malware on the victim\u2019s network encodes data into subdomain queries: <code>cGFzc3dvcmQ=.tunnel.attacker.com</code>.</li><li>The query travels through the local DNS resolver to the attacker\u2019s nameserver.</li><li>The attacker\u2019s server decodes the data and sends instructions back in TXT record responses.</li></ol>'
   '<p>Each query can carry ~180 bytes of payload. At 10 queries per second, that\u2019s ~1.8 KB/s: enough for credentials, keys, and documents over time.</p>'),
  ("Detection signals",
   '<ul class="list-disc space-y-1.5 pl-5"><li>Unusually high DNS query volume to a single domain.</li><li>Long, random-looking subdomains (base32/hex encoded data).</li><li>DNS TXT record queries from workstations (rare in normal traffic).</li><li>Queries for NXDOMAIN names at an unusually high rate.</li></ul>'),
  ("Prevention",
   '<ul class="list-disc space-y-1.5 pl-5"><li>Monitor DNS query patterns for anomalies (volume, entropy, unique domain count).</li><li>Restrict which DNS servers internal devices can use (force your resolver, block outbound port 53).</li><li>Block or alert on TXT queries from non-DNS-infrastructure hosts.</li><li>Use DNS-layer security tools (Cisco Umbrella, Infoblox) that detect tunneling patterns.</li></ul>'),
 ],
 [
  ["Is DNS tunneling the same as DNS hijacking?","No. Hijacking redirects traffic; tunneling exfiltrates data through legitimate-looking DNS queries. Both abuse the protocol."],
  ["Can HTTPS prevent DNS tunneling?","No: tunneling uses DNS queries themselves (port 53 or DoH), not the HTTP connection. Even DoH can carry tunneling if the attacker controls the resolver."],
  ["How much data can be exfiltrated?","At realistic query rates without triggering alerts: kilobytes per minute, megabytes per hour. Enough for credentials and source code over time."],
  ["What should I monitor?","DNS query volume per client, entropy of queried names, NXDOMAIN rate, and TXT query frequency. Spikes indicate tunneling."],
  ["Does my DNS provider detect tunneling?","Some managed providers offer DNS-layer threat detection as an add-on. Self-hosted DNS requires dedicated monitoring."],
  ["Is DNS tunneling used in real attacks?","Yes: documented in advanced persistent threat (APT) campaigns and by malware families for command-and-control channels."],
 ],
 [("DNS security","/what-is-dnssec/"), ("How DNS works","/how-dns-works/"), ("DNS record lookup","/dns-record-lookup/")],
)
N += 1

build_page('dns-rebinding-explained',
 'DNS Rebinding Attacks Explained',
 'DNS rebinding explained: how attackers bypass the same-origin policy using DNS to access internal networks, and how to prevent it.',
 'DNS Rebinding Explained',
 "DNS rebinding exploits the time gap between DNS resolution and browser security checks. The attacker\u2019s domain first resolves to their own server (to plant malicious JavaScript), then rebinds to an internal IP (to access devices on your network) using the browser\u2019s trust.",
 [
  ("The attack sequence",
   '<ol class="list-decimal space-y-1.5 pl-5"><li>The victim visits attacker.com, which resolves to the attacker\u2019s server.</li><li>The page loads JavaScript that keeps running in the victim\u2019s browser.</li><li>The DNS TTL expires; the page re-queries attacker.com.</li><li>This time the DNS answer is 192.168.1.1 (the victim\u2019s router).</li><li>The JavaScript can now read responses from 192.168.1.1 because the browser thinks it\u2019s still same-origin (same domain name).</li></ol>'),
  ("What attackers target",
   '<ul class="list-disc space-y-1.5 pl-5"><li>Router admin panels (change DNS, open ports, install firmware).</li><li>IoT devices (cameras, thermostats) with unauthenticated APIs.</li><li>Development servers (localhost:3000, :8080) running on the victim\u2019s machine.</li><li>Enterprise applications on internal networks accessible from the employee\u2019s browser.</li></ul>'),
  ("Defenses",
   '<ul class="list-disc space-y-1.5 pl-5"><li><strong class="text-ink">Browser-level:</strong> modern browsers pin the resolved IP for the page\u2019s lifetime (defense in depth).</li><li><strong class="text-ink">DNS-level:</strong> your resolver can filter rebinding attempts (answer A records for public domains only with public IPs).</li><li><strong class="text-ink">Application-level:</strong> validate the Host header on internal services; reject requests for external domain names.</li><li><strong class="text-ink">Router-level:</strong> don\u2019t expose admin interfaces on the LAN without authentication.</li></ul>'),
 ],
 [
  ["Is DNS rebinding still a threat?","Yes, especially against IoT devices and internal services that lack host-header validation. Browsers have improved, but the attack surface persists."],
  ["How is this different from DNS spoofing?","Spoofing forges answers. Rebinding uses legitimate answers that change over time: the DNS is working correctly, the attack exploits the time gap."],
  ["Does HTTPS prevent rebinding?","It complicates it (the attacker needs a valid certificate for their domain that rebinding preserves), but does not eliminate the underlying issue for internal HTTP services."],
  ["Can I prevent rebinding on my own devices?","Set your resolver to filter rebind attempts (dnsmasq: stop-dns-rebind). Most modern routers and Pi-hole include this."],
  ["Why doesn\u2019t the same-origin policy prevent this?","The browser judges origin by domain NAME, not IP. attacker.com resolving to 192.168.1.1 is still attacker.com to the browser."],
  ["What is the DNS TTL requirement for rebinding?","The attacker needs a very low TTL (0 or 1) so the browser re-queries quickly. Legitimate domains should never use TTL 0."],
 ],
 [("DNS security","/what-is-dnssec/"), ("Public vs private IP","/public-vs-private-ip/"), ("How DNS works","/how-dns-works/")],
)
N += 1

# ===== OPS PAGES =====

build_page('dns-error-messages',
 'DNS Error Messages: The Complete Reference',
 "Every DNS error message explained: SERVFAIL, NXDOMAIN, REFUSED, timeouts, and browser errors like DNS_PROBE_FINISHED_NXDOMAIN, with causes and fixes.",
 'DNS Error Messages: The Complete Reference',
 "DNS errors are cryptic by design: they tell you what layer failed without telling you why. This reference decodes every common DNS error, from resolver status codes to browser-specific messages.",
 [
  ("Resolver status codes", T('Code', [
   ('NOERROR (0)','The query succeeded','May still have zero answers for the requested type'),
   ('FORMERR (1)','Malformed query','A client or proxy bug, not a DNS issue'),
   ('SERVFAIL (2)','The server failed to process','DNSSEC failure, upstream timeout, or configuration error'),
   ('NXDOMAIN (3)','Name does not exist','Typo, deleted record, or negative-cached'),
   ('NOTIMP (4)','Not implemented','The server does not support the requested operation'),
   ('REFUSED (5)','The server refuses to answer','ACL blocking, AXFR denied, or policy'),
  ])),
  ("Browser-specific messages", T('Error', [
   ('DNS_PROBE_FINISHED_NXDOMAIN','Name doesn\u2019t exist','Check spelling, verify the domain exists, flush local cache'),
   ('DNS_PROBE_FINISHED_NO_INTERNET','Network unreachable','Check connection, then DNS server settings'),
   ('DNS_PROBE_FINISHED_BAD_CONFIG','Invalid DNS configuration','Reset DNS settings to automatic or use 1.1.1.1/8.8.8.8'),
   ('This site can\u2019t be reached','Generic: could be DNS, server, or network','Run the propagation checker to narrow down'),
  ])),
  ("The diagnostic flow", L([
    'Run the domain through the <a href="/dns-record-lookup/">record lookup</a>: if it returns answers, DNS is fine and the problem is the server or network.',
    'If the lookup fails with SERVFAIL, check DNSSEC (stale DS) and nameserver health.',
    'If NXDOMAIN, check spelling and whether the record was accidentally deleted.',
    'If one resolver works but another doesn\u2019t, it\u2019s a propagation or caching issue: use the <a href="/dns-propagation-checker/">propagation checker</a>.',
   ])),
 ],
 [
  ["What does SERVFAIL actually mean?","The server tried to answer but failed: DNSSEC validation failed, the upstream authoritative server timed out, or internal configuration is broken."],
  ["Why does NXDOMAIN persist after I added a record?","Negative caching: the resolver cached the NXDOMAIN answer for the SOA minimum TTL. Wait or flush local caches."],
  ["Can I fix DNS errors on the user's side?","Only if the issue is local (cache, settings). Authoritative DNS errors must be fixed in the zone."],
  ["What's the difference between a DNS error and a connection error?","DNS errors mean the name couldn't be resolved to an address. Connection errors mean the address was reached but the server didn't respond."],
  ["Does clearing browser data fix DNS errors?","It clears the browser's internal DNS cache, which helps for locally cached bad answers. System-level flush (ipconfig /flushdns) is more thorough."],
  ["Are DNS errors ever caused by malware?","Yes: some malware changes DNS settings to redirect through a malicious resolver, causing selective failures and redirects."],
 ],
 [("Website not resolving","/website-not-resolving/"), ("Site down after DNS change","/site-down-after-dns-change/"), ("Flush DNS cache","/flush-dns-cache/")],
)
N += 1

# ===== DELIVERABILITY DEPTH =====

build_page('cold-email-deliverability',
 'Cold Email Deliverability: Staying Out of Spam',
 'Cold email deliverability: authentication, warm-up, volume control, and list quality for outbound campaigns that land in the inbox.',
 'Cold Email Deliverability',
 "Cold email faces the hardest deliverability test: unsolicited mail to people who haven't opted in. Authentication, warm-up, and list quality aren't optional; they're the minimum to avoid the spam folder.",
 [
  ("The compliance foundation", L([
    'SPF, DKIM, and DMARC configured and passing: the <a href="/">homepage scanner</a> verifies all three in one pass.',
    'A custom domain (never a free address) with a verified sending subdomain.',
    'Reverse DNS (PTR) on your sending IP, matching your HELO name.',
    'A working unsubscribe mechanism: one-click for Gmail/Yahoo compliance.',
   ])),
  ("Volume discipline", L([
    'Start a new domain at 10-20 emails per day, doubling weekly.',
    'Never exceed 50% of your daily capacity in a single burst.',
    'Separate cold outreach from transactional mail on different domains or subdomains.',
    'Keep daily volume below 10% of your total sent history for the identity.',
   ])),
  ("Content that avoids filters", L([
    'No URL shorteners (they hide destination and trigger filters).',
    'Minimal HTML; plain text or light formatting performs better for cold.',
    'No spam-trigger words in subject lines (free, guaranteed, act now).',
    'Personalization that\u2019s real (name, company, context), not mail-merge tokens.',
    'One clear call to action; no link farms.',
   ])),
  ("Monitoring", L([
    'Track bounce rate (under 2%), complaint rate (under 0.1%), and reply rate.',
    'Check <a href="/blacklist-checker/">blocklists</a> weekly.',
    'Use Google Postmaster Tools for domain reputation trends.',
    'Run the <a href="/">homepage scanner</a> after any infrastructure change.',
   ])),
 ],
 [
  ["How many cold emails can I send per day?","From a warmed-up domain: 20-50 per mailbox, scaling to 200-500 across multiple mailboxes. Exceeding this on a new domain is the fastest route to spam folders."],
  ["Does using multiple domains help?","Yes: spreading across 2-5 domains with separate inboxes isolates reputation damage. Each domain needs its own authentication and warm-up."],
  ["What bounce rate is acceptable for cold email?","Under 2% for verified lists; under 5% for semi-verified. Above that, your list quality (or verification tool) is the problem."],
  ["Should I use a subdomain for cold email?","Yes: mail.yourdomain.com isolates campaign reputation from your main domain. It needs its own SPF, DKIM, and DMARC records."],
  ["How do I avoid spam traps?","Never use purchased or scraped lists. Verify addresses before sending. Remove unengaged contacts after 90 days."],
  ["Can I use the same domain for cold and transactional?","Strongly discouraged: one bad campaign can affect password resets and receipts. Use separate subdomains at minimum."],
 ],
 [("Why emails go to spam","/why-emails-go-to-spam/"), ["Email sender reputation","/email-sending-reputation/"], ("Email deliverability hub","/email-deliverability/")],
)
N += 1

# ===== write all =====
print('wrote', N, 'pages')
