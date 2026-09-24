import { readFileSync } from 'node:fs'
import { relative, resolve } from 'node:path'
import { defineConfig } from 'vite'
import { SITE_URL, locales, localizedFile, pages, urlPath } from './site.mjs'

const root = import.meta.dirname

// Every page is a plain HTML file that Vite builds as its own entry: each page in every
// language, plus the English-only 404 page.
const entries = [...locales.flatMap(({ code }) => pages.map((page) => localizedFile(code, page))), '404.html']

const escapeHtml = (text) =>
  text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;')

const globeIcon =
  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9" /><path d="M3 12h18" /><path d="M12 3a14 14 0 0 1 0 18a14 14 0 0 1 0-18z" /></svg>'
const chevronIcon =
  '<svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6" /></svg>'

// Values for the `{{name}}` placeholders in the partials, based on the page's language folder.
function pageContext(filename) {
  const file = relative(root, filename).replaceAll('\\', '/')
  const locale = locales.find(({ code }) => code !== 'en' && file.startsWith(`${code}/`)) ?? locales[0]
  const page = locale.code === 'en' ? file : file.slice(locale.code.length + 1)
  // The 404 page has no translations, so its language links go to each homepage instead.
  const translatable = pages.includes(page)
  const href = (code) => urlPath(localizedFile(code, translatable ? page : 'index.html'))
  const ui = Object.fromEntries(Object.entries(locale.ui).map(([key, text]) => [key, escapeHtml(text)]))

  const languageLinks = locales.map((l) => {
    const current = l.code === locale.code ? ' aria-current="true"' : ''
    return `<li><a href="${href(l.code)}" hreflang="${l.code}" lang="${l.htmlLang}" data-lang="${l.code}"${current}>${l.name}</a></li>`
  })
  const languageMenu = `<details class="lang-menu">
          <summary class="lang-toggle">
            ${globeIcon}<span class="visually-hidden">${ui.language}: </span>${locale.short}${chevronIcon}
          </summary>
          <ul class="lang-list">
            ${languageLinks.join('\n            ')}
          </ul>
        </details>`

  const alternates = translatable
    ? [...locales.map((l) => [l.code, href(l.code)]), ['x-default', href('en')]]
        .map(([lang, path]) => `<link rel="alternate" hreflang="${lang}" href="${SITE_URL}${path}" />`)
        .join('\n    ')
    : ''

  let translationNote = ''
  if (locale.code !== 'en') {
    const [before, linkText, after] = locale.ui.translated.split(/\{(.+?)\}/)
    translationNote = `<p class="translation-note">${escapeHtml(before)}<a href="${href('en')}" hreflang="en" data-lang="en">${escapeHtml(linkText)}</a>${escapeHtml(after)}</p>`
  }

  return {
    file,
    year: String(new Date().getFullYear()),
    lang: locale.code,
    langCodes: JSON.stringify(locales.map(({ code }) => code)),
    // Only English pages redirect to the visitor's language; a translated URL always opens as is.
    autoRedirect: String(locale.code === 'en' && translatable),
    home: urlPath(localizedFile(locale.code, 'index.html')),
    ogLocale: locale.ogLocale,
    ui,
    alternates,
    languageMenu,
    translationNote,
  }
}

// Inlines `<!-- include: partials/x.html -->` so all pages share one head, header, and footer
// without a templating dependency, then fills the `{{name}}` placeholders for the page's
// language. An unknown placeholder fails the build instead of shipping `{{...}}` text.
function htmlIncludes() {
  return {
    name: 'html-includes',
    transformIndexHtml: {
      order: 'pre',
      handler(html, { filename }) {
        const context = pageContext(filename)
        return html
          .replace(/<!--\s*include:\s*([\w./-]+)\s*-->/g, (_, file) => readFileSync(resolve(root, file), 'utf8').trim())
          .replace(/\{\{\s*([\w.]+)\s*\}\}/g, (placeholder, key) => {
            const value = key.split('.').reduce((object, part) => object?.[part], context)
            if (typeof value !== 'string') throw new Error(`Unknown placeholder ${placeholder} in ${context.file}`)
            return value
          })
      },
    },
    // The sitemap lists every page in every language, so it never falls out of date.
    generateBundle() {
      const urls = locales.flatMap(({ code }) =>
        pages.map((page) => `  <url><loc>${SITE_URL}${urlPath(localizedFile(code, page))}</loc></url>`),
      )
      this.emitFile({
        type: 'asset',
        fileName: 'sitemap.xml',
        source: `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`,
      })
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
      input: entries.map((page) => resolve(root, page)),
    },
  },
})
