import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { defineConfig } from 'vite'

const root = import.meta.dirname

// Every page is a plain HTML file that Vite builds as its own entry.
const pages = [
  'index.html',
  '404.html',
  'work/semantic-search/index.html',
  'work/aws-data-pipeline/index.html',
  'work/solar-mlops/index.html',
  'work/catalog-agent/index.html',
]

// Inlines `<!-- include: partials/x.html -->` so all pages share one head, header, and
// footer without a templating dependency. `{{year}}` is filled in at build time.
function htmlIncludes() {
  return {
    name: 'html-includes',
    transformIndexHtml: {
      order: 'pre',
      handler(html) {
        return html
          .replace(/<!--\s*include:\s*([\w./-]+)\s*-->/g, (_, file) => readFileSync(resolve(root, file), 'utf8').trim())
          .replaceAll('{{year}}', String(new Date().getFullYear()))
      },
    },
    handleHotUpdate({ file, server }) {
      if (file.includes('/partials/')) server.ws.send({ type: 'full-reload' })
    },
  }
}

export default defineConfig({
  appType: 'mpa',
  plugins: [htmlIncludes()],
  build: {
    outDir: 'docs',
    rollupOptions: {
      input: pages.map((page) => resolve(root, page)),
    },
  },
})
