import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';
import { isHeld } from './src/data/publish-queue.js';

export default defineConfig({
  site: 'https://promptdns.com',
  integrations: [sitemap({ filter: (page) => !isHeld(new URL(page).pathname) })],
  vite: {
    plugins: [tailwindcss()],
  },
});
