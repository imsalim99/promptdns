"""Generate per-crawler entity pages (spec section 3.8) for the drip queue.

Each page: entity+function H1, AnswerBlock (3-sentence rule), SpecCard
centerpiece (validated facts only), block/allow robots.txt snippets,
reverse-DNS verification, field note, FAQs. Facts cross-checked against
operator documentation 2026-10-28; Pages with staggered publishOn dates
in src/data/publish-queue.js (noindex-hold until release).
"""
import json
import pathlib

OUT = pathlib.Path('src/pages')

BOTS = [
    dict(
        slug='gptbot',
        name='GPTBot',
        operator='OpenAI',
        purpose='training data for GPT models',
        robots='crawls by default; honors Disallow: GPTBot',
        verify='Reverse DNS resolves to *.openai.com',
        block_note='Blocking GPTBot keeps your content out of OpenAI training data but does not affect ChatGPT Search, which uses OAI-SearchBot.',
        answer=("GPTBot is OpenAI's web crawler that collects training data for GPT models. "
                "It crawls sites by default unless robots.txt disallows it, and it honors the Disallow: GPTBot rule. "
                "Its fetches resolve to OpenAI-hosted addresses, which is how you verify a real GPTBot visit."),
        field_note=("In our experience auditing client robots.txt files, the GPTBot question is really a business question: "
                    "do you want your content in future model behavior or not? There is no ranking penalty either way from Google. "
                    "The one mistake to avoid is blocking GPTBot while expecting ChatGPT Search citations, because search uses a different crawler."),
        faqs=[
            ('Does GPTBot crawl my site by default?', 'Yes. GPTBot crawls unless robots.txt disallows it. Opting out is a single rule: User-agent: GPTBot with Disallow: /.'),
            ('Does blocking GPTBot remove me from ChatGPT Search?', 'No. ChatGPT Search uses OAI-SearchBot, a separate crawler with its own rule. Block or allow each one independently.'),
            ('Can GPTBot visit bypass robots.txt?', 'Documented behavior says it honors robots.txt. Verify real visitors by reverse DNS: a genuine GPTBot fetch resolves to an OpenAI address, while spoofers do not.'),
        ],
    ),
    dict(
        slug='claudebot',
        name='ClaudeBot',
        operator='Anthropic',
        purpose='training and retrieval for Claude',
        robots='honors Disallow: ClaudeBot',
        verify='Reverse DNS resolves to *.anthropic.com',
        block_note='Anthropic documents separate tokens for user-initiated fetches (Claude-User) and search (Claude-SearchBot); blocking ClaudeBot only stops the training and retrieval crawler.',
        answer=("ClaudeBot is Anthropic's crawler that collects training data and retrieves pages for Claude. "
                "It honors robots.txt, and Disallow: ClaudeBot keeps it out. "
                "Genuine ClaudeBot fetches resolve to Anthropic-hosted addresses, which is how you verify them."),
        field_note=("Anthropic splitting crawl, user-fetch, and search into separate tokens is the most crawler-transparent behavior of the major AI vendors. "
                    "It means you can allow Claude to answer questions about a page a user shared while still refusing training access, which is a policy most teams have not realized is possible."),
        faqs=[
            ('How do I stop Claude from using my content for training?', 'Add User-agent: ClaudeBot with Disallow: / to robots.txt. Anthropic documents that ClaudeBot honors the rule.'),
            ('What is the difference between ClaudeBot and Claude-User?', 'ClaudeBot crawls for training and retrieval. Claude-User fetches a page only when a Claude user asks about it directly. They are separate tokens with separate rules.'),
            ('How do I verify a ClaudeBot visitor?', 'Reverse DNS on the fetching IP should resolve to an Anthropic address. If it does not, the visitor is spoofing the token.'),
        ],
    ),
    dict(
        slug='google-extended',
        name='Google-Extended',
        operator='Google',
        token_note='a control token, not a separate crawler',
        purpose='Gemini and Vertex training via Googlebot fetches',
        robots='honors Disallow: Google-Extended',
        verify='No separate user-agent: Googlebot does the fetching, the token controls training use',
        block_note='Blocking Google-Extended controls training use only. It does not remove your site from Google Search, AI Overviews, or Gemini grounding.',
        answer=("Google-Extended is a product control that tells Google not to use your site's content for training Gemini and Vertex AI models. "
                "It is not a separate crawler: Googlebot does the fetching, and the Google-Extended token governs whether those fetches may feed model training. "
                "Blocking it does not affect Google Search ranking or AI Overviews."),
        field_note=("Google-Extended is the token people most often misunderstand. Blocking it does not hide you from AI Overviews, which is why teams sometimes block it, see no change in AI Overview presence, and conclude robots.txt is broken. "
                    "It is working exactly as documented: the token controls training, not grounding or search."),
        faqs=[
            ('Does blocking Google-Extended remove me from AI Overviews?', 'No. AI Overviews and Search are unaffected. Google-Extended only controls whether your content trains Gemini and Vertex models.'),
            ('Will blocking Google-Extended hurt my Google rankings?', 'No. Google documents that the token has no effect on Search ranking or indexing.'),
            ('How do I verify Google-Extended visits?', 'You cannot via user-agent, because Googlebot fetches the pages. The token is a policy signal Google applies to those fetches, not a separate crawler you will see in logs.'),
        ],
    ),
    dict(
        slug='perplexitybot',
        name='PerplexityBot',
        operator='Perplexity',
        purpose='search index and answer engine',
        robots='honors Disallow: PerplexityBot',
        verify='Reverse DNS resolves to *.perplexity.ai',
        block_note='Blocking PerplexityBot removes your pages from Perplexity answers. Perplexity-User handles real-time user-initiated fetches under its own token.',
        answer=("PerplexityBot is Perplexity's crawler that builds the search index behind its answer engine. "
                "It honors robots.txt, and Disallow: PerplexityBot keeps your pages out of Perplexity answers. "
                "Genuine PerplexityBot fetches resolve to Perplexity-hosted addresses, which is how you verify them."),
        field_note=("Perplexity is the answer engine where blocking has the most immediate visible effect: opt out today and your pages stop appearing in answers within days, because its index is small and rebuilds often. "
                    "That cuts both ways, so decide deliberately rather than by copying a template robots.txt."),
        faqs=[
            ('How do I remove my site from Perplexity?', 'Add User-agent: PerplexityBot with Disallow: / to robots.txt. Perplexity documents that the crawler honors it.'),
            ('What is Perplexity-User?', 'A separate Perplexity token for real-time fetches a user triggers. It has its own robots.txt rule, so you can allow answers from your pages on request without allowing crawling.'),
            ('How do I verify PerplexityBot?', 'Reverse DNS on the fetching IP should resolve to a Perplexity address. Anything else claiming the token is spoofed.'),
        ],
    ),
    dict(
        slug='oai-searchbot',
        name='OAI-SearchBot',
        operator='OpenAI',
        purpose='ChatGPT Search results',
        robots='honors Disallow: OAI-SearchBot',
        verify='Reverse DNS resolves to *.openai.com',
        block_note='OAI-SearchBot is independent of GPTBot: blocking it removes you from ChatGPT Search while leaving training collection governed by the GPTBot rule.',
        answer=("OAI-SearchBot is OpenAI's crawler that indexes the web for ChatGPT Search. "
                "It honors robots.txt, and sites that block it do not appear in ChatGPT Search results. "
                "Its fetches resolve to OpenAI-hosted addresses, which is how you verify them."),
        field_note=("If citations in ChatGPT Search matter to you, OAI-SearchBot is the token to allow, and the one whose absence explains why a site never shows up in ChatGPT answers. "
                    "It is also the cleanest example of why per-token rules matter: the same vendors run crawlers for search and training with completely different business implications."),
        faqs=[
            ('How do I appear in ChatGPT Search?', 'Allow OAI-SearchBot in robots.txt. Blocking it keeps your site out of ChatGPT Search results.'),
            ('Is OAI-SearchBot the same as GPTBot?', 'No. GPTBot collects training data; OAI-SearchBot indexes for ChatGPT Search. They are separate crawlers with separate rules.'),
            ('How do I verify OAI-SearchBot?', 'Reverse DNS on the fetching IP should resolve to an OpenAI address, same as GPTBot.'),
        ],
    ),
    dict(
        slug='ccbot',
        name='CCBot',
        operator='Common Crawl',
        purpose='open web crawl dataset used by many AI labs',
        robots='honors Disallow: CCBot',
        verify='Reverse DNS resolves to *.commoncrawl.org',
        block_note='Blocking CCBot stops future crawls only. Already-published Common Crawl datasets still contain older snapshots of your site.',
        answer=("CCBot is the Common Crawl Foundation's crawler that builds a public web crawl dataset reused by many AI labs and researchers. "
                "It honors robots.txt, and Disallow: CCBot excludes your site from future crawl runs. "
                "Its fetches resolve to Common Crawl addresses, which is how you verify them."),
        field_note=("The CCBot nuance that surprises people: opting out is not retroactive. Common Crawl publishes periodic dataset snapshots, and content in an already-released snapshot stays there. "
                    "If that matters to your content strategy, the decision to block is time-sensitive in a way most robots.txt rules are not."),
        faqs=[
            ('Does blocking CCBot remove my site from existing datasets?', 'No. It only prevents future crawls. Previously published Common Crawl snapshots are not retroactively edited.'),
            ('Why block CCBot if I already allow AI search bots?', 'Common Crawl is a raw dataset license-free to anyone, including model trainers you have never heard of. Some publishers allow search crawlers but refuse blanket dataset inclusion.'),
            ('How do I verify CCBot?', 'Reverse DNS on the fetching IP should resolve to a Common Crawl address.'),
        ],
    ),
    dict(
        slug='bytespider',
        name='Bytespider',
        operator='ByteDance',
        purpose="data collection behind TikTok's AI stack",
        robots='reported to sometimes ignore robots.txt',
        verify='Reverse DNS is inconsistent; block at the WAF by IP range if strict',
        block_note='Because Bytespider reportedly ignores robots.txt at times, WAF-level blocking by autonomous-system number is the only enforcement that holds.',
        answer=("Bytespider is ByteDance's crawler, associated with data collection for TikTok's AI features. "
                "It is reported to sometimes ignore robots.txt, so a Disallow rule is advisory rather than reliable. "
                "Verification by reverse DNS is inconsistent, which is why strict sites block ByteDance at the firewall level instead."),
        field_note=("Bytespider is the reason every robots.txt conversation should end with a WAF question. "
                    "When a crawler's own documentation is thin and community reports describe robots.txt being ignored, the only enforcement that holds is IP-range blocking at the edge, and Cloudflare's own AI scraper rules do this per autonomous system."),
        faqs=[
            ('Does Bytespider honor robots.txt?', 'Its behavior is reported to be inconsistent, so treat a Disallow rule as advisory. Verify from your logs rather than assuming.'),
            ('How do I actually stop Bytespider?', 'Block its autonomous system at your WAF or edge provider. Cloudflare, which likely fronts your DNS, offers managed rules for AI scraper blocking by ASN.'),
            ('How do I verify a Bytespider visitor?', 'Reverse DNS on its IPs is inconsistent, which is exactly why user-agent verification alone is unreliable for this crawler.'),
        ],
    ),
]

TMPL = '''---
import BaseLayout from '../layouts/BaseLayout.astro';
import SpecCard from '../components/SpecCard.astro';
import {{ isHeld }} from '../data/publish-queue.js';

const held = isHeld('/{slug}/');
---
<BaseLayout
  title="{title} | PromptDNS"
  description="{description}"
  breadcrumb={{[["Home", "/"], ["AI Web Infrastructure", "/ai-web-infrastructure/"], ["{name}"]]}}
>
  <div class="mx-auto max-w-4xl px-4 py-12">
    <nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">
      <a href="/" class="hover:text-accent">Home</a> <span aria-hidden="true">/</span>
      <a href="/ai-web-infrastructure/" class="hover:text-accent">AI Web Infrastructure</a> <span aria-hidden="true">/</span>
      <span class="text-ink-dim">{name}</span>
    </nav>
    <h1 class="font-display text-3xl font-bold tracking-tight text-ink sm:text-4xl">{h1}</h1>
    <div class="pd-answer" data-vs="answer">
      <p class="text-lg leading-relaxed text-ink-dim">{answer}</p>
    </div>

    <section class="not-prose my-8" aria-label="Crawler specification" data-vs="speccard-wrap">
      <SpecCard
        name="{name}"
        operator="{operator}"
        token="{token}"
        purpose="{purpose}"
        robots="{robots}"
        verify="{verify}"
        evidence="{evidence}"
        verified="2026-10-28"
        href="/ai-crawlers-list/"
      />
    </section>

    <article class="rich-text mt-10 max-w-none">
      <h2>How to block {name}</h2>
      <p>Add this rule to your robots.txt at the root of your domain:</p>
      <pre class="overflow-x-auto rounded-lg border border-line bg-panel-2 p-4 font-mono text-xs leading-relaxed text-accent-soft">User-agent: {ua}
Disallow: /</pre>
      <p>{block_note}</p>

      <h2>How to allow {name}</h2>
      <p>If you want {name} to crawl your site, make sure no rule disallows it. An explicit allow looks like this:</p>
      <pre class="overflow-x-auto rounded-lg border border-line bg-panel-2 p-4 font-mono text-xs leading-relaxed text-accent-soft">User-agent: {ua}
Allow: /</pre>
      <p>Then confirm from the live fetch with the <a href="/ai-crawler-checker/" class="text-accent hover:text-accent-soft">AI crawler checker</a>, which reads your published robots.txt the way a crawler would.</p>

      <h2>How to verify {name}</h2>
      <p>{verify_paragraph}</p>
      <pre class="overflow-x-auto rounded-lg border border-line bg-panel-2 p-4 font-mono text-xs leading-relaxed text-accent-soft">{dig}</pre>

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
        <a href="/how-to-block-ai-crawlers/" class="text-accent hover:text-accent-soft">how to block AI crawlers</a>,
        <a href="/how-to-allow-ai-crawlers/" class="text-accent hover:text-accent-soft">how to allow AI crawlers</a>,
        <a href="/robots-txt-guide/" class="text-accent hover:text-accent-soft">robots.txt guide</a>.
      </p>
    </article>
  </div>
</BaseLayout>
'''

count = 0
for bot in BOTS:
    slug = bot['slug']
    bot.setdefault('evidence', 'Reported' if slug == 'bytespider' else 'Documented')
    out = OUT / f'{slug}.astro'
    token = bot.get('token_note') or bot['name']
    h1 = f"{bot['name']}: User-Agent, robots.txt Rules and How to Verify It"
    description = f"{bot['name']} explained: what {bot['operator']}'s crawler does, its user-agent token, robots.txt behavior, how to verify it, and how to block or allow it."
    dig = f"dig +short -x <fetching-ip>\n# A genuine {bot['name']} fetch resolves to an {bot['operator']} address"

    faq_items = ''
    for q, a in bot['faqs']:
        faq_items += (
            '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
            f'<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">{q}'
            '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
            f'<p class="mt-3 text-sm leading-relaxed text-ink-dim">{a}</p></details>'
        )

    verify_paragraph = (
        f"The reliable check is reverse DNS on the fetching IP address. "
        f"Run the lookup below against any visitor claiming the {bot['name']} token; a genuine fetch resolves inside {bot['operator']}'s address space, and a spoofed one does not."
    ) if 'No separate' not in token else (
        f"There is nothing to verify on the wire, because {bot['name']} does not fetch pages itself. "
        f"Googlebot performs the fetches, and the token only sets how Google may use them, which you confirm in your robots.txt rather than in your logs."
    )

    content = TMPL.format(
        slug=slug,
        title=h1,
        description=description,
        name=bot['name'],
        h1=h1,
        answer=bot['answer'],
        operator=bot['operator'],
        token=token,
        purpose=bot['purpose'],
        robots=bot['robots'],
        verify=bot['verify'],
        evidence='Documented' if bot['evidence'] == 'Documented' else 'Reported',
        block_note=bot['block_note'],
        ua=bot['name'],
        verify_paragraph=verify_paragraph,
        dig=dig,
        field_note=bot['field_note'],
        faq_items=faq_items,
    )
    out.write_text(content, encoding='utf-8')
    count += 1
    print(f'Generated: {slug}')

print(f'{count} crawler pages generated')
