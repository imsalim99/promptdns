"""Replace the generic six-question FAQ boilerplate on flagship tool pages
with unique, result-state-derived FAQs (audit section 7.4/7.5 rules).
One-off content migration; content lives here as the source record.
Rules applied: unique questions per page, answer-first, no em dashes,
one truthful privacy FAQ per tool, FAQ text in JSON-LD matches visible text.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "src" / "pages"

FAQS = {
    "spf-record-checker.astro": [
        ("What does 'too many DNS lookups' mean in SPF?",
         "SPF evaluation is capped at 10 DNS lookup terms (include:, a, mx, ptr, exists:, redirect=). Beyond the cap the receiver stops evaluating and returns permerror, so the record stops protecting the domain. <a href=\"/spf-permerror/\" class=\"text-accent\">See the permerror guide</a>."),
        ("Can a domain have two SPF records?",
         "No. RFC 7208 requires exactly one v=spf1 record per domain; multiple records cause evaluation to end in permerror regardless of what they say. Merge all senders into a single record."),
        ("Should SPF end in ~all or -all?",
         "With DMARC enforcing policy, ~all (softfail) is the common safe default. Move to -all (hard fail) only once every legitimate sender is listed, or unlisted senders get rejected."),
        ("Why does SPF pass here but fail in Gmail headers?",
         "This checker inspects the published record only. Real evaluation depends on the sending server's IP, envelope-from alignment, and forwarding hops. Send a test message and read its Authentication-Results header for the verdict that matters."),
        ("How do I fix an SPF record over the lookup limit?",
         "Remove include: entries for services you no longer use and re-check. Avoid automatic flattening unless you monitor the result: flattened IP lists go stale when providers change infrastructure."),
        ("Is my domain sent to a server when I use this checker?",
         "No. The lookup runs in your browser against public DNS-over-HTTPS resolvers. PromptDNS has no server in the lookup path and stores nothing."),
    ],
    "dmarc-record-checker.astro": [
        ("What is a good DMARC grade?",
         "Grade A (p=reject with rua reporting) is the goal, but C (p=none with rua) is the correct starting point. Advance none to quarantine to reject as aggregate reports confirm every legitimate sender passes."),
        ("What does p=none actually do?",
         "It monitors only: receivers send aggregate reports but still deliver failing mail. Spoofed mail keeps reaching inboxes until the policy moves to quarantine or reject."),
        ("Why does the record need a rua address?",
         "Without rua= no aggregate reports are sent, so you cannot see who sends as your domain or confirm legitimate mail passes. A policy without reports cannot be tuned safely."),
        ("Can subdomains have a different DMARC policy?",
         "Yes, with the sp= tag. Without it, subdomains inherit the root domain's p= policy."),
        ("What is DMARC alignment?",
         "SPF or DKIM must pass AND the authenticated domain must match the visible From: domain. <a href=\"/dmarc-alignment/\" class=\"text-accent\">The alignment guide</a> explains relaxed versus strict matching with examples."),
        ("Is my domain sent to a server when I use this checker?",
         "No. The lookup runs in your browser against public DNS-over-HTTPS resolvers. PromptDNS has no server in the lookup path and stores nothing."),
    ],
    "dkim-record-checker.astro": [
        ("What is a DKIM selector?",
         "The label that names a DKIM key: the public key lives at selector._domainkey.yourdomain.com, and each signed message carries its selector in the s= field of the DKIM-Signature header."),
        ("Why does my provider's selector return nothing?",
         "A miss usually means the wrong selector name, not missing DKIM. Providers pick their own (google for Workspace, selector1/2 for Microsoft 365, k1 for Mailchimp). Find the real one in the s= field of a sent message's DKIM-Signature header."),
        ("Is a 1024-bit DKIM key a problem?",
         "It is considered weak, and some receivers reject or distrust mail signed with it. 2048-bit is the current standard; rotate the key in your provider's DKIM settings."),
        ("Does DKIM stop spoofing on its own?",
         "No. Receivers only act on DKIM failures through a DMARC policy. DKIM proves messages were not altered in transit and provides the identity DMARC aligns against."),
        ("Can a domain have multiple DKIM records?",
         "Yes, one per selector, and that is normal when several services send mail for you. Each service signs with its own selector."),
        ("Is my domain sent to a server when I use this checker?",
         "No. The lookup runs in your browser against public DNS-over-HTTPS resolvers. PromptDNS has no server in the lookup path and stores nothing."),
    ],
    "dns-propagation-checker.astro": [
        ("How long does DNS propagation take?",
         "It is governed by the record's TTL: each resolver may serve the old value until its cached copy expires, so worst case equals the full TTL. New names with no cached history resolve immediately everywhere."),
        ("Why do some resolvers still show old values?",
         "Their cached copy has not expired yet. The TTL column in the results shows how much longer each resolver may keep serving the old answer."),
        ("Can I speed up propagation?",
         "Not for a change already made. For future changes, lower the TTL to 300 seconds a day before, make the change, then raise it back."),
        ("Propagation finished but I still see the old site. Why?",
         "The remaining cache is usually local: your browser, operating system, or ISP resolver keeps its own copy. Flush the local DNS cache and restart the browser."),
        ("Which resolvers does this checker query?",
         "Cloudflare (1.1.1.1), Google (8.8.8.8), and AliDNS (223.5.5.5) over DNS-over-HTTPS, directly from your browser. These are three vantage points, not every network on earth."),
        ("Is my domain sent to a server when I use this checker?",
         "No. All queries run in your browser against the public resolvers above. PromptDNS has no server in the lookup path and stores nothing."),
    ],
    "blacklist-checker.astro": [
        ("Which blocklists does this checker query?",
         "The major publicly queryable lists, including SURBL, URIBL, SpamCop, SORBS, and Barracuda. Some lists (notably Spamhaus) refuse queries from public resolvers; those show as not checkable rather than clean, and should be verified on the list's own site."),
        ("My domain is listed. What now?",
         "Open the list's own site and read the return code, which states the reason. Fix the root cause (compromised account, open redirect, misconfigured server) before requesting delisting, or the listing returns. Our <a href=\"/remove-from-spamhaus-blocklist/\" class=\"text-accent\">removal guides</a> cover the big lists."),
        ("Why is a shared sending IP listed?",
         "Other customers of your email provider share that IP and caused the listing. Ask the provider to resolve it, send from your dedicated IP, or request delisting as their process allows."),
        ("I'm listed but my mail still delivers. Does it matter?",
         "Not every receiver consults every list, so delivery can continue while some providers silently spam-folder you. Treat any listing as deliverability risk to fix promptly."),
        ("How often should I check blocklists?",
         "Whenever deliverability drops, and routinely afterward. The listing reason tells you what to prevent next time."),
        ("Is my domain sent to a server when I use this checker?",
         "No. The queries run in your browser against public DNS-over-HTTPS resolvers. PromptDNS has no server in the lookup path and stores nothing."),
    ],
    "dmarc-report-analyzer.astro": [
        ("Where do I get a DMARC report file to upload?",
         "Mailbox providers email daily aggregate reports to the address in your rua= tag, usually as a .zip or .gz attachment. That attachment is exactly what you upload here; the file never leaves your browser."),
        ("Why won't my forensic report parse?",
         "This tool parses aggregate (rua) reports, the daily XML summaries. Forensic (ruf) failure reports have a different format and are not supported."),
        ("What does a failing source in the report mean?",
         "One of two things: a legitimate sender with broken SPF or DKIM that you should fix, or an unknown sender spoofing your domain, which your policy is catching. You tell them apart by whether you recognize the IP and its volume pattern."),
        ("What pass rate do I need before moving to p=reject?",
         "Every legitimate source should pass SPF or DKIM alignment with unknown sources expected to fail. Reject stops only what fails, so legitimate volume passing is the green light."),
        ("Why are Google and Microsoft the only reporters?",
         "A provider sends reports only for mail claiming your domain that passed through it. As your senders and volume vary across providers, so does who reports."),
        ("Is my report file uploaded anywhere?",
         "No. Parsing happens entirely in your browser with JavaScript; the file is never sent to any server."),
    ],
}

import re

def strip_html(s):
    s = re.sub(r'<a href="[^"]*" class="text-accent">', '', s)
    s = s.replace('</a>', '')
    return s

def schema_for(pairs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": strip_html(a)}}
            for q, a in pairs
        ],
    }

def details_html(pairs):
    parts = []
    for q, a in pairs:
        parts.append(
            '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
            f'<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">{q}'
            '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
            f'<p class="mt-3 text-sm leading-relaxed text-ink-dim">{a}</p></details>'
        )
    return '<div class="mt-3 grid gap-3">' + ''.join(parts) + '</div>'

changed = 0
for fname, pairs in FAQS.items():
    path = ROOT / fname
    lines = path.read_text(encoding="utf-8").splitlines(keepends=False)
    out, i, did_schema, did_div = [], 0, False, False
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("const faqSchema = {"):
            depth, j = 0, i
            while j < len(lines):
                depth += lines[j].count("{") - lines[j].count("}")
                if depth == 0 and j > i:
                    break
                j += 1
            out.append("const faqSchema = " + json.dumps(schema_for(pairs), indent=1))
            i = j + 1
            did_schema = True
            continue
        if line.lstrip().startswith('<div class="mt-3 grid gap-3"><details') and "How accurate are the results?" in line:
            out.append(details_html(pairs))
            i += 1
            did_div = True
            continue
        out.append(line)
        i += 1
    if not (did_schema and did_div):
        print(f"FAIL {fname}: schema={did_schema} div={did_div}")
        sys.exit(1)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    changed += 1
    print(f"OK {fname}: {len(pairs)} unique FAQs")

print(f"{changed} pages updated")
