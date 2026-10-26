"""One-off patch: visual semantics implementation (Koray framework).
- Attribute badges inside every ToolPanel (centerpiece annotation).
- Tool pages: compact H1, tool panel promoted above the fold.
- Entity-dense first tokens on descriptions.
"""
import pathlib, re

# ---------- 1. ToolPanel: attribute badges ----------
p = pathlib.Path("src/components/ToolPanel.astro")
s = p.read_text(encoding="utf-8")
old = """<section class="not-prose">
  <div class="glass rounded-xl p-5 shadow-lg">
    <slot />
  </div>
</section>"""
new = """<section class="not-prose">
  <div class="glass rounded-xl p-5 shadow-lg">
    <div class="mb-4 flex flex-wrap items-center gap-2" aria-label="Tool attributes">
      <span class="inline-flex items-center gap-1 rounded-full border border-pass/30 bg-pass/10 px-2.5 py-0.5 text-[11px] font-medium text-pass">
        <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M20 6L9 17l-5-5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        Free forever
      </span>
      <span class="inline-flex items-center gap-1 rounded-full border border-accent/30 bg-accent/10 px-2.5 py-0.5 text-[11px] font-medium text-accent">
        <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        No sign up
      </span>
      <span class="inline-flex items-center gap-1 rounded-full border border-violet/30 bg-violet/10 px-2.5 py-0.5 text-[11px] font-medium text-violet">
        <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
        Instant
      </span>
    </div>
    <slot />
  </div>
</section>"""
assert old in s, "ToolPanel anchor"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("ToolPanel badges: done")

# ---------- 2. tool page descriptions -> compact, entity-dense ----------
pages_dir = pathlib.Path("src/pages")
replacements = {
    "spf-record-checker.astro": (
        "Check any domain's SPF record: syntax validation, mechanism-by-mechanism breakdown, and the all-important 10-DNS-lookup limit.",
        "Free SPF checker: validate SPF syntax, count DNS lookups, find permerrors. No sign up.",
    ),
    "dmarc-record-checker.astro": (
        "Check any domain's DMARC record: policy strength, reporting configuration, alignment settings, graded A to F.",
        "Free DMARC checker: validate p= policy, rua reporting, alignment, subdomain sp=. No sign up.",
    ),
    "dkim-record-checker.astro": (
        "Look up a DKIM public key by selector, verify key type and length, and catch weak keys before Gmail does.",
        "Free DKIM checker: find selectors, verify key type and size, catch weak 1024-bit keys. No sign up.",
    ),
    "dns-propagation-checker.astro": (
        "Check whether your DNS changes have propagated. We query your record across independent public resolvers, when they all agree, your change is live everywhere.",
        "Free DNS propagation checker: query A, AAAA, MX, TXT, CNAME across Cloudflare, Google and AliDNS. No sign up.",
    ),
    "blacklist-checker.astro": (
        "Check a domain (and optionally a sending IP) against the major email blocklists. One listing can send all your mail to spam, find out now.",
        "Free blacklist checker: check your domain and IP against SURBL, URIBL, SpamCop, Barracuda and more. No sign up.",
    ),
    "dmarc-report-analyzer.astro": (
        "Upload a DMARC aggregate report (<span class=\"font-mono text-sm\">.xml</span> or the <span class=\"font-mono text-sm\">.zip</span> your mailbox received) and get a readable breakdown, parsed entirely in your browser, nothing uploaded anywhere.",
        "Free DMARC report analyzer: upload XML or ZIP aggregate reports and see every source IP, pass rate and disposition. Parsed in your browser.",
    ),
    "dnssec-checker.astro": (
        "Check whether a domain is signed: DS record at the parent, DNSKEYs in the zone, and key algorithm strength.",
        "Free DNSSEC checker: verify DS records, DNSKEY algorithms, and chain of trust. No sign up.",
    ),
    "ttl-checker.astro": (
        "See the TTL of every DNS record on a domain. Planning a migration? Anything above 300 seconds is a wait you can avoid.",
        "Free TTL checker: see every DNS record's cache time at once. Plan migrations, catch bloated caches. No sign up.",
    ),
}
for fname, (old_desc, new_desc) in replacements.items():
    fp = pages_dir / fname
    if not fp.exists():
        print(f"SKIP {fname} (not found)")
        continue
    txt = fp.read_text(encoding="utf-8")
    if old_desc in txt:
        txt = txt.replace(old_desc, new_desc, 1)
        fp.write_text(txt, encoding="utf-8")
        print(f"description: {fname}")
    else:
        print(f"SKIP desc {fname} (anchor not found)")

print("visual semantics patch done")
