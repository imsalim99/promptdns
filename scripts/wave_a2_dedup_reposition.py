"""Fix all remaining table issues: deduplicate ALL duplicate h2+table sections
and move table sections below TocRail/hero diagram."""
import pathlib
import re
from collections import Counter

PAGES = pathlib.Path('src/pages')

TABLE_HEADING_RE = re.compile(
    r'\n?\s*<h2 class="font-display mt-10 text-xl font-semibold text-ink">([^<]+)</h2>\s*\n'
    r'\s*<section class="not-prose my-4" aria-label="Reference table">\s*\n'
    r'\s*<div class="glass rounded-2xl p-5 shadow-lg sm:p-7 overflow-x-auto">\s*\n'
    r'(?:.*?)</section>',
    re.S,
)

def extract_table_sections(s):
    """Extract all table sections, returning (before_tables, table_list, after_tables)."""
    sections = list(TABLE_HEADING_RE.finditer(s))
    if not sections:
        return s, [], None
    first_start = sections[0].start()
    last_end = sections[-1].end()
    before = s[:first_start]
    after = s[last_end:]
    tables = [(m.group(1).strip(), m.group(0).strip()) for m in sections]
    return before, tables, after

def deduplicate(tables):
    seen = set()
    result = []
    for heading, html in tables:
        if heading in seen:
            continue
        seen.add(heading)
        result.append((heading, html))
    return result

for slug in ['what-is-dns', 'spf-record', 'dkim', 'what-is-llms-txt', 'dns-propagation', 'dmarc']:
    p = PAGES / f'{slug}.astro'
    s = p.read_text(encoding='utf-8')

    # Step 1: find the TocRail position (the insertion anchor for tables)
    toc_pos = s.find('class="pd-toc"')
    if toc_pos < 0:
        toc_pos = s.find('On this page')

    # Step 2: extract all table sections
    before, tables, after = extract_table_sections(s)
    if not tables:
        print(f'{slug}: no tables found')
        continue

    # Step 3: deduplicate
    deduped = deduplicate(tables)
    removed = len(tables) - len(deduped)

    # Step 4: find the insertion point (after TocRail close, or after AnswerBlock, whichever is later)
    # TocRail ends with </nav>
    toc_end = s.find('</nav>', toc_pos) if toc_pos >= 0 else -1
    if toc_end >= 0:
        toc_end += len('</nav>')
    # AnswerBlock ends with </div> after data-vs="answer"
    ans_start = s.find('data-vs="answer"')
    ans_end = s.find('</div>', ans_start) + len('</div>') if ans_start >= 0 else -1

    # insertion point: after whichever comes later (TocRail or AnswerBlock)
    insert_at = max(toc_end, ans_end)
    if insert_at < 0:
        insert_at = ans_end

    # Step 5: remove old table sections from current position
    # (they might be scattered, so remove them all then re-insert at the right spot)
    for _, table_html in reversed(tables):
        idx = s.find(table_html)
        if idx >= 0:
            s = s[:idx] + s[idx + len(table_html):]

    # clean up extra blank lines left behind
    s = re.sub(r'\n{3,}', '\n\n', s)

    # Step 6: re-insert deduplicated tables at the insertion point
    # re-find the insertion point after cleanup
    toc_pos2 = s.find('class="pd-toc"')
    if toc_pos2 < 0:
        toc_pos2 = s.find('On this page')
    toc_end2 = s.find('</nav>', toc_pos2) + len('</nav>') if toc_pos2 >= 0 else -1
    ans_start2 = s.find('data-vs="answer"')
    ans_end2 = s.find('</div>', ans_start2) + len('</div>') if ans_start2 >= 0 else -1
    insert_at = max(toc_end2, ans_end2)
    if insert_at < 0:
        insert_at = ans_end2

    table_html = '\n\n    ' + '\n\n    '.join(t[1] for t in deduped)
    s = s[:insert_at] + table_html + s[insert_at:]

    p.write_text(s, encoding='utf-8')
    print(f'{slug}: {len(deduped)} tables kept, {removed} duplicates removed, moved below TocRail')
