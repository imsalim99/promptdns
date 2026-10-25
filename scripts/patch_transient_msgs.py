"""One-off patch: app.astro transient messages.
Both message surfaces (add-domain box, per-card scan result) get a close
button and auto-dismiss: 6s for pass/info, 12s for warn/fail.
"""
import pathlib

p = pathlib.Path("src/pages/app.astro")
s = p.read_text(encoding="utf-8")

# 1. insert the shared transient-message helper before setCardStatus
old = """    function setCardStatus(domain: string, cls: string, text: string) {
      const card = document.querySelector<HTMLElement>(`[data-domain="${CSS.escape(domain)}"]`);
      const el = card?.querySelector<HTMLElement>('.card-status');
      if (!el) return;
      el.className = `card-status mt-3 rounded-md px-3 py-2 text-xs font-medium ${cls}`;
      el.textContent = text;
      el.classList.remove('hidden');
    }"""
new = """    const AUTO_DISMISS_MS = 6000;
    const dismissTimers = new WeakMap<HTMLElement, number>();

    function showTransient(el: HTMLElement, cls: string, text: string) {
      el.className = cls;
      el.textContent = '';
      el.appendChild(document.createTextNode(text));
      const x = document.createElement('button');
      x.type = 'button';
      x.className = 'float-right ml-2 leading-none text-ink-faint hover:text-ink';
      x.setAttribute('aria-label', 'Dismiss message');
      x.textContent = '\\u00d7';
      x.addEventListener('click', () => {
        const t = dismissTimers.get(el);
        if (t) clearTimeout(t);
        el.classList.add('hidden');
      });
      el.appendChild(x);
      el.classList.remove('hidden');
      const prev = dismissTimers.get(el);
      if (prev) clearTimeout(prev);
      const wait = cls.includes('fail') || cls.includes('warn') ? AUTO_DISMISS_MS * 2 : AUTO_DISMISS_MS;
      dismissTimers.set(el, window.setTimeout(() => el.classList.add('hidden'), wait));
    }

    function setCardStatus(domain: string, cls: string, text: string) {
      const card = document.querySelector<HTMLElement>(`[data-domain="${CSS.escape(domain)}"]`);
      const el = card?.querySelector<HTMLElement>('.card-status');
      if (!el) return;
      showTransient(el, `card-status mt-3 rounded-md px-3 py-2 text-xs font-medium ${cls}`, text);
    }"""
assert old in s, "setCardStatus anchor"
s = s.replace(old, new, 1)

# 2. rewrite showMsg to use the helper
old = """    const showMsg = (cls: string, text: string) => {
      const el = document.getElementById('dom-msg')!;
      el.className = `mt-4 rounded-md px-4 py-3 text-sm font-medium ${cls}`;
      el.textContent = text;
      el.classList.remove('hidden');
    };"""
new = """    const showMsg = (cls: string, text: string) => {
      showTransient(document.getElementById('dom-msg')!, `mt-4 rounded-md px-4 py-3 text-sm font-medium ${cls}`, text);
    };"""
assert old in s, "showMsg anchor"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("app.astro messages patched")
