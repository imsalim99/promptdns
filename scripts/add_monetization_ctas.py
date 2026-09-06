# -*- coding: utf-8 -*-
"""Add monetization CTAs (Fix My Domain + Send Full Report) to every tool page."""
import re, glob, os

CTA = '''
    <div class="mt-8 rounded-xl border border-accent/25 bg-gradient-to-br from-accent/10 to-violet/10 p-6 not-prose">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 class="font-display font-bold text-ink text-base">Don\\u2019t want to fix this yourself?</h3>
          <p class="mt-1 text-sm text-ink-dim">Our experts will audit and fix every issue on your domain in 48 hours.</p>
        </div>
        <div class="flex gap-3 flex-wrap">
          <a href="/pricing/" class="rounded-lg border border-line bg-panel px-4 py-2.5 text-sm font-medium text-ink hover:border-accent/40 transition">Full Report \\u2014 $9</a>
          <a href="/pricing/" class="btn-cta btn-shimmer px-5 py-2.5 text-sm">Fix My Domain \\u2014 $99</a>
        </div>
      </div>
    </div>'''

count = 0
for f in sorted(glob.glob('src/pages/*.astro')):
    s = open(f, encoding='utf-8').read()
    # Only tool pages (have ToolPanel or similar tool structure)
    if 'ToolPanel' not in s and 'tool-panel' not in s and 'pdns-form' not in s and 'scan-form' not in s:
        continue
    # Skip if already has the CTA
    if 'Fix My Domain' in s:
        continue
    # Skip non-tool pages (guides don't have ToolPanel)
    if 'import ToolPanel' not in s and 'id="propagation-checker"' not in s:
        continue
    
    # Insert CTA right after the closing </section> of the ToolPanel
    # Find the </section> that follows the ToolPanel component
    idx = s.find('</section>')
    if idx > 0:
        insert_at = idx + len('</section>')
        cta = CTA.replace('\\u2019', '\u2019').replace('\\u2014', '\u2014')
        s = s[:insert_at] + '\n' + cta + s[insert_at:]
        open(f, 'w', encoding='utf-8').write(s)
        count += 1
        print('CTA added:', os.path.basename(f))

print(f'\nTotal CTAs added: {count}')
