# PromptDNS — promptdns.com

Free DNS, email-authentication, and domain-health tools + the complete guide network
(435-URL topical map; see `../promptdns-topical-map-v2.xlsx`).

## Stack

- **Astro 5** (static-first; zero-JS content pages, islands for tools)
- **Tailwind CSS v4** (CSS-first tokens in `src/styles/global.css`)
- **Vanilla TypeScript tools** — no framework runtime, no backend
- **DNS-over-HTTPS** client engine in `src/lib/doh.ts` (Cloudflare, Google, Quad9 — free, CORS-enabled)
- `@astrojs/sitemap` for sitemap generation

## Develop

```bash
npm install
npm run dev        # http://localhost:4321
```

## Build & deploy

```bash
npm run build      # static output in ./dist
npm run preview
```

Deploy `dist/` to **Cloudflare Pages** (free):
1. Push this folder to a GitHub repo.
2. Cloudflare Pages → Create project → connect repo.
3. Build command `npm run build`, output directory `dist`.
4. Add custom domain `promptdns.com`.

## Structure

```
src/
  lib/doh.ts                      # shared DoH lookup engine (powers all tools)
  components/
    PropagationChecker.astro      # flagship tool island (vanilla TS)
  layouts/BaseLayout.astro        # SEO head + schema.org + header/footer
  pages/
    index.astro                   # homepage (hero checker + tool grid)
    dns-propagation-checker.astro # flagship tool page (FAQ schema included)
    dns/index.astro               # hub: DNS complete guide
    dns-records/index.astro       # hub: record types reference
    email-authentication/index.astro # hub: SPF/DKIM/DMARC
    about.astro                   # author/entity page
```

## Roadmap

Phase 1 launch batch = 24 URLs (3 hubs + 12 flagship tools + 9 pillar guides).
Next tools to build on the same engine: SPF/DKIM/DMARC checkers, blacklist checker,
My IP / IP lookup, AI crawler checker. Each is a thin wrapper over `src/lib/doh.ts`.
