// Checks every translated page against its English page. Read-only: it never changes files.
//
//   node tools/check-translations.mjs          all languages
//   node tools/check-translations.mjs ko de    only these languages
//
// A translation must have:
// - the right <html lang>, canonical URL, and og:url, and a translated title and description;
// - the same body markup as English (elements, classes, ids, links, and image sources), with links
//   to pages under its language folder, e.g. /ko/work/semantic-search/, and links to files, such
//   as /certificates/woosong-diploma.jpg, exactly as in English;
// - identical technology tags, code, and inline SVG icons;
// - the same numbers. Values are compared, not text, so "2M+" (en), "200만+" (ko), "2 Mio.+" (de),
//   "2 млн+" (ru), and "2 mln+" (uz) all count as 2,000,000. English numbers written as words ("four", "twice")
//   may appear as digits in a translation.
// - none of the banned words below.

import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { SITE_URL, locales, localizedFile, pages, urlPath } from '../site.mjs'

const root = resolve(import.meta.dirname, '..')

// Each language's digit-group and decimal separators, and scale words that multiply the number
// before them. Attached "M" and "K" (2M, 300K) work in every language. Russian and Uzbek group
// digits with a space (300 000), usually a non-breaking one.
const numberFormats = {
  en: { group: ',', decimal: '\\.', scales: { million: 1e6 } },
  ko: { group: ',', decimal: '\\.', scales: { 만: 1e4 } },
  de: { group: '\\.', decimal: ',', scales: { Mio: 1e6, Millionen: 1e6 } },
  ru: { group: '[ \\u00a0\\u202f]', decimal: ',', scales: { млн: 1e6, тыс: 1e3 } },
  uz: { group: '[ \\u00a0\\u202f]', decimal: ',', scales: { mln: 1e6, million: 1e6, ming: 1e3 } },
}

const englishNumberWords = { one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10, twice: 2 }

// Words a translation must not contain: `all` applies to every language, other keys to one.
const banned = {
  all: [
    [/\bRex\b/i, 'the company is spelled "Recs Innovation"'],
    [/Kotlin/i, 'Kotlin is never listed as a skill'],
  ],
  de: [
    [/Ingenieur/i, 'job titles stay in English: "Ingenieur" is a protected title in Germany'],
    [/\b(?:du|dich|dir|dein\w*)\b/i, 'address the reader formally, with "Sie"'],
  ],
  // \b only knows Latin letters, so Russian words are bounded by Cyrillic lookarounds.
  ru: [
    [/(?<![а-яё])(?:ты|тебя|тебе|тобой|тво(?:й|я|ё|е|и|его|ей|ему|им|ими|их|ю))(?![а-яё])/i, 'address the reader formally, with "вы"'],
    [/Котлин/i, 'Kotlin is never listed as a skill'],
  ],
  // Uzbek Latin writes oʻ and gʻ with ʻ (U+02BB) and the tutuq belgisi with ʼ (U+02BC), as in
  // maʼlumot. Typed apostrophes look the same but break search and spell checking.
  uz: [
    [/(?<!\p{L})(?:sen|seni|senga|sendan|senda|sening|senlar\p{L}*)(?!\p{L})/iu, 'address the reader formally, with "Siz"'],
    [/\p{L}['‘’`]/u, 'write oʻ and gʻ with ʻ (U+02BB) and the tutuq belgisi with ʼ (U+02BC)'],
    [/[oOgG]ʼ/u, 'oʻ and gʻ take ʻ (U+02BB), not ʼ (U+02BC)'],
    [/(?<![oOgG])ʻ/u, 'ʻ (U+02BB) follows only o and g; the tutuq belgisi is ʼ (U+02BC)'],
  ],
}

const decode = (text) =>
  text
    .replace(/&nbsp;/g, ' ')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
    .replace(/&amp;/g, '&')

const between = (html, pattern) => html.match(pattern)?.[1]
const bodyOf = (html) => between(html, /<body>([\s\S]*)<\/body>/) ?? ''
const titleOf = (html) => decode(between(html, /<title>([\s\S]*?)<\/title>/) ?? '').trim()
const metaOf = (html, key) =>
  decode(between(html, new RegExp(`<meta\\s+(?:name|property)="${key}"\\s+content="([^"]*)"`)) ?? '').trim()
const lineAt = (html, index) => html.slice(0, index).split('\n').length

function visibleText(html) {
  const body = bodyOf(html)
    .replace(/<script[\s\S]*?<\/script>/g, ' ')
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<[^>]+>/g, ' ')
  return decode([titleOf(html), metaOf(html, 'description'), metaOf(html, 'og:title'), metaOf(html, 'og:description'), body].join('\n'))
}

// Numeric values in a text. Years count; Korean month numbers (3월) are skipped because English
// writes months as words.
function numbersIn(text, code) {
  const { group, decimal, scales } = numberFormats[code]
  const number = `\\d{1,3}(?:${group}\\d{3})+(?:${decimal}\\d+)?|\\d+(?:${decimal}\\d+)?`
  const words = Object.keys(scales).join('|')
  // The lookbehinds skip digits inside names such as GPT-4o, ResNet50, Neo4j, S3, and accuracy@1.
  const pattern = new RegExp(
    `(?<![A-Za-z\\d@])(?<![A-Za-z]-)(?<!\\d[.,])(${number})(?:([MK])(?![A-Za-z])|\\s?(${words})|(?![A-Za-z\\d]))`,
    'g',
  )
  const values = new Set()
  for (const match of text.matchAll(pattern)) {
    const [whole, digits, suffix, word] = match
    if (/^\s?월/.test(text.slice(match.index + whole.length))) continue
    const plain = digits.replace(new RegExp(group, 'g'), '').replace(new RegExp(decimal), '.')
    const scale = suffix ? { M: 1e6, K: 1e3 }[suffix] : word ? scales[word] : 1
    values.add(Math.round(Number(plain) * scale * 1000) / 1000)
  }
  if (code === 'en') {
    for (const [, word] of text.toLowerCase().matchAll(/\b(one|two|three|four|five|six|seven|eight|nine|ten|twice)\b/g)) {
      values.add(-englishNumberWords[word]) // negative: allowed in a translation, not required
    }
  }
  return values
}

// A site path is a page when it ends in a folder or .html, before any #fragment or ?query. Other
// paths, such as /certificates/woosong-diploma.jpg, are files that every language shares.
const isPage = (path) => /(?:\/|\.html)$/.test(path.replace(/[?#].*$/, ''))

// Opening tags with the attributes that define structure and navigation.
function markupOf(html, code, report) {
  const body = bodyOf(html)
  const offset = html.indexOf(body)
  const tokens = []
  for (const match of body.matchAll(/<([a-zA-Z][\w-]*)((?:\s[^>]*)?)>/g)) {
    const [, tag, attrs] = match
    const line = lineAt(html, offset + match.index)
    const attr = (name) => attrs.match(new RegExp(`\\s${name}="([^"]*)"`))?.[1]
    let href = attr('href')
    if (code !== 'en' && href?.startsWith('/') && isPage(href)) {
      if (href.startsWith(`/${code}/`)) href = href.slice(code.length + 1)
      else report(`line ${line}: internal link ${href} is not under /${code}/`)
    }
    const parts = [tag]
    for (const [name, value] of [['class', attr('class')], ['id', attr('id')], ['href', href], ['src', attr('src')], ['rel', attr('rel')], ['aria-labelledby', attr('aria-labelledby')]]) {
      if (value !== undefined) parts.push(`${name}="${value}"`)
    }
    tokens.push({ text: `<${parts.join(' ')}>`, line })
  }
  return tokens
}

const listsOf = (html, pattern) => [...bodyOf(html).matchAll(pattern)].map((match) => match[1].replace(/\s+/g, ' ').trim())

function checkPage(locale, page, report) {
  const file = localizedFile(locale.code, page)
  const en = readFileSync(resolve(root, page), 'utf8')
  const html = readFileSync(resolve(root, file), 'utf8')

  // Head
  if (!html.includes(`<html lang="${locale.htmlLang}">`)) report(`<html lang> must be "${locale.htmlLang}"`)
  const url = SITE_URL + urlPath(file)
  if (!html.includes(`<link rel="canonical" href="${url}" />`)) report(`canonical link must be ${url}`)
  if (metaOf(html, 'og:url') !== url) report(`og:url must be ${url}`)
  for (const [label, value, source] of [
    ['<title>', titleOf(html), titleOf(en)],
    ['description', metaOf(html, 'description'), metaOf(en, 'description')],
    ['og:title', metaOf(html, 'og:title'), metaOf(en, 'og:title')],
    ['og:description', metaOf(html, 'og:description'), metaOf(en, 'og:description')],
  ]) {
    if (!value) report(`${label} is missing`)
    else if (value === source) report(`${label} is not translated`)
  }
  if (/application\/ld\+json|google-site-verification/.test(html)) {
    report('JSON-LD and the Search Console tag belong on the English homepage only')
  }
  const includes = (text) => [...text.matchAll(/<!--\s*include:\s*([\w./-]+)\s*-->/g)].map((match) => match[1]).join(', ')
  if (includes(html) !== includes(en)) report(`partial includes must match English: ${includes(en)}`)

  // Markup: compare tag by tag and report the first difference; later ones follow from it.
  const expected = markupOf(en, 'en', report)
  const actual = markupOf(html, locale.code, report)
  for (let i = 0; i < Math.max(expected.length, actual.length); i++) {
    if (expected[i]?.text === actual[i]?.text) continue
    const found = actual[i] ? `line ${actual[i].line}: found ${actual[i].text}` : 'the page ends early'
    report(`markup differs from English (${page} line ${expected[i]?.line ?? 'end'}: ${expected[i]?.text ?? 'nothing more'}); ${found}`)
    break
  }

  // Technology tags, code, and inline icons stay exactly as in English.
  for (const [label, pattern] of [
    ['technology tags', /<ul class="tags"[^>]*>([\s\S]*?)<\/ul>/g],
    ['code', /<code>([\s\S]*?)<\/code>/g],
    ['icons (inline SVG)', /(<svg[\s\S]*?<\/svg>)/g],
  ]) {
    if (listsOf(html, pattern).join(' | ') !== listsOf(en, pattern).join(' | ')) report(`${label} must match English exactly`)
  }

  // Names
  const text = visibleText(html)
  for (const name of ['G-Man Auto Parts', 'Recs Innovation']) {
    if (visibleText(en).includes(name) && !text.includes(name)) report(`"${name}" must stay as written in English`)
  }
  for (const [pattern, reason] of [...banned.all, ...(banned[locale.code] ?? [])]) {
    const match = text.match(pattern)
    if (match) report(`found "${match[0]}": ${reason}`)
  }

  // Numbers
  const source = numbersIn(visibleText(en), 'en')
  const target = numbersIn(text, locale.code)
  const missing = [...source].filter((value) => value >= 0 && !target.has(value))
  const extra = [...target].filter((value) => !source.has(value) && !source.has(-value))
  if (missing.length) report(`numbers in English but not here: ${missing.join(', ')}`)
  if (extra.length) report(`numbers here but not in English: ${extra.join(', ')}`)
}

const requested = process.argv.slice(2)
const unknown = requested.filter((code) => !locales.some((locale) => locale.code === code && code !== 'en'))
if (unknown.length) {
  console.error(`Unknown language: ${unknown.join(', ')}. Use: ${locales.slice(1).map(({ code }) => code).join(', ')}`)
  process.exit(2)
}
const unformatted = locales.filter(({ code }) => !numberFormats[code]).map(({ code }) => code)
if (unformatted.length) {
  console.error(`Add the number format of ${unformatted.join(', ')} to numberFormats in tools/check-translations.mjs.`)
  process.exit(2)
}

let problems = 0
let checked = 0
for (const locale of locales.filter(({ code }) => code !== 'en' && (!requested.length || requested.includes(code)))) {
  for (const page of pages) {
    const file = localizedFile(locale.code, page)
    const issues = []
    if (!existsSync(resolve(root, file))) issues.push('missing: translate the English page into this file')
    else checkPage(locale, page, (message) => issues.push(message))
    checked++
    if (!issues.length) continue
    problems += issues.length
    console.log(`\n${file}`)
    for (const issue of issues) console.log(`  - ${issue}`)
  }
}

console.log(problems ? `\n${problems} problem(s) in ${checked} translated pages.` : `All ${checked} translated pages match English.`)
process.exit(problems ? 1 : 0)
