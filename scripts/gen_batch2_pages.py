"""Generate drip batch 2: AI-cluster decision and operations guides.

All facts are either our own scanner methodology or crawler behavior validated
against operator documentation 2026-10-28. No competitor pricing claims.
Pages carry staggered publishOn dates via the drip queue (noindex-hold).
"""
import pathlib

OUT = pathlib.Path('src/pages')

PAGES = [
    dict(
        slug='does-blocking-ai-crawlers-hurt-seo',
        h1='Does Blocking AI Crawlers Hurt SEO?',
        title='Does Blocking AI Crawlers Hurt SEO? What Actually Changes',
        description='Blocking AI crawlers: what changes for Google rankings, ChatGPT citations, and AI Overviews, and what does not. Per-crawler facts.',
        answer=("Blocking AI crawlers does not hurt your Google Search rankings. "
                "Googlebot and Google-Extended are separate systems: ranking uses Googlebot, and the AI-training token changes nothing about indexing or position. "
                "What blocking does change is visibility in AI answers, because each AI vendor's crawler feeds its own product, and a blocked crawler means a missing citation."),
        body_sections=[
            ('What blocking does not change',
             ['Your Google rankings, indexing, and Core Web Vitals are unaffected. Google has stated that blocking Google-Extended has no effect on Search ranking or AI Overviews.',
              'Your traffic from traditional search stays the same. None of the major AI crawler rules touch ranking signals.',
              'Your ability to rank in AI Overviews stays intact, because AI Overviews are generated from search results, not from third-party crawler access.']),
            ('What blocking does change',
             ['ChatGPT Search citations disappear if OAI-SearchBot is blocked, because that crawler builds the index ChatGPT cites from.',
              'Perplexity answers drop your pages if PerplexityBot is disallowed, usually within days because its index rebuilds often.',
              'Future model training loses your content where the vendor honors robots.txt, such as GPTBot and ClaudeBot. Note that Common Crawl datasets already published are not retroactive.']),
            ('The decision framework',
             ['Decide per crawler, not with a single block-all rule: allow the search crawlers whose citations you want, and decide training access separately.',
              'Publishers with paywalled or proprietary content usually block training crawlers and allow search crawlers. Sites competing for AI-answer visibility do the opposite.',
              'Whatever you choose, verify from your logs: reverse DNS on the fetching IP confirms a crawler is genuine before you react to it.']),
        ],
        table=('Decision', 'Consequence', [
            ('Block training crawlers only (GPTBot, ClaudeBot, CCBot)', 'Content stays out of model training; search and AI Overview presence unchanged'),
            ('Block search crawlers (OAI-SearchBot, PerplexityBot)', 'Removes you from those AI answer engines; rankings unchanged'),
            ('Block Google-Extended', 'Gemini and Vertex training opt-out; Search and AI Overviews unchanged'),
            ('Block everything including Googlebot', 'Also removes you from Google Search: this is not an AI decision anymore'),
        ]),
        field_note=("The question behind the question is usually about AI citations as a traffic source. "
                    "Our position after watching these tools evolve: treat AI answer visibility like a new referral channel, decide it per vendor, and re-visit the decision quarterly, because each vendor's product boundaries keep moving."),
        faqs=[
            ('Does robots.txt blocking affect my Google ranking?', 'No. robots.txt controls crawling, not ranking. Blocking AI training tokens has no documented effect on Search position.'),
            ('Will I lose AI Overviews visibility if I block AI crawlers?', 'No. AI Overviews come from Google Search results. Google-Extended does not control them.'),
            ('Can I allow some AI crawlers and block others?', 'Yes, and it is the recommended approach: each vendor publishes a separate user-agent token with its own rules.'),
        ],
        release='2026-11-19',
    ),
    dict(
        slug='ai-crawler-verification',
        h1='AI Crawler Verification: Confirm a Crawler Is Genuine with Reverse DNS',
        title='AI Crawler Verification: Reverse DNS Checks for GPTBot, ClaudeBot and More',
        description='Verify AI crawler visitors with reverse DNS: the dig method for GPTBot, ClaudeBot, PerplexityBot and CCBot, and why spoofed tokens fail it.',
        answer=("AI crawler verification is the reverse DNS check on the fetching IP address. "
                "A genuine GPTBot, ClaudeBot, PerplexityBot, or CCBot fetch resolves to the operator's own address space, while a spoofed token does not. "
                "The check matters because user-agent strings are trivial to fake, and security decisions should rest on the IP, not the header."),
        body_sections=[
            ('The reverse DNS method',
             ['Take the fetching IP from your server or WAF logs and run a PTR lookup on it.',
              'A genuine OpenAI fetch resolves inside the openai.com space, Anthropic inside anthropic.com, Perplexity inside perplexity.ai, and Common Crawl inside commoncrawl.org.',
              'For defense in depth, forward-confirm the result: resolve the returned hostname back to an IP and check it matches the original visitor. This is FCrDNS, the same standard email verification uses.']),
            ('Where crawlers publish their ranges',
             ['OpenAI publishes its IP ranges publicly, so you can allow-list or match by range instead of by single lookup.',
              'Anthropic and Perplexity document verification by reverse DNS on their help pages.',
              'Common Crawl and Google both resolve cleanly; Google-Extended is the exception, because it is a training control rather than a crawler and never appears in logs.']),
            ('The exception that proves the rule',
             ['Bytespider reverse DNS is inconsistent, which is why the recommendation for that crawler is edge-level blocking by autonomous system rather than token matching.',
              'Any crawler whose verification is unreliable should be handled at the WAF, not in robots.txt.']),
        ],
        table=('Token', 'Verification method', 'Genuine fetch resolves to', [
            ('GPTBot', 'Reverse DNS + published ranges', 'openai.com space'),
            ('ClaudeBot', 'Reverse DNS', 'anthropic.com space'),
            ('PerplexityBot', 'Reverse DNS', 'perplexity.ai space'),
            ('CCBot', 'Reverse DNS', 'commoncrawl.org space'),
            ('OAI-SearchBot', 'Reverse DNS', 'openai.com space'),
            ('Google-Extended', 'Not verifiable in logs', 'Googlebot fetches; token is policy'),
            ('Bytespider', 'Unreliable', 'Block by ASN at the edge'),
        ]),
        field_note=("Verification is the step teams skip and then regret: someone reads a GPTBot spike in the logs, panics, blocks all of OpenAI at the firewall, and takes out their own ChatGPT Search presence in the same move. "
                    "One reverse DNS check on two sample IPs would have shown which token was real and what it was doing."),
        faqs=[
            ('Why is reverse DNS better than the user-agent string?', 'User-agent strings are trivial to spoof; a reverse DNS lookup ties the visitor to infrastructure the operator actually controls.'),
            ('What is FCrDNS?', 'Forward-confirmed reverse DNS: the PTR hostname is resolved back to an IP and must match the original visitor. It closes the loop on hostname spoofing.'),
            ('Do any AI crawlers publish IP ranges?', 'Yes, OpenAI publishes its ranges. Others are verified by reverse DNS on the documented domain.'),
        ],
        release='2026-11-21',
    ),
    dict(
        slug='block-ai-crawlers-cloudflare',
        h1='Block AI Crawlers with Cloudflare: WAF Rules That Actually Hold',
        title='Block AI Crawlers with Cloudflare: WAF and ASN Rules for Tokens That Ignore robots.txt',
        description='Block AI crawlers at the Cloudflare edge: WAF custom rules, managed AI scraper blocking, and ASN rules for crawlers that ignore robots.txt.',
        answer=("Cloudflare can block AI crawlers at the edge, before robots.txt is even consulted, which is the only enforcement that holds against crawlers reported to ignore robots.txt. "
                "The two mechanisms are managed AI scraper blocking in the Cloudflare dashboard and custom WAF rules that match user-agent or autonomous system number. "
                "robots.txt remains the right tool for well-behaved crawlers, and edge blocking is the right tool for the rest."),
        body_sections=[
            ('When to use the edge instead of robots.txt',
             ['Use robots.txt for crawlers that document compliance: GPTBot, ClaudeBot, PerplexityBot, OAI-SearchBot, CCBot.',
              'Use the WAF for crawlers with inconsistent compliance, such as Bytespider, and for aggressive agents hammering your origin regardless of rules.',
              'The edge also protects paths robots.txt cannot: robots.txt is public and tells scrapers exactly which paths you value.']),
            ('The mechanisms in Cloudflare',
             ['Managed rules: Cloudflare offers a one-click AI scraper blocking control that matches known AI crawler signatures, including by autonomous system.',
              'Custom WAF rules: match on the user-agent token for documented crawlers, or on ASN for the unreliable ones. Cloudflare documents each visitor ASN, which is more stable than any single IP.',
              'Rate limiting: for crawlers that respect robots.txt but crawl too aggressively, rate limiting by ASN or token preserves the relationship while protecting the origin.']),
            ('What to keep in the robots.txt anyway',
             ['Keep your robots.txt decisions current even when enforcing at the edge: compliant crawlers read it, and it documents your policy publicly.',
              'Our AI crawler pages pair each token with its verified behavior, so the robots.txt and the WAF can tell the same story.']),
        ],
        table=('Crawler', 'Enforcement that holds', [
            ('GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, CCBot', 'robots.txt (documented compliance); WAF optional for rate'),
            ('Google-Extended', 'robots.txt token (no fetches to block)'),
            ('Bytespider', 'Cloudflare WAF by ASN or managed AI scraper rule'),
            ('Unknown aggressive agents', 'Custom WAF rule + rate limiting'),
        ]),
        field_note=("The distinction that matters operationally: robots.txt is a request, the WAF is a rule. "
                    "Every site we have migrated to edge enforcement for the unreliable crawlers kept their robots.txt as the public statement of policy, and the two documents finally agree, which makes audits trivial."),
        faqs=[
            ('Does Cloudflare block AI crawlers by default?', 'No. The AI scraper blocking control is opt-in per zone. Enable it in the dashboard security settings.'),
            ('Will WAF blocking affect Googlebot?', 'Not if you scope the rules correctly: match the AI crawler tokens or their ASNs, never all bot traffic.'),
            ('Is WAF blocking free on Cloudflare?', 'The managed AI scraper control and basic custom rules are available on free plans; advanced rules depend on your plan tier.'),
        ],
        release='2026-11-24',
    ),
    dict(
        slug='gptbot-vs-claudebot',
        h1='GPTBot vs ClaudeBot: Training Crawlers Compared',
        title='GPTBot vs ClaudeBot: OpenAI and Anthropic Training Crawlers Compared',
        description='GPTBot vs ClaudeBot: how OpenAI and Anthropic training crawlers differ in defaults, verification, opt-out, and what blocking each one changes.',
        answer=("GPTBot and ClaudeBot are the training crawlers of OpenAI and Anthropic, and they differ in one important default: GPTBot crawls unless you disallow it, while both honor a Disallow rule once present. "
                "Both verify by reverse DNS into their operator's address space, and both are separate from their vendors' search crawlers. "
                "Blocking either removes your content from that vendor's future training data without touching the other vendor or any search engine."),
        body_sections=[
            ('The one default that matters',
             ['GPTBot crawls by default: sites are included in training data unless robots.txt says otherwise.',
              'ClaudeBot also crawls by default, so for both vendors the opt-out is the action that requires a decision.',
              'Neither vendor needs permission to crawl; robots.txt is the only switch.']),
            ('Tokens beyond the training crawler',
             ['OpenAI runs GPTBot for training and OAI-SearchBot for ChatGPT Search, with separate rules.',
              'Anthropic runs ClaudeBot for training and retrieval, plus Claude-User for user-initiated fetches and Claude-SearchBot for search, each with its own rule.',
              'This separation means you can, for example, refuse training while remaining answerable when a user of the product asks about your pages.']),
            ('Verification and enforcement',
             ['Both verify by reverse DNS: GPTBot into the OpenAI space, ClaudeBot into the Anthropic space.',
              'Both honor robots.txt, so the Disallow rule is reliable enforcement; neither needs edge blocking under documented behavior.',
              'Check your own exposure with the AI crawler checker before deciding.']),
        ],
        table=('', 'GPTBot (OpenAI)', 'ClaudeBot (Anthropic)', [
            ('Purpose', 'Training data for GPT models', 'Training and retrieval for Claude'),
            ('Default', 'Crawls unless disallowed', 'Crawls unless disallowed'),
            ('Opt-out rule', 'Disallow: GPTBot', 'Disallow: ClaudeBot'),
            ('Verification', 'Reverse DNS to *.openai.com', 'Reverse DNS to *.anthropic.com'),
            ('Search sibling', 'OAI-SearchBot', 'Claude-SearchBot'),
            ('User-fetch sibling', 'ChatGPT-User', 'Claude-User'),
        ]),
        field_note=("When a client asks which training crawler to block first, the honest answer is that the question is backwards: both are compliant and easy to opt out of, so the hard decisions are Perplexity and Bytespider, where behavior is newer and enforcement is edge-level. "
                    "GPTBot and ClaudeBot are the easy, reversible switches."),
        faqs=[
            ('Should I block both GPTBot and ClaudeBot?', 'Only if your content policy excludes AI training. Both are compliant and reversible, so the decision is low-risk either way.'),
            ('Does blocking GPTBot affect Claude or vice versa?', 'No. Each rule is vendor-specific and independent.'),
            ('Which other tokens should I know about?', 'OAI-SearchBot and ChatGPT-User for OpenAI products, and Claude-SearchBot and Claude-User for Anthropic products, each with separate robots.txt rules.'),
        ],
        release='2026-11-26',
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
  breadcrumb={{[["Home", "/"], ["AI Web Infrastructure", "/ai-web-infrastructure/"], ["{crumb_name}"]]}}
>
  <div class="mx-auto max-w-4xl px-4 py-12">
    <nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">
      <a href="/" class="hover:text-accent">Home</a> <span aria-hidden="true">/</span>
      <a href="/ai-web-infrastructure/" class="hover:text-accent">AI Web Infrastructure</a> <span aria-hidden="true">/</span>
      <span class="text-ink-dim">{crumb_name}</span>
    </nav>
    <h1 class="font-display text-3xl font-bold tracking-tight text-ink sm:text-4xl">{h1}</h1>
    <div class="pd-answer" data-vs="answer">
      <p class="text-lg leading-relaxed text-ink-dim">{answer}</p>
    </div>

    <section class="not-prose my-8" aria-label="Decision table">
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
        Related:
        <a href="/ai-crawlers-list/" class="text-accent hover:text-accent-soft">all AI crawlers</a>,
        <a href="/ai-crawler-checker/" class="text-accent hover:text-accent-soft">AI crawler checker</a>,
        <a href="/does-blocking-ai-crawlers-hurt-seo/" class="text-accent hover:text-accent-soft">does blocking AI crawlers hurt SEO</a>.
      </p>
    </article>
  </div>
</BaseLayout>
'''

count = 0
for pg in PAGES:
    out = OUT / f"{pg['slug']}.astro"
    headers = ''.join(f'<th>{h}</th>' for h in pg['table'][1])
    rows = ''
    for row in pg['table'][2]:
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
        crumb_name=pg['h1'],
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

print(f'{count} batch-2 pages generated')
