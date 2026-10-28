"""Wave D: add contextual in-body link blocks to the 8 pages below 3 links.
Links are chosen per page topic, pointing at real sibling pages and tools."""
import pathlib

PAGES = pathlib.Path('src/pages')

BLOCKS = {
  'asn-explained': (
    '<h2>Related</h2>\n      <ul>\n'
    '        <li><a href="/ip-lookup/">IP lookup</a>, see the ASN behind any address</li>\n'
    '        <li><a href="/public-vs-private-ip/">Public vs private IP</a>, how ranges are divided</li>\n'
    '        <li><a href="/nat-explained/">NAT explained</a>, why private ranges need translation</li>\n'
    '      </ul>'
  ),
  'common-network-ports': (
    '<h2>Related</h2>\n      <ul>\n'
    '        <li><a href="/email-ports-587-465-25/">Email ports 25, 465, and 587</a>, the mail-specific subset</li>\n'
    '        <li><a href="/imap-vs-smtp/">IMAP vs SMTP</a>, retrieval vs sending</li>\n'
    '        <li><a href="/smtp-tester/">SMTP tester</a>, watch the port-level dialogue live</li>\n'
    '      </ul>'
  ),
  'dns-load-balancing': (
    '<h2>Related</h2>\n      <ul>\n'
    '        <li><a href="/dns-propagation-checker/">DNS propagation checker</a>, confirm every resolver sees the new weights</li>\n'
    '        <li><a href="/ttl-checker/">TTL checker</a>, control how fast load shifts propagate</li>\n'
    '        <li><a href="/dns-monitoring/">DNS monitoring</a>, get alerted when a weighted record drifts</li>\n'
    '      </ul>'
  ),
  'does-blocking-ai-crawlers-hurt-seo': (
    '<h2>Related</h2>\n      <ul>\n'
    '        <li><a href="/ai-crawler-verification/">AI crawler verification</a>, confirm which bot actually visited</li>\n'
    '        <li><a href="/block-ai-crawlers-cloudflare/">Block AI crawlers with Cloudflare</a>, edge-level enforcement</li>\n'
    '        <li><a href="/gptbot/">GPTBot</a> and <a href="/claudebot/">ClaudeBot</a>, per-token decisions</li>\n'
    '      </ul>'
  ),
  'imap-vs-smtp': (
    '<h2>Related</h2>\n      <ul>\n'
    '        <li><a href="/email-ports-587-465-25/">Email ports 25, 465, and 587</a>, which port carries which protocol</li>\n'
    '        <li><a href="/smtp-tester/">SMTP tester</a>, verify your sending path end to end</li>\n'
    '        <li><a href="/how-to-read-email-headers/">How to read email headers</a>, trace the delivery story</li>\n'
    '      </ul>'
  ),
  'list-unsubscribe-header': (
    '<h2>Related</h2>\n      <ul>\n'
    '        <li><a href="/gmail-yahoo-bulk-sender-requirements/">Gmail and Yahoo bulk sender requirements</a>, where one-click is mandated</li>\n'
    '        <li><a href="/why-emails-go-to-spam/">Why emails go to spam</a>, the reputation factors behind placement</li>\n'
    '        <li><a href="/email-header-analyzer/">Email header analyzer</a>, inspect the headers on real mail</li>\n'
    '      </ul>'
  ),
  'methodology': (
    '<h2>Related</h2>\n      <ul>\n'
    '        <li><a href="/dns-propagation-checker/">DNS propagation checker</a>, the multi-resolver method in practice</li>\n'
    '        <li><a href="/email-header-analyzer/">Email header analyzer</a>, the local parsing example from this page</li>\n'
    '        <li><a href="/how-it-works/">How PromptDNS works</a>, the product walkthrough</li>\n'
    '      </ul>'
  ),
  'public-vs-private-ip': (
    '<h2>Related</h2>\n      <ul>\n'
    '        <li><a href="/reserved-ip-ranges/">Reserved IP ranges</a>, the full address map</li>\n'
    '        <li><a href="/nat-explained/">NAT explained</a>, the translation that makes private ranges work</li>\n'
    '        <li><a href="/my-ip/">What is my IP</a>, see the public address you present</li>\n'
    '      </ul>'
  ),
}

applied = 0
for slug, block in BLOCKS.items():
    p = PAGES / f'{slug}.astro'
    s = p.read_text(encoding='utf-8')
    if 'Related</h2>' in s:
        # append the list items into the existing Related section instead of adding a heading
        anchor = s.find('<h2>Related</h2>')
        ul_start = s.find('<ul>', anchor)
        ul_end = s.find('</ul>', ul_start)
        existing = s[ul_start:ul_end]
        extra = block[block.find('<ul>') + 4:block.rfind('</ul>')]
        s = s[:ul_end] + extra + s[ul_end:]
        how = 'merged into Related'
    else:
        # insert before the last </div> before </BaseLayout>
        bl = s.rfind('</BaseLayout>')
        dv = s.rfind('</div>', 0, bl)
        s = s[:dv] + '\n    ' + block + '\n  ' + s[dv:]
        how = 'new block'
    p.write_text(s, encoding='utf-8')
    applied += 1
    print(f'{slug}: links added ({how})')
print('applied:', applied)
