# -*- coding: utf-8 -*-
"""Phase 3 batch 2: IP/networking cluster + SSL cluster (13 pages)."""
import json

def build_page(slug, title, desc, h1, intro, body, faqs, related, schema=True):
    faq_const = ("const faqSchema = " + json.dumps(
        {'@context': 'https://schema.org', '@type': 'FAQPage',
         'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]},
        ensure_ascii=False, indent=1) + "\n") if schema else ""
    faq_line = "  schema={[faqSchema]}\n" if schema else ""
    sec = ""
    for h2, html in body:
        sec += '      <h2 class="font-display mt-10 text-xl font-semibold text-ink">' + h2 + '</h2>\n      ' + html + '\n'
    faq_html = '<div class="mt-3 grid gap-3">' + ''.join(
        '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
        '<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">' + q +
        '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
        '<p class="mt-3 text-sm leading-relaxed text-ink-dim">' + a + '</p></details>' for q, a in faqs) + '</div>'
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
        '      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>\n'
        '      ' + faq_html + '\n'
        '      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Related</h2>\n'
        '      ' + rel + '\n'
        '    </div>\n'
        '  </div>\n'
        '</BaseLayout>\n'
    )
    open('src/pages/' + slug + '.astro', 'w', encoding='utf-8').write(doc)

def T(h, rows, headers=None):
    th = ''.join('<th>' + x + '</th>' for x in (headers or ['', '', '']))
    trs = ''.join('<tr>' + ''.join('<td class="text-sm text-ink-dim">' + c + '</td>' for c in r) + '</tr>' for r in rows)
    return '<div class="overflow-x-auto rounded-xl border border-line bg-panel/60"><table class="pdns-table"><thead><tr>' + th + '</tr></thead><tbody>' + trs + '</tbody></table></div>'

def L(items):
    return '<ul class="list-disc space-y-1.5 pl-5">' + ''.join('<li class="leading-relaxed">' + x + '</li>' for x in items) + '</ul>'

N = 0

# ---------- IP cluster ----------
build_page('ip-and-networking',
 'IP & Networking Guides | PromptDNS',
 'IP and networking guides: IP addresses, NAT, ASNs, ports, CDNs, and the concepts every webmaster eventually needs.',
 'IP & Networking Guides',
 'The concepts under every DNS decision: what addresses mean, who operates networks, how traffic flows, and where the web ends and the network begins.',
 [('Start here', L([
    '<a href="/what-is-an-ip-address/">What is an IP address</a> — addresses from first principles',
    '<a href="/ipv4-vs-ipv6/">IPv4 vs IPv6</a> — the two protocol generations',
    '<a href="/public-vs-private-ip/">Public vs private IPs</a> — and the RFC 1918 ranges',
   ])),
  ('Digging deeper', L([
    '<a href="/asn-explained/">What is an ASN</a> — the networks behind addresses',
    '<a href="/nat-explained/">NAT explained</a> — how one public IP serves a whole network',
    '<a href="/static-vs-dynamic-ip/">Static vs dynamic IPs</a> — and when stability matters',
   ])),
  ('Tools', L([
    '<a href="/ip-lookup/">IP Lookup</a>, <a href="/reverse-ip-lookup/">Reverse IP</a>, <a href="/my-ip/">What Is My IP</a>',
    '<a href="/cidr-calculator/">CIDR calculator</a> for subnet math',
   ]))],
 [("Is DNS part of networking?","DNS is the internet's addressing layer: pure networking, but with its own deep specialization, which is why this site treats it as a first-class topic."),
  ("Where should a beginner start?","What is an IP address, then IPv4 vs IPv6, then NAT. Those three unlock most of the rest."),
  ("Do I need this for basic website management?","Only the DNS layer. The deeper networking pages matter when troubleshooting mail, running servers, or reading logs.")],
 [("IP lookup tool","/ip-lookup/"), ("CIDR calculator","/cidr-calculator/")])
N += 1

build_page('nat-explained',
 'NAT Explained: How One Public IP Serves a Whole Network',
 'NAT (Network Address Translation) explained: how routers share one public IP among many devices, what NAT breaks, and its role in IPv4 survival.',
 'NAT Explained',
 "Network Address Translation is the trick that let the internet survive IPv4 exhaustion: your router rewrites addresses so an entire household shares one public IP, and somehow everything still works.",
 [
  ("How it works", L([
    'A device inside sends a packet out; the router replaces its private source address (192.168.1.x) with the public IP and records the connection in a translation table.',
    'Replies come back to the public IP; the router matches them to the table entry and forwards to the original device.',
    'Unsolicited inbound packets with no table entry are dropped: that is why NAT is accidental firewall protection, and why hosting behind it needs port forwarding.',
   ])),
  ("What NAT breaks and why", L([
    'Inbound hosting: nothing can reach your devices until you forward ports.',
    'End-to-end applications: VoIP, P2P, and some games need NAT traversal (STUN/TURN).',
    'Mail sending: consumer NAT space is blocklisted by policy (that is what Spamhaus PBL tracks), so mail must relay through a smarthost.',
   ])),
 ],
 [("Does NAT protect me from hackers?","It blocks unsolicited inbound connections, which is real protection, but it is not a firewall you configure: outbound threats and phishing pass freely."),
  ("Why does IPv6 remove NAT?","Every device gets a globally routable address, so translation is unnecessary; the same protection comes from proper firewalls."),
  ("What is CGNAT?","Carrier-grade NAT: your ISP applies the same trick to whole neighborhoods, stacking another layer. It breaks port forwarding entirely and puts hundreds of users behind one address."),
 ],
 [("What Is My IP","/my-ip/"), ("IPv4 vs IPv6","/ipv4-vs-ipv6/"), ("Public vs private IP","/public-vs-private-ip/")])
N += 1

build_page('common-network-ports',
 'Common Network Ports: The Reference List',
 'The common network ports reference: web, mail, DNS, remote access, and database ports with what each protocol does and safe defaults.',
 'Common Network Ports',
 'Ports are numbered doors on a machine: the port in a connection decides which program answers. Firewalls and servers live and die by getting this list right.',
 [
  ("The ports that matter", T('Port', [
   ('80','HTTP','Web, unencrypted (redirects to HTTPS)'),
   ('443','HTTPS','Web, encrypted: the modern default'),
   ('53','DNS','Queries (UDP) and zone transfers (TCP)'),
   ('25','SMTP','Server-to-server mail relay'),
   ('587','SMTP submission','User outgoing mail with STARTTLS'),
   ('465','SMTPS','User outgoing mail, implicit TLS'),
   ('993','IMAPS','Receiving mail, encrypted'),
   ('995','POP3S','Receiving mail (POP), encrypted'),
   ('22','SSH','Remote server administration'),
   ('3389','RDP','Windows remote desktop'),
  ])),
  ("Well-known vs ephemeral", L([
    '0-1023 are well-known ports reserved for core services; servers listen there.',
    '49152-65535 are ephemeral: your browser picks a random one as the source port for each connection.',
    'Firewalls block inbound on ephemeral ranges by default; that is correct and normal.',
   ])),
 ],
 [("Why is port 25 blocked on my connection?","ISPs block consumer outbound 25 to kill spam botnets. Send mail through port 587/465 submission or a smarthost."),
  ("Can two programs share a port?","Not on the same address: one listener per port per address. Multiple addresses or protocols can coexist."),
  ["Which ports must be open for a website?","Inbound 80 and 443 on the web server; everything else can stay closed. Management ports (22/3389) should be restricted to known IPs."],
  ["Does closing ports improve security?","Reducing the exposed surface always helps, but hardening the services behind open ports matters more."],
  ["How do I check open ports?","From outside: an online port scanner against your address. From the server: ss -tlnp or netstat -tlnp."],
  ["What is port forwarding?","Telling a NAT router to send inbound traffic on one port to a specific internal device: the workaround for hosting behind NAT."],
 ][2:6],
 [("DNS port numbers","/dns-port-numbers/"), ("SMTP preflight","/smtp-tester/"), ("Email ports guide","/smtp-tester/")])
N += 1

build_page('reserved-ip-ranges',
 'Reserved and Private IP Ranges (RFC 1918 and More)',
 'Every reserved IP range: private (RFC 1918), loopback, link-local, and documentation ranges, with what each is for.',
 'Reserved IP Ranges',
 'Not every IP address routes on the internet. Several ranges are reserved for private networks, testing, and documentation: knowing them on sight prevents a whole family of configuration mistakes.',
 [
  ("The complete table", T('Range', [
   ('10.0.0.0/8','Private (RFC 1918)','Enterprise networks, cloud VPCs'),
   ('172.16.0.0/12','Private (RFC 1918)','Mid-size networks'),
   ('192.168.0.0/16','Private (RFC 1918)','Home and small office'),
   ('127.0.0.0/8','Loopback','The machine itself (localhost)'),
   ('169.254.0.0/16','Link-local','Self-assigned when DHCP fails'),
   ('100.64.0.0/10','CGNAT','Carrier-grade NAT space'),
   ('192.0.2.0/24 + others','Documentation','Examples and tutorials (TEST-NET)'),
   ('224.0.0.0/4','Multicast','One-to-many delivery'),
  ])),
  ("The rules that follow", L([
    'Private and loopback addresses never appear in public DNS: an A record pointing at one resolves only inside your network.',
    'Documentation ranges (192.0.2.x, 198.51.100.x, 203.0.113.x) are guaranteed safe for examples, which is why our guides use them.',
    'Seeing 169.254.x.x on a device means DHCP failed: it self-assigned and has no real network.',
   ])),
 ],
 [("Why do tutorials use 203.0.113.x?","The documentation ranges are reserved so examples can never collide with real networks."),
  ["Is 100.64.x.x a public IP?","No: carrier-grade NAT space. If that is your outbound address, you are behind CGNAT and cannot host inbound services."],
  ["Can I use private IPs in my VPC?","Yes: cloud VPCs are built on RFC 1918 ranges with public gateways handling translation."],
  ["What should I do if my device has 169.254.x.x?","DHCP failed: restart the router/DHCP server. The address cannot reach the internet."],
  ["Are multicast ranges dangerous?","Not dangerous, but often filtered: some networks block multicast to prevent flooding."],
  ["How do I check if an IP is private?","Match it against the ranges in this table, or run it through the IP lookup: private ranges report as reserved."],
 ][1:6],
 [("Public vs private IP","/public-vs-private-ip/"), ("CIDR calculator","/cidr-calculator/"), ("IP lookup","/ip-lookup/")])
N += 1

build_page('reverse-proxy-explained',
 'Reverse Proxy Explained (Nginx, Cloudflare)',
 'Reverse proxies explained: how Nginx and Cloudflare sit in front of your servers, what they add, and how they differ from a load balancer.',
 'Reverse Proxy Explained',
 'A forward proxy hides clients; a reverse proxy hides servers. It sits in front of your infrastructure, receives all traffic, and forwards requests to your backend: adding TLS termination, caching, load balancing, and a security layer on the way.',
 [
  ("What it adds", L([
    'TLS termination: one certificate at the proxy, plain HTTP to your backends internally.',
    'Caching: static assets and hot responses served without touching the origin.',
    'Load distribution: round-robin or health-checked forwarding across multiple backends.',
    'Security: rate limiting, IP filtering, WAF integration, and hidden backend topology.',
   ])),
  ("The examples you already know", L([
    '<strong class="text-ink">Nginx:</strong> the classic self-hosted reverse proxy; proxy_pass directives route paths to upstreams.',
    '<strong class="text-ink">Cloudflare:</strong> a reverse proxy as a global service, with the orange cloud enabling it; DNS points at the edge, not your origin.',
    '<strong class="text-ink">Load balancers</strong> (AWS ALB, GCP LB) are reverse proxies specialized for distribution with health checks.',
   ])),
 ],
 [("Does a reverse proxy hide my server completely?","Only with discipline: Direct Connect leaks, certificate transparency logs reveal hostnames, and misconfigured subdomains expose origins. Full origin hiding is an architecture, not a toggle."),
  ["Is a reverse proxy the same as a CDN?","A CDN is a globally distributed reverse proxy with caching at hundreds of locations; a local Nginx proxy is the same concept on one machine."],
  ["Does it break WebSockets?","Proxies need explicit upgrade handling for WebSockets; both Nginx and Cloudflare support it with configuration."],
  ["Why terminate TLS at the proxy?","Centralized certificate management. Internal traffic between proxy and backend can then use a private PKI or plain HTTP on a trusted network."],
  ["Do I need one with a PaaS?","No: Vercel/Netlify/Heroku already front your app with their own proxies and load balancers."],
  ["What is X-Forwarded-For?","The header a reverse proxy adds to carry the real client IP to your backend; trust it only from your own proxies, or attackers can spoof it."],
 ][1:6],
 [("What is a CDN","/what-is-a-cdn/"), ("DNS load balancing","/dns-load-balancing/"), ("CNAME flattening","/cname-flattening/")])
N += 1

build_page('dns-load-balancing',
 'DNS Load Balancing: Techniques Compared',
 'DNS load balancing explained: round-robin, weighted, latency-based, and health-checked failover, with the limits of each approach.',
 'DNS Load Balancing',
 'DNS can distribute traffic across servers by returning different answers to the same query. It is the simplest load balancing layer that exists, with sharp limits you must design around.',
 [
  ("The techniques", T('', [
   ('Round-robin','Multiple A records, returned in rotation','Simple; no health checking'),
   ('Weighted','Traffic split by ratio','Controlled rollout, canary releases'),
   ('Latency-based','Answer from the fastest region for each user','Requires provider support (Route 53)'),
   ('Geo / geoproximity','Answer based on user location','Data residency, regional content'),
   ('Health-checked failover','Monitor endpoints; remove dead ones automatically','Real resilience (provider feature)'),
   ('Weighted + health','Canary with automatic rollback','Advanced (Route 53, NS1)'),
  ])),
  ("The limits you must respect", L([
    'Resolvers cache answers for the TTL: failover takes at least one TTL to propagate everywhere.',
    'Round-robin keeps sending traffic to a dead server until you remove its record.',
    'DNS balancing balances QUERIES, not connections: a single user makes one lookup and hammers one server.',
   ])),
  ("The practical stack",
   '<p>For anything beyond hobby scale: DNS-level distribution (geo or weighted) pointing at health-checked load balancers, which handle per-connection decisions. DNS steers regions; load balancers steer sessions. Verify both layers with the <a href="/dns-propagation-checker/">propagation checker</a> after changes.</p>'),
 ],
 [("Is DNS round-robin real load balancing?","It is load distribution: no health checks, no session affinity. Use it for stateless services with tolerable blips."),
  ["What TTL should load-balanced records use?","Low: 60-300 seconds, so failover and reweighting take effect quickly."],
  ["Can DNS failover replace a load balancer?","No: DNS removes dead servers after detection delay, while a load balancer stops sending traffic to dead nodes per-connection, instantly."],
  ["Which providers support health checks?","Route 53, NS1, Constellix, and enterprise tiers of most managed DNS providers. Free tiers generally do not."],
  ["How do CDN and DNS balancing interact?","The CDN does per-request balancing at the edge; your DNS points users at the nearest edge. Both layers, different jobs."],
  ["What is split-horizon DNS?","Different answers for internal vs external queries: internal users get private IPs, external users get public ones."],
 ][1:6],
 [("Propagation checker","/dns-propagation-checker/"), ("DNS failover guide","/dns-failover/"), ("Provider comparison","/cloudflare-vs-route53/")])
N += 1

# ---------- SSL cluster ----------
build_page('ssl-tls',
 'SSL/TLS and Web Security Basics',
 'SSL/TLS hub: certificates, HTTPS, encryption basics, and the guides that secure your connection from browser to server.',
 'SSL/TLS and Web Security Basics',
 'TLS is the encryption and authentication layer that turns HTTP into HTTPS. This hub collects everything a webmaster needs: what certificates are, how encryption works, and the configurations that keep connections trusted.',
 [
  ('Core guides', L([
    '<a href="/what-is-ssl-tls/">What is SSL/TLS?</a> — the protocol and the handshake',
    '<a href="/certificate-authorities-explained/">Certificate authorities</a> — who vouches for certificates',
    '<a href="/https-vs-dnssec/">HTTPS vs DNSSEC</a> — encryption vs DNS authentication',
   ])),
  ('Practical setup', L([
    '<a href="/free-ssl-lets-encrypt/">Free certificates with Let\u2019s Encrypt</a> — automated via ACME',
    '<a href="/tls-versions-explained/">TLS versions explained</a> — 1.0 through 1.3',
    '<a href="/ssl-certificate-errors/">Certificate errors fixed</a> — every common cause',
    '<a href="/mixed-content-fix/">Mixed content fixes</a> — when HTTPS pages load HTTP resources',
    '<a href="/hsts-explained/">HSTS explained</a> — forcing HTTPS permanently',
   ])),
  ('Verify', L([
    '<a href="/dns-record-lookup/">CAA record lookup</a> — restrict who may issue your certificates',
    '<a href="/ai-readiness-checker/">Security scanner</a> — TLS alongside DNS and auth checks',
   ])),
 ],
 [("Does this site use TLS?","Yes: promptdns.com is served over HTTPS with automated certificates, like every modern site should be."),
  ("SSL vs TLS in one line?","Same family: SSL is the retired name, TLS 1.2/1.3 is the living protocol."),
 ],
 [("DNSSEC guide","/what-is-dnssec/"), ("Email authentication hub","/email-authentication/")])
N += 1

build_page('free-ssl-lets-encrypt',
 'Let\u2019s Encrypt: Free Certificates and ACME Automation',
 'Let\u2019s Encrypt explained: free TLS certificates via ACME, how issuance and renewal work, and the 90-day model that made HTTPS universal.',
 'Let\u2019s Encrypt: Free Certificates',
 "Let's Encrypt is a free, automated certificate authority that made HTTPS universal. Certificates last 90 days by design and renew automatically via the ACME protocol: the cost of TLS dropped to zero, and the excuse to skip it vanished with it.",
 [
  ("How ACME works",
   '<ol class="list-decimal space-y-1.5 pl-5"><li>An ACME client on your server (certbot, acme.sh, or your host\u2019s built-in integration) requests a certificate for your domain.</li><li>Let\u2019s Encrypt challenges control: HTTP-01 (a file at a known URL) or DNS-01 (a TXT record).</li><li>Verified: the certificate issues, valid 90 days.</li><li>The client renews automatically at 60 days; the cycle never stops.</li></ol>'),
  ("The paths",
   '<ul class="list-disc space-y-1.5 pl-5"><li><strong class="text-ink">Managed hosting:</strong> TLS is a toggle (Cloudflare, Vercel, Netlify, Railway all run ACME for you).</li><li><strong class="text-ink">Your own server:</strong> certbot with the Nginx/Apache plugin handles issuance and renewal end to end.</li><li><strong class="text-ink">DNS-01 challenge:</strong> for wildcard certificates (*.domain) or when port 80 is blocked: requires DNS API access for automated TXT records.</li></ul>'),
  ("The rate limits that matter",
   '<p>50 certificates per registered domain per week, 5 duplicate certificates per week, 5 failed validations per hour per account. Most deployments never touch these; massive automation occasionally does.</p>'),
 ],
 [("Is a free certificate weaker than paid?","No: the encryption is identical. Paid certificates add warranties, organization validation, and support, not stronger crypto."),
  ["Why 90 days?","Short-lived certificates limit damage from key compromise and force automation, which is the entire point."],
  ["Can I get a wildcard from Let's Encrypt?","Yes, via the DNS-01 challenge with an API-connected DNS provider."],
  ["What happens if renewal fails?","Browsers block the expired site outright. Certbot emails at 20 days remaining; monitor expiry like any other certificate."],
  ["Do subdomains need separate certificates?","No: one certificate covers listed SANs (www, api, etc.) or use a wildcard via DNS-01."],
  ["Is Let's Encrypt trusted everywhere?","Yes: its root ISRG Root X1 is trusted by all major browsers and platforms; very old systems needed the cross-sign, which has since been retired."],
 ][1:6],
 [("SSL/TLS hub","/ssl-tls/"), ("CAA records","/caa-record/"), ("HTTPS vs DNSSEC","/https-vs-dnssec/")])
N += 1

build_page('tls-versions-explained',
 'TLS Versions Explained: 1.0 to 1.3',
 'TLS versions explained: what changed from SSL 3.0 and TLS 1.0 through TLS 1.3, which to disable, and how to test your server.',
 'TLS Versions Explained',
 "Every TLS version is a security generation. SSL 3.0 and TLS 1.0/1.1 are broken and retired; TLS 1.2 is the workhorse; TLS 1.3 is the modern protocol: faster, simpler, and more secure. Your server should offer 1.2 and 1.3, and nothing else.",
 [
  ("The versions", T('Version', [
   ('SSL 3.0','Dead (POODLE)','Retired 2015; disable everywhere'),
   ('TLS 1.0','Dead (BEAST, weak ciphers)','Retired 2020/2021 by browsers'),
   ('TLS 1.1','Dead (weak integrity)','Retired 2020/2021 by browsers'),
   ('TLS 1.2','Workhorse','Secure with modern cipher suites; still widely required'),
   ('TLS 1.3','Modern','Faster handshake (1-RTT), removed legacy ciphers, forward secrecy mandatory'),
  ])),
  ("Why 1.3 matters",
   '<ul class="list-disc space-y-1.5 pl-5"><li>One round-trip handshake instead of two: measurably faster connections.</li><li>Removed every legacy cipher, compression, and renegotiation: a smaller attack surface.</li><li>Forward secrecy on every connection: past traffic stays past even if keys leak later.</li><li>0-RTT resumption exists but carries replay caveats: use for GETs only.</li></ul>'),
  ("Server configuration",
   '<p>Enable TLS 1.2 + 1.3, disable everything older, and prefer modern cipher suites (Cloudflare and major CDNs do this by default). Test with SSL Labs or <code>openssl s_client -tls1_2 -connect host:443</code>. PCI DSS and every modern compliance framework require disabling 1.0/1.1.</p>'),
 ],
 [("Will disabling TLS 1.0 break my users?","A tiny fraction of very old systems; the industry retired it collectively in 2020, so the break happened whether you participate or not."),
  ["Is TLS 1.3 backward compatible?","It has a compatibility mode so middleboxes tolerate it, but 1.3-only servers drop ancient clients by design."],
  ["What is a cipher suite?","The negotiated recipe: key exchange, bulk encryption, and hash algorithms. Modern suites are all forward-secret."],
  ["How do I check my server's TLS?","SSL Labs Server Test grades protocol and cipher configuration, or openssl s_client with -tls1_2/-tls1_3 flags."],
  ["Does DNSSEC affect TLS?","No: different layers. DNSSEC authenticates addresses; TLS authenticates and encrypts the session."],
  ["Why did old TLS die?","POODLE, BEAST, and downgrade attacks against design flaws that cannot be patched, only retired."],
 ][1:6],
 [("What is SSL/TLS","/what-is-ssl-tls/"), ("HSTS explained","/hsts-explained/"), ("SSL errors","/ssl-certificate-errors/")])
N += 1

build_page('hsts-explained',
 'HSTS: HTTP Strict Transport Security',
 'HSTS explained: how the Strict-Transport-Security header forces HTTPS permanently, protects against downgrade attacks, and the risks of getting it wrong.',
 'HSTS: HTTP Strict Transport Security',
 'HSTS is one response header that changes your security posture permanently: once a browser sees it for your domain, it refuses to connect over HTTP at all, eliminating downgrade attacks and the "type http:// manually" gap.',
 [
  ("The header",
   '<pre class="rounded-lg border border-line bg-panel-2 p-4 font-mono text-xs leading-relaxed text-accent-soft">Strict-Transport-Security: max-age=31536000; includeSubDomains; preload</pre>'
   '<ul class="list-disc space-y-1.5 pl-5 mt-3"><li><strong class="text-ink">max-age:</strong> how long the browser remembers (seconds). Start small (300) while testing, raise to 31536000 once confident.</li><li><strong class="text-ink">includeSubDomains:</strong> forces HTTPS on every subdomain, including ones you add later.</li><li><strong class="text-ink">preload:</strong> permission to embed you in the browser-built-in list; the strongest form, and effectively irreversible.</li></ul>'),
  ("What HSTS stops",
   '<ul class="list-disc space-y-1.5 pl-5"><li>SSL-stripping attacks: the man-in-the-middle trick of downgrading to HTTP.</li><li>Users typing http:// or clicking http links on the first visit after the policy is cached.</li><li>Warnings suppressed: browsers fail hard instead of offering an override.</li></ul>'),
  ("The deployment ritual",
   '<ol class="list-decimal space-y-1.5 pl-5"><li>Confirm HTTPS works on the apex, www, and every subdomain.</li><li>Send max-age=300 for a week; watch for breakage.</li><li>Raise to max-age=86400, then 31536000.</li><li>Only then add includeSubDomains, and preload last, after submitting to hstspreload.org.</li></ol>'
   '<p>Rolling back preload is genuinely slow (list removal takes weeks through browser releases). Never preload a domain whose subdomains you do not fully control.</p>'),
 ],
 [("Does HSTS work on first visit?","Not from the header alone: first-visit protection requires the preload list. Hence the deployment ritual."),
  ["Does HSTS affect SEO?","Google indexes HTTPS preferentially; HSTS signals and enforces commitment. Redirects remain necessary for HTTP requests."],
  ["Can I exclude one subdomain?","Not with includeSubDomains active: that flag covers everything. Plan subdomains before enabling it."],
  ["What is HSTS for cookies?","The same idea applies to cookies (Secure flag): HSTS complements it by forcing the transport itself."],
  ["I set max-age=0 to disable HSTS. Did it work?","For browsers that saw the header: yes, max-age=0 expires the policy. Preload list removal is separate and slow."],
  ["Does my CDN handle HSTS?","Cloudflare and others can inject it; check the response header to confirm what is actually being sent."],
 ][1:6],
 [("SSL/TLS hub","/ssl-tls/"), ("Mixed content fixes","/mixed-content-fix/"), ("TLS versions","/tls-versions-explained/")])
N += 1

build_page('mixed-content-fix',
 'Mixed Content Warnings: Causes and Fixes',
 'Mixed content explained: why HTTPS pages loading HTTP resources trigger browser warnings, the types, and how to find and fix every occurrence.',
 'Mixed Content Warnings: Causes and Fixes',
 'A mixed-content warning means an HTTPS page is loading a resource over HTTP: the lock breaks, browsers block the resource, and users see "not fully secure." The fix is always the same hunt: find every http:// reference and upgrade it.',
 [
  ("The two types", T('Type', [
   ('Passive','Images, audio, video loaded over HTTP','Browsers may display but warn; content downgraded'),
   ('Active','Scripts, iframes, CSS, XHR over HTTP','Blocked outright: breaks the page'),
  ])),
  ("The hunt",
   '<ol class="list-decimal space-y-1.5 pl-5"><li>Open the browser console on the affected page: mixed-content errors list the exact blocked URLs.</li><li>Fix in source: change http:// to https:// (most resources exist over HTTPS), or make URLs protocol-relative, or use a CSP upgrade-insecure-requests header as a stopgap.</li><li>Database-driven content (WordPress posts, CMS bodies): a search-and-replace through the database, since the http:// links live in stored content.</li><li>Re-validate: the console should be silent and the padlock solid.</li></ol>'),
  ("Prevention",
   '<ul class="list-disc space-y-1.5 pl-5"><li>Add Content-Security-Policy: upgrade-insecure-requests as a safety net.</li><li>Never hardcode protocol in content URLs; use relative paths or https.</li><li>Check third-party widgets support HTTPS before embedding them.</li></ul>'),
 ],
 [("Does mixed content hurt SEO?","HTTPS pages with mixed content lose the secure-page treatment, and blocked resources can break rendering, which cascades into ranking."),
  ["Why do browsers block active content?","A script loaded over HTTP can be rewritten in transit even on an HTTPS page: it would defeat the entire encryption model."],
  ["What is the padlock with a warning?","Passive mixed content: the page loads but is flagged as 'not fully secure.'"],
  ["My images broke after moving to HTTPS. Why?","They are referenced over http:// and now blocked: update the URLs (often stored in the CMS database)."],
  ["Can I whitelist one HTTP resource?","No: the browser decides. The resource must move to HTTPS or be removed."],
  ["Does the CSP header fix it for users?","upgrade-insecure-requests rewrites subresource requests to HTTPS before fetching: a stopgap while you fix sources."],
 ][1:6],
 [("SSL errors guide","/ssl-certificate-errors/"), ("HSTS explained","/hsts-explained/"), ("SSL/TLS hub","/ssl-tls/")])
N += 1

build_page('ssl-certificate-errors',
 'SSL Certificate Errors: Causes and Fixes',
 'Every SSL certificate error explained: NET::ERR_CERT_DATE_INVALID, authority errors, name mismatches, and the fix for each by cause.',
 'SSL Certificate Errors: Causes and Fixes',
 'Certificate errors block pages outright with distinct error names. Each name is a diagnosis: expired, wrong name, untrusted chain, or self-signed. Match the error to the cause below and the fix is usually mechanical.',
 [
  ("The error decoder", T('Browser error', [
   ('NET::ERR_CERT_DATE_INVALID','Expired (or not yet valid) certificate','Renew now; check server clock for not-yet-valid'),
   ('NET::ERR_CERT_COMMON_NAME_INVALID','Certificate does not cover this hostname','Add the name to the SANs or issue a matching certificate'),
   ('NET::ERR_CERT_AUTHORITY_INVALID','Chain not trusted: self-signed or missing intermediate','Install the full chain; replace self-signed with a CA certificate'),
   ('ERR_SSL_VERSION_OR_CIPHER_MISMATCH','No common TLS version/cipher','Enable TLS 1.2/1.3 with modern suites'),
   ('NET::ERR_CERT_REVOKED','Certificate revoked by its CA','Reissue immediately; investigate why it was revoked'),
   ('HSTS errors','Policy forces HTTPS and something is broken','Fix the underlying TLS problem; HSTS blocks overrides'),
  ])),
  ("The universal diagnosis flow",
   '<ol class="list-decimal space-y-1.5 pl-5"><li>Click the warning, view the certificate: check dates, then Subject Alternative Names, then the issuer chain.</li><li>Test with an external checker (SSL Labs) to see the chain as strangers see it: missing intermediates often work on your machine via cached chains.</li><li>Confirm the certificate is served for THIS hostname: shared infrastructure sometimes serves the wrong vhost\u2019s certificate.</li></ol>'),
  ("Prevention",
   '<ul class="list-disc space-y-1.5 pl-5"><li>Automated renewal (ACME/Let\u2019s Encrypt) or managed certificates on your platform.</li><li>Expiry monitoring with alerts at 30 days.</li><li>Deploy the full chain (leaf + intermediates), and include every hostname variant in SANs.</li></ul>'),
 ],
 [("The date on the error says 1970 or 2036","The device clock is wrong, not the certificate: fix the system time."),
  ["Can I click through safely?","For a certificate you just issued and understand: maybe. For any public site: never, because that is exactly what phishing relies on."],
  ["Why does it work in one browser and not another?","Different certificate stores and HSTS state. Test in a private window and a second browser."],
  ["What is an intermediate certificate?","The CA\u2019s signing certificate linking yours to the trusted root; servers must serve it along with the leaf."],
  ["Does Let's Encrypt expire faster?","Yes: 90 days versus a year, by design for automation. Missing a renewal fails the same way any expiry does."],
  ["My site works but shows not secure in the address bar","That is mixed content, not a certificate error: an HTTPS page loading HTTP subresources."],
 ][1:6],
 [("Mixed content fixes","/mixed-content-fix/"), ("TLS versions","/tls-versions-explained/"), ("Certificate authorities","/certificate-authorities-explained/")])
N += 1

build_page('certificate-authorities-explained',
 'Certificate Authorities and the Web of Trust',
 'Certificate authorities explained: how CAs vouch for certificates, the web of trust, validation levels, and CAA records that constrain issuance.',
 'Certificate Authorities Explained',
 'A Certificate Authority (CA) is an organization that browsers pre-trust to vouch for the link between a domain and a public key. Every HTTPS connection starts with that trust: the CA is the third party that makes first contact with a stranger safe.',
 [
  ("How the trust works",
   '<ol class="list-decimal space-y-1.5 pl-5"><li>Root CAs are embedded in operating systems and browsers (a few dozen organizations).</li><li>Roots sign intermediate CAs; intermediates sign your certificates: a chain from browser trust to your domain.</li><li>CAs verify control of the domain before issuing (email, DNS, or file challenge), then the certificate is public in Certificate Transparency logs.</li></ol>'),
  ("Validation levels",
   '<ul class="list-disc space-y-1.5 pl-5"><li><strong class="text-ink">Domain Validation (DV):</strong> proof you control the domain. Minutes, free (Let\u2019s Encrypt). All a standard site needs.</li><li><strong class="text-ink">Organization Validation (OV):</strong> adds verified company details.</li><li><strong class="text-ink">Extended Validation (EV):</strong> deepest vetting; browsers no longer visually distinguish it much, so its practical value has narrowed.</li></ul>'),
  ("Trust is enforced, not assumed",
   '<p>CAs get audited and misissuance gets punished: when a CA fails, browsers distrust them (multiple have died this way). Your levers: <a href="/caa-record/">CAA records</a> restrict which CAs may issue for you, and Certificate Transparency monitoring alerts you when certificates appear that you did not request.</p>'),
 ],
 [("Which CA should I choose?","For standard needs: Let's Encrypt (free, automated). For organization-validated or wildcard-with-support needs: DigiCert, Sectigo, GlobalSign."),
  ["What happens if a CA is hacked?","Browsers revoke trust in the CA or its intermediates; certificates stop working. CAs have died this way, which is why the system self-corrects."],
  ["Why do certificates go into public logs?","Certificate Transparency makes every issuance observable, so fraudulent certificates for your domain become detectable within hours."],
  ["Can a CA issue for any domain?","Only after domain-control validation, and only if your CAA records permit that CA."],
  ["What is a root program?","The policy bundle a browser or OS maintains: which roots are trusted, and under what requirements (Chrome, Mozilla, Microsoft, Apple each run one)."],
  ["Do I need a paid certificate for e-commerce?","No: DV certificates provide identical encryption. Compliance and customer perception, not crypto, are the arguments for paid tiers."],
 ][1:6],
 [("SSL/TLS hub","/ssl-tls/"), ("CAA records","/caa-record/"), ("What is SSL/TLS","/what-is-ssl-tls/")])
N += 1

print('wrote', N, 'pages')
