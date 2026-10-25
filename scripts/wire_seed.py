"""One-off: wire dev seed route + SEND_EMAIL env into worker/index.ts."""
import pathlib

p = pathlib.Path("worker/index.ts")
s = p.read_text(encoding="utf-8")

old = "import { handleDmarcEmail, handleDmarcQuery } from './dmarc-ingest';"
new = "import { handleDmarcEmail, handleDmarcQuery } from './dmarc-ingest';\nimport { handleDmarcSeed } from './dev-tools';"
assert old in s, "import anchor"
s = s.replace(old, new, 1)

old = """interface Env {
  DB?: D1Database;
  ASSETS: { fetch(request: Request): Promise<Response> };
}"""
new = """interface Env {
  DB?: D1Database;
  ASSETS: { fetch(request: Request): Promise<Response> };
  SEND_EMAIL?: { send(message: unknown): Promise<void> };
}"""
assert old in s, "env anchor"
s = s.replace(old, new, 1)

old = "    if (path === '/api/domains/dmarc') return handleDmarcQuery(request, env);"
new = "    if (path === '/api/domains/dmarc') return handleDmarcQuery(request, env);\n    if (path === '/api/dev/dmarc-seed') return handleDmarcSeed(request, env);"
assert old in s, "route anchor"
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("index.ts wired")
