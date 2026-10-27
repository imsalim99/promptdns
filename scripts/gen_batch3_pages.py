"""Generate drip batch 3: troubleshooting + fundamentals guides.

All facts are standard OS/browser troubleshooting and DNS fundamentals.
Pages carry staggered publishOn dates via the drip queue (noindex-hold).
"""
import pathlib

OUT = pathlib.Path('src/pages')

PAGES = [
    dict(
        slug='dns-server-not-responding',
        h1='DNS Server Not Responding: How to Fix It on Windows, Router and Browser',
        title='DNS Server Not Responding: 7 Fixes That Work, in Order',
        description='DNS server not responding on Windows: fix it in order, from flushing the DNS cache and switching resolvers to router and driver checks. With verification steps.',
        crumb='DNS Server Not Responding',
        answer=('The "DNS server not responding" error means your device reached the network but got no answer from the DNS resolver it asked. '
                'The fix sequence is always the same: flush the local cache, switch to a known-good public resolver, rule out the router, then check firewall and driver settings. '
                'Most cases are solved by the first two steps, and you can verify every step with a live DNS lookup rather than guessing.'),
        steps=('Fix', 'Action', [
            ('1. Flush the DNS cache', 'Windows: ipconfig /flushdns in an elevated prompt. macOS: sudo dscacheutil -flushcache. Then retry the site.'),
            ('2. Switch resolver', 'Set your adapter DNS to Cloudflare 1.1.1.1 and 8.8.8.8 manually, overriding the router-provided resolver.'),
            ('3. Restart and re-test the router', 'Power-cycle the router, then test on another device on the same network to isolate device vs router.'),
            ('4. Disable other adapters and VPNs', 'VPN and virtual adapters can capture DNS traffic. Disable them and retest to rule out interference.'),
            ('5. Check firewall and antivirus DNS filtering', 'Some security suites intercept DNS. Pause the filter and retest.'),
            ('6. Update the network driver', 'An outdated Wi-Fi or Ethernet driver is a documented cause on Windows.'),
            ('7. Verify the fix', 'Confirm resolution works end to end with the DNS record lookup and check resolver agreement with the propagation checker.'),
        ]),
        body_sections=[
            ('What the error actually means',
             ['The message reports a transport-level failure: your device sent a DNS query and received no usable answer.',
              'It is different from NXDOMAIN, where the DNS answered correctly and said the name does not exist. Here the conversation itself failed.',
              'That distinction drives the fix order: cache and resolver changes come first because they are the most common and the cheapest to try.']),
            ('Verifying the fix',
             ['After switching resolvers, do not trust the browser alone: query a record directly to confirm the new resolver answers.',
              'Our propagation checker shows Cloudflare, Google, and AliDNS side by side, so you can see whether your new resolver agrees with the rest of the world.']),
        ],
        field_note=("The fastest isolation question is: does another device on the same network resolve? If yes, the problem is local to the machine and the flush-and-switch sequence almost always wins. "
                    "If no, skip straight to the router, because no amount of Windows settings will fix a dead resolver upstream."),
        faqs=[
            ('Is "DNS server not responding" a problem with my ISP?', 'Often yes: the resolver your router hands out may be down. Switching your device to a public resolver routes around it instantly.'),
            ('Will flushing DNS lose my settings?', 'No. Flushing only clears cached answers; network settings, passwords, and history are untouched.'),
            ('Why does only one website show the error?', 'Then the resolver answered but that domain failed: check the domain itself with a record lookup before changing any settings.'),
        ],
        release='2026-11-28',
    ),
    dict(
        slug='dns-probe-finished-nxdomain',
        h1='DNS Probe Finished NxDomain: What It Means and How to Fix It',
        title='DNS Probe Finished NxDomain: Meaning and 6 Fixes for Chrome',
        description='DNS probe finished nxdomain explained: what NXDOMAIN means, why Chrome shows it, and 6 fixes in order, from DNS cache flushes to resolver changes.',
        crumb='DNS Probe Finished NxDomain',
        answer=('"DNS probe finished nxdomain" is Chrome reporting that a DNS lookup returned NXDOMAIN: the resolver answered correctly but said the domain does not exist. '
                'The causes are a mistyped or expired domain, a stale negative cache entry on your device, or a filtering resolver blocking the name. '
                'The fixes follow that order: verify the domain is real, flush your caches, then change the resolver you are using.'),
        steps=('Fix', 'Action', [
            ('1. Confirm the domain exists', 'Look the domain up with a record lookup: if it has an A record, the problem is local; if every resolver says NXDOMAIN, the domain is gone or mistyped.'),
            ('2. Flush the DNS cache', 'Chrome has its own cache: chrome://net-internals/#dns then Clear host cache. Flush the OS cache too.'),
            ('3. Clear the sockets', 'chrome://net-internals/#sockets, Flush socket pools: stale connections keep serving the failed lookup.'),
            ('4. Switch resolver', 'Move from a filtering resolver (ISP, corporate, or a VPN) to a neutral public resolver and retest.'),
            ('5. Check the hosts file', 'A leftover entry in the hosts file forces NXDOMAIN for real domains. Remove stale lines.'),
            ('6. Verify worldwide', 'If our propagation checker shows NXDOMAIN everywhere, the domain itself has a problem, not your device.'),
        ]),
        body_sections=[
            ('What NXDOMAIN means',
             ['NXDOMAIN is a legitimate DNS answer code: the name you asked for does not exist in the eyes of the resolver that replied.',
              'Chrome adds its own wording around it, which is why the error looks scarier than the underlying fact.',
              'There are two flavors: the domain really is gone (expired, mistyped, or deleted), or your local environment is wrongly saying so because of caching or filtering.']),
            ('The negative-cache subtlety',
             ['Resolvers cache negative answers too, for the TTL in the SOA record, so a domain that was just re-registered or fixed can still show NXDOMAIN locally.',
              'That is why flushing the Chrome cache and the OS cache is step two, and why the propagation checker is the referee: it queries fresh, unfiltered resolvers.']),
        ],
        field_note=("The most common real-world case I see is a filtering resolver: office networks and VPNs answer NXDOMAIN for domains they block, and Chrome relays it verbatim. "
                    "Before touching anything, open the propagation checker: if other resolvers answer fine, your resolver is filtering you, and no amount of cache flushing will change a policy."),
        faqs=[
            ('Is NXDOMAIN the same as the site being down?', 'No. A site can be down with valid DNS. NXDOMAIN means the name itself did not resolve to anything.'),
            ('Why does only Chrome show this error?', 'The lookup failure affects every browser, but Chrome has its own DNS cache and error wording, so it is the place you notice it.'),
            ('Can a VPN cause NXDOMAIN?', 'Yes: many VPN tunnels route DNS to a resolver that filters or fails for some domains. Disconnect and retest to confirm.'),
        ],
        release='2026-12-01',
    ),
    dict(
        slug='err-name-not-resolved',
        h1='err_name_not_resolved: What It Means and How to Fix It',
        title='err_name_not_resolved: Meaning and Fixes for Chrome and Android',
        description='err_name_not_resolved explained: the Chrome and Android DNS resolution failure, its causes and fixes, from DNS cache and private DNS to resolver changes.',
        crumb='err_name_not_resolved',
        answer=("err_name_not_resolved is the Chromium error for a failed DNS lookup: the browser asked for the domain's address and got no valid answer. "
                'It is the same failure Windows calls "DNS server not responding" or NXDOMAIN, seen from the browser side. '
                'The fixes mirror those cases: flush caches, check Android private DNS, then change the resolver.'),
        steps=('Fix', 'Action', [
            ('1. Confirm the domain resolves', 'Look the domain up with a record lookup: if records exist everywhere, the problem is on your device or network.'),
            ('2. Clear Chrome DNS cache and sockets', 'chrome://net-internals/#dns and #sockets, then clear both and reload.'),
            ('3. Check Android private DNS', 'Android Private DNS (DNS over TLS) misconfigurations cause exactly this error. Set it to a working hostname or turn it off.'),
            ('4. Switch resolver', 'Set the device or router DNS to a known-good public resolver and retest on the same network.'),
            ('5. Flush the OS cache', 'Android: toggle airplane mode or reboot, which resets the DNS cache. Windows: ipconfig /flushdns.'),
            ('6. Verify with fresh resolvers', 'Use the propagation checker to confirm the domain resolves on independent resolvers before blaming your device.'),
        ]),
        body_sections=[
            ('One error, three platforms',
             ['Chromium reports failed lookups as err_name_not_resolved on Chrome desktop, Chrome on Android, and Edge alike.',
              'The underlying causes match the platform equivalents: stale caches, a failing resolver, or a DNS-over-TLS misconfiguration on Android.',
              'Android private DNS is the special case worth checking first on phones: a typo in the TLS hostname produces this error for every site.']),
            ('Ruling out the domain itself',
             ['Before fixing your device, confirm the domain resolves globally with fresh resolvers.',
              'If every independent resolver returns NXDOMAIN, the domain has expired or its records were removed, and no device setting will fix it.']),
        ],
        field_note=("On Android phones this error is dominated by Private DNS misconfigurations: users set a hostname like one.one.one.one and then switch providers, leaving a TLS hostname that no longer resolves. "
                    "Checking that single setting fixes most mobile cases in under a minute."),
        faqs=[
            ('Is err_name_not_resolved a Chrome bug?', 'No. It is Chromium accurately reporting that a DNS lookup failed. The fix is on the network or device side.'),
            ('Why does my phone show it but not my laptop?', 'Different devices use different resolvers and caches. Android Private DNS or carrier filtering commonly diverges from your laptop.'),
            ('Does a VPN fix it or cause it?', 'Both: a VPN can route around a broken ISP resolver, or its own DNS can fail. Test with the tunnel off and on.'),
        ],
        release='2026-12-03',
    ),
    dict(
        slug='registrar-vs-dns-hosting',
        h1='Registrar vs DNS Hosting: Who Controls What',
        title='Registrar vs DNS Hosting: Where Your Domain Actually Lives',
        description='Registrar vs DNS hosting explained: what each one controls, where records actually live, what changing nameservers does, and the gotcha that breaks sites.',
        crumb='Registrar vs DNS Hosting',
        answer=('A registrar is where you bought the domain and where delegation is set: it decides which nameservers the world asks. '
                'DNS hosting is where your records actually live: the service that answers the queries. '
                'They are often the same company, but they are two different jobs, and knowing which one holds the problem is half of every DNS troubleshooting session.'),
        steps=('Question', 'Registrar', 'DNS hosting', [
            ('What it holds', 'Registration, delegation (NS), renewals, ownership', 'The actual records: A, MX, TXT, CNAME, DNSSEC keys'),
            ('What changing it does', 'Changing registrars moves ownership; delegation stays', 'Changing nameservers moves where records are answered'),
            ('Where records are edited', 'Nowhere, unless it also provides DNS', 'In the DNS panel of the hosting provider'),
            ('Common confusion', 'Renewing here does not update records', 'Editing records here does nothing if nameservers point elsewhere'),
        ]),
        body_sections=[
            ('The delegation chain in one paragraph',
             ['When a resolver looks up your domain, it asks the root servers, which point to the .com registry, which reads the delegation your registrar published, and only then queries your DNS host.',
              'That chain is why a nameserver change at the registrar can take up to 48 hours: the parent zone caches the old answer for its TTL.',
              'It is also why editing a record at your DNS host is fast: no delegation changes, just the record itself and its TTL.']),
            ('The gotcha that breaks sites',
             ['The most expensive mistake is editing records at a registrar panel that is no longer authoritative, because the nameservers were moved to another provider during a migration.',
              'Symptom: the panel shows your records, everything looks right, and nothing changes in the real world.',
              'Check where delegation points first with a nameserver lookup, then edit only at the authoritative host.']),
            ('Split or combined, both are normal',
             [' registrar + separate DNS host (Cloudflare DNS on a GoDaddy domain) is common and healthy.',
              'Combined works too, as long as you know which panel is authoritative: our provider playbooks show the menu path for each.']),
        ],
        field_note=("Half of the 'I changed my DNS and nothing happened' tickets start here: the person edited the registrar's placeholder panel instead of the authoritative host. "
                    "Make the delegation check a reflex: nameserver lookup first, record edit second. It turns a two-day mystery into a two-minute diagnosis."),
        faqs=[
            ('Do I need DNS hosting at my registrar?', 'No. Point delegation at any DNS host you like; many registrars also sell hosting, but it is optional.'),
            ('What happens if I change nameservers?', 'Delegation moves to the new host, so its records become the ones the world sees, with a propagation window up to 48 hours for NS.'),
            ('Where do I edit my records?', 'At the authoritative DNS host, the one your nameservers point to. Verify with a nameserver lookup before editing.'),
        ],
        release='2026-12-05',
    ),
    dict(
        slug='check-spf-dkim-dmarc-dig',
        h1='Check SPF, DKIM and DMARC with dig: The Command-Line Trio',
        title='Check SPF, DKIM and DMARC with dig: Exact Commands and How to Read Them',
        description='Check SPF, DKIM and DMARC from the command line with dig: exact commands for each record, how to read the output, and what fail and pass look like.',
        crumb='Check SPF, DKIM and DMARC with dig',
        answer=('The three email authentication records are one dig command each: SPF at the root TXT, DKIM at selector._domainkey, and DMARC at _dmarc. '
                'Reading them is pattern matching: SPF must start v=spf1 and stay under 10 lookups, DKIM must carry a non-empty p= key, and DMARC must carry a p= policy. '
                'The commands below are the same checks our tools run, so the browser route and the terminal route always agree.'),
        steps=('Record', 'Command', [
            ('SPF', 'dig example.com TXT +short'),
            ('DKIM', 'dig default._domainkey.example.com TXT +short'),
            ('DMARC', 'dig _dmarc.example.com TXT +short'),
            ('All three live', 'dig example.com TXT +short, then the two subdomain lookups above'),
        ]),
        body_sections=[
            ('Reading the SPF answer',
             ['A healthy SPF starts with v=spf1 and ends with an all mechanism, usually ~all or -all.',
              'Count the DNS-querying terms: every include, a, mx, exists, and redirect consumes one of the 10 allowed lookups (RFC 7208).',
              'Two v=spf1 records on the same name is a permerror: receivers stop evaluating entirely.']),
            ('Reading the DKIM answer',
             ['A healthy DKIM record has v=DKIM1, a k= field (rsa is standard), and a long p= value with the public key.',
              'An empty p=, like v=DKIM1; p=, means the key was revoked or never published: mail signed with that selector will fail.',
              'The selector matters: mail signed with s=20230601 must be checked at 20230601._domainkey, not at default._domainkey.']),
            ('Reading the DMARC answer',
             ['A valid record starts v=DMARC1 and must carry a p= tag: none, quarantine, or reject.',
              'A rua= address means aggregate reports arrive daily; enforcement without rua is flying blind.',
              'No record at _dmarc is itself the finding: the domain has no DMARC policy at all.']),
        ],
        field_note=("The terminal route is the fastest way to sanity-check what our tools show you, and the fastest way to embarrass a vendor: ask them for the selector and the dmarc address, run three dig commands, and you know in ten seconds whether their setup exists. "
                    "Just remember dig answers from one resolver: our checkers query three and show you the disagreement."),
        faqs=[
            ('Which selector does my DKIM use?', 'Read the DKIM-Signature header of a real message you sent: the s= value is the selector. Common defaults are default, google, selector1, and selector2.'),
            ('Why does dig show my record but mail still fails?', 'dig proves publication, not alignment: DMARC also needs the From domain to align with the SPF or DKIM domain. Check alignment with the DMARC checker.'),
            ('Does +short hide anything important?', 'It trims DNS noise, not data. Drop +short when debugging to see TTLs and record types in full.'),
        ],
        release='2026-12-08',
    ),
]

TMPL = '''---
import BaseLayout from '../layouts/BaseLayout.astro';
import {{ isHeld }} from '../data/publish-queue.js';

const held = isHeld('/{slug}/');
---
<BaseLayout
  title="{title} | PromptDNS"
  description="{description}"
  breadcrumb={{[["Home", "/"], ["DNS Guide", "/dns/"], ["{crumb}"]]}}
>
  <div class="mx-auto max-w-4xl px-4 py-12">
    <nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">
      <a href="/" class="hover:text-accent">Home</a> <span aria-hidden="true">/</span>
      <a href="/dns/" class="hover:text-accent">DNS Guide</a> <span aria-hidden="true">/</span>
      <span class="text-ink-dim">{crumb}</span>
    </nav>
    <h1 class="font-display text-3xl font-bold tracking-tight text-ink sm:text-4xl">{h1}</h1>
    <div class="pd-answer" data-vs="answer">
      <p class="text-lg leading-relaxed text-ink-dim">{answer}</p>
    </div>

    <section class="not-prose my-8" aria-label="Fix table">
      <div class="glass rounded-2xl p-5 shadow-lg sm:p-7 overflow-x-auto">
        <table class="pdns-table" style="width:100%">
          <thead><tr>{headers}</tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>

    <article class="rich-text mt-10 max-w-none">
      {body_html}

      <aside class="mt-8 rounded-xl border-l-3 border-l-violet/50 bg-violet/5 p-5" aria-label="Practitioner field notes">
        <p class="font-mono text-[10px] uppercase tracking-[0.16em] text-violet mb-2">Field notes</p>
        <p class="text-sm leading-relaxed text-ink-dim italic">{field_note}</p>
      </aside>

      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>
      <div class="mt-3 grid gap-3">
        {faq_items}
      </div>

      <p class="mt-8 text-xs text-ink-faint">
        Verify with our free tools:
        <a href="/dns-record-lookup/" class="text-accent hover:text-accent-soft">DNS record lookup</a>,
        <a href="/dns-propagation-checker/" class="text-accent hover:text-accent-soft">propagation checker</a>,
        <a href="/flush-dns-cache/" class="text-accent hover:text-accent-soft">flush DNS cache guide</a>.
      </p>
    </article>
  </div>
</BaseLayout>
'''

count = 0
for pg in PAGES:
    out = OUT / f"{pg['slug']}.astro"
    headers = ''.join(f'<th>{h}</th>' for h in pg['steps'][1])
    rows = ''
    for row in pg['steps'][2]:
        cells = ''.join(
            f'<td class="font-medium text-ink">{c}</td>' if i == 0 else f'<td class="text-sm text-ink-dim">{c}</td>'
            for i, c in enumerate(row)
        )
        rows += f'<tr>{cells}</tr>'
    body_html = ''
    for h2, paras in pg['body_sections']:
        body_html += f'\n      <h2>{h2}</h2>'
        for para in paras:
            body_html += f'\n      <p class="mt-3">{para}</p>'
    faq_items = ''
    for q, a in pg['faqs']:
        faq_items += (
            '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
            f'<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">{q}'
            '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
            f'<p class="mt-3 text-sm leading-relaxed text-ink-dim">{a}</p></details>'
        )
    content = TMPL.format(
        slug=pg['slug'],
        title=pg['title'],
        description=pg['description'],
        crumb=pg['crumb'],
        h1=pg['h1'],
        answer=pg['answer'],
        headers=headers,
        rows=rows,
        body_html=body_html,
        field_note=pg['field_note'],
        faq_items=faq_items,
    )
    out.write_text(content, encoding='utf-8')
    count += 1
    print(f"Generated: {pg['slug']} (release {pg['release']})")

print(f'{count} batch-3 pages generated')
