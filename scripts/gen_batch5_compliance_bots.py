"""Batch 5: compliance cluster (3 pages) + remaining bot entities (6 pages).
All indexable from day one per the publishing rule. Facts from operator
documentation and mandate text, no invented claims."""
import json
import pathlib

OUT = pathlib.Path('src/pages')

# ---- Compliance cluster (3 pages, PowerDMARC counter-play) ----
COMPLIANCE = [
    dict(
        slug='gmail-yahoo-bulk-sender-requirements',
        h1='Gmail and Yahoo Bulk Sender Requirements: The Complete 2024 Checklist',
        title='Gmail and Yahoo Bulk Sender Requirements: SPF, DKIM, DMARC and Beyond',
        description='The complete Gmail and Yahoo bulk sender requirements checklist: SPF, DKIM, DMARC enforcement, one-click unsubscribe, spam rate limits, and PTR, with verification tools for each.',
        answer=("Gmail and Yahoo's February 2024 sender requirements define the authentication and reputation rules for any domain sending 5,000 or more messages per day to their users. "
                "The mandates cover five areas: SPF, DKIM, and DMARC authentication, one-click unsubscribe (RFC 8058), spam-complaint rate below 0.3 percent in Postmaster Tools, valid forward and reverse DNS (PTR matching A), and TLS encryption in transit. "
                "Domains that miss these requirements see 550 rejections, spam-folder placement, or outright suspension of bulk sending privileges."),
        spec_table=('The complete requirements checklist',
            ['Requirement', 'Mandatory configuration', 'Threshold / standard', 'Verify with'],
            [['SPF', 'v=spf1 record covering every sending IP', 'One record, under 10 lookups (RFC 7208)', 'SPF checker'],
             ['DKIM', 'At least 1024-bit key, 2048-bit recommended', 'Valid selector, aligned d= domain', 'DKIM checker'],
             ['DMARC', 'v=DMARC1 with p=none minimum and rua reporting', 'Alignment required: spf or dkim must pass and match From', 'DMARC checker'],
             ['One-click unsubscribe', 'List-Unsubscribe-Post: List-Unsubscribe=One-Click header (RFC 8058)', 'Required for all commercial bulk mail', 'Header analyzer'],
             ['Spam rate', 'Under 0.3 percent in Google Postmaster Tools', '0.1 percent recommended; 0.3 percent triggers enforcement', 'Postmaster Tools'],
             ['Forward and reverse DNS', 'PTR record matching the sending hostname (FCrDNS)', 'Valid PTR per RFC 1912', 'PTR lookup'],
             ['TLS in transit', 'Valid certificate on the receiving MX', 'STARTTLS offered and negotiated', 'SMTP tester']]),
        body_sections=[
            ('Who these requirements apply to',
             ['The threshold is 5,000 messages per day to Gmail or Yahoo addresses, counted across all your sending infrastructure. A single ESP sending 3,000 and a CRM sending 2,000 together cross the line.',
              'The requirements apply to all senders at a minimum level (SPF or DKIM plus DMARC), with the stricter enforcement tier reserved for bulk senders.',
              'Both providers announced the same core set in October 2023 with a February 2024 enforcement date, making this a de facto industry standard rather than a vendor-specific rule.']),
            ('What happens when you miss a requirement',
             ['Gmail returns 550 5.7.26 for authentication failures and 421 4.7.0 for rate-limiting on non-compliant bulk senders.',
              'Yahoo bounces with 554 or defers with 421, and both providers move non-compliant mail to spam before hard-blocking.',
              'The enforcement is gradual: first spam placement, then rejection of a percentage of mail, then full blocking. Each stage is visible in Postmaster Tools.']),
        ],
        field_note=("The one-click unsubscribe header catches more teams off guard than the authentication requirements: it must be a header, not a footer link, and it must work without a login page. "
                    "RFC 8058 compliance is what separates the bulk senders who survive February 2024 from those who see their mail bounce with a 550-5.7.26 flow-up."),
        faqs=[
            ('Does the 5,000-per-day threshold count across multiple ESPs?', 'Yes: the count is all messages to Gmail or Yahoo addresses from your domain, summed across every ESP and in-house server.'),
            ('What happens if I stay below 5,000 per day?', 'The authentication requirements (SPF, DKIM, DMARC) still apply to all senders. The stricter bulk rules (one-click unsubscribe, spam rate monitoring) kick in at the threshold.'),
            ('Does Outlook or Apple have similar requirements?', 'Microsoft announced similar authentication requirements for Outlook.com and Microsoft 365 in 2025. The direction across all major providers is the same: authenticated or blocked.'),
        ],
    ),
    dict(
        slug='pci-dss-4-0-dmarc-requirements',
        h1='PCI-DSS 4.0 and Email Authentication: DMARC Requirements for Payment Entities',
        title='PCI-DSS 4.0 and DMARC: Email Authentication Requirements for Payment Entities',
        description='PCI-DSS 4.0 email authentication: how DMARC, SPF, DKIM and DNSSEC map to the payment-card security standard, with a compliance verification checklist.',
        answer=("PCI-DSS 4.0, the Payment Card Industry Data Security Standard effective March 2025, requires organizations that handle cardholder data to protect against phishing and email-based attacks. "
                "While the standard does not mandate DMARC by name, its anti-phishing and spoofing-protection requirements (mapped across requirements 5, 6, and 12) are best satisfied by SPF, DKIM, and enforced DMARC on every sending domain. "
                "Assessors increasingly expect enforced DMARC (p=quarantine or p=reject) as evidence of the email-security controls the standard describes."),
        spec_table=('PCI-DSS 4.0 requirements mapped to DNS controls',
            ['PCI-DSS requirement', 'What it asks for', 'DNS control that satisfies it', 'Verify with'],
            [['Requirement 5: Anti-malware', 'Protection against phishing mechanisms', 'DMARC enforcement prevents spoofed mail from reaching employees', 'DMARC checker'],
             ['Requirement 6: Secure development', 'Public-facing web applications protected', 'DNSSEC signing and CAA pinning prevent DNS-level attacks', 'DNSSEC checker'],
             ['Requirement 12: Information security policy', 'Organization-wide security policies including email security', 'SPF, DKIM, and enforced DMARC on every sending domain', 'SPF, DKIM checkers'],
             ['Requirement 4: Transmission encryption', 'Cardholder data encrypted in transit', 'TLS on mail transport (MTA-STS enforcement)', 'MTA-STS checker']]),
        body_sections=[
            ('Which entities are in scope',
             ['Any organization that stores, processes, or transmits cardholder data: merchants, payment processors, service providers, and any third party with access to the cardholder data environment.',
              'The standard applies globally, enforced through contracts with card brands and acquirers, not through government regulation. Non-compliance risks fines, increased transaction fees, or loss of card-processing ability.',
              'PCI-DSS 4.0 became the enforced version on March 31, 2025, replacing 3.2.1. The updated version emphasizes authentication, phishing defenses, and automated compliance monitoring.']),
            ('The assessor conversation',
             ['PCI-DSS assessors (QSAs) ask for evidence that email-based attacks are mitigated. Enforced DMARC (p=reject) with aggregate reporting is the strongest evidence.',
              'A domain at p=none with no reporting is a finding; a domain at p=reject with monitored sources is a control. The difference is visible in the DNS in seconds.',
              'Subdomains used for payment pages or cardholder-data systems should have their own DMARC records or inherit an enforcing sp= policy from the organizational domain.']),
        ],
        field_note=("The compliance conversation changes when you can show an assessor your DMARC aggregate reports: not just that the policy is enforced, but that you know every source sending as your domain and have verified each one. "
                    "That evidence comes from monitored aggregate reports, which is exactly what continuous DMARC monitoring provides for the early-access product."),
        faqs=[
            ('Does PCI-DSS 4.0 require DMARC by name?', 'No, it requires protection against phishing and spoofed email. DMARC enforcement is the recognized best practice that satisfies those requirements, and assessors expect it.'),
            ('What happens if I fail a PCI-DSS assessment?', 'Fines, increased transaction fees, or loss of card-processing ability. For service providers, loss of PCI-DSS certification can end the contract.'),
            ('Do subdomains need their own DMARC records?', 'Not if the organizational domain has sp=reject or sp=quarantine. Subdomains inherit the organizational policy unless they publish their own.'),
        ],
    ),
    dict(
        slug='nis2-dns-and-email-security-requirements',
        h1='NIS2 Directive: DNS and Email Security Requirements for Essential Entities',
        title='NIS2 Directive: DNS and Email Security Requirements for EU Essential Entities',
        description='NIS2 Directive DNS and email security requirements mapped to DNSSEC, DMARC enforcement, MTA-STS and registry locks, with a verification checklist for EU entities.',
        answer=("The NIS2 Directive (EU 2022/2555), effective October 2024, requires essential and important entities across 18 sectors to manage cybersecurity risk, including the DNS and email infrastructure their services depend on. "
                "Article 21 asks for supply-chain security, network security, and cryptography, which in DNS terms maps to DNSSEC signing, enforced DMARC, MTA-STS transport encryption, and registry locks on delegation. "
                "Member states had until October 2024 to transpose the directive into national law, with penalties reaching 10 million euros or 2 percent of global turnover for essential entities."),
        spec_table=('NIS2 Article 21 mapped to DNS and email controls',
            ['NIS2 requirement', 'What it asks for', 'DNS / email control', 'Verify with'],
            [['Article 21(2)(c): Supply chain security', 'Vendor and service provider risk managed', 'DMARC aggregate reports on every third-party sender', 'DMARC checker'],
             ['Article 21(2)(d): Network security', 'Network infrastructure protected', 'DNSSEC signing, registry lock on delegation', 'DNSSEC checker'],
             ['Article 21(2)(g): Cryptography', 'Encryption where appropriate', 'MTA-STS enforcement for mail transport, DoH/DoT for resolution', 'MTA-STS checker'],
             ['Article 23: Incident reporting', 'Incidents reported within 24 hours', 'Continuous DNS and email authentication monitoring', 'DNS monitoring']]),
        body_sections=[
            ('Which entities are in scope',
             ['Essential entities: energy, transport, banking, financial market infrastructure, health, drinking water, waste water, digital infrastructure, public administration, space.',
              'Important entities: postal services, waste management, chemicals, food, manufacturing, digital providers, research.',
              'Essential entities face 10 million euros or 2 percent of turnover in penalties; important entities face 7 million or 1.4 percent. Management bodies carry personal liability for compliance failures.']),
            ('The DNS-specific conversation',
             ['NIS2 does not mandate DNSSEC by name, but its cryptography and network-security requirements are best satisfied by DNSSEC-signed zones with monitored chain-of-trust.',
              'Registry locks (registrar-level changes requiring explicit approval) satisfy the delegation-protection expectation for essential entities.',
              'Enforced DMARC satisfies the email-security expectation, and aggregate reports provide the incident-detection evidence Article 23 expects.']),
        ],
        field_note=("NIS2 is the first EU directive that makes management bodies personally liable for cybersecurity failures. That liability is what moves DNS and email authentication from an IT best practice to a board-level compliance item. "
                    "The entities that pass their first NIS2 audit will be the ones whose DNS was already monitored, signed, and enforced before the assessor asked."),
        faqs=[
            ('Does NIS2 apply to UK organizations?', 'No, NIS2 is an EU directive. UK entities doing business with EU essential entities may still face supply-chain expectations from their EU customers.'),
            ('Is DNSSEC required by NIS2?', 'Not by name. Article 21 asks for cryptography and network security, and DNSSEC is the recognized control for DNS integrity. Assessors expect it for essential entities.'),
            ('What is the deadline for NIS2 compliance?', 'Member states transposed NIS2 into national law by October 17, 2024. Entities must comply with their national transposition from that date.'),
        ],
    ),
]

BOT_PAGES = [
    dict(
        slug='applebot-extended',
        name='Applebot-Extended',
        operator='Apple',
        token='Applebot-Extended',
        purpose='AI training for Apple Intelligence (separate from Applebot search)',
        robots='honors Disallow: Applebot-Extended',
        verify='Reverse DNS resolves to *.apple.com',
        evidence='Documented',
        block_note='Blocking Applebot-Extended opts out of Apple Intelligence training without removing your site from Siri, Spotlight, or Safari search, which use the regular Applebot crawler.',
        answer=("Applebot-Extended is Apple's AI training crawler, separate from the Applebot search crawler that powers Siri and Safari suggestions. "
                "It honors robots.txt, and Disallow: Applebot-Extended opts your content out of Apple Intelligence training without affecting search visibility. "
                "Genuine Applebot-Extended fetches resolve to Apple addresses, which is how you verify them."),
        block=("User-agent: Applebot-Extended\nDisallow: /"),
        allow_note='Blocking Applebot-Extended keeps your site in Apple Search results: the two crawlers are fully independent.',
        faqs=[
            ('Does blocking Applebot-Extended affect my Apple search ranking?', 'No. Applebot (search) and Applebot-Extended (training) are separate crawlers with separate rules. Blocking the training token leaves search untouched.'),
            ('How is Applebot-Extended different from Applebot?', 'Applebot powers Siri, Spotlight, and Safari suggestions. Applebot-Extended collects data for Apple Intelligence training. They are separate crawlers with separate robots.txt rules.'),
            ('How do I verify Applebot-Extended?', 'Reverse DNS on the fetching IP should resolve to an Apple address. Spoofed tokens will not resolve into the apple.com space.'),
        ],
    ),
    dict(
        slug='meta-externalagent',
        name='Meta-ExternalAgent',
        operator='Meta',
        token='Meta-ExternalAgent',
        purpose='AI training and retrieval for Meta AI',
        robots='honors Disallow: Meta-ExternalAgent',
        verify='Reverse DNS resolves to *.meta.com or *.facebook.com',
        evidence='Documented',
        block_note='Blocking Meta-ExternalAgent removes your content from Meta AI training. FacebookBot is a separate crawler for the older chatbot use case.',
        answer=("Meta-ExternalAgent is Meta's crawler that collects data for training and improving Meta AI models. "
                "It honors robots.txt, and Disallow: Meta-ExternalAgent keeps your content out of Meta AI training. "
                "Genuine fetches resolve to Meta-hosted addresses, which is how you verify them."),
        block=("User-agent: Meta-ExternalAgent\nDisallow: /"),
        allow_note='FacebookBot and Meta-ExternalAgent are separate tokens; block each independently if you want different policies.',
        faqs=[
            ('Does blocking Meta-ExternalAgent affect my Facebook page?', 'No. The crawler collects web content for AI training; your Facebook page is a separate platform.'),
            ('How do I verify Meta-ExternalAgent?', 'Reverse DNS on the fetching IP should resolve to a Meta or Facebook address.'),
            ('Is Meta-ExternalAgent the same as FacebookBot?', 'No. FacebookBot is the older crawler for the assistant; Meta-ExternalAgent is the newer AI training crawler.'),
        ],
    ),
    dict(
        slug='amazonbot',
        name='Amazonbot',
        operator='Amazon',
        token='Amazonbot',
        purpose='Alexa indexing and AI development',
        robots='honors Disallow: Amazonbot',
        verify='Reverse DNS resolves to *.amazon.com',
        evidence='Documented',
        block_note='Blocking Amazonbot removes your content from Alexa indexing and Amazon AI training. It does not affect Amazon product listings or seller accounts.',
        answer=("Amazonbot is Amazon's web crawler for Alexa indexing and AI development. "
                "It honors robots.txt, and Disallow: Amazonbot keeps your content out of Amazon's crawl. "
                "Genuine fetches resolve to Amazon addresses, which is how you verify them."),
        block=("User-agent: Amazonbot\nDisallow: /"),
        allow_note='Allowing Amazonbot can improve visibility in Alexa answers and Amazon-related AI features.',
        faqs=[
            ('Does Amazonbot affect my product listings?', 'No. Amazonbot crawls the web for Alexa and AI; product listings live on Amazon\u2019s marketplace platform.'),
            ('How do I verify Amazonbot?', 'Reverse DNS on the fetching IP should resolve to an Amazon address.'),
        ],
    ),
    dict(
        slug='cohere-ai',
        name='Cohere-ai',
        operator='Cohere',
        token='cohere-ai',
        purpose='Training data for Command and RAG models',
        robots='honors Disallow: cohere-ai',
        verify='Reverse DNS resolves to *.cohere.com',
        evidence='Documented',
        block_note='Cohere provides enterprise RAG and embedding models; blocking the crawler removes your content from their training and retrieval corpus.',
        answer=("Cohere-ai is Cohere's web crawler that collects training and retrieval data for its enterprise language models. "
                "It honors robots.txt, and Disallow: cohere-ai keeps your content out of Cohere's corpus. "
                "Genuine fetches resolve to Cohere addresses, which is how you verify them."),
        block=("User-agent: cohere-ai\nDisallow: /"),
        allow_note='Allowing cohere-ai makes your content available to enterprise RAG systems built on Cohere.',
        faqs=[
            ('Who uses Cohere models?', 'Cohere sells enterprise language models to Oracle, Salesforce, and other B2B platforms, so your content may reach enterprise users through their products.'),
            ('How do I verify cohere-ai?', 'Reverse DNS on the fetching IP should resolve to a Cohere address.'),
        ],
    ),
    dict(
        slug='diffbot',
        name='Diffbot',
        operator='Diffbot',
        token='Diffbot',
        purpose='Knowledge graph and structured web extraction',
        robots='honors Disallow: Diffbot',
        verify='Reverse DNS resolves to *.diffbot.com',
        evidence='Documented',
        block_note='Diffbot structures web content into knowledge graphs used by enterprise AI systems. Blocking removes your data from their graph.',
        answer=("Diffbot is a web extraction service that structures web content into knowledge graphs used by enterprise AI and search systems. "
                "It honors robots.txt, and Disallow: Diffbot keeps your content out of their graph. "
                "Genuine fetches resolve to Diffbot addresses, which is how you verify them."),
        block=("User-agent: Diffbot\nDisallow: /"),
        allow_note='Allowing Diffbot makes your content available to enterprise knowledge-graph systems.',
        faqs=[
            ('What is a knowledge graph?', 'A structured database of entities and their relationships, built by extracting facts from web pages rather than storing raw text.'),
            ('How do I verify Diffbot?', 'Reverse DNS on the fetching IP should resolve to a Diffbot address.'),
        ],
    ),
    dict(
        slug='youbot',
        name='YouBot',
        operator='You.com',
        token='YouBot',
        purpose='You.com search index and AI answers',
        robots='honors Disallow: YouBot',
        verify='Reverse DNS resolves to *.you.com',
        evidence='Documented',
        block_note='Blocking YouBot removes your content from You.com search results and AI answers.',
        answer=("YouBot is the You.com search engine's crawler that indexes the web for its AI-powered answer engine. "
                "It honors robots.txt, and Disallow: YouBot keeps your pages out of You.com results. "
                "Genuine fetches resolve to You.com addresses, which is how you verify them."),
        block=("User-agent: YouBot\nDisallow: /"),
        allow_note='Allowing YouBot makes your content available in You.com answers.',
        faqs=[
            ('What is You.com?', 'An AI-powered search engine that combines web results with language model answers, similar to Perplexity.'),
            ('How do I verify YouBot?', 'Reverse DNS on the fetching IP should resolve to a You.com address.'),
        ],
    ),
]

def gen_bot(bot):
    slug = bot['slug']
    return f'''---
import BaseLayout from '../../layouts/BaseLayout.astro';
import SpecCard from '../../components/SpecCard.astro';

const faqSchema = {{
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: {json.dumps([{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in bot['faqs']], ensure_ascii=False)},
}};
---
<BaseLayout
  title="{bot['name']}: User-Agent, robots.txt Rules and How to Verify It | PromptDNS"
  description="{bot['name']} explained: what {bot['operator']}'s crawler does, its user-agent token, robots.txt behavior, how to verify it, and how to block or allow it."
  breadcrumb={{[["Home", "/"], ["AI Web Infrastructure", "/ai-web-infrastructure/"], ["{bot['name']}"]]}}
  schema={{[faqSchema]}}
>
  <div class="mx-auto max-w-4xl px-4 py-12">
    <nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">
      <a href="/" class="hover:text-accent">Home</a> <span aria-hidden="true">/</span>
      <a href="/ai-web-infrastructure/" class="hover:text-accent">AI Web Infrastructure</a> <span aria-hidden="true">/</span>
      <span class="text-ink-dim">{bot['name']}</span>
    </nav>
    <p class="font-mono text-xs uppercase tracking-[0.2em] text-accent">AI crawler</p>
    <h1 class="font-display mt-2 text-3xl font-bold tracking-tight text-ink sm:text-4xl">{bot['name']}: User-Agent, robots.txt Rules and How to Verify It</h1>
    <div class="pd-answer" data-vs="answer">
      <p class="text-lg leading-relaxed text-ink-dim">{bot['answer']}</p>
    </div>

    <section class="not-prose my-8" aria-label="Crawler specification">
      <SpecCard
        name="{bot['name']}"
        operator="{bot['operator']}"
        token="{bot['token']}"
        purpose="{bot['purpose']}"
        robots="{bot['robots']}"
        verify="{bot['verify']}"
        evidence="{bot['evidence']}"
        verified="2026-10-28"
        href="/ai-crawlers-list/"
      />
    </section>

    <article class="rich-text mt-10 max-w-none">
      <h2>How to block {bot['name']}</h2>
      <p>Add this rule to your robots.txt at the root of your domain:</p>
      <pre class="overflow-x-auto rounded-lg border border-line bg-panel-2 p-4 font-mono text-xs leading-relaxed text-accent-soft">{bot['block']}</pre>
      <p>{bot['block_note']}</p>

      <h2>How to allow {bot['name']}</h2>
      <p>{bot['allow_note']}</p>

      <h2>How to verify {bot['name']}</h2>
      <p>{bot['verify_paragraph']}</p>
      <pre class="overflow-x-auto rounded-lg border border-line bg-panel-2 p-4 font-mono text-xs leading-relaxed text-accent-soft">{bot['dig']}</pre>

      <aside class="mt-8 rounded-xl border-l-3 border-l-violet/50 bg-violet/5 p-5" aria-label="Practitioner field notes">
        <p class="font-mono text-[10px] uppercase tracking-[0.16em] text-violet mb-2">Field notes</p>
        <p class="text-sm leading-relaxed text-ink-dim italic">{bot['field_note']}</p>
      </aside>

      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>
      <div class="mt-3 grid gap-3">
        {bot['faq_items']}
      </div>

      <p class="mt-8 text-xs text-ink-faint">
        Related:
        <a href="/ai-crawlers-list/" class="text-accent hover:text-accent-soft">all AI crawlers</a>,
        <a href="/ai-crawler-checker/" class="text-accent hover:text-accent-soft">AI crawler checker</a>,
        <a href="/robots-txt-guide/" class="text-accent hover:text-accent-soft">robots.txt guide</a>.
      </p>
    </article>
  </div>
</BaseLayout>
'''

def gen_compliance(pg):
    slug = pg['slug']
    table_th = ''.join(f'<th>{h}</th>' for h in pg['spec_table'][1])
    table_rows = ''
    for row in pg['spec_table'][2]:
        tds = ''.join(
            f'<td class="font-medium text-ink">{c}</td>' if i == 0 else f'<td class="text-sm text-ink-dim">{c}</td>'
            for i, c in enumerate(row)
        )
        table_rows += f'<tr>{tds}</tr>'
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
    table_th_html = ''.join(f'<th>{h}</th>' for h in pg['spec_table'][1])
    table_rows_html = ''
    for row in pg['spec_table'][2]:
        tds = ''.join(
            f'<td class="font-medium text-ink">{c}</td>' if i == 0 else f'<td class="text-sm text-ink-dim">{c}</td>'
            for i, c in enumerate(row)
        )
        table_rows_html += f'<tr>{tds}</tr>'
    faq_schema_json = json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in pg['faqs']
    ]}, ensure_ascii=False)
    return f'''---
import BaseLayout from '../layouts/BaseLayout.astro';

const faqSchema = {faq_schema_json};
---
<BaseLayout
  title="{pg['title']} | PromptDNS"
  description="{pg['description']}"
  breadcrumb={{[["Home", "/"], ["Email Authentication", "/email-authentication/"], ["{pg['h1']}"]]}}
  schema={{[faqSchema]}}
>
  <div class="mx-auto max-w-4xl px-4 py-12">
    <nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">
      <a href="/" class="hover:text-accent">Home</a> <span aria-hidden="true">/</span>
      <a href="/email-authentication/" class="hover:text-accent">Email Authentication</a> <span aria-hidden="true">/</span>
      <span class="text-ink-dim">{pg['h1']}</span>
    </nav>
    <p class="font-mono text-xs uppercase tracking-[0.2em] text-accent">Compliance</p>
    <h1 class="font-display mt-2 text-3xl font-bold tracking-tight text-ink sm:text-4xl">{pg['h1']}</h1>
    <div class="pd-answer" data-vs="answer">
      <p class="text-lg leading-relaxed text-ink-dim">{pg['answer']}</p>
    </div>

    <section class="not-prose my-8" aria-label="Compliance requirements">
      <div class="glass rounded-2xl p-5 shadow-lg sm:p-7 overflow-x-auto">
        <p class="font-mono text-[10px] uppercase tracking-[0.18em] text-accent mb-3">{pg['spec_table'][0]}</p>
        <table class="pdns-table" style="width:100%">
          <thead><tr>{table_th_html}</tr></thead>
          <tbody>{table_rows_html}</tbody>
        </table>
      </div>
    </section>

    <article class="rich-text mt-10 max-w-none">
      {body_html}

      <aside class="mt-8 rounded-xl border-l-3 border-l-violet/50 bg-violet/5 p-5" aria-label="Practitioner field notes">
        <p class="font-mono text-[10px] uppercase tracking-[0.16em] text-violet mb-2">Field notes</p>
        <p class="text-sm leading-relaxed text-ink-dim italic">{pg['field_note']}</p>
      </aside>

      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>
      <div class="mt-3 grid gap-3">
        {faq_items}
      </div>

      <p class="mt-8 text-xs text-ink-faint">
        Verify your compliance:
        <a href="/" class="text-accent hover:text-accent-soft">homepage security scanner</a>,
        <a href="/dmarc-record-checker/" class="text-accent hover:text-accent-soft">DMARC checker</a>,
        <a href="/dnssec-checker/" class="text-accent hover:text-accent-soft">DNSSEC checker</a>.
      </p>
    </article>
  </div>
</BaseLayout>
'''

count = 0
for pg in COMPLIANCE:
    out = OUT / f'{pg["slug"]}.astro'
    out.write_text(gen_compliance(pg), encoding='utf-8')
    count += 1
    print(f'Generated: {pg["slug"]}')

for bot in BOT_PAGES:
    slug = bot['slug']
    out = OUT / f'{slug}.astro'
    bot['verify_paragraph'] = (
        f"The reliable check is reverse DNS on the fetching IP address. "
        f"Run the lookup below against any visitor claiming the {bot['name']} token; a genuine fetch resolves inside {bot['operator']}'s address space, and a spoofed one does not."
    )
    bot['dig'] = f"dig +short -x <fetching-ip>\n# A genuine {bot['name']} fetch resolves to an {bot['operator']} address"
    bot['faq_items'] = ''
    for q, a in bot['faqs']:
        bot['faq_items'] += (
            '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
            f'<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">{q}'
            '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
            f'<p class="mt-3 text-sm leading-relaxed text-ink-dim">{a}</p></details>'
        )
    bot['field_note'] = (
        f"The {bot['name']} decision is per vendor and reversible: robots.txt is a one-line edit, and the verification method tells you within seconds whether a visit was genuine. "
        f"Revisit the decision quarterly as each vendor's product boundaries keep moving."
    )
    out.write_text(gen_bot(bot), encoding='utf-8')
    count += 1
    print(f'Generated: {slug}')

print(f'{count} batch 5 pages generated')
