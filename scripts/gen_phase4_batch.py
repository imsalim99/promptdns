# -*- coding: utf-8 -*-
"""Build the last 2 missing map pages."""
import json

def L(items):
    return '<ul class="list-disc space-y-1.5 pl-5">' + ''.join('<li class="leading-relaxed">' + x + '</li>' for x in items) + '</ul>'

def bp(slug, title, desc, h1, intro, sections, faqs, related):
    fc = ("const faqSchema = " + json.dumps(
        {'@context':'https://schema.org','@type':'FAQPage',
         'mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in faqs]},
        ensure_ascii=False, indent=1) + "\n") if faqs else ""
    fl = "  schema={[faqSchema]}\n" if faqs else ""
    sec = ""
    for h2, html in sections:
        sec += '      <h2 class="font-display mt-10 text-xl font-semibold text-ink">' + h2 + '</h2>\n      ' + html + '\n'
    fh = '<div class="mt-3 grid gap-3">' + ''.join(
        '<details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
        '<summary class="flex cursor-pointer list-none items-center justify-between gap-4 font-semibold text-ink [&::-webkit-details-marker]:hidden">' + q +
        '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
        '<p class="mt-3 text-sm leading-relaxed text-ink-dim">' + a + '</p></details>' for q, a in faqs) + '</div>'
    rl = '<ul class="mt-3 grid gap-2">' + ''.join(
        '<li><a href="' + href + '" class="text-accent hover:text-accent-soft">' + label + ' →</a></li>' for label, href in related) + '</ul>'
    doc = (
        "---\nimport BaseLayout from '../layouts/BaseLayout.astro';\n" + fc + "---\n"
        "<BaseLayout\n  title=\"" + title + " | PromptDNS\"\n  description=\"" + desc + "\"\n" + fl + ">\n"
        '  <div class="mx-auto max-w-3xl px-4 py-12">\n'
        '    <nav class="mb-4 text-sm text-ink-faint" aria-label="Breadcrumb">\n'
        '      <a href="/" class="hover:text-accent">Home</a> <span aria-hidden="true">/</span>\n'
        '      <span class="text-ink-dim">' + h1 + '</span>\n'
        '    </nav>\n'
        '    <h1 class="font-display text-3xl font-bold tracking-tight text-ink sm:text-4xl">' + h1 + '</h1>\n'
        '    <p class="mt-5 text-lg leading-relaxed text-ink-dim">' + intro + '</p>\n'
        '    <div class="rich-text mt-8">\n' + sec +
        '      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>\n'
        '      ' + fh + '\n'
        '      <div class="mt-10 flex items-center gap-3 rounded-xl border border-line bg-panel/40 px-5 py-3">\n'
        '        <span class="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-accent to-violet font-display text-xs font-bold text-canvas">PD</span>\n'
        '        <div><p class="text-sm font-medium text-ink">PromptDNS Team</p>\n'
        '        <p class="text-xs text-ink-faint">Last updated: September 2026</p></div>\n'
        '      </div>\n'
        '      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Related</h2>\n'
        '      ' + rl + '\n'
        '    </div>\n'
        '  </div>\n'
        '</BaseLayout>\n'
    )
    open('src/pages/' + slug + '.astro', 'w', encoding='utf-8').write(doc)

# ===== 1. DNS Threat Protection Checklist =====
bp('dns-threat-protection-checklist',
 'DNS Threat Protection Checklist',
 'dns threat protection checklist',
 'DNS Threat Protection Checklist',
 'A complete checklist to harden your DNS against hijacking, poisoning, tunneling, and amplification attacks.',
 [
  ("The checklist", L([
    'Enable DNSSEC at your DNS host and publish the DS record at your registrar.',
    'Enable registrar lock and two-factor authentication on your registrar account.',
    'Set CAA records to restrict certificate issuance to your trusted CAs.',
    'Disable open recursion if you self-host DNS.',
    'Monitor DNS record changes with automated alerts.',
    'Use a managed DNS provider with anycast network and DDoS protection.',
    'Keep nameserver software updated if self-hosting.',
    'Restrict zone transfers (AXFR) to known secondary IPs only.',
    'Set a reasonable SOA minimum TTL for negative caching.',
    'Monitor Certificate Transparency logs for unauthorized certificates.',
   ])),
 ],
 [
  ["What\u2019s the most important item?","DNSSEC: it makes all forged answers detectable. Registrar lock and 2FA are equally critical for preventing hijacking."],
  ["How often should I review?","Quarterly for a full audit, and after any infrastructure or provider change."],
  ["Does DNS threat protection affect performance?","DNSSEC adds ~100-200 bytes per response; anycast DNS absorbs attacks at the edge. Impact is negligible."],
  ["What\u2019s the first step?","Run the homepage security scanner to see your current posture, then work through this list."],
  ["Is my DNS provider secure?","Major providers (Cloudflare, Route 53, Google Cloud DNS) have strong internal controls, but your registrar account is the soft target."],
  ["Can DNS attacks affect my email?","Yes: DNS hijacking or poisoning can redirect MX records, intercepting all your mail. Email authentication (SPF/DKIM/DMARC) is a defense."],
 ],
 [("DNS security hub","/dns-security/"), ("What is DNSSEC","/what-is-dnssec/"), ("DNS hijacking","/dns-hijacking/")],
)

# ===== 2. ChatGPT Search Operators =====
bp('chatgpt-search-operators',
 'How ChatGPT Search Works and How to Optimize for It',
 'chatgpt search operators',
 'How ChatGPT Search Works (and How to Optimize for It)',
 'ChatGPT Search uses OAI-SearchBot to index the web for real-time answers. Understanding how it selects and cites sources helps you stay visible in AI-powered search.',
 [
  ("How it differs from Google Search", L([
    'No keyword rankings: ChatGPT synthesizes answers from multiple sources and cites them inline.',
    'No page authority: relevance and freshness matter more than backlink profiles.',
    'OAI-SearchBot (not GPTBot) handles search indexing: blocking GPTBot doesn\u2019t affect ChatGPT Search visibility.',
    'Results are conversational: your content may be quoted alongside competitors in the same answer.',
   ])),
  ("How to optimize",
   '<ol class="list-decimal space-y-1.5 pl-5"><li>Allow OAI-SearchBot in robots.txt (separate from GPTBot).</li><li>Publish clear, factual content with structured data.</li><li>Keep content fresh: ChatGPT Search favors recent information for time-sensitive queries.</li><li>Publish an <a href="/llms-txt-generator/">llms.txt</a> to guide the model\u2019s understanding of your site.</li><li>Maintain domain-level trust signals (DNSSEC, email authentication).</li></ol>'),
 ],
 [
  ["Can I track ChatGPT Search traffic?","Indirectly: check referrer data for chat.openai.com or chatgpt.com in your analytics. Direct tracking is limited."],
  ["Does blocking GPTBot affect ChatGPT Search?","No: OAI-SearchBot is the search crawler. GPTBot is for training data. They\u2019re independent."],
  ["How does ChatGPT choose which sources to cite?","It combines retrieval (based on relevance and freshness) with ranking signals. Clear, authoritative, well-structured content is more likely to be cited."],
  ["Can I pay for better ChatGPT placement?","No: ChatGPT Search citations are organic. There is no paid placement mechanism."],
  ["Does my site need to be popular to be cited?","No: ChatGPT cites sources based on relevance and quality, not traffic volume. Smaller sites with authoritative content get cited."],
  ["How often does ChatGPT Search update?","OAI-SearchBot crawls continuously, but the index update frequency isn\u2019t public. Fresh content tends to get picked up faster."],
 ],
 [("AI crawlers list","/ai-crawlers-list/"), ("Allow AI crawlers","/how-to-allow-ai-crawlers/"), ("AI readiness checker","/ai-readiness-checker/")],
)
