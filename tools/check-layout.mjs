// Opens every built page (docs/) in headless Chrome or Edge at phone, tablet, and desktop widths
// and fails when something sticks out sideways. Read-only: it never changes files.
//
//   node tools/check-layout.mjs    after `vite build`; `npm run build` runs both
//
// Rules checked on every page in every language, with the language menu open, at 320px (the
// narrowest phone screen that web accessibility rules require) and wider phone widths, tablet
// and desktop widths, and both sides of every width breakpoint in the stylesheet:
// - the page never scrolls sideways, and nothing reaches past the left or right screen edge,
//   unless a box around it clips or scrolls it;
// - no text sticks out of its box, such as a long word poking out of a card or a button;
// - the header stays on one row: the menu does not wrap to a second line.
// These are checked with reduced motion, so every chart and drawing is in its final place. Then
// every page is scrolled from top to bottom with motion on, at a phone and a desktop width:
// - the page never scrolls sideways while things move in;
// - every animation has played or is playing by the end, so nothing is left hidden because it
//   never counted as scrolled into view (see src/motion.css).
//
// Text is measured in Arial (Windows) or Liberation Sans (Linux) and Courier New or Liberation
// Mono, because each pair has identical letter widths, so this PC and the GitHub build get the
// same result. They are about as wide as the phone fonts (Roboto, SF Mono) and a little wider
// than Segoe UI and Consolas on Windows, which leaves room for real phones.

import { existsSync } from 'node:fs'
import { resolve } from 'node:path'
import { chromium } from 'playwright-core'
import { preview } from 'vite'
import { locales, localizedFile, pages, urlPath } from '../site.mjs'

const root = resolve(import.meta.dirname, '..')
const docs = resolve(root, 'docs')
const minWidth = 320
const maxWidth = 1440
// Common screens: small and large phones, tablets, laptops, and desktops.
const deviceWidths = [320, 360, 375, 390, 412, 430, 600, 768, 820, 1024, 1280, 1440]
const testFonts = `:root, :root:lang(ko) {
  --font-sans: Arial, "Liberation Sans", sans-serif !important;
  --font-mono: "Courier New", "Liberation Mono", monospace !important;
}`

const files = [...locales.flatMap(({ code }) => pages.map((page) => localizedFile(code, page))), '404.html']
const missing = files.filter((file) => !existsSync(resolve(docs, file)))
if (missing.length) {
  console.error(`Missing built pages: ${missing.join(', ')}. Run vite build first.`)
  process.exit(2)
}

// Runs in the page: whether the test fonts are installed. A missing font falls back to the last
// one in the list, which has different letter widths.
function testFontsInstalled() {
  const context = document.createElement('canvas').getContext('2d')
  const width = (font) => {
    context.font = `16px ${font}`
    return context.measureText('Experience Erfahrung Опыт 0123').width
  }
  const sans = width('Arial, "Liberation Sans", monospace') !== width('monospace')
  const mono = width('"Courier New", "Liberation Mono", serif') !== width('serif')
  return sans && mono
}

// Runs in the page: lists the widths just below, at, and above every width breakpoint.
function breakpointWidths() {
  const widths = []
  const visit = (rules) => {
    for (const rule of rules) {
      if (rule.media && /width/.test(rule.media.mediaText)) {
        for (const [, value, unit] of rule.media.mediaText.matchAll(/(\d+(?:\.\d+)?)(px|r?em)/g)) {
          const px = Math.floor(unit === 'px' ? Number(value) : Number(value) * 16)
          widths.push(px - 1, px, px + 1)
        }
      }
      if (rule.cssRules) visit(rule.cssRules)
    }
  }
  for (const sheet of document.styleSheets) visit(sheet.cssRules)
  return widths
}

// Runs in the page at one width: returns a description of each problem found.
function findProblems() {
  const screen = document.documentElement.clientWidth
  const problems = []
  const describe = (el) => {
    const name = el.tagName.toLowerCase() + (el.id ? `#${el.id}` : '') + [...el.classList].map((c) => `.${c}`).join('')
    const text = el.textContent.trim().replace(/\s+/g, ' ')
    return text ? `${name} "${text.length > 40 ? `${text.slice(0, 40)}…` : text}"` : name
  }
  const clips = (el) => getComputedStyle(el).overflowX !== 'visible'
  // The part of an element that is not cut off by a box around it. The page itself (html and
  // body) does not count, so overflow hidden there cannot hide content that runs off the screen.
  const visibleSpan = (el, rect) => {
    let { left, right } = rect
    for (let box = el.parentElement; box && box !== document.body; box = box.parentElement) {
      if (!clips(box)) continue
      const clip = box.getBoundingClientRect()
      left = Math.max(left, clip.left)
      right = Math.min(right, clip.right)
    }
    return { left, right }
  }

  const pageWidth = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)
  if (pageWidth > screen) problems.push(`the page scrolls sideways: it is ${pageWidth}px wide`)

  // Only the outermost element that runs off the screen is reported, not everything inside it.
  const reported = new Set()
  for (const el of document.body.querySelectorAll('*')) {
    if (el.parentElement && reported.has(el.parentElement)) {
      reported.add(el)
      continue
    }
    const rect = el.getBoundingClientRect()
    if (!rect.width || getComputedStyle(el).visibility === 'hidden') continue
    const { left, right } = visibleSpan(el, rect)
    if (right <= left) continue
    if (right > screen + 0.5 || left < -0.5) {
      reported.add(el)
      const side = right > screen + 0.5 ? `${Math.ceil(right - screen)}px past the right edge` : `${Math.ceil(-left)}px past the left edge`
      problems.push(`${describe(el)} reaches ${side}`)
    }
  }

  // Text is checked against its nearest box (a block, flex, or grid item, a button, or a tag).
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT)
  const range = document.createRange()
  const seen = new Set()
  while (walker.nextNode()) {
    const node = walker.currentNode
    if (!node.data.trim() || node.parentElement.closest('svg, script, style, template')) continue
    let box = node.parentElement
    while (box.parentElement && ['inline', 'contents'].includes(getComputedStyle(box).display)) box = box.parentElement
    if (seen.has(box) || clips(box)) continue
    const boxRect = box.getBoundingClientRect()
    range.selectNodeContents(node)
    for (const line of range.getClientRects()) {
      const outside = Math.max(line.right - boxRect.right, boxRect.left - line.left)
      if (line.width && outside > 1) {
        seen.add(box)
        problems.push(`text in ${describe(box)} sticks out of its box by ${Math.ceil(outside)}px`)
        break
      }
    }
  }

  // One row: every visible header item overlaps every other one vertically.
  const items = [...document.querySelectorAll('.site-header .brand, .site-header .site-nav li, .site-header .lang-toggle')]
    .map((el) => el.getBoundingClientRect())
    .filter((rect) => rect.width)
  if (items.length && Math.max(...items.map((r) => r.top)) >= Math.min(...items.map((r) => r.bottom))) {
    problems.push('the header does not fit on one row: the menu wraps to a second line')
  }
  return problems
}

// Runs in the page with motion on: scrolls down half a screen at a time, then returns a
// description of each problem found.
async function scrollThrough() {
  const frames = (count) =>
    new Promise((done) => {
      const next = () => (count-- ? requestAnimationFrame(next) : done())
      next()
    })
  if (!document.documentElement.classList.contains('motion')) return ['the motion script did not start']
  const problems = []
  const screen = document.documentElement.clientWidth
  const bottom = () => document.documentElement.scrollHeight - innerHeight
  for (let y = 0; ; y = Math.min(y + innerHeight / 2, bottom())) {
    scrollTo({ top: y, behavior: 'instant' })
    // Time for the script to see what came into view, and for its animations to start.
    await frames(3)
    const pageWidth = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)
    if (pageWidth > screen && !problems.length) {
      problems.push(`the page scrolls sideways while things move in, ${Math.round(scrollY)}px down: it is ${pageWidth}px wide`)
    }
    if (y >= bottom()) break
  }
  // A paused animation is still waiting for its item to come into view, so what it shows stays hidden.
  const waiting = document.getAnimations().filter((animation) => animation.playState === 'paused')
  for (const animation of waiting.slice(0, 5)) {
    const { target, pseudoElement } = animation.effect
    const name = target.tagName.toLowerCase() + [...target.classList].map((c) => `.${c}`).join('') + (pseudoElement ?? '')
    problems.push(`${name} never plays its "${animation.animationName}" animation: it never counted as scrolled into view`)
  }
  if (waiting.length > 5) problems.push(`and ${waiting.length - 5} more animations never play`)
  return problems
}

// Chrome is installed on GitHub's build servers, and Edge on every Windows PC.
async function launchBrowser() {
  for (const channel of ['chrome', 'msedge']) {
    try {
      return await chromium.launch({ channel })
    } catch {
      // Not installed; try the next one.
    }
  }
  console.error('The layout check needs Google Chrome or Microsoft Edge.')
  process.exit(2)
}

const browser = await launchBrowser()
const device = { isMobile: true, hasTouch: true, deviceScaleFactor: 2, locale: 'en-US' }
// The layout is measured with reduced motion, so nothing is still moving into place.
const context = await browser.newContext({ ...device, reducedMotion: 'reduce' })
const moving = await browser.newContext({ ...device, reducedMotion: 'no-preference' })
const motionWidths = [375, 1280]
const probe = await context.newPage()
if (!(await probe.evaluate(testFontsInstalled))) {
  console.error(
    'The layout check needs Arial and Courier New, or on Linux Liberation Sans and Liberation Mono (fonts-liberation).',
  )
  await browser.close()
  process.exit(2)
}
await probe.close()
const server = await preview({ root, logLevel: 'silent', preview: { port: 4180, open: false } })
const origin = new URL(server.resolvedUrls.local[0]).origin
for (const browserContext of [context, moving]) {
  // Stay offline: no Google Analytics hits or other outside requests from the check.
  await browserContext.route((url) => url.origin !== origin, (route) => route.abort())
  await browserContext.addInitScript((css) => {
    document.addEventListener('DOMContentLoaded', () => {
      const style = document.createElement('style')
      style.textContent = css
      document.head.append(style)
    })
  }, testFonts)
}

let failures = 0
let layouts = 0
async function checkPage(file) {
  const page = await context.newPage()
  await page.setViewportSize({ width: minWidth, height: 800 })
  await page.goto(`${origin}${urlPath(file)}`)
  // Load lazy images now, so every image has its real size, and open the language menu.
  await page.evaluate(async () => {
    const images = [...document.images]
    for (const image of images) image.loading = 'eager'
    await Promise.all(images.map((image) => image.decode().catch(() => {})))
    await document.fonts.ready
    for (const menu of document.querySelectorAll('.lang-menu')) menu.open = true
  })
  const widths = [...new Set([...deviceWidths, ...(await page.evaluate(breakpointWidths))])]
    .filter((width) => width >= minWidth && width <= maxWidth)
    .sort((a, b) => a - b)
  const found = []
  for (const width of widths) {
    await page.setViewportSize({ width, height: 800 })
    const problems = await page.evaluate(findProblems)
    layouts++
    if (problems.length) found.push(`  ${width}px: ${problems.join('\n         ')}`)
  }
  await page.close()
  failures += found.length
  console.log(`${found.length ? 'FAIL' : 'ok  '}  ${urlPath(file)} at ${widths.length} widths, ${widths[0]}–${widths.at(-1)}px`)
  for (const line of found) console.log(line)
}

async function checkMotion(file) {
  const found = []
  for (const width of motionWidths) {
    const page = await moving.newPage()
    await page.setViewportSize({ width, height: 800 })
    await page.goto(`${origin}${urlPath(file)}`)
    const problems = await page.evaluate(scrollThrough)
    await page.close()
    if (problems.length) found.push(`  ${width}px: ${problems.join('\n         ')}`)
  }
  failures += found.length
  console.log(`${found.length ? 'FAIL' : 'ok  '}  ${urlPath(file)} with motion at ${motionWidths.join(' and ')}px`)
  for (const line of found) console.log(line)
}

try {
  // A few pages at a time keeps the check fast without overloading the PC.
  const queue = [...files]
  await Promise.all(Array.from({ length: 4 }, async () => {
    while (queue.length) {
      const file = queue.shift()
      await checkPage(file)
      await checkMotion(file)
    }
  }))
} finally {
  await browser.close()
  await server.close()
}

console.log(
  failures
    ? `\n${failures} page width(s) have layout or motion problems. Fix the CSS or the text; do not skip the check.`
    : `\nAll ${files.length} pages fit on screens from ${minWidth}px up (${layouts} layouts checked), and their animations play without pushing the page sideways.`,
)
process.exit(failures ? 1 : 0)
