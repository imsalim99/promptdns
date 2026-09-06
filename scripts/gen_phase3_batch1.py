# -*- coding: utf-8 -*-
"""Phase 3 batch 1: deliverability hub + cluster, IP/networking, SSL starter pages."""
import json, os

HEAD = """---
import BaseLayout from '../layouts/BaseLayout.astro';
import FaqAccordion from '../components/FaqAccordion.astro';
const faq = { schema }
---
"""
HEAD_SCHEMA = """---
import BaseLayout from '../layouts/BaseLayout.astro';
import FaqAccordion from '../components/FaqAccordion.astro';
const faqSchema = { schema }
---
"""

def page(slug, title, desc, h1, intro, body, faqs, related, schema=True):
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
        "---\n" + ("import BaseLayout from '../layouts/BaseLayout.astro';\nimport FaqAccordion from '../components/FaqAccordion.astro';\n" if False else
                    "import BaseLayout from '../layouts/BaseLayout.astro';\n") +
        faq_const +
        "---\n"
        "<BaseLayout\n  title=\"" + title + "\"\n  description=\"" + desc + "\"\n" + faq_line + ">\n"
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
    open(f'src/pages/{slug}.astro', 'w', encoding='utf-8').write(doc)

P = []

# ---------- HUB: email deliverability ----------
P.append(("email-deliverability", None))

# ---------- deliverability cluster ----------
P.append(("email-bounced-reasons", {
 "t": "Why Emails Bounce: Hard vs Soft Bounces",
 "d": "Email bounces explained: hard vs soft bounce types, what each SMTP code means, and the fix for the most common bounce reasons.",
 "i": "A bounce is the receiving mail server refusing your message and returning it with a reason code. Every bounce falls into two families, and telling them apart decides whether you fix, retry, or remove the address forever.",
 "b": [
  ("Hard bounces: permanent failure",
   '<p>The address is invalid and will never work: the mailbox does not exist, the domain has no mail setup, or the recipient server actively blocks you permanently. Codes like <code>550 5.1.1</code> (unknown user) are hard failures.</p><p><strong class="text-ink">The only correct action is removal.</strong> Continuing to send to hard bounces destroys your sender reputation and walks you toward spam traps.</p>'),
  ("Soft bounces: temporary failure",
   '<p>The problem is transient: a full mailbox (<code>552</code>), the server is temporarily down (<code>421</code>), greylisting is deferring you (<code>450</code>), or the message is too large (<code>552 message size</code>). Retry with backoff: most soft bounces deliver on the second or third attempt spaced hours apart.</p>'),
  ("The bounce codes that matter most",
   '<div class="overflow-x-auto rounded-xl border border-line bg-panel/60"><table class="pdns-table"><thead><tr><th>Code</th><th>Meaning</th><th>Action</th></tr></thead><tbody>'
   '<tr><td class="font-mono text-xs text-accent">550 5.1.1</td><td class="text-sm text-ink-dim">User unknown</td><td class="text-sm text-ink-dim">Remove address (hard)</td></tr>'
   '<tr><td class="font-mono text-xs text-accent">550 5.7.1</td><td class="text-sm text-ink-dim">Message rejected by policy</td><td class="text-sm text-ink-dim">Check authentication and blocklists</td></tr>'
   '<tr><td class="font-mono text-xs text-accent">421 / 450</td><td class="text-sm text-ink-dim">Temporary failure, greylisting</td><td class="text-sm text-ink-dim">Retry with backoff</td></tr>'
   '<tr><td class="font-mono text-xs text-accent">552</td><td class="text-sm text-ink-dim">Mailbox full / message too large</td><td class="text-sm text-ink-dim">Retry later; reduce attachments</td></tr>'
   '</tbody></table></div>'),
  ("The bounce-handling routine",
   '<ol class="list-decimal space-y-1.5 pl-5"><li>Parse every bounce for its code (your ESP usually classifies them automatically).</li><li>Suppress hard bounces immediately, permanently.</li><li>Retry soft bounces three times over 48 hours, then suppress.</li><li>Watch your bounce rate: above ~2% starts hurting inbox placement at Gmail and Yahoo.</li></ol>'),
 ],
 "f": [
  ("Do bounces hurt deliverability?","Yes, and rapidly: bounce rates above roughly 2% begin degrading inbox placement, and hard-bounce-heavy sending is a spam-trap magnet. Suppress bounces the day they happen."),
  ("What is the difference between a bounce and a spam complaint?","A bounce is the server refusing delivery before or at arrival; a complaint is a recipient marking your mail as spam after receiving it. Both damage reputation; complaints hurt more per event."),
  ("Can a hard bounce be temporary?","Rarely: a full mailbox that is later emptied, or a domain temporarily misconfigured. But the safe default is to treat 5.1.1 unknown-user as permanent."),
  ("Should I re-verify old lists before sending?","Yes: lists older than six months accumulate dead addresses. Email verification services catch most hard bounces before you send."),
  ("Does greylisting mean my mail failed?","No: greylisting (421/450) is a deliberate first-contact deferral. Legitimate servers retry, and the mail delivers on the second attempt."),
  ("How do I see my bounce rate?","Your ESP's campaign dashboard shows it; the sender-side log (postfix, SES) gives per-recipient codes for deeper analysis."),
 ],
 "r": [("Why emails go to spam","/why-emails-go-to-spam/"), ("Blacklist checker","/blacklist-checker/"), ("Email authentication hub","/email-authentication/")],
}))

P.append(("dedicated-vs-shared-ip", {
 "t": "Dedicated vs Shared IP for Email Sending",
 "d": "Dedicated vs shared IP for email: reputation isolation, warm-up requirements, cost, and how to decide which your sending volume actually needs.",
 "i": "A shared IP means your mail leaves alongside other senders' traffic; a dedicated IP is yours alone. The choice shapes who controls your sender reputation, how fast you can ramp, and what happens when someone else misbehaves.",
 "b": [
  ("The trade-off, plainly",
   '<div class="overflow-x-auto rounded-xl border border-line bg-panel/60"><table class="pdns-table"><thead><tr><th></th><th>Shared IP</th><th>Dedicated IP</th></tr></thead><tbody>'
   '<tr><td class="text-sm font-medium text-ink">Reputation</td><td class="text-sm text-ink-dim">Shared with the pool: neighbors affect you</td><td class="text-sm text-ink-dim">Yours alone: total control</td></tr>'
   '<tr><td class="text-sm font-medium text-ink">Warm-up</td><td class="text-sm text-ink-dim">Instant (pool is pre-warmed)</td><td class="text-sm text-ink-dim">2-6 weeks of gradual ramp</td></tr>'
   '<tr><td class="text-sm font-medium text-ink">Volume needed</td><td class="text-sm text-ink-dim">Any</td><td class="text-sm text-ink-dim">Only makes sense above ~50k emails/month</td></tr>'
   '<tr><td class="text-sm font-medium text-ink">Cost</td><td class="text-sm text-ink-dim">Included with most ESPs</td><td class="text-sm text-ink-dim">Add-on fee or your own server</td></tr>'
   '</tbody></table></div>'),
  ("How to decide",
   '<ul class="list-disc space-y-1.5 pl-5"><li><strong class="text-ink">Under ~50k/month or irregular sending:</strong> shared IP. A cold dedicated IP with low volume looks worse than a warm shared pool.</li><li><strong class="text-ink">High, consistent volume:</strong> dedicated, so one bad neighbor can never touch you and reputation is fully yours to build.</li><li><strong class="text-ink">Mixed mail (transactional + marketing):</strong> dedicated IPs for each stream, so marketing problems never delay receipts and password resets.</li></ul>'),
  ("If you go dedicated: warm-up discipline",
   '<p>A fresh IP has zero reputation. Start at a few hundred messages a day, roughly double every two to three days while engagement stays healthy, and keep authentication (<a href="/spf-record/">SPF</a>, <a href="/dkim/">DKIM</a>, <a href="/dmarc/">DMARC</a>) airtight throughout. Rushing warm-up is the fastest route to the spam folder.</p>'),
 ],
 "f": [
  ("Can I check whether my shared IP has problems?","Yes: run the blacklist checker and IP reputation scan on the IP your ESP sends from; repeated listings point at pool trouble worth escalating to the provider."),
  ("Does a dedicated IP guarantee better deliverability?","No. It guarantees isolated reputation. Deliverability still depends on authentication, list quality, and engagement."),
  ("How long does IP warm-up take?","Typically two to six weeks depending on daily volume and engagement quality; the schedule matters more than the speed."),
  ("Can I have both shared and dedicated?","Yes, and high-volume senders often do: dedicated for bulk marketing, shared or separate dedicated IP for transactional mail."),
 ],
 "r": [("Why emails go to spam","/why-emails-go-to-spam/"), ("Blacklist checker","/blacklist-checker/"), ("Email deliverability hub","/email-deliverability/")],
}))

P.append(("how-to-warm-up-email-server", {
 "t": "How to Warm Up an Email Server or New Domain",
 "d": "Email warm-up schedule: how to ramp a new server or domain from zero to full volume over 4-6 weeks without landing in spam.",
 "i": "Mailbox providers judge senders by history. A brand-new domain or IP has none, so the only safe strategy is to earn it: start small, deliver engagement, and ramp volume on a schedule. Rushing this is the single most common self-inflicted deliverability wound.",
 "b": [
  ("The 4-week ramp template",
   '<div class="overflow-x-auto rounded-xl border border-line bg-panel/60"><table class="pdns-table"><thead><tr><th>Week</th><th>Daily volume</th><th>Focus</th></tr></thead><tbody>'
   '<tr><td class="text-sm text-ink-dim">1</td><td class="text-sm text-ink-dim">10-50 to your most engaged contacts</td><td class="text-sm text-ink-dim">Openers who will reply: engagement signals build the base</td></tr>'
   '<tr><td class="text-sm text-ink-dim">2</td><td class="text-sm text-ink-dim">Double weekly</td><td class="text-sm text-ink-dim">Keep bounce rate under 2%; watch spam-folder placement</td></tr>'
   '<tr><td class="text-sm text-ink-dim">3</td><td class="text-sm text-ink-dim">Double again</td><td class="text-sm text-ink-dim">Introduce regular campaign content</td></tr>'
   '<tr><td class="text-sm text-ink-dim">4-6</td><td class="text-sm text-ink-dim">Reach target volume</td><td class="text-sm text-ink-dim">Only if placement and engagement stayed healthy</td></tr>'
   '</tbody></table></div>'),
  ("Non-negotiables during warm-up",
   '<ul class="list-disc space-y-1.5 pl-5"><li>Authentication complete before message one: <a href="/spf-record/">SPF</a>, <a href="/dkim/">DKIM</a>, <a href="/dmarc/">DMARC</a> at p=none minimum.</li><li>Reverse DNS set on the sending IP, matching your HELO name.</li><li>Send to your <em>best</em> addresses first: recent openers and clickers, never scraped or purchased lists.</li><li>Keep complaint rates near zero; pause and investigate at the first spike.</li><li>Monitor placement: seed accounts or the Gmail \"Why this message\" view across providers.</li></ul>'),
  ("Signs you are ramping too fast",
   '<p>Open rates collapsing mid-week, mail arriving in spam at Gmail/Outlook, or bounce codes shifting to policy rejections (5.7.x). The response is always the same: cut volume back to the last healthy level, hold for several days, then resume the ramp.</p>'),
 ],
 "f": [
  ("How long does warm-up take?","Typically 4-6 weeks to reach substantial volume; transactional-only servers with strong engagement can move faster, cold outreach slower."),
  ("Do I need to warm up a subdomain?","If it is newly created and will send at scale: yes. Reputation attaches to the sending identity, including subdomains."),
  ("Can warm-up tools help?","Engagement-based warm-up (automatic replies to simulated mail) has limited, debated value. Real engagement from real recipients is the durable path."),
  ("What volume is 'safe' immediately?","Small: tens to low hundreds per day from a new identity. Volume is earned, not configured."),
  ("Does DMARC need to be at reject before warm-up?","No: p=none with reporting is correct during warm-up; enforcement comes after the identity stabilizes."),
  ("My warm-up was fine but mail went to spam in week 3. Why?","Volume outgrew engagement, or a content/link change tripped filters. Cut volume in half, raise engagement, then resume."),
 ],
 "r": [("Dedicated vs shared IP","/dedicated-vs-shared-ip/"), ("Why emails go to spam","/why-emails-go-to-spam/"), ("Email deliverability hub","/email-deliverability/")],
}))

P.append(("email-sending-reputation", {
 "t": "Email Sender Reputation: How It Works",
 "d": "Email sender reputation explained: IP vs domain reputation, how mailbox providers score you, and the levers that move your score up or down.",
 "i": "Every sending identity carries a reputation score at each mailbox provider: a rolling judgment built from your volume, complaints, engagement, infrastructure, and authentication history. It is the invisible number that decides whether your campaign lands in the inbox or the junk folder.",
 "b": [
  ("Two reputations, two layers",
   '<ul class="list-disc space-y-1.5 pl-5"><li><strong class="text-ink">IP reputation:</strong> attached to the sending address. Damaged by spam volume from that IP, blocklist hits, and sudden spikes. Shared with other senders on pooled IPs.</li><li><strong class="text-ink">Domain reputation:</strong> attached to your From domain (via DMARC alignment). Survives IP changes, which is why aligned sending on a clean domain recovers faster than raw IP reputation.</li></ul>'),
  ("What moves the score",
   '<div class="overflow-x-auto rounded-xl border border-line bg-panel/60"><table class="pdns-table"><thead><tr><th>Signal</th><th>Direction</th></tr></thead><tbody>'
   '<tr><td class="text-sm text-ink-dim">Recipients marking spam</td><td class="text-sm text-fail">Strong negative</td></tr>'
   '<tr><td class="text-sm text-ink-dim">Low open/read rates over time</td><td class="text-sm text-warn">Negative drift</td></tr>'
   '<tr><td class="text-sm text-ink-dim">Consistent replies and folder moves to inbox</td><td class="text-sm text-pass">Strong positive</td></tr>'
   '<tr><td class="text-sm text-ink-dim">Blocklist listings</td><td class="text-sm text-fail">Severe negative</td></tr>'
   '<tr><td class="text-sm text-ink-dim">Stable volume + full authentication</td><td class="text-sm text-pass">Positive baseline</td></tr>'
   '</tbody></table></div>'),
  ("How to check and repair",
   '<p>Google Postmaster Tools shows domain/IP reputation for Gmail traffic (needs <a href="/dmarc/">DMARC</a> live). For broader signals: watch bounce and complaint rates in your ESP, run the <a href="/blacklist-checker/">blacklist checker</a> weekly, and confirm authentication with the homepage scanner. Repair recipe: fix authentication, cut volume to engaged contacts only, remove complainers, hold steady for two to four weeks while the score rebuilds.</p>'),
 ],
 "f": [
  ("How long does reputation damage last?","IP reputation: days to weeks of clean behavior. Domain reputation: two to eight weeks of disciplined sending; repeated abuse extends it."),
  ("Does a new domain start with neutral reputation?","Close to it, but new senders face extra scrutiny: Gmail and Yahoo apply stricter limits to domains without sending history."),
  ("Can one bad campaign ruin everything?","One campaign with high complaints does real damage; recovery follows the same recipe (authentication, engagement-only volume, patience)."),
  ("Do free From addresses (gmail.com) have reputation?","They use the provider's shared reputation: your ability to build independent domain reputation requires your own domain."),
 ],
 "r": [("Gmail and Yahoo sender requirements","/why-emails-go-to-spam/"), ("How to warm up","/how-to-warm-up-email-server/"), ("Email deliverability hub","/email-deliverability/")],
}))

P.append(("list-unsubscribe-header", {
 "t": "List-Unsubscribe Headers: Requirements and Setup",
 "d": "The List-Unsubscribe header explained: one-click unsubscribe requirements from Gmail and Yahoo, header syntax, and how ESPs implement it.",
 "i": "The List-Unsubscribe header is a machine-readable unsubscribe instruction inside the email itself. Since 2024 it is effectively mandatory: Gmail and Yahoo require a one-click unsubscribe for bulk senders, and enforcement means rejection, not just spam-foldering.",
 "b": [
  ("What the header looks like",
   '<pre class="rounded-lg border border-line bg-panel-2 p-4 font-mono text-xs leading-relaxed text-accent-soft">List-Unsubscribe: &lt;https://example.com/unsub/user-token&gt;, &lt;mailto:unsub@example.com?subject=unsubscribe&gt;\nList-Unsubscribe-Post: List-Unsubscribe=One-Click</pre>'),
  ("The pieces",
   '<ul class="list-disc space-y-1.5 pl-5"><li><strong class="text-ink">URL method:</strong> a link that unsubscribes in one click, without login or confirmation page (that is what List-Unsubscribe-Post: One-Click demands).</li><li><strong class="text-ink">mailto method:</strong> an unsubscribe address the client can email; legacy but still accepted.</li><li>The mail client renders its own native Unsubscribe button from this header, above your content.</li></ul>'),
  ("How it gets set up",
   '<p>You rarely add it by hand: reputable ESPs (Mailchimp, Klaviyo, SendGrid and friends) add the header automatically to campaigns. Your jobs are: keep the unsubscribe landing flow one-click compliant, never require login to unsubscribe, process opt-outs promptly, and verify the header exists on your live mail (view original message, check the headers).</p>'),
 ],
 "f": [
  ("Is List-Unsubscribe the same as the unsubscribe link in my footer?","No: the footer link is content; the header is metadata clients read to offer a native one-click unsubscribe. Bulk senders need both."),
  ("What happens without it?","Gmail and Yahoo's 2024 sender requirements classify non-compliant bulk mail toward rejection, and complaint rates rise because unsubscribing is harder than reporting spam."),
  ("Does one-click unsubscribe need a confirmation page?","No: confirmation pages defeat the point. One click, immediate opt-out, brief confirmation notice afterwards."),
  ("Can I use it for transactional email?","Transactional mail is generally exempt, but including the header harms nothing and respects user choice."),
 ],
 "r": [("Gmail and Yahoo sender requirements","/why-emails-go-to-spam/"), ("Why emails go to spam","/why-emails-go-to-spam/"), ("Email deliverability hub","/email-deliverability/")],
}))

P.append(("imap-vs-smtp", {
 "t": "IMAP vs SMTP vs POP3: Email Protocols Explained",
 "d": "IMAP vs SMTP vs POP3 explained: which protocol receives, which sends, how they work together, and which to choose for your devices.",
 "i": "Every email you send or receive uses at least two protocols: one to move mail between servers, one to sync it to your devices. SMTP sends; IMAP and POP3 receive. The differences decide how your mail behaves across phone, laptop, and webmail.",
 "b": [
  ("The division of labor",
   '<div class="overflow-x-auto rounded-xl border border-line bg-panel/60"><table class="pdns-table"><thead><tr><th>Protocol</th><th>Job</th><th>Ports</th><th>Behavior</th></tr></thead><tbody>'
   '<tr><td class="font-mono text-xs text-accent">SMTP</td><td class="text-sm text-ink-dim">Sending and server-to-server relay</td><td class="text-sm text-ink-dim">587 (STARTTLS), 465 (TLS), 25 (server relay)</td><td class="text-sm text-ink-dim">Push only: outgoing</td></tr>'
   '<tr><td class="font-mono text-xs text-accent">IMAP</td><td class="text-sm text-ink-dim">Receiving + multi-device sync</td><td class="text-sm text-ink-dim">993 (TLS)</td><td class="text-sm text-ink-dim">Mail stays on server; all devices mirror</td></tr>'
   '<tr><td class="font-mono text-xs text-accent">POP3</td><td class="text-sm text-ink-dim">Receiving to one device</td><td class="text-sm text-ink-dim">995 (TLS)</td><td class="text-sm text-ink-dim">Downloads and (usually) deletes from server</td></tr>'
   '</tbody></table></div>'),
  ("IMAP vs POP3: the real decision",
   '<p>IMAP keeps mail on the server: read on your phone, it shows as read on your laptop. POP3 downloads to one device and typically removes it from the server: fine for a single-desktop archive, poor for modern multi-device life. Default to IMAP unless you specifically want server-side deletion.</p>'),
  ("How they cooperate",
   '<p>You compose in your client, the client hands it to your SMTP submission server (587/465 with authentication), that server relays via SMTP port 25 to the recipient\u2019s MX host, and the recipient\u2019s IMAP/POP3 service delivers it to their devices. Both ends, four protocol touches.</p>'),
 ],
 "f": [
  ("Is SMTP only for sending?", "Yes: SMTP handles outgoing mail and server-to-server relay. Receiving uses IMAP or POP3 on the client side and delivery into the mailbox store on the server side."),
  ["Why is port 25 blocked on my ISP?","ISPs block outbound port 25 on consumer lines to stop spam botnets. Use your ISP's smarthost or a provider's submission port instead."],
  ["Should I use 465 or 587?","Either: 465 is implicit TLS from the first byte, 587 starts plaintext and upgrades via STARTTLS. Modern guidance accepts both; 587 is the traditional submission port."],
  ["Does IMAP need SMTP?","Yes: IMAP only stores and syncs. Sending always rides SMTP."],
  ["What is Exchange ActiveSync then?","A Microsoft sync protocol that handles mail, calendar, and contacts together; conceptually the IMAP+SMTP replacement in Microsoft ecosystems."],
  ["Can I use IMAP without TLS?","Technically yes on port 143, but you should never: credentials cross the network in plaintext. Always 993 with TLS."],
 ][0:6],
 "r": [["Email ports explained","/smtp-tester/"], ["Email authentication hub","/email-authentication/"]][0:2],
}))

# ---------- IP / networking ----------
P.append(("ipv4-vs-ipv6", {
 "t": "IPv4 vs IPv6: The Key Differences",
 "d": "IPv4 vs IPv6 compared: address space, notation, NAT, security model, and why dual-stack is the practical answer for every modern site.",
 "i": "IPv4 gives the internet about 4.3 billion addresses; IPv6 gives it 340 undecillion. That single difference drives everything else: exhaustion, NAT, carrier transitions, and why AAAA records exist alongside A records.",
 "b": [
  ("Side by side",
   '<div class="overflow-x-auto rounded-xl border border-line bg-panel/60"><table class="pdns-table"><thead><tr><th></th><th>IPv4</th><th>IPv6</th></tr></thead><tbody>'
   '<tr><td class="text-sm font-medium text-ink">Address size</td><td class="text-sm text-ink-dim">32-bit</td><td class="text-sm text-ink-dim">128-bit</td></tr>'
   '<tr><td class="text-sm font-medium text-ink">Total addresses</td><td class="text-sm text-ink-dim">~4.3 billion</td><td class="text-sm text-ink-dim">~340 undecillion</td></tr>'
   '<tr><td class="text-sm font-medium text-ink">Notation</td><td class="text-sm text-ink-dim">203.0.113.10 (decimal, dotted)</td><td class="text-sm text-ink-dim">2606:2800::1946 (hex, colon)</td></tr>'
   '<tr><td class="text-sm font-medium text-ink">NAT</td><td class="text-sm text-ink-dim">Ubiquitous (address scarcity workaround)</td><td class="text-sm text-ink-dim">Unnecessary by design</td></tr>'
   '<tr><td class="text-sm font-medium text-ink">DNS record</td><td class="text-sm text-ink-dim">A</td><td class="text-sm text-ink-dim">AAAA</td></tr>'
   '<tr><td class="text-sm font-medium text-ink">Broadcast</td><td class="text-sm text-ink-dim">Yes</td><td class="text-sm text-ink-dim">No (multicast instead)</td></tr>'
   '</tbody></table></div>'),
  ("Why dual-stack is the answer",
   '<p>Neither protocol is going away soon: IPv4 carries legacy and much of the existing internet; IPv6 is where mobile carriers and new networks prefer to live. Servers should answer on both (A + AAAA records, listeners on both stacks), which is exactly what our <a href="/aaaa-record/">AAAA guide</a> walks through. The failure mode to avoid is publishing AAAA without a working v6 path: v6-preferring clients time out while v4 users never notice.</p>'),
  ("What changes for webmasters",
   '<ul class="list-disc space-y-1.5 pl-5"><li>Firewall rules must cover the v6 address explicitly.</li><li>Reverse DNS exists in both worlds (in-addr.arpa and ip6.arpa).</li><li>Log analysis: the same visitor can appear under two addresses.</li><li>Security groups and allowlists need both entries.</li></ul>'),
 ],
 "f": [
  ("Is IPv6 faster than IPv4?", "Often slightly, on carrier networks that prefer it: fewer NAT hops. On well-peered v4 paths the difference is imperceptible."),
  ["Do I have to choose one?","No: dual-stack (both) is the standard deployment."],
  ["Why does IPv6 exist if NAT works?","NAT breaks end-to-end connectivity and merely delays exhaustion; IPv6 restores direct addressing at global scale."],
  ["Is IPv6 more secure?","IPsec support was designed in from the start, and scan-space is astronomically larger, but real security still depends on your configuration."],
  ["How do I test IPv6 connectivity?","Publish an AAAA record and load the site from a v6 connection, or use online v6 checkers; our AAAA lookup confirms what DNS publishes."],
  ["What is 6to4 or Teredo?","Legacy transition tunnels; modern deployments prefer native dual-stack and disable tunneling."],
 ][0:6],
 "r": [["AAAA record guide","/aaaa-record/"], ["A record guide","/a-record/"], ["Check your AAAA records","/dns-record-lookup/"]][0:3],
}))

P.append(("public-vs-private-ip", {
 "t": "Public vs Private IP Addresses",
 "d": "Public vs private IP addresses explained: RFC 1918 ranges, NAT translation, when each matters, and how to tell which one you are looking at.",
 "i": "Private IP addresses only work inside a local network; public IPs are routable on the internet. The distinction is defined by three reserved ranges, and confusing them causes a whole genre of configuration failure.",
 "b": [
  ("The private ranges (RFC 1918)",
   '<div class="overflow-x-auto rounded-xl border border-line bg-panel/60"><table class="pdns-table"><thead><tr><th>Range</th><th>Size</th><th>Typical use</th></tr></thead><tbody>'
   '<tr><td class="font-mono text-xs text-accent">10.0.0.0/8</td><td class="text-sm text-ink-dim">16.7M addresses</td><td class="text-sm text-ink-dim">Large enterprise networks</td></tr>'
   '<tr><td class="font-mono text-xs text-accent">172.16.0.0/12</td><td class="text-sm text-ink-dim">1M addresses</td><td class="text-sm text-ink-dim">Mid-size networks, some clouds</td></tr>'
   '<tr><td class="font-mono text-xs text-accent">192.168.0.0/16</td><td class="text-sm text-ink-dim">65k addresses</td><td class="text-sm text-ink-dim">Home routers, small offices</td></tr>'
   '</tbody></table></div>'),
  ("How they relate",
   '<p>Your laptop holds a private address (192.168.1.x from the router). Your router holds the single public IP (from your ISP) and translates between the two via NAT. Everything behind the router shares the public identity. Cloud VPCs work the same way at larger scale: instances get private IPs, a gateway holds the public one.</p>'),
  ("Where the confusion bites",
   '<ul class="list-disc space-y-1.5 pl-5"><li>Publishing a private IP in a public DNS record: the site resolves only inside your network.</li><li>Expecting a private IP to be reachable remotely: it is not routable, by design.</li><li>Firewall rules written for the public interface applied to private ranges (or vice versa).</li></ul>'),
 ],
 "f": [
  ("Which one is my real IP?", "For the internet: the public one (our What Is My IP tool shows it). The 192.168.x.x address on your laptop is local-only."),
  ["Can two networks use the same private IPs?","Yes, constantly: millions of homes all use 192.168.1.x. They never see each other, so no conflict."],
  ["Are private IPs more secure?","They are unreachable from outside, which is its own protection, but it is not a substitute for host security."],
  ["What about 127.0.0.1?","That is the loopback: the machine itself, a third category entirely (link-local and loopback are also non-routable)."],
  ["Can I make a private server public?","Only by exposing it through the gateway: port forwarding, a reverse proxy, or a public load balancer."],
  ["Do cloud providers use these ranges?","Yes: VPCs in AWS, Azure, and GCP are built on private ranges with public gateways."],
 ][0:6],
 "r": [["NAT explained","/public-vs-private-ip/"], ["What Is My IP","/my-ip/"], ["Reserved IP ranges","/public-vs-private-ip/"]][0:3],
}))

P.append(("what-is-a-cdn", {
 "t": "What Is a CDN and How Does It Work?",
 "d": "CDNs explained: how edge networks cache and serve your site globally, why DNS routes users to the nearest node, and what changes for your DNS records.",
 "i": "A Content Delivery Network stores copies of your site at hundreds of global locations (edge nodes) and serves each visitor from the closest one. The result: lower latency, absorbed traffic spikes, and an attack surface that is the CDN's problem instead of yours.",
 "b": [
  ("The mechanics",
   '<ol class="list-decimal space-y-1.5 pl-5"><li>You point your DNS at the CDN: either an A record to their anycast IPs or a CNAME to their hostname (flattened at the apex).</li><li>A visitor resolves your domain; DNS answers with the nearest edge node\u2019s address.</li><li>The edge serves cached content instantly; misses fetch from your origin and cache per your rules.</li><li>Dynamic requests pass through the edge to your origin over optimized routes.</li></ol>'),
  ("What it changes for you",
   '<ul class="list-disc space-y-1.5 pl-5"><li><strong class="text-ink">Your origin IP hides</strong> behind the CDN: an uptime and security win, and the reason A records point at edge IPs.</li><li><strong class="text-ink">Cache rules become configuration:</strong> what to cache, for how long, and what always passes through (APIs, logged-in pages).</li><li><strong class="text-ink">TLS is terminated at the edge:</strong> certificates are managed by the CDN or uploaded by you.</li><li><strong class="text-ink">Purge control matters:</strong> deploys need cache invalidation or versioned asset names.</li></ul>'),
  ("CDN vs no CDN",
   '<p>A personal blog on a single-region server gains global speed and DDoS absorption. An already-fast site gains resilience more than speed. What no site gains: freedom from correct DNS, because the CDN is only reachable if your records point at it reliably. Verify changes with the <a href="/dns-propagation-checker/">propagation checker</a>; CDN cutovers live and die on DNS.</p>'),
 ],
 "f": [
  ("Does a CDN host my website?", "No: it caches and serves copies. Your origin server or hosting remains the source of truth."),
  ["Why is my origin IP still visible?","Direct connections to historical IPs, subdomains not proxied, or mail records revealing infrastructure. Full origin hiding requires deliberate configuration."],
  ["Do CDNs work with dynamic content?","Yes: dynamic requests are not cached but still benefit from optimized routes between edge and origin."],
  ["What is cache poisoning then?","An attack on the cache itself: tricking the edge into storing attacker-controlled responses. Reputable CDNs defend against it; keep cache keys conservative."],
  ["Do I need a CDN with static hosting?","Static hosts on global platforms already behave like CDNs; a second layer is usually redundant."],
  ["How do I purge the cache after deploying?","Every CDN has a purge API/dashboard action; versioned asset filenames make most purges unnecessary."],
 ][0:6],
 "r": [["Cloudflare DNS-only vs proxied","/manage-dns-in-cloudflare/"], ["CNAME flattening","/cname-flattening/"], ["DNS propagation checker","/dns-propagation-checker/"]][0:3],
}))

P.append(("asn-explained", {
 "t": "What Is an ASN (Autonomous System Number)?",
 "d": "ASN explained: what autonomous systems are, how ASNs route internet traffic via BGP, and what an IP's ASN tells you in an IP lookup.",
 "i": "An Autonomous System is a network, or group of networks, operated under one administration with one routing policy: an ISP, a cloud provider, a university, a big company. Its ASN is the public ID it uses to announce its IP addresses to the rest of the internet.",
 "b": [
  ("How ASNs route the internet",
   '<p>The internet has no central switch: it is ~75,000 autonomous systems exchanging reachability via BGP (Border Gateway Protocol). Each AS announces the IP ranges it owns to its neighbors; those announcements propagate, and every router builds a map of where to send traffic. When you run an IP lookup, the ASN in the result is the network currently announcing that address.</p>'),
  ("What an ASN tells you in practice",
   '<ul class="list-disc space-y-1.5 pl-5"><li><strong class="text-ink">Who operates an address:</strong> AS13335 is Cloudflare, AS15169 is Google, AS16509 is AWS. In logs and IP lookups, the ASN is the fastest identity signal.</li><li><strong class="text-ink">Reputation context:</strong> mail from a residential ASN behaves differently from mail from a hosting ASN; filters notice.</li><li><strong class="text-ink">Routing health:</strong> BGP hijacks are ASN-level events; monitoring your own ASN\u2019s announcements is a real (if advanced) security practice.</li></ul>'),
 ],
 "f": [
  ("Who assigns ASNs?", "The five Regional Internet Registries (ARIN, RIPE NCC, APNIC, LACNIC, AFRINIC), which also allocate the IP blocks each AS announces."),
  ["Do I need an ASN?","Only if you operate a network that talks BGP with multiple providers. Hosting a server on someone else's network never requires one."],
  ["Why did an IP's ASN change?","Address blocks get transferred between networks, or announcements change during incidents; lookups reflect the current announcer."],
  ["Is an ASN public information?","Yes: ASN, name, and announced prefixes are public routing data, visible in every IP lookup."],
  ["What is a private ASN?","Ranges reserved for internal BGP (not routed publicly); used inside large enterprise networks."],
  ["Can one company have many ASNs?","Yes: after acquisitions or for separate product networks; each announces its own ranges."],
 ][0:6],
 "r": [["IP lookup tool","/ip-lookup/"], ["Reserved IP ranges","/public-vs-private-ip/"], ["IP and networking hub","/ip-lookup/"]][0:3],
}))

P.append(("static-vs-dynamic-ip", {
 "t": "Static vs Dynamic IP Addresses",
 "d": "Static vs dynamic IP explained: how dynamic assignment works, when a static IP matters, and the workarounds when you cannot get one.",
 "i": "A static IP never changes; a dynamic IP is leased from a pool and can change at your provider's whim. For browsing, the difference is invisible. For hosting, mail, remote access, and VPNs, it is the difference between working and broken.",
 "b": [
  ("How dynamic assignment works",
   '<p>Dynamic Host Configuration Protocol (DHCP): your device asks the network for an address, and a DHCP server leases one from a pool for a set time. Renewals usually return the same address, but reboots, outages, and lease expirations can hand you a different one. Most consumer ISPs assign dynamic addresses; business lines and cloud providers offer static as standard or paid options.</p>'),
  ("When static matters",
   '<ul class="list-disc space-y-1.5 pl-5"><li><strong class="text-ink">Self-hosting anything</strong> (website, mail, game server): DNS records and reverse DNS (PTR) assume a stable address.</li><li><strong class="text-ink">Firewall allowlists:</strong> partners granting you access by IP will break on a dynamic address.</li><li><strong class="text-ink">VPN endpoints and remote access:</strong> predictable addressing is the point.</li><li><strong class="text-ink">Email sending:</strong> dynamic space is blocklisted by policy on major lists (Spamhaus PBL exists for exactly this).</li></ul>'),
  ("The workaround when static is unavailable",
   '<p>Dynamic DNS (DDNS): a small client updates a hostname\u2019s DNS record whenever your address changes. It solves naming but not reputation: dynamic ranges still cannot send mail directly. For business needs, business-grade internet with a static IP (often a small monthly fee) is the clean answer.</p>'),
 ],
 "f": [
  ("Does a static IP improve speed or gaming?", "Not meaningfully: latency and bandwidth are routing properties, not address stability. Static addresses are about reachability, not performance."),
  ["Is a dynamic IP more private?","Marginally: your address changes, but tracking methods work around it, and the ISP still logs the assignment."],
  ["How do I know which I have?","Reboot your router and compare: a changed public address means dynamic (our What Is My IP tool shows it before and after)."],
  ["Can a dynamic IP be blocklisted?","Yes, and you inherit it: check new assignments with the IP reputation checker before sending mail."],
  ["What is a static lease?","A DHCP reservation: your device always receives the same PRIVATE address from the router. Useful internally, unrelated to your public IP."],
  ["Do cloud servers have static IPs?","Cloud VMs typically keep their address for the instance's life; Elastic IPs (AWS) and reserved IPs make it explicit and portable."],
 ][0:6],
 "r": [["What Is My IP","/my-ip/"], ["PTR records for mail","/ptr-record/"], ["IP reputation checker","/ip-reputation-checker/"]][0:3],
}))

# SSL cluster (2 pages)
P.append(("what-is-ssl-tls", {
 "t": "What Is SSL/TLS and Why HTTPS Matters",
 "d": "SSL/TLS explained: how certificates and encryption secure web traffic, the handshake process, and why HTTPS is non-negotiable today.",
 "i": "SSL is the retired name; TLS is the living protocol. Both refer to the encryption layer that turns HTTP into HTTPS: proving the server's identity with a certificate, then encrypting everything between browser and server so no one on the path can read or alter it.",
 "b": [
  ("What the handshake does",
   '<ol class="list-decimal space-y-1.5 pl-5"><li>The browser connects and proposes TLS versions and ciphers.</li><li>The server presents its certificate: identity + public key, signed by a Certificate Authority the browser already trusts.</li><li>The browser verifies the chain (and may check DNS-level CAA policy was respected at issuance).</li><li>Keys are agreed via ephemeral exchange; all further traffic is encrypted and tamper-evident.</li></ol>'),
  ("What TLS gives you, precisely",
   '<ul class="list-disc space-y-1.5 pl-5"><li><strong class="text-ink">Confidentiality:</strong> no one on the network reads your traffic.</li><li><strong class="text-ink">Integrity:</strong> content cannot be modified in transit without detection.</li><li><strong class="text-ink">Authenticity:</strong> the certificate proves you are talking to the real domain.</li></ul>'
   '<p>What it does not do: confirm the site is honest (a phishing site can have a valid certificate), or hide the domain you are visiting (that is <a href="/doh-vs-dot/">encrypted DNS</a> territory).</p>'),
  ("HTTPS is table stakes",
   '<p>Browsers mark plain HTTP as Not Secure, rank it lower, and block its subresources on HTTPS pages. Free certificates (Let\u2019s Encrypt) removed the cost excuse years ago. If any page of yours still serves HTTP, redirect it and enable HSTS; our homepage scanner checks the DNS-side trust signals that complement TLS.</p>'),
 ],
 "f": [
  ("Is SSL different from TLS?", "SSL is the old name (SSL 2.0/3.0, all broken and retired). Modern certificates are 'SSL certificates' colloquially, but the protocol in use is TLS 1.2/1.3."),
  ["How long are certificates valid?","Public certificates max out at 398 days (industry policy); Let's Encrypt issues 90-day ones meant for automated renewal."],
  ["Does a certificate mean the site is safe?","No: it means the connection is encrypted to THAT domain. Phishing sites get valid certificates too; TLS authenticates the domain, not the operator's honesty."],
  ["What is a certificate chain?","Your certificate signed by an intermediate, signed by a root CA pre-trusted in browsers. Missing intermediates cause the classic 'works for me' errors."],
  ["Do I need TLS on a site with no forms?","Yes: content integrity, browser warnings, ranking signals, and referral data all depend on it."],
  ["What breaks when certificates expire?","Browsers block the page outright. Automated renewal (ACME) exists precisely to prevent this."],
 ][0:6],
 "r": [["CAA records","/caa-record/"], ["Enable DNSSEC","/what-is-dnssec/"], ["Free certificates","/what-is-ssl-tls/"]][0:3],
}))

P.append(("https-vs-dnssec", {
 "t": "HTTPS vs DNSSEC: Encryption vs Authentication",
 "d": "HTTPS vs DNSSEC compared: TLS encrypts and authenticates your web connection, DNSSEC authenticates DNS answers, and you need to understand both layers.",
 "i": "HTTPS and DNSSEC both protect trust on the internet, at different layers: TLS protects the connection between browser and server; DNSSEC protects the DNS answers that led the browser there. They complement each other and neither substitutes for the other.",
 "b": [
  ("The layers",
   '<div class="overflow-x-auto rounded-xl border border-line bg-panel/60"><table class="pdns-table"><thead><tr><th></th><th>HTTPS (TLS)</th><th>DNSSEC</th></tr></thead><tbody>'
   '<tr><td class="text-sm font-medium text-ink">Protects</td><td class="text-sm text-ink-dim">Web traffic content + server identity</td><td class="text-sm text-ink-dim">DNS answers from tampering</td></tr>'
   '<tr><td class="text-sm font-medium text-ink">Trust anchor</td><td class="text-sm text-ink-dim">Certificate Authorities</td><td class="text-sm text-ink-dim">The DNS root chain</td></tr>'
   '<tr><td class="text-sm font-medium text-ink">Encryption</td><td class="text-sm text-ink-dim">Yes (confidentiality)</td><td class="text-sm text-ink-dim">No (signatures only)</td></tr>'
   '<tr><td class="text-sm font-medium text-ink">Failure mode</td><td class="text-sm text-ink-dim">Browser warning</td><td class="text-sm text-ink-dim">SERVFAIL (no answer)</td></tr>'
   '</tbody></table></div>'),
  ("Why both",
   '<p>Without DNSSEC, an attacker who can poison your resolver\u2019s cache can point your domain at their server; TLS makes the browser warn, but users click through warnings. Without TLS, valid DNS answers still deliver users to a server that reads everything. Defense in depth: <a href="/what-is-dnssec/">DNSSEC</a> guarantees the address is genuinely yours; <a href="/what-is-ssl-tls/">TLS</a> guarantees the session to it is private and intact.</p>'),
  ("The deployment checklist",
   '<ul class="list-disc space-y-1.5 pl-5"><li>TLS everywhere, HTTP redirected, HSTS enabled.</li><li>DNSSEC enabled at your DNS host with the DS published at the registrar.</li><li>CAA records restricting which CAs may issue for you.</li><li>Validate the whole stack with the <a href="/">homepage security scanner</a>.</li></ul>'),
 ],
 "f": [
  ("If I have HTTPS, do I still need DNSSEC?", "Yes: TLS cannot help if DNS redirects users before they ever reach your real server. DNSSEC closes that pre-connection gap."),
  ["Does DNSSEC encrypt my DNS queries?","No: it signs answers so tampering is detectable. Encrypting the queries themselves is DoH/DoT."],
  ["Which is harder to deploy?","TLS is now near-automatic (Let's Encrypt, platform defaults). DNSSEC is a toggle at good providers; the risk zone is manual key rotation."],
  ["Do both affect SEO?","HTTPS is a confirmed (small) ranking signal and mandatory for modern browser UX. DNSSEC is a trust and reliability signal."],
  ["What happens if either fails?","TLS failure: a visible certificate warning users can click past. DNSSEC failure: SERVFAIL, no page at all. Different symptoms, same outage effect."],
  ["Is DNSSEC why my mail fails?","Unrelated layers: mail authentication is SPF/DKIM/DMARC. But a DNSSEC misconfiguration takes down web AND mail resolution together."],
 ][0:6],
 "r": [["What is DNSSEC","/what-is-dnssec/"], ["What is SSL/TLS","/what-is-ssl-tls/"], ["DoH vs DoT","/doh-vs-dot/"]][0:3],
}))

# ---------- write all ----------
for item in P:
    if item[1] is None:
        continue
    d = dict(item[1])
    h1 = d.pop('t')
    desc = d.pop('d')
    intro = d.pop('i')
    body = d.pop('b')
    faqs = [tuple(x) for x in d.pop('f')]
    related = [tuple(x) for x in d.pop('r')]
    page(item[0], h1 + ' | PromptDNS', desc, h1, intro, body, faqs, related)
    print('wrote', item[0])

# hub page (special layout)
hub = """---
import BaseLayout from '../layouts/BaseLayout.astro';
---
<BaseLayout
  title="Email Deliverability: The Complete Guide"
  description="Email deliverability explained: authentication, sender reputation, blocklists, warm-up, and the infrastructure decisions that keep mail in the inbox."
>
  <div class="mx-auto max-w-4xl px-4 py-12">
    <nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">
      <a href="/" class="hover:text-accent">Home</a> <span aria-hidden="true">/</span>
      <span class="text-ink-dim">Email Deliverability</span>
    </nav>
    <h1 class="font-display text-3xl font-bold tracking-tight text-ink sm:text-4xl">Email Deliverability: The Complete Guide</h1>
    <p class="mt-5 text-lg leading-relaxed text-ink-dim">
      Deliverability is the discipline of getting mail delivered to the inbox instead of the spam
      folder or a bounce. It rests on four pillars: authentication (proving you are you),
      reputation (earned by behavior), infrastructure (IPs, PTR, TLS), and recipient engagement.
      This hub connects every piece.
    </p>

    <div class="mt-10 grid gap-4">
      {[
        { href: '/why-emails-go-to-spam/', title: 'Why emails go to spam', desc: 'The 14 causes, strongest first, with the fix for each.' },
        { href: '/email-bounced-reasons/', title: 'Why emails bounce', desc: 'Hard vs soft bounces, SMTP codes, and the handling routine.' },
        { href: '/email-sending-reputation/', title: 'Sender reputation', desc: 'How IP and domain reputation are built, damaged, and repaired.' },
        { href: '/how-to-warm-up-email-server/', title: 'Warm-up schedule', desc: 'Ramp a new server or domain over 4-6 weeks safely.' },
        { href: '/dedicated-vs-shared-ip/', title: 'Dedicated vs shared IP', desc: 'Which sending infrastructure your volume actually needs.' },
        { href: '/list-unsubscribe-header/', title: 'List-Unsubscribe headers', desc: 'The one-click unsubscribe requirement, implemented.' },
        { href: '/imap-vs-smtp/', title: 'IMAP vs SMTP vs POP3', desc: 'Which protocol does what, and ports that matter.' },
      ].map((s) => (
        <a href={s.href} class="group rounded-xl border border-line bg-panel/60 p-5 transition-all duration-300 hover:-translate-y-0.5 hover:border-accent/40">
          <h2 class="font-display font-semibold text-ink group-hover:text-accent">{s.title}</h2>
          <p class="mt-1 text-sm text-ink-dim">{s.desc}</p>
        </a>
      ))}
    </div>

    <div class="mt-12 rounded-xl border border-accent/25 bg-gradient-to-br from-accent/10 to-violet/10 p-6">
      <h2 class="font-display font-semibold text-ink">Start with the diagnosis</h2>
      <p class="mt-1 text-sm text-ink-dim">
        Run the <a href="/" class="font-medium text-accent hover:text-accent-soft">homepage security scanner</a> (SPF, DKIM,
        DMARC, DNSSEC in one pass), then the <a href="/blacklist-checker/" class="font-medium text-accent hover:text-accent-soft">blacklist checker</a>.
        Authentication and listings account for most deliverability failures.
      </p>
    </div>
  </div>
</BaseLayout>
"""
open('src/pages/email-deliverability.astro', 'w', encoding='utf-8').write(hub)
print('wrote email-deliverability hub')
print('TOTAL batch pages:', len(P) + 1)
