# -*- coding: utf-8 -*-
"""Generate the Provider DNS Playbooks: 8 majors x3 + 4 minors x2 + 2 comparisons."""
import json, os

MAJORS = {
"cloudflare": {
 "name": "Cloudflare",
 "panel": "The Cloudflare dashboard, dash.cloudflare.com: select your domain, then DNS, Records. Cloudflare is authoritative DNS for every domain on its nameservers, so all record management happens here, not at your registrar.",
 "addSteps": [
  ("Open the DNS panel", "dash.cloudflare.com, click the domain, then DNS, Records in the left menu."),
  ("Add the record", "Click Add record. Pick the type (A, CNAME, MX...), enter the name (the @ symbol means the root domain) and the value. TTL is auto-managed by Cloudflare."),
  ("Decide the proxy status", "The orange cloud (Proxied) routes traffic through Cloudflare's CDN and hides your origin IP; the grey cloud (DNS only) serves the raw record. Mail records (MX, SPF) must stay grey."),
  ("Save and verify", "Changes are live on Cloudflare's edge in seconds. Verify with the DNS record lookup, then check worldwide agreement with the propagation checker."),
 ],
 "nsPanel": "Cloudflare assigns your personal nameserver pair when the domain is added (shown on the Cloudflare DNS overview page). You don't change nameservers IN Cloudflare; you point your registrar at Cloudflare's pair.",
 "nsSteps": [
  ("Get your assigned pair", "Cloudflare dashboard, your domain, Overview: note the two nameservers (like ada.ns.cloudflare.com)."),
  ("Change them at the registrar", "Wherever the domain is registered (Namecheap, GoDaddy...), set Custom nameservers to Cloudflare's pair."),
  ("Wait for activation", "Cloudflare marks the domain Active when the registry delegation updates, usually 15-30 minutes, up to 24 hours."),
 ],
 "quirk": "Cloudflare proxies (orange-clouds) most records by default. That's great for websites and terrible for mail: an MX or SPF-related record that must stay DNS-only will break email if proxied.",
 "issues": [
  ("Error 522 or 521 on the website", "The origin server refused or timed out Cloudflare's proxy connection. Check that your server firewall allows Cloudflare IP ranges, and that the origin is actually up."),
  ("Mail breaks after adding the domain", "An MX/TXT record was proxied. Edit the record and switch it to DNS only (grey cloud)."),
  ("I see Cloudflare's nameservers but edits don't appear", "You may be editing a different Cloudflare account's zone, or the domain was added twice. Check the zone status is Active and you're in the right account."),
  ("DNSSEC mismatch errors after moving away", "If you previously enabled DNSSEC here, delete the DS record at your registrar before switching nameservers away, or the whole domain SERVFAILs."),
 ],
 "faqs": [
  ("Does Cloudflare charge for DNS?","No: the DNS plan is free for standard record counts, generous for any normal site."),
  ("Can I proxy MX records?","No, mail-related records must stay DNS only. Proxied mail is the most common Cloudflare misconfiguration."),
 ]
},
"godaddy": {
 "name": "GoDaddy",
 "panel": "GoDaddy account, My Products, Domains, next to the domain click DNS (or DNS, DNS Zones). The DNS Records table manages everything for domains using GoDaddy's nameservers.",
 "addSteps": [
  ("Open DNS records", "My Products, find the domain, click DNS. You land on the DNS Records table."),
  ("Add the record", "Click Add New Record. Choose the type, set Name (use @ for the root), Value, and TTL (600 seconds is the default and fine)."),
  ("Save", "Changes save per-record. Edits take effect after the old TTL expires, so drop TTL to 600 a day before any planned cutover."),
  ("Verify", "Use the DNS record lookup to confirm exactly what the world now sees."),
 ],
 "nsPanel": "Domain Settings page (not the DNS records page): Nameservers section, Change Nameservers. Choose GoDaddy's default (use GoDaddy nameservers) or Custom to point at another host such as Cloudflare.",
 "nsSteps": [
  ("Open Domain Settings", "My Products, the domain, Domain Settings tab (not DNS)."),
  ("Nameservers, Change", "Scroll to Nameservers, click Change Nameservers, pick Enter my own nameservers (custom)."),
  ("Paste and save", "Enter the two nameservers your new DNS host gave you, remove leftovers, Save. Registry delegation updates within the hour, full propagation up to 48 hours."),
 ],
 "quirk": "GoDaddy aggressively offers DNS add-ons and parking during the flow; also, after a nameserver change to an external host, GoDaddy's own DNS Records page stops being authoritative even though it still shows your records.",
 "issues": [
  ("Records edited in GoDaddy don't take effect","Your nameservers point elsewhere (Cloudflare, Route 53): GoDaddy's DNS page is no longer authoritative. Edit records at the current DNS host."),
  ("Site shows a GoDaddy parking page","Default parked-nameservers state. Set the correct A/CNAME records or switch nameservers to your DNS host."),
  ("Propagation seems stuck at 48 hours","GoDaddy sometimes leaves old NS TTLs long. Confirm the registry delegation updated with an NS lookup; then wait out caches."),
  ("Cannot add a CNAME at the root","Correct: the apex forbids CNAME. Use GoDaddy's Forwarding feature or an ALIAS-style host."),
 ],
 "faqs": [
  ("Is GoDaddy DNS free?","Yes, DNS hosting for domains registered there is included; the paid items are add-ons (premium DNS, SSL), not basic records."),
 ]
},
"namecheap": {
 "name": "Namecheap",
 "panel": "Namecheap account, Domain List, Manage next to the domain, then the Advanced DNS tab. Host Records is the table where A, CNAME, MX, TXT and friends live.",
 "addSteps": [
  ("Open Advanced DNS","Domain List, Manage, Advanced DNS tab."),
  ("Add the host record","Add New Record: choose type, set Host (@ for root, www for the alias, or a subdomain), Value, and TTL (60 minimum, 5min default is fine)."),
  ("Mind the toggle","At the top, Nameservers must be Namecheap BasicDNS / PremiumDNS / Custom DNS. If it says Web Hosting DNS, records on this tab are not what the domain uses."),
  ("Verify","Confirm live values with the record lookup before declaring victory."),
 ],
 "nsPanel": "Domain tab, Nameservers section: two dropdown states, Namecheap Web Hosting DNS (for Namecheap hosting customers), Namecheap BasicDNS (default), and Custom DNS for external hosts like Cloudflare.",
 "nsSteps": [
  ("Open Nameservers","Domain List, Manage, Domain tab, Nameservers dropdown."),
  ("Choose Custom DNS","Select Custom DNS and paste the two nameservers from your new DNS host (Cloudflare, Route 53...)."),
  ("Save and wait","Click the green check. Registry delegation updates within the hour; caches up to 48 hours."),
 ],
 "quirk": "The Web Hosting DNS vs BasicDNS/Custom DNS dropdown silently changes which record set is live. Records edited under the wrong mode do nothing.",
 "issues": [
  ("Edits on Advanced DNS do nothing","Nameservers are set to Web Hosting DNS or Custom: this tab is only live under Namecheap BasicDNS."),
  ("Parking page after transfer-in","Namecheap adds default parking records; replace the A/CNAME records with your own, or switch nameservers."),
  ("My free WHOIS guard exposes email","It doesn't: Namecheap includes free privacy on most TLDs; check Domain, Privacy tab."),
  ("Emails fail after adding MX","Mail-related records must not be proxied; on Namecheap there is no proxy, so check the MX values and priority numbers instead."),
 ],
 "faqs": [
  ("Minimum TTL on Namecheap?","60 seconds, handy for migrations. Raise it back to 5 minutes or more afterwards."),
 ]
},
"route53": {
 "name": "AWS Route 53",
 "panel": "AWS console, Route 53, Hosted zones. Each hosted zone holds the records; AWS assigns four nameservers per zone.",
 "addSteps": [
  ("Open the hosted zone","AWS console, Route 53, Hosted zones, click the zone."),
  ("Create record","Create record: choose Simple routing, define the record (name, type, value). Alias records can point at AWS resources (load balancers, CloudFront) directly."),
  ("TTL and verify","Set TTL (300 for volatile records, 3600 otherwise). Verify with the record lookup."),
 ],
 "nsPanel": "Route 53 gives the zone's four NS nameservers on the hosted zone page. To USE Route 53, your registrar's nameservers must be set to that NS set. To LEAVE Route 53, update the NS record inside the zone if your new host also manages it, and repoint the registrar.",
 "nsSteps": [
  ("Copy the NS set","Hosted zone details: copy all four nameservers."),
  ("Update the registrar","Set those four as custom nameservers wherever the domain is registered."),
  ("Wait and verify","Delegation updates within the hour typically; confirm with an NS lookup, then watch propagation."),
 ],
 "quirk": "Route 53 hosted zones cost about $0.50/month each (plus query charges) — the only DNS host in our playbook that bills for hosting. Also: NS and SOA records are managed records; don't delete them.",
 "issues": [
  ("Whole domain SERVFAIL after DNSSEC","The DS record at the registrar references old keys. Remove or update the DS, or complete the key-signing setup in Route 53."),
  ("Zone not answering","Hosted zone exists but the registrar still points at old nameservers: delegation must change at the registrar."),
  ("Unexpected monthly bill","Each hosted zone bills monthly; delete unused zones (and mind query charges on high-traffic domains)."),
  ("Alias vs CNAME confusion","Use Alias records for AWS resources: free queries, faster, apex-legal, unlike CNAME."),
 ],
 "faqs": [
  ("Why is Route 53 paid when others are free?","It's an AWS infrastructure service with SLAs and global anycast; pricing is per zone and per query, integrated into your AWS bill."),
 ]
},
"azure-dns": {
 "name": "Azure DNS",
 "panel": "Azure portal, search DNS zones, open the zone for your domain. Record sets are listed and created there.",
 "addSteps": [
  ("Open the DNS zone","Portal, DNS zones, click the zone (create one first if missing, in a resource group)."),
  ("Add a record set","+ Record set: name, type, TTL, then value(s). Azure groups multiple values of one type into a single record set."),
  ("Verify","Record lookup on the name and type; Azure's anycast answers within its region network quickly."),
 ],
 "nsPanel": "Each Azure DNS zone gets four nameservers (like ns1-03.azure-dns.com). Use them at your registrar to delegate the domain into Azure.",
 "nsSteps": [
  ("Copy the name servers","Zone overview page lists the four Azure nameservers."),
  ("Delegate at the registrar","Set them as custom nameservers where the domain is registered."),
  ("Verify delegation","NS lookup shows the azure-dns set; zone status in portal shows the domain registered."),
 ],
 "quirk": "Azure DNS zones bill per zone and per million queries, and the portal's record-set model (one set per name+type) confuses people expecting GoDaddy-style rows.",
 "issues": [
  ("Zone created but domain down","Registrar still points elsewhere: delegation must change at the registrar to Azure's four nameservers."),
  ("Cannot create the record set","A set with the same name+type exists: edit it instead of creating a duplicate."),
  ("SOA/NS records look odd","They're zone-managed; Azure maintains them, leave them be."),
 ],
 "faqs": [
  ("Azure DNS vs Azure Private DNS?","Public zones answer for internet domains (this guide). Private zones resolve names inside virtual networks only."),
 ]
},
"google-cloud-dns": {
 "name": "Google Cloud DNS",
 "panel": "Google Cloud console, Network Services, Cloud DNS: zones list, open a zone to manage its record sets.",
 "addSteps": [
  ("Open the zone","Console, Cloud DNS, click the public zone."),
  ("Add record set","Add record set: DNS name, resource record type, TTL, and data. Google groups values per name+type like Azure."),
  ("Verify","Record lookup confirms the values; changes serve from Google's anycast network rapidly."),
 ],
 "nsPanel": "The zone detail page shows the assigned nameservers (ns-cloud-XX.googledomains.com plus partners). Delegate at the registrar to these.",
 "nsSteps": [
  ("Copy the NS set","Zone details: Registrar setup section shows the exact nameservers."),
  ("Delegate","Set them at the registrar as custom nameservers."),
  ("Confirm","NS lookup shows the ns-cloud set; Google marks the zone as visible when delegation lands."),
 ],
 "quirk": "Zones live inside a GCP project: people edit the wrong project's zone constantly. Also the registrar-setup block is the authoritative NS list, not guesswork.",
 "issues": [
  ("Edits vanish","You were in another project's zone. Check the project selector."),
  ("Domain SERVFAIL after enabling DNSSEC","DS mismatch at the registrar; update or remove the DS to match the zone's DNSKEYs."),
  ("Propagation confusion","Google serves fast, but resolver caches obey TTLs: the propagation checker shows the truth."),
 ],
 "faqs": [
  ("Pricing?","Per managed zone and per million queries; free tier covers modest traffic. Billing lives in the GCP project."),
 ]
},
"cpanel": {
 "name": "cPanel (hosting)",
 "panel": "Your hosting account's cPanel, Domains section, Zone Editor. It manages the DNS zone for each domain on the hosting account, when your host runs the nameservers.",
 "addSteps": [
  ("Open Zone Editor","cPanel, Domains, Zone Editor, click Manage next to the domain (or use the quick +A Record / +CNAME buttons)."),
  ("Add the record","+Add Record: name, type, TTL (14400 default), record value. Save."),
  ("Watch defaults","cPanel adds a webmail/autoconfig CNAME set by default; don't delete mail-related records if you use the host's email."),
  ("Verify","Record lookup for each record you added; hosting NS changes can take longer."),
 ],
 "nsPanel": "cPanel is the DNS host, not the registrar: to point a domain AT this hosting's nameservers, get the two NS values from your host (often ns1.hostdomain.com) and set them at the registrar.",
 "nsSteps": [
  ("Get the host's nameservers","Hosting welcome email or cPanel home, General Information: the shared/reseller nameservers."),
  ("Set at the registrar","Custom nameservers at the registrar to those NS values."),
  ("Wait","Host NS changes are standard delegation: minutes to 48 hours."),
 ],
 "quirk": "Hosting providers often run cPanel AND the registrar role; changing nameservers at the host-registrar to their own defaults is usually a one-click preset.",
 "issues": [
  ("Emails fail after adding an addon domain","The zone was created without mail records; re-add MX (and webmail CNAME) in Zone Editor for that domain."),
  ("Zone Editor shows records that do nothing","Nameservers point elsewhere (Cloudflare etc.): edit records there instead."),
  ("Serial number errors after manual edits","cPanel manages serials; hand-edited zone files are the usual culprit for stale secondaries."),
 ],
 "faqs": [
  ("Is cPanel DNS separate from my registrar?","Yes: cPanel is hosting software. If your domain is registered elsewhere and pointed at the host's nameservers, cPanel's Zone Editor manages it."),
 ]
},
"plesk": {
 "name": "Plesk (hosting)",
 "panel": "Plesk panel, Websites & Domains, the domain, DNS Settings (or the DNS section per subscription). Plesk runs the zone when DNS is enabled for the subscription.",
 "addSteps": [
  ("Open DNS Settings","Websites & Domains, the domain, DNS Settings."),
  ("Add the record","Add Record: type, domain name, value. OK, then Update to apply."),
  ("Template awareness","Changes apply to the domain's zone; the DNS template only affects NEW domains."),
  ("Verify","Record lookup after saving; confirm the record with its TTL."),
 ],
 "nsPanel": "Plesk is hosting-side DNS: point the registrar at the host's nameservers (server-level NS values, provided by your provider). If you use external DNS, disable Plesk DNS for the domain to avoid split-brain zones.",
 "nsSteps": [
  ("Get the host NS","Provider docs or Plesk server info."),
  ("Delegate at the registrar","Custom nameservers to the host's NS pair."),
  ("Confirm one source of truth","If DNS is disabled in Plesk for the domain, records shown there are cosmetic only."),
 ],
 "quirk": "Plesk can disable its DNS per domain (Tools, DNS Settings, Disable). When disabled, the panel still shows the template records, which do nothing: the classic Plesk trap.",
 "issues": [
  ("Records exist but don't answer","Plesk DNS is disabled for that domain, or nameservers point elsewhere. One source of truth only."),
  ("Mail breaks after enabling external DNS","Mail records live in Plesk's zone; recreate MX/SPF/DKIM at the external DNS host when you move."),
  ("DNS template changes did nothing","Templates only affect newly created domains; edit the existing zone's records."),
 ],
 "faqs": [
  ("Should Plesk or Cloudflare hold DNS?","External anycast DNS (Cloudflare etc.) is more resilient than a single hosting server; keep Plesk DNS only for simplicity's sake."),
 ]
},
}

MINORS = {
"wix": {
 "name": "Wix",
 "connect": [
  ("Get Wix's values","Wix, Domains: either point nameservers to NS1.wixdns.net / NS2.wixdns.net (recommended) or use the Pointing method with Wix's displayed A/AAAA values."),
  ("Publish at the registrar","Set the nameservers or the A records per the chosen method."),
  ("Verify in Wix","Wix checks and shows the domain connected; SSL is then provisioned automatically."),
 ],
 "quirk": "Wix's Pointing method only covers the homepage well; the nameserver method is Wix's recommended path because it lets them manage records for you.",
 "faqs": [("How long until my Wix site loads on my domain?","Up to 48 hours after nameserver changes, usually much less. Check propagation with the checker.")],
},
"squarespace": {
 "name": "Squarespace",
 "connect": [
  ("Start the connection","Squarespace, Settings, Domains: Use a domain I own, enter it, choose Connect."),
  ("Publish the records","Squarespace shows verification CNAME plus four A records (198.185.159.x range); add all in your DNS host."),
  ("Verify","Back in Squarespace, click Refresh; SSL follows automatically after verification."),
 ],
 "quirk": "Squarespace requires all four A records plus the verification CNAME; adding only one A record gives intermittent site loads.",
 "faqs": [("Nameservers instead?","Squarespace offers a nameserver option (use squarespace.domains NS); the CNAME/A-record pointing method keeps your current DNS host, which is usually better.")],
},
"shopify": {
 "name": "Shopify",
 "connect": [
  ("Add the custom domain","Shopify admin, Settings, Domains: Connect existing domain."),
  ("Point the records","A record at @ to 23.227.38.65, and CNAME www to shops.myshopify.com (the exact address Shopify displays)."),
  ("Verify in Shopify","Domains page shows Connected once records propagate; SSL is issued by Shopify automatically."),
 ],
 "quirk": "Shopify's A record IP (23.227.38.65) is stable and documented; if an old tutorial shows a different IP, use Shopify's admin value.",
 "faqs": [("Keep my email working?","Yes: only add/replace the A and www records Shopify needs; leave MX/SPF/DKIM untouched.")],
},
"netlify": {
 "name": "Netlify",
 "connect": [
  ("Add the custom domain","Netlify, Site configuration, Domain management: Add custom domain."),
  ("Point DNS","Either Netlify DNS (nameservers) or external DNS: A record at @ to Netlify's load-balancer IP (75.2.60.5) and CNAME www to your netlify.app subdomain, as displayed."),
  ("HTTPS","Netlify provisions Let's Encrypt certificates automatically once DNS verifies."),
 ],
 "quirk": "Netlify's recommended external setup uses the load-balancer A record (single stable IP) rather than many rotating IPs; follow the values in your site's domain panel.",
 "faqs": [("Apex on Netlify without ALIAS?","The load-balancer A record makes the apex work with plain A records; no flattening tricks needed.")],
},
}

COMPARISONS = {
"cloudflare-dns-vs-google-dns": {
 "names": ["Cloudflare DNS", "Google Cloud DNS"],
 "rows": [
  ["Pricing","Free tier (records + bandwidth)","Per zone + per million queries"],
  ["Network","Global anycast, 300+ cities","Google's global backbone"],
  ["Proxy/CDN included","Yes (orange cloud)","No, DNS only"],
  ["DNSSEC","One-click, auto-managed","Supported, manual key handling"],
  ["Speed to resolve","Consistently top-tier (1.1.1.1 heritage)","Excellent, ties Cloudflare in most regions"],
  ["Best for","Websites wanting CDN + security bundled","GCP-centric teams consolidating on Google"],
 ],
 "verdict": "For most independent sites, Cloudflare wins on price and the bundled CDN/WAF. Google Cloud DNS earns its keep when your infrastructure already lives in GCP and you want IAM, logging, and billing unified.",
},
"cloudflare-vs-route53": {
 "names": ["Cloudflare DNS", "AWS Route 53"],
 "rows": [
  ["Pricing","Free records; paid plans add features","~$0.50/zone/mo + per-query charges"],
  ["Records model","Flat records; proxy toggle per record","Record sets; Alias records to AWS resources"],
  ["Propagation","Near-instant on edge","Fast; TTL-driven caching"],
  ["CDN/Security","Bundled (CDN, WAF, bot fights)","Separate products (CloudFront, WAF)"],
  ["API/Infrastructure","REST API, Terraform","Deep AWS integration, IAM, health-checked failover"],
  ["Best for","Sites wanting free fast DNS + CDN","AWS-native stacks needing health checks and routing policies"],
 ],
 "verdict": "Route 53 is the power tool for AWS architectures: health-checked failover, latency/geo routing, deep IAM. Cloudflare wins the default choice for everything else: free, faster to manage, and the bundled proxy changes what DNS can do for your site.",
},
}

# ---------- generate pages ----------
def page(kind, slug, data, extra_related=None):
    rel = data.get("related") or []
    base = [
      ["DNS record types reference", "/dns-records/"],
      ["TTL explained", "/what-is-ttl-in-dns/"],
    ]
    data["related"] = (extra_related or []) + base
    page = "---\nimport ProviderPlaybookTemplate from '../components/ProviderPlaybookTemplate.astro';\nconst data = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n---\n<ProviderPlaybookTemplate data={data} />\n"
    open(f'src/pages/{slug}.astro', 'w', encoding='utf-8').write(page)

n = 0
def provider_faqs(name):
    return [
      (f"How long do DNS changes take in {name}?", "The provider serves new values quickly, but resolvers keep old answers until each record's TTL expires. Verify live values with the record lookup, then watch the propagation checker until resolvers agree."),
      (f"Where do I find {name}'s nameservers?", "This playbook's nameservers guide covers the exact location. They are the delegation pair your registrar must point at for {name} to be authoritative."),
      (f"Should I lower TTL before changing records in {name}?", "Yes, for anything planned: set TTL to 300 seconds at least one old-TTL cycle ahead, make the change, confirm propagation, then restore the TTL."),
      (f"Can I keep email with one provider and DNS in {name}?", "Yes: DNS host and mail provider are independent. Publish the mail provider's MX, SPF, DKIM, and DMARC records in {name}, and keep those records unproxied."),
      (f"Which records should every domain have?", "A (and ideally AAAA) for the website, MX plus SPF/DKIM/DMARC for mail, and CAA to restrict certificate issuance. Everything else is per-service."),
    ]

for slug, d in MAJORS.items():
    name = d["name"]
    page('manage', f'manage-dns-in-{slug}', {
      "kind": "manage", "name": name,
      "title": f"How to Add and Manage DNS Records in {name}",
      "description": f"Add, edit, and delete DNS records in {name} step by step, with the gotchas that break sites and mail, and free tools to verify every change.",
      "intro": f"Managing DNS in {name} is a short walk once you know where the records live and which defaults to watch. This is the complete flow, with the verification step most guides skip.",
      "panel": d["panel"], "steps": d["addSteps"], "quirk": d["quirk"], "faqs": d["faqs"] + provider_faqs(name),
      "related": [[f"{name} DNS troubleshooting", f"/{slug}-dns-troubleshooting/"], [f"Change nameservers in {name}", f"/{slug}-change-nameservers/"]],
    }); n+=1
    page('nameservers', f'{slug}-change-nameservers', {
      "kind": "nameservers", "name": name,
      "title": f"How to Change Nameservers in {name}",
      "description": f"Change nameservers in {name} step by step: where the setting lives, what values to enter, and the propagation window to expect.",
      "intro": f"Nameserver changes are delegation changes: you're telling the internet which servers hold your domain's records. Here is exactly where {name} keeps that setting and what to expect.",
      "panel": d["nsPanel"], "steps": d["nsSteps"], "quirk": d["quirk"], "faqs": d["faqs"] + provider_faqs(name),
      "related": [["NS records explained","/ns-record/"], [f"Manage DNS records in {name}", f"/manage-dns-in-{slug}/"]],
    }); n+=1
    page('troubleshooting', f'{slug}-dns-troubleshooting', {
      "kind": "troubleshooting", "name": name,
      "title": f"{name} DNS Problems: Common Issues and Fixes",
      "description": f"The most common {name} DNS problems, from broken mail to SERVFAIL, with the diagnosis and fix for each.",
      "intro": f"Most {name} DNS complaints collapse into the same handful of causes. Match your symptom below; every fix includes the free tool that confirms it.",
      "issues": d["issues"], "quirk": d["quirk"], "faqs": d["faqs"] + provider_faqs(name),
      "related": [["Website not resolving?","/website-not-resolving/"], ["DNS error messages","/dns-error-messages/"]],
    }); n+=1

for slug, d in MINORS.items():
    name = d["name"]
    page('manage', f'manage-dns-in-{slug}', {
      "kind": "manage", "name": name,
      "title": f"How to Add DNS Records in {name}",
      "description": f"Add and manage DNS records for {name} domains and connected domains, step by step with verification.",
      "intro": f"{name} manages DNS a little differently from classic hosts: this is the flow, plus the records each integration actually needs.",
      "steps": d["connect"][:2], "quirk": d["quirk"], "faqs": d["faqs"] + provider_faqs(name)[:3],
      "related": [[f"Connect a domain to {name}", f"/{slug}-connect-domain/"]],
    }); n+=1
    page('connect', f'{slug}-connect-domain', {
      "kind": "connect", "name": name,
      "title": f"How to Connect a Domain to {name}",
      "description": f"Point your custom domain to {name}: exact records, method choice, and verification.",
      "intro": f"Connecting an existing domain to {name} takes two DNS changes done carefully. Here is the exact method and the verification step.",
      "steps": d["connect"], "quirk": d["quirk"], "faqs": d["faqs"] + provider_faqs(name)[:4],
      "related": [[f"Manage DNS records in {name}", f"/manage-dns-in-{slug}/"]],
    }); n+=1

for slug, d in COMPARISONS.items():
    a, b = d["names"]
    page('comparison', slug, {
      "kind": "comparison", "name": f"{a} vs {b}",
      "title": f"{a} vs {b}: Which Should You Use?",
      "description": f"{a} vs {b} compared: pricing, network, features, and the honest verdict for websites, teams, and AWS shops.",
      "intro": f"Both are excellent anycast DNS networks. The right choice depends on what you want DNS to do besides answering queries.",
      "rows": d["rows"], "colA": a, "colB": b,
      "steps": [("The short version", d["verdict"])], "faqs": provider_faqs(a)[:4] + [("Which is faster to resolve?","Both run global anycast networks; real-world differences are milliseconds and vary by region. Decide on features, integration, and cost."), ("Can I switch later?","Yes, DNS hosts are swappable: create the zone at the new host, delegate, wait out the 48-hour window before cancelling.")],
      "related": [["DNS providers hub","/dns-providers/"], ["What is DNS?","/what-is-dns/"]],
    }); n+=1

print('wrote', n, 'provider pages')
