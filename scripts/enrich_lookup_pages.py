# -*- coding: utf-8 -*-
"""Enrich the 12 record-lookup tool pages with per-type editorial articles + FAQs."""
import re, glob

NOTES = {
 "a": ("An A record answer is an IPv4 address belonging to the server or CDN edge that serves the domain. Multiple answers mean round-robin distribution: traffic splits across the listed addresses, with no health checking, so a dead server keeps its share until the record is edited.","The TTL column shows how long resolvers may cache each answer. High TTLs mean edits take hours to appear everywhere; low TTLs mean minutes. Compare values after any change to confirm the cutover landed."),
 "aaaa": ("An AAAA answer is an IPv6 address: the same role as an A record over the newer protocol. Dual-stack domains publish both record types, and visitors use whichever protocol their network prefers.","Empty AAAA results with a NOERROR status are common: the domain simply has no IPv6 yet. That is a future-proofing gap, not an emergency."),
 "mx": ("Each MX answer has two parts: a priority number and a mail hostname. Lower priorities are tried first; equal priorities share load. The hostname must itself resolve for delivery to work.","No MX records with a NOERROR status means senders fall back to the domain's A record. For mail-only subdomains that can be intentional; on a main domain it usually means email is not set up."),
 "ns": ("NS answers list the authoritative nameservers: the servers holding the domain's actual records. Two to four is typical, and they must match the delegation at the registrar.","Compare this answer against your DNS provider's documented set to catch lame delegation, the leading cause of intermittent resolution failures."),
 "txt": ("TXT answers are quoted strings whose prefixes identify their jobs: v=spf1 is SPF, v=DKIM1 is a DKIM key, v=DMARC1 is policy, and unprefixed strings are usually service verification tokens.","Long values are split into 255-character strings in DNS but shown joined here, which is how receivers read them: they concatenate before parsing."),
 "soa": ("The SOA answer packs the zone's metadata into one record: primary nameserver, admin contact (dot instead of @), serial, and four timers. The serial is the change counter secondaries watch.","If a manually edited zone serves stale data, the serial did not increase: this lookup reveals that immediately."),
 "cname": ("A CNAME answer is another hostname: the alias target. Resolvers restart the lookup at the target, so the final answer comes from its A or AAAA records.","If the target is also an alias the chain continues; one hop is healthy, long chains add latency and break when an intermediate hop moves."),
 "ptr": ("PTR answers map an IP back to a hostname via the in-addr.arpa reverse zone. Mail servers check these aggressively: a sending IP without a matching PTR scores as spam.","After reading the answer, verify forward confirmation: the hostname should resolve back to the same IP. The IP Lookup tool does both steps in one pass."),
 "srv": ("SRV answers carry four fields: priority (lower tried first), weight (share among equal priorities), port, and target hostname. The underscored prefix names the service and protocol.","The target must have its own A record: SRV does not usefully chase CNAME chains, so point it at an address-bearing name."),
 "caa": ("CAA answers use tags: issue permits a certificate authority, issuewild governs wildcards, iodef receives violation reports. Values are the CA's documented issuance domain.","No CAA records means any public CA may issue for the domain. Adding them restricts issuance to your list and shrinks the misissuance surface."),
 "ds": ("A DS answer proves DNSSEC delegation: the parent publishes a digest of your key-signing key as key tag, algorithm, digest type, and digest.","An empty answer on a signed zone is the dangerous state: keys exist but nobody can trust them. Publish the DS at the registrar."),
 "dnskey": ("DNSKEY answers are the zone's public keys: flag 257 marks the key-signing key referenced by the parent's DS, 256 the zone-signing key for everyday records.","Check the algorithm field: 13 (ECDSA P-256) or 15 (Ed25519) are modern and compact; long RSA keys work but bloat responses."),
}

FAQS = {
 "a": [("Why does the IP differ from my hosting panel?","A cached answer whose TTL has not expired, or a proxied CDN setup that intentionally hides the origin. Both are normal."),
       ("Can one A record point at several IPs?","Yes, that is round-robin distribution: it spreads load but does not remove dead servers from rotation."),
       ("A record vs CNAME for www?","A points www at an IP directly; CNAME aliases it. Never both on the same name."),
       ("How do I change my A record without downtime?","Lower TTL to 300 a day ahead, keep the old server live through the window, change the record, verify propagation, then decommission.")],
 "mx": [("Can MX point to an IP?","No: MX values are hostnames that must resolve to addresses themselves."),
        ("What MX priority should I use?","Distinct numbers, 10 and 20 by convention. Lower wins; equal values share load."),
        ("Why does mail arrive at the old server?","Cached MX records: lower TTL before provider changes and watch the propagation checker."),
        ("Do MX records affect outgoing mail?","No: MX routes incoming mail only. Outgoing authentication is SPF, DKIM, and DMARC.")],
}

def notes_for(slug):
    return NOTES.get(slug, ("Each answer comes live from a public DNS-over-HTTPS resolver: values, names, and TTLs exactly as resolvers worldwide receive them. TTL counts down from the zone's published value as caches age.","Cross-check changes with the propagation checker: it queries the same record across independent resolvers, showing whether the new value has spread or old answers still linger."))

def faqs_for(slug):
    if slug in FAQS: return FAQS[slug]
    return [("How often should I check this record?","After any change to it, after provider switches, and whenever symptoms point this direction. Records do not drift on their own."),
      ("Do these lookups work for subdomains?","Yes: enter any hostname. Subdomains carry their own records for many types."),
      ("Why do results differ from my DNS panel?","Panels show the authoritative zone; this shows what resolvers actually serve, which can be a cached earlier answer within TTL."),
      ("Is this lookup cached on my side?","The query runs fresh in your browser; any caching is the resolver's own, exactly as the wider internet experiences it.")]

patched = 0
for path in glob.glob('src/pages/*-record-lookup.astro'):
    s = open(path, encoding='utf-8').read()
    m = re.search(r'<RecordLookupTool type="([A-Z0-9]+)"', s)
    if not m:
        print('skip:', path); continue
    t = m.group(1)
    slug = 'aaaa' if t == 'AAAA' else t.lower()
    art1, art2 = notes_for(slug)
    faq_items = '\n'.join('        <li><strong>' + q + '</strong> ' + a + '</li>' for q, a in faqs_for(slug))
    start = s.find('    <article class="rich-text mt-12 max-w-none">')
    end = s.find('</article>', start)
    if start < 0 or end < 0:
        print('no article block:', path); continue
    block = (
        '    <article class="rich-text mt-12 max-w-none">\n'
        '      <h2>How to read the results</h2>\n'
        '      <p>' + art1 + '</p>\n'
        '      <p>' + art2 + '</p>\n'
        '      <h2>Common questions</h2>\n'
        '      <ul>\n' + faq_items + '\n      </ul>\n'
        '      <h2>Related</h2>\n'
        '      <ul>\n'
        '        <li><a href="/' + slug + '-record/">' + t + ' records explained (guide)</a></li>\n'
        '        <li><a href="/dns-record-lookup/">All-in-one record lookup</a> and <a href="/dns-propagation-checker/">propagation checker</a></li>\n'
        '      </ul>\n'
        '    </article>'
    )
    s = s[:start] + block + s[end + len('</article>'):]
    open(path, 'w', encoding='utf-8').write(s)
    patched += 1
print('patched', patched)
