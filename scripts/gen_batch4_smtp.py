import json
"""Batch 4: SMTP error-code pages (gap-analysis v2 batch 4, zero claim risk).
4 pages: 550 5.7.26, 550 5.7.1, 554 5.4.14, 421. Indexable from day one.
Structure per the SERP outline: H1, 3-sentence AnswerBlock, raw transcript block,
root-cause table, fix steps, cross-code comparison, edge cases, FAQs."""
import pathlib

OUT = pathlib.Path('src/pages')

PAGES = [
    dict(
        slug='smtp-550-5-7-26',
        code='550 5.7.26',
        cls='permanent',
        h1='SMTP Error 550 5.7.26: Meaning, Causes, and How to Fix It',
        title='SMTP Error 550 5.7.26: DMARC Rejection Explained and Fixed',
        description='SMTP 550 5.7.26 explained: Gmail DMARC rejection for unauthenticated mail. The 5 root causes, the exact fixes for SPF, DKIM and DMARC, and how to verify.',
        answer=("SMTP error 550 5.7.26 is a permanent rejection code defined by the enhanced status code system (RFC 3463) that Gmail returns when mail claiming your domain fails DMARC: it did not authenticate with SPF or DKIM, or the authentication did not align. "
                "Gmail applies it during the end-of-DATA phase when the sender's domain publishes an enforcing DMARC policy, and since 2024 it applies to all bulk senders (5,000+ messages per day to Gmail) under the sender requirements. "
                "The fastest way to isolate which mechanism failed is to paste the raw bounce into the email header analyzer and read the Authentication-Results line."),
        transcript='''550-5.7.26 [147-20-228-0.spf.example] This mail has been blocked because
550-5.7.26 the sender is unauthenticated. Gmail requires all senders
550-5.7.26 to authenticate with either SPF or DKIM.
550-5.7.26
550-5.7.26  Authentication results:
550-5.7.26  spf=none (sender IP is 203.0.113.9)
550-5.7.26  dkim=none (message not signed)
550-5.7.26  dmarc=fail action=reject header.from=example.com''',
        seg_table=('Code segment breakdown',
            [['550', 'Class', 'Permanent failure: do not retry the same message unchanged'],
             ['5.7.26', 'Enhanced status', 'Security/Policy step 7, reason 26: authentication required by policy'],
             ['header.from=example.com', 'Alignment test', 'The domain DMARC evaluated against']]),
        causes=('Root causes ranked by frequency',
            [['Missing both SPF and DKIM', 'spf=none, dkim=none in the results line', 'Publish an SPF include for your sender and enable DKIM signing', 'SPF and DKIM checkers'],
             ['DMARC enforcing with an alignment mismatch', 'Header From differs from the SPF or DKIM domain', 'Align the Return-Path or DKIM d= domain with the visible From domain', 'DMARC record checker'],
             ['SPF permerror', 'Record over 10 lookups or malformed', 'Rebuild the record; flatten or remove dead includes', 'SPF lookup limit auditor'],
             ['Bulk sender gaps', '5,000+ messages/day to Gmail without full authentication or one-click unsubscribe', 'Complete the Gmail sender requirements, including List-Unsubscribe-Post', 'Header analyzer'],
             ['Broken DKIM key', 'Selector published with empty or expired key material', 'Regenerate the key in your ESP and republish the selector', 'DKIM checker']]),
        fixes=['Run the SPF record checker: confirm exactly one v=spf1 record containing the include for every legitimate sender, within the 10-lookup limit.',
               'Run the DKIM checker on the selector your ESP signs with: the key must be live and at least 1024-bit (2048-bit preferred).',
               'Check the DMARC record: if p=reject or p=quarantine is live, every legitimate source must pass alignment first, or lower pct while you fix sources.',
               'For bulk senders: add List-Unsubscribe-Post (RFC 8058) headers and keep the spam-complaint rate under 0.1 percent.',
               'Resend only after the header analyzer shows spf=pass and dkim=pass with alignment; a 550 never clears by retrying unchanged.'],
        edge=('Two production edge cases cause most 5.7.26 surprises: auto-forwarding, which changes the envelope sender and breaks SPF alignment unless DKIM survives the hop, and ESP migrations, where the old include is removed before the new one is added. '
              'Continuous monitoring of the SPF, DKIM, and DMARC records catches the vendor-side drift that starts these bounces before your users report them.'),
        faqs=[
            ('Does 550 5.7.26 mean my domain is blacklisted?', 'No. This code is pure DMARC enforcement: the fix is authentication and alignment, not delisting. Blacklist issues usually return 550 5.7.1 instead.'),
            ('How long after fixing DNS does 5.7.26 stop?', 'Once the corrected records have propagated and your sender signs mail with the new values, the next message is evaluated fresh. Retrying the old queued message unchanged still bounces.'),
            ('Can the recipient whitelist me past 5.7.26?', 'No. Gmail applies DMARC policy domain-wide; there is no per-recipient bypass. The only fix is passing authentication on the sending side.'),
        ],
    ),
    dict(
        slug='smtp-550-5-7-1',
        code='550 5.7.1',
        cls='permanent',
        h1='SMTP Error 550 5.7.1: Meaning, Causes, and How to Fix It',
        title='SMTP Error 550 5.7.1: Delivery Not Authorized, Explained and Fixed',
        description='SMTP 550 5.7.1 explained: delivery not authorized. The causes from blacklists to missing PTR, relay denial and strict SPF, with the fix for each.',
        answer=("SMTP error 550 5.7.1 is a permanent rejection code (RFC 3463 enhanced status: delivery not authorized) that the receiving server returns when policy forbids accepting your message. "
                "The triggers span four layers: your sending IP sits on a blocklist, your reverse DNS fails forward-confirmation, your server attempted relay it is not permitted, or the recipient's SPF policy hard-failed you. "
                "Each cause has a different fix, so the first step is reading the full text after the code: the receiving server names its reason."),
        transcript='''550 5.7.1 Service unavailable; Client host [203.0.113.9] blocked
550 5.7.1 using Spamhaus. To request removal from the list see
550 5.7.1 https://www.spamhaus.org/query/ip/203.0.113.9''',
        seg_table=('Code segment breakdown',
            [['550', 'Class', 'Permanent failure'],
             ['5.7.1', 'Enhanced status', 'Delivery not authorized by policy'],
             ['blocked using Spamhaus', 'Named cause', 'The sending IP is on a DNS blocklist']]),
        causes=('Root causes ranked by frequency',
            [['Sending IP on a DNS blocklist', 'Spamhaus, Barracuda, SpamCop', 'Delist after fixing the sending behavior', 'Blacklist checker'],
             ['Missing or generic PTR record', 'Forward-confirmed reverse DNS fails', 'Ask the IP owner to publish a PTR matching your hostname', 'PTR record lookup'],
             ['Relay access denied', 'Your server tried to send through an MX that does not relay for you', 'Authenticate or correct the outbound MX configuration', 'SMTP tester'],
             ['Strict SPF hardfail', 'Sending IP is not in the recipient-visible SPF record', 'Add the include or IP, or soften to ~all during diagnosis', 'SPF record checker']]),
        fixes=['Read the full bounce text: the blocklist or policy is usually named after the code.',
               'If named: delist at the named service after fixing the sending behavior that caused the listing.',
               'If PTR is the cause: request a reverse DNS record from your hosting provider matching the mail hostname.',
               'If relay denied: your outbound path targets the wrong server; authenticate with the relay or fix the MX.',
               'If strict SPF: add the sending IP or include to the record, then verify with the SPF checker.'],
        edge=('Two edge cases cause repeat 5.7.1 pain: shared sending infrastructure, where one neighbor\u2019s bad behavior lists the whole pool and your only real fix is a dedicated IP, and forwarding chains, where a recipient\u2019s own forwarder re-sends from an IP you cannot influence. '
              'In the forwarding case the receiving admin must allowlist the forwarder, because no change on your side controls their hop.'),
        faqs=[
            ('Does 550 5.7.1 mean my domain is blacklisted?', 'Often the IP, not the domain: the bounce text names the blocklist. Run the blacklist checker on your sending IP to see every list at once.'),
            ('How do I stop 5.7.1 from recurring?', 'Fix the named cause and keep the sending behavior clean: authenticated, warmed, low-complaint volume. Repeat listings mean the source is still active.'),
            ('Can the recipient whitelist my address?', 'Yes: recipient-side allowlists bypass most 5.7.1 policy rejections. That works for a known partner, not for a campaign.'),
        ],
    ),
    dict(
        slug='smtp-554-5-4-14',
        code='554 5.4.14',
        cls='permanent',
        h1='SMTP Error 554 5.4.14: Meaning, Causes, and How to Fix It',
        title='SMTP Error 554 5.4.14: Mail Loop Detected, Explained and Fixed',
        description='SMTP 554 5.4.14 explained: hop count exceeded, the mail loop error. The four causes from connector loops to forwarding rules, and how to trace the Received chain.',
        answer=("SMTP error 554 5.4.14 is a permanent rejection (RFC 3463 enhanced status: routing loop detected) returned when the Received header count on a message exceeds the server's hop limit, typically 20 to 30 hops. "
                "The message bounced between two or more servers that each believed the next one was the destination: an outbound connector pointing back at the same MX, a forwarding rule that loops to itself, or an MX that resolves to a filter routing back to the sender. "
                "The diagnosis is the Received chain itself: paste the headers into the email header analyzer and read the loop directly."),
        transcript='''554 5.4.14 Hop count exceeded - possible mail loop
550 5.4.14 RESOLVER.POP.InvalidHopCount; message routed through
550 5.4.14 too many gateways''',
        seg_table=('Code segment breakdown',
            [['554', 'Class', 'Permanent failure: no retry'],
             ['5.4.14', 'Enhanced status', 'Routing loop detected (hop count exceeded)'],
             ['InvalidHopCount', 'Named cause', 'The Microsoft 365 resolver verdict for looping mail']]),
        causes=('Root causes ranked by frequency',
            [['Connector loop between gateways', 'M365 outbound connector routes back to *.mail.protection.outlook.com', 'Fix the connector address space so mail exits, not re-enters', 'Header analyzer'],
             ['Catch-all forwarding rule', 'A forwarding rule sends back to an alias on the same domain', 'Remove the self-referencing forwarding entry', 'MX record lookup'],
             ['MX points to a filter that points back', 'Spam filter MX chains to the same MX', 'Correct the filter outbound path', 'MX record lookup'],
             ['Excessive legitimate hops', 'Long forwarding chains past the hop limit', 'Shorten the chain or raise the hop limit where you own it', 'Header analyzer']]),
        fixes=['Read the Received headers bottom-up: each server appends a hop, and the loop repeats once you pass the point where routing went wrong.',
               'Identify the pair of servers trading the message: the same two hostnames appearing twice is the loop.',
               'Fix at the boundary you control: the outbound connector address space, the forwarding rule, or the MX record.',
               'Verify by sending a fresh message and confirming the Received chain terminates at your real mailbox host.'],
        edge=('The nastiest 5.4.14 variant: a user sets auto-forwarding on their mailbox to an external address, and the external address auto-forwards back to an alias on your domain. '
              'Each forward adds two hops until the limit trips. No MX change fixes it; the fix is the forwarding rule pair, and the Received chain names both servers so you know exactly which two admins to call.'),
        faqs=[
            ('Does 554 5.4.14 mean my message is lost?', 'Yes for that copy: the hop limit exists to stop infinite loops, and the message is not delivered. Fix the loop and send fresh.'),
            ('Why does only one recipient trigger 5.4.14?', 'The loop is in that recipient\u2019s routing: their forwarding or connector path. Other recipients on different paths never hit it.'),
            ('Can DNS changes cause 5.4.14?', 'Indirectly: an MX edit that points a domain back at a filter routing to itself creates the loop. Check the MX record after any change.'),
        ],
    ),
    dict(
        slug='smtp-421-temporary-error',
        code='421',
        cls='temporary',
        h1='SMTP Error 421: Meaning, Causes, and How to Fix It',
        title='SMTP Error 421: Service Not Available, Throttling Explained and Fixed',
        description='SMTP 421 explained: the transient service-unavailable code. Rate limiting, greylisting and TLS negotiation causes, and why retrying with backoff is the fix.',
        answer=("SMTP error 421 is a transient failure code (RFC 5321: service not available, closing transmission channel) telling the sending server the receiving mail service cannot take the message right now. "
                "The triggers are throttling during volume spikes, greylisting on unfamiliar sending IPs, concurrent connection limits, and TLS negotiation failures. "
                "Unlike a 5xx code, 421 means retry: RFC 5321 expects the sending server to try again with backoff, and most attempts succeed once the receiver's conditions clear."),
        transcript='''421 4.7.0 Try again later, closing connection
421-4.7.28 The IP address sending this message does not have a
421-4.7.28 PTR record setup, or the DNS lookup failed... Try again later''',
        seg_table=('Code segment breakdown',
            [['421', 'Class', 'Transient: retry with backoff'],
             ['4.7.0', 'Enhanced status', 'Security/policy step 7: throttling or policy hold'],
             ['Try again later', 'Receiver instruction', 'The message is not lost; the channel closed']]),
        causes=('Root causes ranked by frequency',
            [['Rate limiting', 'Sudden volume spike from one IP or domain', 'Slow the sending rate; volume that grew gradually rarely trips this', 'SMTP tester'],
             ['Greylisting', 'New sending IP unfamiliar to the receiver', 'Retry after the greylist window (minutes); the retry is accepted', 'SMTP tester'],
             ['Suspicious-activity hold', 'Gmail-style throttling after pattern changes', 'Keep the retry schedule; fix authentication while waiting', 'Blacklist checker'],
             ['TLS negotiation failure', 'Certificate or STARTTLS problems on the receiving MX', 'Fix the certificate chain on the receiving host', 'SMTP tester'],
             ['Concurrent connection limit', 'Too many simultaneous connections from one IP', 'Reduce parallel connections; queue the rest']]),
        fixes=['Retry with exponential backoff: 15 minutes, then 30, then hourly. RFC 5321 expects senders to keep trying 4xx responses for days.',
               'If throttling repeats: reduce the sending rate. 421 on a volume spike is the receiver protecting itself.',
               'If greylisting: a single retry after the window clears it permanently for that sender-receiver pair.',
               'Check authentication while waiting: 421 plus authentication gaps often escalates to a 550 once the hold clears.',
               'Verify the queue is aging properly: messages should retry for days, not expire in hours.'],
        edge=('The 421 that fools teams most: a greylisting deferral on a brand-new sending IP looks like a hard failure in a dashboard that collapses codes, and someone rewrites working SPF in response. '
              'Read the class digit before touching anything: 4xx is the receiver asking for patience, 5xx is the receiver refusing. They demand opposite responses.'),
        faqs=[
            ('Is 421 the same as my email being blocked?', 'No. 421 is a temporary refusal: the message is not accepted yet and the sender is expected to retry. Blocks use 5xx codes.'),
            ('How long should my server keep retrying a 421?', 'RFC 5321 expects retries for days; typical queues age messages 3 to 5 days. If every retry returns 421 for that long, contact the receiving admin.'),
            ('Does 421 mean my IP is on a blacklist?', 'Not by itself: 421 is throttling or unavailability. A blocklist rejection uses 550 5.7.1 with the list named in the text.'),
        ],
    ),
]

TMPL = '''---
{faq_const}import BaseLayout from '../layouts/BaseLayout.astro';
---
<BaseLayout
  title="{title} | PromptDNS"
  description="{description}"
  breadcrumb={{[["Home", "/"], ["Email Authentication", "/email-authentication/"], ["SMTP {code}"]]}}
>
  <div class="mx-auto max-w-4xl px-4 py-12">
    <nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">
      <a href="/" class="hover:text-accent">Home</a> <span aria-hidden="true">/</span>
      <a href="/email-authentication/" class="hover:text-accent">Email Authentication</a> <span aria-hidden="true">/</span>
      <span class="text-ink-dim">SMTP {code}</span>
    </nav>
    <p class="font-mono text-xs uppercase tracking-[0.2em] text-accent">{cls} error</p>
    <h1 class="font-display mt-2 text-3xl font-bold tracking-tight text-ink sm:text-4xl">{h1}</h1>
    <div class="pd-answer" data-vs="answer">
      <p class="text-lg leading-relaxed text-ink-dim">{answer}</p>
    </div>

    <section class="not-prose my-8" aria-label="Raw bounce transcript">
      <div class="glass rounded-2xl p-5 shadow-lg sm:p-7">
        <p class="font-mono text-[10px] uppercase tracking-[0.18em] text-accent mb-3">Raw bounce transcript</p>
        <pre class="overflow-x-auto rounded-lg border border-line bg-panel-2 p-4 font-mono text-xs leading-relaxed text-accent-soft">{transcript}</pre>
      </div>
    </section>

    <article class="rich-text mt-10 max-w-none">
      <h2>{seg_table[0]}</h2>
      <section class="not-prose my-4" aria-label="Code segments">
        <div class="glass rounded-2xl p-5 shadow-lg sm:p-7 overflow-x-auto">
          <table class="pdns-table" style="width:100%">
            <thead><tr>{seg_table[1]}</tr></thead>
            <tbody>{seg_rows}</tbody>
          </table>
        </div>
      </section>

      <h2>{causes[0]}</h2>
      <section class="not-prose my-4" aria-label="Root causes">
        <div class="glass rounded-2xl p-5 shadow-lg sm:p-7 overflow-x-auto">
          <table class="pdns-table" style="width:100%">
            <thead><tr>{causes[1]}</tr></thead>
            <tbody>{cause_rows}</tbody>
          </table>
        </div>
      </section>

      <h2>Step-by-step fixes</h2>
      <ol class="mt-3 grid gap-3">
        {fix_items}
      </ol>

      <h2>{edge_title}</h2>
      <p class="mt-3">{edge}</p>

      <aside class="mt-8 rounded-xl border-l-3 border-l-violet/50 bg-violet/5 p-5" aria-label="Practitioner field notes">
        <p class="font-mono text-[10px] uppercase tracking-[0.16em] text-violet mb-2">Field notes</p>
        <p class="text-sm leading-relaxed text-ink-dim italic">{field_note}</p>
      </aside>

      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>
      <div class="mt-3 grid gap-3">
        {faq_items}
      </div>

      <p class="mt-8 text-xs text-ink-faint">
        Diagnose with our free tools:
        <a href="/email-header-analyzer/" class="text-accent hover:text-accent-soft">email header analyzer</a>,
        <a href="/blacklist-checker/" class="text-accent hover:text-accent-soft">blacklist checker</a>,
        <a href="/spf-record-checker/" class="text-accent hover:text-accent-soft">SPF checker</a>.
      </p>
    </article>
  </div>
</BaseLayout>
'''

FIELD_NOTES = {
  'smtp-550-5-7-26': ("The 5.7.26 that stumps teams is the forwarded-mail case: a recipient forwards your message, the forwarder re-sends it, and DKIM breaks on the modified body while SPF breaks on the new IP. "
                      "The original sender did nothing wrong, and the fix belongs to the forwarder (SRS or allowlisting). Reading the Authentication-Results line tells you which side owns the failure."),
  'smtp-550-5-7-1': ("The 5.7.1 bounce text is the most informative error in email: the receiving server names its exact reason, unlike the vague 421. "
                     "Teams that keep a log of the named causes per bounce see patterns within a week, usually one compromised account or one misconfigured newsletter stack."),
  'smtp-554-5-4-14': ("The 5.4.14 loop is the one error where the header analyzer is not just helpful but essential: the Received chain is the evidence, and the loop is visible as a repeating hostname pair. "
                      "No DNS record change fixes a forwarding rule; the fix location is named in the headers."),
  'smtp-421-temporary-error': ("The discipline 421 tests is patience: every team eventually rewrites a working configuration in response to a 421 spike, and the fix that helps is almost always slowing down, not changing records. "
                               "Watch the class digit, and let the retry schedule do what RFC 5321 designed it to do."),
}

COMPANION = {
  'smtp-550-5-7-26': ('SMTP 550 5.7.26 vs related bounce codes',
    ['Code', 'Class', 'Primary layer', 'Typical trigger'],
    [['550 5.7.26', 'Permanent', 'DMARC authentication policy', 'Unauthenticated mail to an enforcing domain'],
     ['550 5.7.1', 'Permanent', 'Blocklist / relay / SPF policy', 'Listed IP, bad PTR, relay denial'],
     ['554 5.4.14', 'Permanent', 'Routing', 'Hop count exceeded by a loop'],
     ['421 4.7.0', 'Transient', 'Throttling', 'Volume spike or greylisting, retry succeeds']]),
  'smtp-550-5-7-1': ('SMTP 550 5.7.1 vs related bounce codes',
    ['Code', 'Class', 'Primary layer', 'Typical trigger'],
    [['550 5.7.1', 'Permanent', 'Blocklist / relay / SPF policy', 'Listed IP, bad PTR, relay denial'],
     ['550 5.7.26', 'Permanent', 'DMARC authentication policy', 'Unauthenticated mail to an enforcing domain'],
     ['554 5.4.14', 'Permanent', 'Routing', 'Hop count exceeded by a loop'],
     ['421 4.7.0', 'Transient', 'Throttling', 'Volume spike, retry succeeds']]),
  'smtp-554-5-4-14': ('SMTP 554 5.4.14 vs related bounce codes',
    ['Code', 'Class', 'Primary layer', 'Typical trigger'],
    [['554 5.4.14', 'Permanent', 'Routing', 'Hop count exceeded by a loop'],
     ['550 5.7.26', 'Permanent', 'DMARC authentication policy', 'Unauthenticated mail'],
     ['550 5.7.1', 'Permanent', 'Blocklist / relay / SPF policy', 'Listed IP or relay denial'],
     ['421 4.7.0', 'Transient', 'Throttling', 'Volume spike, retry succeeds']]),
  'smtp-421-temporary-error': ('SMTP 421 vs related bounce codes',
    ['Code', 'Class', 'Primary layer', 'Typical trigger'],
    [['421 4.7.0', 'Transient', 'Throttling', 'Volume spike or greylisting, retry succeeds'],
     ['550 5.7.26', 'Permanent', 'DMARC authentication policy', 'Unauthenticated mail'],
     ['550 5.7.1', 'Permanent', 'Blocklist / relay / SPF policy', 'Listed IP or relay denial'],
     ['554 5.4.14', 'Permanent', 'Routing', 'Hop count exceeded by a loop']]),
}
count = 0
NL = chr(10)
for pg in PAGES:
    slug = pg['slug']
    out = OUT / f'{slug}.astro'
    seg_rows = ''
    for row in pg['seg_table'][1]:
        cells = ''.join(
            f'<td class="font-mono text-xs text-accent-soft">{c}</td>' if i == 0 else f'<td class="text-sm text-ink-dim">{c}</td>'
            for i, c in enumerate(row)
        )
        seg_rows += f'<tr>{cells}</tr>'
    cause_rows = ''
    for row in pg['causes'][1]:
        cells = ''.join(
            f'<td class="font-medium text-ink">{c}</td>' if i == 0 else f'<td class="text-sm text-ink-dim">{c}</td>'
            for i, c in enumerate(row)
        )
        cause_rows += f'<tr>{cells}</tr>'
    fix_items = ''
    for i, f in enumerate(pg['fixes']):
        fix_items += f'<li class="flex gap-3"><span class="grid h-6 w-6 shrink-0 place-items-center rounded-md bg-accent/15 font-mono text-xs font-bold text-accent">{i + 1}</span><span class="text-ink-dim">{f}</span></li>'
    faq_items = ''
    for q, a in pg['faqs']:
        faq_items += (
            '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
            f'<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">{q}'
            '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
            f'<p class="mt-3 text-sm leading-relaxed text-ink-dim">{a}</p></details>'
        )
    comp_heading, comp_headers, comp_rows = COMPANION[slug]
    comp_th = ''.join(f'<th>{h}</th>' for h in comp_headers)
    comp_trs = ''
    for row in comp_rows:
        cells = ''.join(
            f'<td class="font-medium text-ink">{c}</td>' if i == 0 else f'<td class="text-sm text-ink-dim">{c}</td>'
            for i, c in enumerate(row)
        )
        comp_trs += f'<tr>{cells}</tr>'
    faq_schema_json = json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in pg['faqs']
    ]}, ensure_ascii=False)
    faq_const = 'const faqSchema = ' + faq_schema_json + ';'

    html = NL.join([
        '---',
        'import BaseLayout from \'../layouts/BaseLayout.astro\';',
        faq_const,
        '---',
        '<BaseLayout',
        '  title="' + pg['title'] + ' | PromptDNS"',
        '  description="' + pg['description'] + '"',
        '  breadcrumb={[["Home", "/"], ["Email Authentication", "/email-authentication/"], ["SMTP ' + pg['code'] + '"]]}',
        '>',
        '  <div class="mx-auto max-w-4xl px-4 py-12">',
        '    <nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">',
        '      <a href="/" class="hover:text-accent">Home</a> <span aria-hidden="true">/</span>',
        '      <a href="/email-authentication/" class="hover:text-accent">Email Authentication</a> <span aria-hidden="true">/</span>',
        '      <span class="text-ink-dim">SMTP ' + pg['code'] + '</span>',
        '    </nav>',
        '    <p class="font-mono text-xs uppercase tracking-[0.2em] text-accent">' + pg['cls'] + ' error</p>',
        '    <h1 class="font-display mt-2 text-3xl font-bold tracking-tight text-ink sm:text-4xl">' + pg['h1'] + '</h1>',
        '    <div class="pd-answer" data-vs="answer">',
        '      <p class="text-lg leading-relaxed text-ink-dim">' + pg['answer'] + '</p>',
        '    </div>',
        '',
        '    <section class="not-prose my-8" aria-label="Raw bounce transcript">',
        '      <div class="glass rounded-2xl p-5 shadow-lg sm:p-7">',
        '        <p class="font-mono text-[10px] uppercase tracking-[0.18em] text-accent mb-3">Raw bounce transcript</p>',
        '        <pre class="overflow-x-auto rounded-lg border border-line bg-panel-2 p-4 font-mono text-xs leading-relaxed text-accent-soft">' + pg['transcript'] + '</pre>',
        '      </div>',
        '    </section>',
        '',
        '    <article class="rich-text mt-10 max-w-none">',
        '      <h2>' + pg['seg_table'][0] + '</h2>',
        '      <section class="not-prose my-4" aria-label="Code segments">',
        '        <div class="glass rounded-2xl p-5 shadow-lg sm:p-7 overflow-x-auto">',
        '          <table class="pdns-table" style="width:100%">',
        '            <thead><tr>' + '<th>Segment</th><th>Field</th><th>Detail</th>' + '</tr></thead>',
        '            <tbody>' + seg_rows + '</tbody>',
        '          </table>',
        '        </div>',
        '      </section>',
        '',
        '      <h2>' + pg['causes'][0] + '</h2>',
        '      <section class="not-prose my-4" aria-label="Root causes">',
        '        <div class="glass rounded-2xl p-5 shadow-lg sm:p-7 overflow-x-auto">',
        '          <table class="pdns-table" style="width:100%">',
        '            <thead><tr>' + '<th>Cause</th><th>Evidence in the results</th><th>Fix</th><th>Verify with</th>' + '</tr></thead>',
        '            <tbody>' + cause_rows + '</tbody>',
        '          </table>',
        '        </div>',
        '      </section>',
        '',
        '      <h2>Step-by-step fixes</h2>',
        '      <ol class="mt-3 grid gap-3">',
        '        ' + fix_items,
        '      </ol>',
        '',
        '      <h2>Production edge cases when debugging ' + pg['code'] + '</h2>',
        '      <p class="mt-3">' + pg['edge'] + '</p>',
        '',
        '      <aside class="mt-8 rounded-xl border-l-3 border-l-violet/50 bg-violet/5 p-5" aria-label="Practitioner field notes">',
        '        <p class="font-mono text-[10px] uppercase tracking-[0.16em] text-violet mb-2">Field notes</p>',
        '        <p class="text-sm leading-relaxed text-ink-dim italic">' + FIELD_NOTES[slug] + '</p>',
        '      </aside>',
        '',
        '      <h2 class="font-display mt-10 text-xl font-semibold text-ink">' + COMPANION[slug][0] + '</h2>',
        '      <section class="not-prose my-4" aria-label="Related codes">',
        '        <div class="glass rounded-2xl p-5 shadow-lg sm:p-7 overflow-x-auto">',
        '          <table class="pdns-table" style="width:100%">',
        '            <thead><tr>' + ''.join('<th>' + h + '</th>' for h in COMPANION[slug][1]) + '</tr></thead>',
        '            <tbody>' + comp_trs + '</tbody>',
        '          </table>',
        '        </div>',
        '      </section>',
        '',
        '      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>',
        '      <div class="mt-3 grid gap-3">',
        '        ' + faq_items,
        '      </div>',
        '',
        '      <p class="mt-8 text-xs text-ink-faint">',
        '        Diagnose with our free tools:',
        '        <a href="/email-header-analyzer/" class="text-accent hover:text-accent-soft">email header analyzer</a>,',
        '        <a href="/blacklist-checker/" class="text-accent hover:text-accent-soft">blacklist checker</a>,',
        '        <a href="/spf-record-checker/" class="text-accent hover:text-accent-soft">SPF checker</a>.',
        '      </p>',
        '    </article>',
        '  </div>',
        '</BaseLayout>',
        '',
    ])
    out.write_text(html, encoding='utf-8')
    count += 1
    print(f'Generated: {slug}')

print(f'{count} SMTP error pages generated')
