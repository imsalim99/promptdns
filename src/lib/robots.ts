/**
 * robots.txt parsing focused on AI crawlers + llms.txt helpers.
 */
export interface AiBot {
  name: string;
  vendor: string;
  tokens: string[];
  purpose: string;
}

export const AI_BOTS: AiBot[] = [
  { name: 'GPTBot', vendor: 'OpenAI', tokens: ['gptbot'], purpose: 'Training data for OpenAI models' },
  { name: 'OAI-SearchBot', vendor: 'OpenAI', tokens: ['oai-searchbot'], purpose: 'Search results in ChatGPT Search' },
  { name: 'ChatGPT-User', vendor: 'OpenAI', tokens: ['chatgpt-user'], purpose: 'Live fetches for ChatGPT users' },
  { name: 'ClaudeBot', vendor: 'Anthropic', tokens: ['claudebot', 'claude-web', 'anthropic-ai'], purpose: 'Training + fetches for Claude' },
  { name: 'Google-Extended', vendor: 'Google', tokens: ['google-extended'], purpose: 'Gemini training (does not affect Search)' },
  { name: 'Googlebot', vendor: 'Google', tokens: ['googlebot'], purpose: 'Google Search + AI Overviews' },
  { name: 'PerplexityBot', vendor: 'Perplexity', tokens: ['perplexitybot'], purpose: 'Answers engine indexing' },
  { name: 'CCBot', vendor: 'Common Crawl', tokens: ['ccbot'], purpose: 'Open dataset used by many AI labs' },
  { name: 'Bytespider', vendor: 'ByteDance', tokens: ['bytespider'], purpose: 'Data collection (often ignores robots)' },
  { name: 'Applebot-Extended', vendor: 'Apple', tokens: ['applebot-extended'], purpose: 'Apple Intelligence training' },
  { name: 'meta-externalagent', vendor: 'Meta', tokens: ['meta-externalagent', 'facebookexternalhit'], purpose: 'Meta AI training' },
  { name: 'Amazonbot', vendor: 'Amazon', tokens: ['amazonbot'], purpose: 'Alexa/Amazon AI' },
];

export interface BotVerdict {
  bot: AiBot;
  status: 'allowed' | 'blocked' | 'partial' | 'no-rules';
  rules: string[];
}

interface RobotsGroup {
  agents: string[];
  disallows: string[];
  allows: string[];
}

export function parseRobots(txt: string): { groups: RobotsGroup[]; sitemaps: string[]; hasWildcard: boolean } {
  const groups: RobotsGroup[] = [];
  const sitemaps: string[] = [];
  let current: RobotsGroup | null = null;

  for (const rawLine of txt.split(/\r?\n/)) {
    const line = rawLine.replace(/#.*$/, '').trim();
    if (!line) continue;
    const colon = line.indexOf(':');
    if (colon < 0) continue;
    const field = line.slice(0, colon).trim().toLowerCase();
    const value = line.slice(colon + 1).trim();

    if (field === 'user-agent') {
      if (current && current.disallows.length + current.allows.length > 0) groups.push(current);
      else if (current) groups.push(current);
      current = { agents: [], disallows: [], allows: [] };
      // consecutive User-agent lines share one group
      const last = groups[groups.length - 1];
      if (last && last.disallows.length === 0 && last.allows.length === 0 && last !== current && groups.length && current.agents.length === 0) {
        last.agents.push(value.toLowerCase());
        current = last;
        continue;
      }
      current.agents.push(value.toLowerCase());
    } else if (current) {
      if (field === 'disallow') current.disallows.push(value);
      else if (field === 'allow') current.allows.push(value);
    }
    if (field === 'sitemap') sitemaps.push(value);
  }
  if (current) groups.push(current);

  return { groups, sitemaps, hasWildcard: groups.some((g) => g.agents.includes('*')) };
}

export function verdictsFor(groups: RobotsGroup[]): BotVerdict[] {
  return AI_BOTS.map((bot) => {
    const applicable = groups.filter((g) =>
      g.agents.some((a) => bot.tokens.some((t) => a.includes(t) || t.includes(a) && a.length > 3)),
    );
    const wildcard = groups.filter((g) => g.agents.includes('*'));
    const use = applicable.length ? applicable : wildcard;
    if (!use.length) {
      return { bot, status: 'no-rules', rules: [] };
    }
    const rules: string[] = [];
    let blocked = false;
    let partial = false;
    for (const g of use) {
      for (const d of g.disallows) {
        rules.push(`Disallow: ${d}`);
        if (d === '/' || d === '/*' || d === '*') blocked = true;
        else partial = true;
      }
      for (const a of g.allows) rules.push(`Allow: ${a}`);
    }
    return { bot, status: blocked ? 'blocked' : partial ? 'partial' : 'allowed', rules: [...new Set(rules)] };
  });
}

export function looksLikeHtml(txt: string): boolean {
  const head = txt.slice(0, 500).toLowerCase();
  return head.includes('<!doctype') || head.includes('<html') || head.includes('<head');
}

export function buildLlmsTxt(opts: {
  siteName: string;
  url: string;
  summary: string;
  sections: { heading: string; links: { url: string; title: string; desc?: string }[] }[];
}): string {
  const lines: string[] = [];
  lines.push(`# ${opts.siteName}`);
  lines.push('');
  lines.push(`> ${opts.summary}`);
  lines.push('');
  for (const s of opts.sections) {
    lines.push(`## ${s.heading}`);
    lines.push('');
    for (const l of s.links) {
      lines.push(`- [${l.title}](${l.url}): ${l.desc ?? ''}`);
    }
    lines.push('');
  }
  return lines.join('\n');
}
