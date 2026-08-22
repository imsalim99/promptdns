# -*- coding: utf-8 -*-
"""Generate dedicated record-lookup tool pages + pure client-side utility tools."""
import json, os

# --- Batch 1: 12 dedicated record lookup pages ---
LOOKUPS = [
 ("a","A Record Lookup","A record lookup for any domain: see the IPv4 addresses it points to, with TTLs, live via DNS-over-HTTPS.","The A record maps a hostname to its IPv4 address. Check yours to confirm where a domain points before and after migrations.","/a-record/"),
 ("aaaa","AAAA Record Lookup (IPv6)","AAAA record lookup: check any domain's IPv6 addresses and TTLs live over DoH.","The AAAA record is the IPv6 counterpart of the A record. Verify dual-stack setups and catch v6-only breakage.","/aaaa-record/"),
 ("mx","MX Record Lookup","MX record lookup: see which mail servers accept email for any domain, with priorities and TTLs.","MX records route inbound mail. Check yours to verify mail routing before and after provider changes.","/mx-record/"),
 ("ns","NS Record Lookup","NS record lookup: see which nameservers are authoritative for any domain.","NS records define delegation. Compare them against your DNS host's expected set to catch lame delegation.","/ns-record/"),
 ("txt","TXT Record Lookup","TXT record lookup: every text record on a domain, including SPF, DKIM keys, and verification tokens.","TXT records carry SPF, DKIM, DMARC, and hundreds of service verifications. See them all in one view.","/txt-record/"),
 ("soa","SOA Record Lookup","SOA record lookup: zone serial, timers, and primary nameserver for any domain.","The SOA record holds zone metadata. Compare serials to debug stale secondaries after zone changes.","/soa-record/"),
 ("cname","CNAME Record Lookup","CNAME record lookup: see the aliases any hostname points to.","CNAME records map aliases to canonical names. Verify service integrations and CDN pointers.","/cname-record/"),
 ("ptr","PTR Record Lookup (Reverse DNS)","PTR record lookup: resolve an IP address back to its hostname via reverse DNS.","PTR records power reverse DNS. Check the IP behind your mail server to confirm forward-confirmed matching.","/ptr-record/"),
 ("srv","SRV Record Lookup","SRV record lookup: find service endpoints (SIP, XMPP, game servers) with priority, weight, and port.","SRV records locate services by protocol. Verify clients can discover your servers.","/srv-record/"),
 ("caa","CAA Record Lookup","CAA record lookup: see which certificate authorities may issue TLS certificates for a domain.","CAA records restrict certificate issuance. Verify only your intended CAs are authorized.","/caa-record/"),
 ("ds","DS Record Lookup (DNSSEC)","DS record lookup: check whether a domain has an active DNSSEC delegation signer at the parent.","The DS record links your zone into DNSSEC's chain of trust. A missing or stale DS breaks validation.","/ds-record/"),
 ("dnskey","DNSKEY Record Lookup","DNSKEY record lookup: inspect a zone's DNSSEC public keys, flags, and algorithms.","DNSKEY records hold DNSSEC public keys. Verify KSK/ZSK presence and algorithm strength.","/dnskey-record/"),
]

os.makedirs('src/pages', exist_ok=True)
for slug, title, desc, intro, guide in LOOKUPS:
    t = slug.upper()
    page = f"""---
import BaseLayout from '../layouts/BaseLayout.astro';
import RecordLookupTool from '../components/RecordLookupTool.astro';
---
<BaseLayout title="{title}" description="{desc}">
  <div class="mx-auto max-w-4xl px-4 py-12">
    <nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">
      <a href="/" class="hover:text-accent">Home</a> <span aria-hidden="true">/</span>
      <span class="text-ink-dim">{title}</span>
    </nav>
    <h1 class="font-display text-3xl font-bold tracking-tight text-ink sm:text-4xl">{title}</h1>
    <p class="mt-4 text-lg text-ink-dim">{intro}</p>
    <div class="mt-8"><RecordLookupTool type="{t}" label="{title}" hint="Lookups run in your browser via public DNS-over-HTTPS. Nothing is logged." /></div>
    <article class="rich-text mt-12 max-w-none">
      <h2>Related</h2>
      <ul>
        <li><a href="{guide}">{t} records explained (guide)</a></li>
        <li><a href="/dns-record-lookup/">All-in-one record lookup</a> and <a href="/dns-propagation-checker/">propagation checker</a></li>
      </ul>
    </article>
  </div>
</BaseLayout>
"""
    # ptr lookup takes an IP; same component works (normalizeDomain passes IPs through fine)
    open(f'src/pages/{slug}-record-lookup.astro', 'w', encoding='utf-8').write(page)

print('wrote', len(LOOKUPS), 'record lookup pages')
