// Runs the inline language and analytics scripts of the built pages (docs/) in simulated browsers
// and checks where each visitor ends up. Read-only: it never changes files.
//
//   node tools/check-language-redirect.mjs    after `vite build`; `npm run build` runs both
//
// Rules checked, for every translated language in site.mjs:
// - an English page opened from outside the site goes to the same page in the visitor's saved
//   language, or else in the first browser language the site has;
// - no redirect for an English-first browser, a language the site does not have, a click inside
//   the site, a translated page, or the 404 page;
// - the redirect still works when browser storage is blocked;
// - the translated page reports the visitor's original referrer to analytics, once.

import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import vm from 'node:vm'
import { SITE_URL, locales, localizedFile, pages, urlPath } from '../site.mjs'

const docs = resolve(import.meta.dirname, '..', 'docs')
const inlineScripts = (file) =>
  [...readFileSync(resolve(docs, file), 'utf8').matchAll(/<script>([\s\S]*?)<\/script>/g)].map((match) => match[1])

// Loads a built page with fake browser settings. Returns where it redirected to, if anywhere, and
// the options it passed to the Google Analytics config (undefined when no page view was sent).
function visit(file, { languages = ['en-US'], saved = null, referrer = '', storageBlocked = false, session = {} }) {
  const [languageScript, analyticsScript] = inlineScripts(file)
  const fail = () => {
    throw new Error('storage is blocked')
  }
  const storage = (data) => ({
    getItem: (key) => (storageBlocked ? fail() : key in data ? data[key] : null),
    setItem: (key, value) => (storageBlocked ? fail() : (data[key] = String(value))),
    removeItem: (key) => (storageBlocked ? fail() : delete data[key]),
  })
  let redirect = null
  const path = urlPath(file)
  const window = {
    dataLayer: [],
    localStorage: storage(saved ? { lang: saved } : {}),
    sessionStorage: storage(session),
    navigator: { languages, language: languages[0] },
    location: { origin: SITE_URL, pathname: path, search: '', hash: '#top', replace: (url) => (redirect = url) },
    document: { referrer, addEventListener() {}, querySelector: () => null },
  }
  window.window = window
  const context = vm.createContext(window)
  vm.runInContext(languageScript, context)
  if (!redirect) vm.runInContext(analyticsScript, context)
  const config = window.dataLayer.find((args) => args[0] === 'config')
  return { redirect, analytics: config?.[2] }
}

let failures = 0
function expect(name, result, redirect) {
  const ok = result.redirect === redirect && Boolean(result.analytics) === !redirect
  if (!ok) failures++
  const outcome = result.redirect ? `redirects to ${result.redirect}` : 'stays'
  console.log(`${ok ? 'ok  ' : 'FAIL'}  ${name}: ${outcome}${result.analytics ? ', page view counted' : ', no page view'}`)
}

const caseStudy = pages.find((page) => page !== 'index.html')
const english = [caseStudy, 'index.html']
const linkedIn = 'https://www.linkedin.com/'
const inside = `${SITE_URL}/`
const missing = [...english, '404.html'].filter((file) => !existsSync(resolve(docs, file)))
if (missing.length) {
  console.error(`Missing built pages: ${missing.join(', ')}. Run vite build first.`)
  process.exit(2)
}

for (const { code, htmlLang, ogLocale } of locales.filter(({ code }) => code !== 'en')) {
  // A browser set to this language with a region, such as ko-KR, and English second.
  const browser = [ogLocale.replace('_', '-'), 'en-US']
  for (const file of english) {
    const target = `${urlPath(localizedFile(code, file))}#top`
    expect(`${code} browser opens ${urlPath(file)} from LinkedIn`, visit(file, { languages: browser, referrer: linkedIn }), target)
  }
  expect(`${code} as a second choice after a language the site lacks`, visit('index.html', { languages: ['qaa', htmlLang] }), `/${code}/#top`)
  expect(`English browser that picked ${code} before`, visit('index.html', { saved: code }), `/${code}/#top`)
  expect(`${code} browser that picked English before`, visit('index.html', { languages: browser, saved: 'en' }), null)
  expect(`${code} browser clicking a link inside the site`, visit('index.html', { languages: browser, referrer: inside }), null)
  expect(`${code} browser with storage blocked`, visit('index.html', { languages: browser, storageBlocked: true }), `/${code}/#top`)
  expect(`English browser on a ${code} page`, visit(localizedFile(code, caseStudy), { saved: 'en' }), null)
  expect(`${code} browser on the 404 page`, visit('404.html', { languages: browser }), null)

  const session = {}
  visit(caseStudy, { languages: browser, referrer: linkedIn, session })
  const landing = visit(localizedFile(code, caseStudy), { languages: browser, referrer: `${SITE_URL}${urlPath(caseStudy)}`, session })
  const next = visit(localizedFile(code, 'index.html'), { languages: browser, referrer: inside, session })
  const kept = landing.analytics?.page_referrer === linkedIn && !next.analytics?.page_referrer
  if (!kept) failures++
  console.log(`${kept ? 'ok  ' : 'FAIL'}  ${code} page after a redirect reports LinkedIn as the referrer, once`)
}
expect('English-first browser', visit('index.html', { languages: ['en-US', ...locales.map(({ code }) => code)] }), null)
expect('browser with only a language the site lacks', visit('index.html', { languages: ['qaa'] }), null)

console.log(failures ? `\n${failures} language redirect check(s) failed.` : '\nLanguage redirects work as expected.')
process.exit(failures ? 1 : 0)
