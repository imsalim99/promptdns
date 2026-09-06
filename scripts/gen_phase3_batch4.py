# -*- coding: utf-8 -*-
"""Phase 3 batch 4: remaining 13 map pages + 5 alias redirects."""
import json

def bp(slug, title, desc, h1, intro, sections, faqs, related):
    faq_const = ("const faqSchema = " + json.dumps(
        {'@context':'https://schema.org','@type':'FAQPage',
         'mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in faqs]},
        ensure_ascii=False, indent=1) + "\n") if faqs else ""
    faq_line = "  schema={[faqSchema]}\n" if faqs else ""
    sec = ""
    for h2, html in sections:
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
         '      ' + faq_html + '\n') if faqs else
        ('      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Related</h2>\n'
         '      ' + rel + '\n')
    )
    if faqs:
        doc += '      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Related</h2>\n'
        doc += '      ' + rel + '\n'
    doc += '    </div>\n  </div>\n</BaseLayout>\n'
    open('src/pages/' + slug + '.astro', 'w', encoding='utf-8').write(doc)

def T(label, rows):
    _ = label
    trs = ''.join('<tr>' + ''.join('<td class="text-sm text-ink-dim">' + c + '</td>' for c in r) + '</tr>' for r in rows)
    return '<div class="overflow-x-auto rounded-xl border border-line bg-panel/60"><table class="pdns-table"><tbody>' + trs + '</tbody></table></div>'

def L(items):
    return '<ul class="list-disc space-y-1.5 pl-5">' + ''.join('<li class="leading-relaxed">' + x + '</li>' for x in items) + '</ul>'

N = 0

# ===== DNS OPERATIONS =====
bp('dns-migration-checklist',
 'DNS Migration Checklist', 'dns migration checklist',
 'The Complete DNS Migration Checklist',
 'Every step for a zero-downtime DNS migration, ordered by when to do it: from lowering TTLs to decommissioning the old server.',
 [
  ("24+ hours before: preparation", L([
    'Lower TTL on ALL records you\u2019ll change to 300 seconds.',
    'Export and back up every record from the current DNS host.',
    'Create the zone at the new provider and verify it answers identically.',
    'Keep the old server running: it must serve traffic during the transition.',
   ])),
  ("At cutover: make the change", L([
    'Update records at the new provider (not the old one).',
    'Change nameservers at the registrar if switching providers.',
    'Test with the propagation checker until resolvers agree.',
   ])),
  ("After: cleanup", L([
    'Raise TTLs back to 3600 on stable records.',
    'Flush local caches on test devices.',
    'Keep the old server live for 48 hours (NS delegation window) before decommissioning.',
    'Update your documentation with the new provider details.',
   ])),
 ],
 [
  ["How long does a DNS migration take?","The DNS change itself is instant at the authoritative server. Propagation takes one old-TTL cycle: minutes with TTL 300, up to 48 hours for nameserver changes."],
  ["Can I migrate without downtime?","Yes, by lowering TTL ahead of time and keeping the old server running during the transition window."],
  ["What breaks most often during migration?","Missing records (MX, TXT for verification), forgetting to lower TTL, and decommissioning the old server too early."],
  ["Do I need to change nameservers to migrate DNS?","Only if you\u2019re switching DNS providers. If you\u2019re just changing A records at the same host, nameservers stay the same."],
  ["Should I export my DNS records first?","Yes: always have a backup before any migration. Most providers offer an export option, or use the record lookup to capture current values."],
  ["What is the biggest migration mistake?","Decommissioning the old server before propagation completes. Cached answers still point there, and users hit a dead server."],
 ],
 [("DNS propagation explained","/dns-propagation/"), ("TTL explained","/what-is-ttl-in-dns/"), ("Propagation checker","/dns-propagation-checker/")],
)
N += 1

bp('export-dns-records',
 'How to Export and Back Up DNS Records',
 'export dns records backup',
 'How to Export and Back Up DNS Records',
 'Export your DNS records before any migration or provider switch: methods for every major provider and a manual fallback.',
 [
  ("Why export before changes", L([
    'A backup lets you restore records instantly if a migration goes wrong.',
    'It captures verification tokens and DKIM keys you might otherwise lose.',
    'It\u2019s the reference document for rebuilding the zone at a new provider.',
   ])),
  ("Export methods by provider", T('Provider', [
   ('Cloudflare','Export button in DNS, Records (downloads a BIND zone file)'),
   ('Route 53','Console: hosted zone, Export (or AWS CLI list-resource-record-sets)'),
   ('GoDaddy','No native export: screenshot the records table or use DNS lookup to capture values'),
   ('Namecheap','No native export: use Advanced DNS page or our record lookup per type'),
   ('Manual fallback','Run a record lookup for each type (A, MX, TXT, CNAME...) and save the output'),
  ])),
  ("What to include in your backup", L([
    'All record types: A, AAAA, CNAME, MX, TXT (SPF, DKIM, DMARC), NS, CAA.',
    'TTL values: they matter for the migration window.',
    'Priority values for MX and SRV records.',
    'The nameserver set at the registrar (delegation, not just the zone).',
   ])),
 ],
 [
  ["How often should I export DNS records?","Before any planned change, after any provider switch, and quarterly as a routine backup for business-critical domains."],
  ["Can I import an exported zone file?","Yes: BIND-format zone files import into most providers (Cloudflare, Route 53). Format-specific exports may need conversion."],
  ["What if I lose my DKIM keys?","Regenerate them from your email provider (they create new key pairs), then update the DNS record. Old mail signed with the old key will fail until the new one propagates."],
  ["Is there a tool to capture all records at once?","Yes: our all-in-one record lookup queries every type in one pass. Screenshot or copy the output as your backup."],
  ["Should I back up nameservers too?","Yes: note which nameservers your registrar points at. This delegation is separate from the zone records."],
  ["How do I restore records after a mistake?","Use your export as a reference and re-create the records in your DNS panel. Verification with the record lookup confirms restoration."],
 ],
 [("DNS migration checklist","/dns-migration-checklist/"), ("Record lookup","/dns-record-lookup/"), ("TTL explained","/what-is-ttl-in-dns/")],
)
N += 1

bp('change-dns-records-safely',
 'How to Change DNS Records Without Downtime',
 'change dns records safely without downtime',
 'How to Change DNS Records Without Downtime',
 'The safe record-change procedure: lower TTL, verify the new value, watch propagation, and keep the old path alive throughout.',
 [
  ("The procedure", L([
    '<strong class="text-ink">T-24 hours: Lower TTL</strong> to 300 on every record you\u2019ll change. This is the single most important step.',
    '<strong class="text-ink">T-24 hours: Back up</strong> all records (export or capture with the record lookup).',
    '<strong class="text-ink">T-0: Make the change</strong> in your DNS panel. Verify the new value with the record lookup immediately.',
    '<strong class="text-ink">T+0 to T+TTL: Monitor</strong> with the propagation checker. Resolvers disagree during this window: that\u2019s expected.',
    '<strong class="text-ink">T+TTL: Confirm and restore</strong> TTLs to 3600 once all resolvers return the new value.',
   ])),
  ("The three rules", L([
    'One change at a time: stacking changes makes diagnosis impossible.',
    'Never delete before you add: create the new record, verify, then remove the old.',
    'Keep the old server running: cached traffic still arrives at the old address for one TTL cycle.',
   ])),
 ],
 [
  ["What does 'without downtime' actually mean?","No user sees an error page. Some users hit the old server, others hit the new one during the propagation window, but both serve content."],
  ["Can I change multiple records at once?","Yes for unrelated records (a web A record and an MX record). For related records (several A records for the same service), change them together."],
  ["What if I need to roll back?","Re-create the old records from your backup. Propagation of the rollback takes one more TTL cycle."],
  ["Does changing DNS affect email?","Only if you change MX records. A/CNAME changes affect web traffic but not email routing (unless the mail host IP changes too)."],
  ["How do I know propagation is complete?","The propagation checker shows all resolvers returning the same answer. When they agree, propagation is done."],
  ["What is the safest day to change DNS?","Any day, if you follow the TTL procedure. Avoid Friday afternoons: if something goes wrong, support teams are unavailable over the weekend."],
 ],
 [("TTL explained","/what-is-ttl-in-dns/"), ("DNS migration checklist","/dns-migration-checklist/"), ("Propagation checker","/dns-propagation-checker/")],
)
N += 1

bp('website-not-resolving',
 'Website Not Resolving? DNS Causes and Fixes',
 'website not resolving DNS',
 'Website Not Resolving? DNS Causes and Fixes',
 'When a website won\u2019t load and the browser shows a DNS error, the problem is almost always in one of five places. This diagnostic finds it fast.',
 [
  ("The five causes, in diagnostic order", L([
    '<strong class="text-ink">1. The domain doesn\u2019t exist (NXDOMAIN).</strong> Typo in the URL, expired domain, or deleted record. Check: run the record lookup; NXDOMAIN means the name isn\u2019t in DNS.',
    '<strong class="text-ink">2. No A/AAAA record.</strong> The domain exists but has no address. Check: record lookup for A and AAAA; empty result means records are missing.',
    '<strong class="text-ink">3. Nameservers don\u2019t answer.</strong> Delegation is broken (lame delegation, expired domain, DNSSEC mismatch). Check: NS lookup shows the wrong set or SERVFAIL.',
    '<strong class="text-ink">4. Local cache has a stale answer.</strong> You see an old IP that no longer works. Check: propagation checker shows resolvers disagreeing; flush your local cache.',
    '<strong class="text-ink">5. The server is down (not DNS).</strong> DNS resolves correctly but the server doesn\u2019t respond. Check: record lookup shows the right IP; the site still doesn\u2019t load = server problem.',
   ])),
  ("Quick reference: error to cause",
   T('Browser error', [
    ('DNS_PROBE_FINISHED_NXDOMAIN','Domain doesn\u2019t exist (cause 1)'),
    ('ERR_NAME_NOT_RESOLVED','No A record or broken delegation (causes 2-3)'),
    ('ERR_CONNECTION_REFUSED','Server down (cause 5)'),
    ('ERR_CONNECTION_TIMED_OUT','Server unreachable: firewall or wrong IP (causes 2 or 5)'),
   ])),
 ],
 [
  ["How do I tell if it's DNS or the server?","If the record lookup returns the correct IP, DNS is fine: the problem is the server. If the lookup fails or returns wrong values, it\u2019s DNS."],
  ["Why does the site work on my phone but not my laptop?","Different DNS caches: your laptop has the old answer cached. Flush your local DNS cache."],
  ["Can expired SSL certificates look like DNS errors?","No: certificate errors show a different warning. DNS errors prevent the page from loading at all."],
  ["What if only one page on my site is broken?","That\u2019s not DNS: DNS resolves at the domain level, not per-page. The issue is server-side routing or the page itself."],
  ["How do I flush my DNS cache?","See our flush DNS guide for commands on Windows, macOS, Linux, and Chrome."],
  ["When should I contact my DNS provider?","When the authoritative answers are wrong (record lookup shows incorrect values you didn\u2019t set) or nameservers don\u2019t answer."],
 ],
 [("DNS error messages","/dns-error-messages/"), ("Flush DNS cache","/flush-dns-cache/"), ("Propagation checker","/dns-propagation-checker/")],
)
N += 1

bp('email-not-working-after-dns-change',
 'Email Stopped Working After a DNS Change',
 'email stopped working after DNS change',
 'Email Stopped Working After a DNS Change',
 'Email breaks after DNS changes more often than websites do, because mail uses more record types (MX, SPF, DKIM, DMARC) and each one can break independently.',
 [
  ("Diagnostic checklist", L([
    '<strong class="text-ink">Incoming mail broken?</strong> Check MX records with the record lookup. Were they accidentally deleted or changed during the DNS update?',
    '<strong class="text-ink">Outgoing mail going to spam?</strong> Check SPF (was it modified?), DKIM (is the selector still resolving?), and DMARC (is the policy still published?).',
    '<strong class="text-ink">Mail rejected with 5.7.x?</strong> A policy rejection: check the <a href="/blacklist-checker/">blacklist checker</a> and verify authentication records.',
    '<strong class="text-ink">Everything broken at once?</strong> The nameserver change may have replaced the entire zone. Check whether MX, SPF, and DKIM records still exist.',
   ])),
  ("The recovery procedure", L([
    'Identify which records are missing or changed (record lookup for each type).',
    'Restore them from your backup (you exported before the change, right?).',
    'Verify each record type individually: MX, SPF, DKIM, DMARC.',
    'Watch the propagation checker until all resolvers agree.',
    'Send test messages to Gmail, Outlook, and a colleague to confirm delivery.',
   ])),
 ],
 [
  ["Why does email break more often than websites after DNS changes?","Websites need one record (A). Email needs four working together (MX, SPF, DKIM, DMARC): four times the chances to break."],
  ["Can I receive mail if MX records are missing?","Not to your domain: senders have no routing instruction. Some servers fall back to the A record, but this is unreliable."],
  ["How long until email works after fixing MX?","The DNS fix propagates in minutes to hours. In-flight mail that bounced is lost (sender gets a bounce notice); new mail delivers normally."],
  ["Should I test email after DNS changes?","Yes: send to yourself at Gmail, Outlook, and a colleague. Check both delivery and spam placement."],
  ["What if only external senders can't reach me?","Internal mail may work via direct delivery. The issue is your MX records as seen by external resolvers: check propagation."],
  ["Does changing my A record affect email?","Only indirectly: if your mail server runs on the same IP as your website, changing the A record redirects web traffic but not mail (MX points at a hostname, not an IP)."],
 ],
 [("MX records","/mx-record/"), ["SPF records","/spf-record/"], ("DMARC guide","/dmarc/")],
)
N += 1

bp('email-ports-587-465-25',
 'Email Ports Explained: 25 vs 465 vs 587',
 'email ports 25 465 587',
 'Email Ports Explained: 25 vs 465 vs 587',
 'The three email ports serve different purposes: 25 for server-to-server relay, 587 for user submission with STARTTLS, and 465 for implicit TLS. Using the wrong one causes connection failures.',
 [
  ("The reference", T('Port', [
   ('25','Server-to-server relay (MX delivery)','Should NOT be used for user submission'),
   ('465','Implicit TLS submission (user to server)','Encrypted from the first byte; recommended'),
   ('587','STARTTLS submission (user to server)','Starts plaintext, upgrades to TLS; most common'),
  ])),
  ("Which should you use?",
   '<ul class="list-disc space-y-1.5 pl-5"><li><strong class="text-ink">Configuring your email client:</strong> 587 or 465, with authentication (username + password or app password). Both are secure.</li><li><strong class="text-ink">Server-to-server delivery:</strong> port 25, handled automatically by mail servers using MX records.</li><li><strong class="text-ink">Never expose port 25 to user devices:</strong> it\u2019s for infrastructure, and most ISPs block it on consumer lines.</li></ul>'),
 ],
 [
  ["Why is port 25 blocked on my network?","ISPs and cloud providers block it to prevent spam botnets from sending directly. Use 587/465 through your mail provider instead."],
  ["Is 465 more secure than 587?","465 uses implicit TLS (encrypted immediately); 587 starts plaintext and upgrades. Both are secure when configured correctly; 465 avoids the downgrade window."],
  ["What port does Gmail use?","587 for SMTP submission (smtp.gmail.com) with STARTTLS, or 465 with SSL. Both require authentication."],
  ["Can I run my own mail server on port 25?","Yes, but your ISP must unblock it (business lines usually allow it; consumer lines don\u2019t). You also need correct PTR, SPF, and DKIM."],
  ["What happens if I use the wrong port?","Connection refused or timeout: the server isn\u2019t listening on that port. The error message tells you which port to use."],
  ["Does the port affect deliverability?","No: the port is just transport. Deliverability depends on authentication, reputation, and content."],
 ],
 [("SMTP preflight","/smtp-tester/"), ("IMAP vs SMTP","/imap-vs-smtp/"), ("MX records","/mx-record/")],
)
N += 1

bp('how-to-read-email-headers',
 'How to Read Email Headers (With Examples)',
 'how to read email headers',
 'How to Read Email Headers',
 'Email headers contain the full delivery story: who sent the message, through which servers, and whether authentication passed. Reading them takes practice; this guide annotates a real header.',
 [
  ("The headers that matter",
   T('Header', [
    ('From','The display address the recipient sees','Can be spoofed: verify with Authentication-Results'),
    ('Authentication-Results','SPF, DKIM, DMARC verdicts from the receiving server','Your deliverability report card'),
    ('Received','The chain of servers, bottom (origin) to top (your inbox)','Read bottom-up to trace the path'),
    ('DKIM-Signature','The signing details including selector (s=) and domain (d=)','Use the selector to look up the public key'),
    ('Return-Path','The envelope sender (bounce address)','Should align with the From domain for DMARC'),
   ])),
  ("Red flags to look for",
   '<ul class="list-disc space-y-1.5 pl-5"><li>spf=fail or dkim=fail in Authentication-Results.</li><li>From address that doesn\u2019t match the Return-Path domain (alignment failure).</li><li>Received hops from unexpected countries or unknown providers.</li><li>Missing DKIM-Signature header entirely.</li></ul>'),
 ],
 [
  ["How do I view email headers?","Gmail: three-dot menu, Show original. Outlook: File, Properties, Internet headers. Apple Mail: View, Message, All Headers."],
  ["Are email headers always honest?","The bottom Received headers (closest to origin) are hardest to fake. Top headers can be injected by the sender. Authentication-Results are added by the receiving server, making them trustworthy."],
  ["What is the difference between From and Return-Path?","From is what the recipient sees. Return-Path is the technical bounce address. DMARC requires alignment between them (via SPF or DKIM)."],
  ["Can I trace where an email actually came from?","Yes: read the Received headers bottom-up. The first Received hop (bottom) is closest to the sender\u2019s server, with its IP address."],
  ["What does X-Mailer tell me?","The software the sender used (e.g., Outlook, PHP mail, a specific ESP). Useful for identifying automated or spoofed mail."],
  ["Should I worry about headers in emails I receive?","For suspicious emails, yes: header analysis reveals whether the claimed sender is genuine. Use our header analyzer to automate the check."],
 ],
 [("Email header analyzer","/email-header-analyzer/"), ("DMARC guide","/dmarc/"), ("SPF records","/spf-record/")],
)
N += 1

bp('nxdomain-attack',
 'NXDOMAIN Attacks and Random Subdomain Attacks',
 'NXDOMAIN attack',
 'NXDOMAIN Attacks and Random Subdomain Attacks',
 "NXDOMAIN attacks flood resolvers with queries for non-existent subdomains, exhaust resources, and can take an entire domain's DNS offline. Here's how they work and how to defend.",
 [
  ("How it works",
   '<ol class="list-decimal space-y-1.5 pl-5"><li>The attacker generates thousands of random subdomains: a1b2c3.yourdomain.com, x9y8z7.yourdomain.com...</li><li>Queries flood your authoritative nameservers and upstream resolvers.</li><li>Each query results in NXDOMAIN (the subdomain doesn\u2019t exist).</li><li>The flood exhausts nameserver resources and resolver negative caches.</li><li>In a targeted variant, random subdomains are chained to amplify DDoS traffic against the authoritative server.</li></ol>'),
  ("Defenses", L([
    '<strong class="text-ink">Response rate limiting (RRL):</strong> throttles identical NXDOMAIN responses from your nameserver.',
    '<strong class="text-ink">Negative caching:</strong> the SOA minimum TTL controls how long NXDOMAIN answers are cached, reducing repeat queries.',
    '<strong class="text-ink">Anycast DNS:</strong> distributes query load across global nodes, absorbing the flood.',
    '<strong class="text-ink">Managed DNS:</strong> Cloudflare, Route 53, and other providers absorb these attacks as part of their service.',
   ])),
 ],
 [
  ["Is my domain being attacked if I see random subdomain queries?","Possibly: check your DNS provider\u2019s query logs for volume spikes on non-existent names. The NXDOMAIN attack pattern is distinctive."],
  ["Does this affect my website visitors?","It can: if the flood exhausts your nameservers, legitimate queries also fail, making your entire domain unreachable."],
  ["How is this different from a DDoS attack?","NXDOMAIN attacks ARE a type of DDoS: they target the DNS layer specifically, using the protocol\u2019s own response mechanism as the weapon."],
  ["What is negative caching?","Resolvers caching NXDOMAIN answers so repeated queries for the same non-existent name don\u2019t hit your server again. It\u2019s a natural defense, controlled by the SOA minimum TTL."],
  ["Can I block specific query patterns?","Yes: response policy zones (RPZ) or your DNS provider\u2019s filtering rules can block queries matching known attack patterns."],
  ["Does DNSSEC help with NXDOMAIN attacks?","Not directly: DNSSEC signs existing records. The attack queries names that don\u2019t exist, so there\u2019s nothing to verify. Negative caching and rate limiting are the defenses."],
 ],
 [("DNS security","/dns-security/"), ["What is DNSSEC","/what-is-dnssec/"], ("Managed DNS providers","/dns-providers/")],
)
N += 1

bp('generative-engine-optimization',
 'Generative Engine Optimization (GEO): The Complete Guide',
 'generative engine optimization GEO',
 'Generative Engine Optimization (GEO): The Complete Guide',
 "GEO is the practice of optimizing your content to be cited by AI answer engines (ChatGPT, Perplexity, Gemini) rather than ranked by traditional search. The signals overlap with SEO but add machine-readability.",
 [
  ("How GEO differs from SEO",
   T('', [
    ('Goal','Rank in a list of links','Be cited as a source in an AI answer'),
    ('Optimization target','Keywords, backlinks, page speed','Machine-readability, structured data, authority signals'),
    ('Discovery path','User clicks a link','AI quotes your content with a citation'),
    ('Measurement','Rankings, organic traffic','Citation frequency, brand mentions in AI answers'),
   ])),
  ("The GEO checklist",
   '<ol class="list-decimal space-y-1.5 pl-5"><li><strong class="text-ink">Allow AI crawlers</strong> in robots.txt (deliberately, not by accident). <a href="/ai-crawler-checker/">Check your verdicts</a>.</li><li><strong class="text-ink">Publish llms.txt</strong> to give models a curated map. <a href="/llms-txt-generator/">Generate one</a>.</li><li><strong class="text-ink">Enable DNSSEC</strong> and full email authentication: domain-level trust signals. <a href="/what-is-dnssec/">Enable it</a>.</li><li><strong class="text-ink">Add structured data</strong> so entities are unambiguous. <a href="/schema-validator/">Validate your schema</a>.</li><li><strong class="text-ink">Create citable content</strong>: clear definitions, step-by-step processes, unique data. Content that answers a question completely gets cited.</li></ol>'),
  ("Measuring GEO",
   '<p>Ask ChatGPT, Perplexity, and Gemini questions your target audience would ask, and note whether your domain is cited. Track this monthly: AI citation is binary (cited or not), making it easier to measure than traditional rankings.</p>'),
 ],
 [
  ["Is GEO replacing SEO?","No: they coexist. Search still drives the majority of traffic, but AI answers are a growing discovery channel. The signals overlap significantly."],
  ["How do I get cited by ChatGPT?","Allow OAI-SearchBot (distinct from GPTBot), publish clear factual content, use structured data, and maintain domain trust signals (DNSSEC, authentication)."],
  ["Does GEO require different content?","Not fundamentally: clear, well-structured, factual content serves both. The additions are machine-readability (schema, llms.txt) and deliberate crawler policy."],
  ["Can I measure AI citations?","Manually: query AI engines with relevant questions and note citations. Automated tools are emerging but immature."],
  ["Is GEO relevant for small sites?","Yes, arguably more so: AI engines evaluate content quality rather than domain authority alone, giving smaller sites a citation opportunity."],
  ["How is GEO related to AI readiness?","AI readiness is the technical foundation (DNS, DNSSEC, crawler access, llms.txt). GEO is the content strategy built on that foundation."],
 ],
 [("AI readiness guide","/ai-readiness-guide/"), ("AI crawlers list","/ai-crawlers-list/"), ("What is llms.txt","/what-is-llms-txt/")],
)
N += 1

# ===== ESP-specific: Google Workspace and Microsoft 365 =====
bp('spf-dkim-dmarc-google-workspace',
 'Set Up SPF, DKIM & DMARC for Google Workspace',
 'Google Workspace SPF DKIM DMARC setup',
 'Set Up SPF, DKIM & DMARC for Google Workspace',
 'Complete Google Workspace email authentication: generate the DKIM key in Admin Console, add the SPF include, and publish DMARC, step by step.',
 [
  ("Step 1: Add the SPF include", L([
    'In your DNS panel, create or edit your SPF TXT record at the root domain.',
    'Add <code>include:_spf.google.com</code> to the existing record (or create: <code>v=spf1 include:_spf.google.com ~all</code>).',
    'Verify with the <a href="/spf-record-checker/">SPF checker</a>: it should show 1 lookup and pass.',
   ])),
  ("Step 2: Generate and publish DKIM", L([
    'Admin Console, Apps, Google Workspace, Gmail, Authenticate email.',
    'Select your domain and click Generate new record. Google creates a 2048-bit RSA key with selector google.',
    'Publish the TXT record at google._domainkey.yourdomain.com with the value Google displays.',
    'Back in the Admin Console, click Start authentication to activate signing.',
    'Verify with the <a href="/dkim-record-checker/">DKIM checker</a> using selector google.',
   ])),
  ("Step 3: Publish DMARC", L([
    'Create a TXT record at _dmarc.yourdomain.com.',
    'Start with: <code>v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com</code>.',
    'Read the aggregate reports for 2-4 weeks (use the <a href="/dmarc-report-analyzer/">report analyzer</a>).',
    'Step up to p=quarantine, then p=reject after confirming all legitimate mail passes.',
   ])),
 ],
 [
  ["How long does Google Workspace authentication take?","SPF verifies immediately after DNS propagation. DKIM takes effect after you click Start authentication and DNS propagates (minutes to hours)."],
  ["Do I need to add SPF for each user?","No: SPF is published once at the domain level and covers all users on the Google Workspace account."],
  ["What if I also use another email service?","Add that service\u2019s include to the same SPF record, and set up DKIM separately in that service. Watch the 10-lookup limit as services stack."],
  ["Why does my Gmail still show sent via or sent on behalf of?","This indicates alignment issues: the From address and the authenticated domain must match. Ensure you\u2019re sending from your own domain, not gmail.com."],
  ["Can I use a subdomain for Google Workspace?","Yes, but it\u2019s unusual. Most organizations use the primary domain for email and subdomains for other services."],
  ["What is the default DKIM key length in Google Workspace?","2048-bit RSA, which is the current standard. Older accounts may have 1024-bit keys: regenerate to upgrade."],
 ],
 [("Email authentication hub","/email-authentication/"), ("SPF flattener","/spf-flattener/"), ("DMARC guide","/dmarc/")],
)
N += 1

bp('spf-dkim-dmarc-microsoft-365',
 'Set Up SPF, DKIM & DMARC for Microsoft 365',
 'Microsoft 365 SPF DKIM DMARC setup',
 'Set Up SPF, DKIM & DMARC for Microsoft 365',
 'Complete Microsoft 365 email authentication: add the SPF include, enable DKIM with selector1/selector2, and publish DMARC, step by step.',
 [
  ("Step 1: Add the SPF include", L([
    'In your DNS panel, create or edit your SPF TXT record at the root domain.',
    'Add <code>include:spf.protection.outlook.com</code> to the existing record.',
    'Verify with the <a href="/spf-record-checker/">SPF checker</a>.',
   ])),
  ("Step 2: Enable DKIM", L([
    'Microsoft 365 Defender, Email & collaboration, Policies, DKIM: select your domain.',
    'Microsoft displays two CNAME records: selector1._domainkey and selector2._domainkey.',
    'Add both CNAME records in your DNS panel (they point to Microsoft\u2019s infrastructure).',
    'Back in Defender, click Enable DKIM signing. If it fails, wait 10 minutes for DNS propagation and retry.',
   ])),
  ("Step 3: Publish DMARC", L([
    'Create a TXT record at _dmarc.yourdomain.com.',
    'Start with: <code>v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com</code>.',
    'Monitor with the <a href="/dmarc-report-analyzer/">report analyzer</a>, then step to quarantine and reject.',
   ])),
 ],
 [
  ["Why do I need TWO DKIM CNAME records?","Microsoft uses selector1 and selector2 for zero-downtime key rotation. Both must be published even though only one is active at a time."],
  ["The Enable DKIM button fails. What now?","The CNAME records haven\u2019t propagated yet. Wait 10-15 minutes and retry. Also verify the CNAME values are exactly as Microsoft displayed."],
  ["Can I use a subdomain for Microsoft 365 email?","Yes, but you\u2019ll need to configure the accepted domain and MX records for that subdomain separately."],
  ["Do I need to add SPF for SharePoint or Teams notifications?","SharePoint and Teams notifications come from Microsoft\u2019s shared infrastructure and don\u2019t need additional SPF. The standard include covers all M365 mail."],
  ["What if I have a hybrid Exchange setup?","You need authentication records for both on-premises and M365 sending paths. This is more complex and requires careful planning."],
  ["How do I verify DKIM is actually signing?","Send a test email and check the DKIM-Signature header and Authentication-Results for dkim=pass. The DKIM checker confirms the DNS side."],
 ],
 [("Email authentication hub","/email-authentication/"), ("SPF flattener","/spf-flattener/"), ("DMARC guide","/dmarc/")],
)
N += 1

print('wrote', N, 'pages')
