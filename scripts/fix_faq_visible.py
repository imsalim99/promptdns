"""Render schema-only FAQ questions as visible accordions on 5 guide pages.

These pages declared FAQPage JSON-LD with unique questions but never rendered
them visibly (the visible slot held the removed boilerplate). Visible HTML must
match the structured data, so insert a visible FAQ section built from the const.
"""
import pathlib

PAGES = ["dmarc.astro", "dns-propagation.astro", "mx-record.astro", "what-is-dns.astro", "what-is-dnssec.astro"]


def read_js_string(s: str, start: int) -> tuple[str, int]:
    """Read a JS single- or double-quoted string starting at the quote in s[start]."""
    quote = s[start]
    i = start + 1
    out = []
    while i < len(s):
        c = s[i]
        if c == chr(92) and i + 1 < len(s):  # backslash escape
            nxt = s[i + 1]
            if nxt == "u" and i + 5 < len(s):
                out.append(chr(int(s[i + 2 : i + 6], 16)))
                i += 6
                continue
            out.append({"n": chr(10), "t": chr(9)}.get(nxt, nxt))
            i += 2
            continue
        if c == quote:
            return "".join(out), i + 1
        out.append(c)
        i += 1
    raise ValueError("unterminated string")


def extract_qa(block: str) -> list[tuple[str, str]]:
    qa = []
    parts = block.split("'@type': 'Question'") + block.split('"@type": "Question"')
    # first split list already contains all question chunks; second split adds duplicates
    chunks = block.split("'@type': 'Question'")[1:] or block.split('"@type": "Question"')[1:]
    for chunk in chunks:
        q = a = None
        for key in ("name:", "text:"):
            idx = chunk.find(key)
            if idx < 0:
                continue
            rest = chunk[idx + len(key):]
            j = 0
            while j < len(rest) and rest[j] in " \t":
                j += 1
            if j < len(rest) and rest[j] in ("'", '"'):
                val, _ = read_js_string(rest, j)
                if key == "name:":
                    q = val
                else:
                    a = val
        if q and a:
            qa.append((q, a))
    return qa


for name in PAGES:
    p = pathlib.Path("src/pages") / name
    s = p.read_text(encoding="utf-8")
    # const block: from 'const NAME = {' to the line '}' or '};' at column 0
    start = s.find("= {", s.find("FAQPage") - 400)
    const_start = s.rfind("const ", 0, start)
    end = start
    while True:
        nl = s.find(chr(10), end + 1)
        if nl < 0:
            break
        line = s[nl + 1 : s.find(chr(10), nl + 1)]
        if line.rstrip() in ("}", "};"):
            end = s.find(chr(10), nl + 1)
            break
        end = nl
    block = s[const_start:end]
    qa = extract_qa(block)
    assert len(qa) >= 3, name + ": only " + str(len(qa)) + " questions parsed"

    BS = chr(92)
    cls_summary = (
        "flex cursor-pointer list-none items-center justify-between gap-4 "
        "font-semibold text-ink [&" + BS + "::-webkit-details-marker]:hidden"
    )
    lines = [
        "",
        '      <h2 class="font-display mt-10 text-xl font-semibold text-ink">Frequently asked questions</h2>',
        '      <div class="mt-3 grid gap-3">',
    ]
    for q, a in qa:
        lines.append(
            '        <details class="group rounded-xl border border-line bg-panel/60 px-5 py-4 open:border-accent/40">'
            '<summary class="' + cls_summary + '">' + q
            + '<span class="text-accent transition-transform duration-200 group-open:rotate-45">+</span></summary>'
            '<p class="mt-3 text-sm leading-relaxed text-ink-dim">' + a + "</p></details>"
        )
    lines.append("      </div>")
    section = chr(10).join(lines)

    anchor = "<h2>Related</h2>"
    if anchor in s:
        s = s.replace(anchor, section + "      " + anchor, 1)
        where = "before Related"
    else:
        i = s.rfind("</div>")
        assert i > 0, name + ": no anchor"
        s = s[:i] + section + s[i:]
        where = "before final div"
    p.write_text(s, encoding="utf-8")
    print(name + ": " + str(len(qa)) + " questions rendered (" + where + ")")
