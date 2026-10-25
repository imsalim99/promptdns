"""One-off patch: feedback message after removing a domain."""
import pathlib

p = pathlib.Path("src/pages/app.astro")
s = p.read_text(encoding="utf-8")

old = """      del.addEventListener('click', async () => {
        del.disabled = true;
        try {
          const res = await fetch(`/api/domains/delete?id=${d.id}`, { method: 'POST' });
          const data = (await res.json()) as { ok: boolean };
          if (data.ok) {
            card.remove();
            ensureEmptyState();
            void loadAlerts();
            return;
          }
        } catch { /* fall through: re-enable */ }
        del.disabled = false;
      });"""
new = """      del.addEventListener('click', async () => {
        del.disabled = true;
        try {
          const res = await fetch(`/api/domains/delete?id=${d.id}`, { method: 'POST' });
          const data = (await res.json()) as { ok: boolean; error?: string };
          if (data.ok) {
            card.remove();
            ensureEmptyState();
            void loadAlerts();
            showMsg('bg-pass/10 text-pass border border-pass/30', `${d.domain} removed from monitoring. You can add it again anytime.`);
            return;
          }
          showMsg('bg-fail/10 text-fail border border-fail/30', data.error ?? 'Could not remove the domain.');
        } catch {
          showMsg('bg-warn/10 text-warn border border-warn/30', 'Could not reach the server.');
        }
        del.disabled = false;
      });"""
assert old in s, "del handler anchor"
p.write_text(s.replace(old, new, 1), encoding="utf-8")
print("remove message added")
