import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { readFileSync } from 'node:fs';

// 옛 WordPress 주소(/directory/<slug>/)를 새 주소로 이동
const vendors = JSON.parse(readFileSync(new URL('./src/data/vendors.json', import.meta.url), 'utf8'));
const redirects = { '/directory': '/vendors/' };
for (const v of vendors) redirects[`/directory/${v.slug}`] = `/vendors/${v.slug}/`;

export default defineConfig({
  site: 'https://buykorea.ca',
  trailingSlash: 'always',
  build: { format: 'directory' },
  integrations: [sitemap()],
  redirects,
});
