# Azizjon Kasimov — Portfolio Website

**Live:** [azizjonkasimov.github.io](https://azizjonkasimov.github.io)

A fast, static portfolio for job applications: a homepage that answers "who, what, proof, and how to
reach me" in a few seconds, plus case-study pages for the main projects. There is no backend and no
client-side framework. The pages are plain HTML and CSS, built with Vite and deployed to GitHub Pages
by GitHub Actions. The site is in English, Korean, German, Russian, Uzbek, and Chinese
(Simplified).

## Structure

| Path | Purpose |
| --- | --- |
| `index.html` | Homepage: photo, headline metrics with small charts, selected work, experience, skills, credentials, contact |
| `work/<slug>/index.html` | Case-study pages (`semantic-search`, `aws-data-pipeline`, `solar-mlops`, `catalog-agent`) |
| `ko/`, `de/`, `ru/`, `uz/`, `zh/` | The same pages in Korean, German, Russian, Uzbek, and Chinese; each new language gets its own folder |
| `404.html` | Not-found page (English only); GitHub Pages serves it for unknown URLs |
| `partials/` | Shared `<head>` tags, header (with the language menu), and footer, plus the diagram icons (`icons/`) and the work-card drawings (`art/`), inlined into pages at build time |
| `site.mjs` | The page list, the languages, and the translated header and footer text |
| `src/styles.css` | All styles, including the dark theme and print styles |
| `src/motion.css` | The animations of the photo, charts, drawings, and diagrams (imported by `styles.css`) |
| `public/` | Files copied as-is: favicon, social preview image, touch icon, the homepage photo (`images/`), certificate scans (`certificates/`), case-study screenshots (`screenshots/`), `robots.txt` |
| `tools/` | The translation, language-redirect, and layout checks, the web image script, and the sources and render script for the social preview image and touch icon |
| `vite.config.mjs` | The build: one entry per page and language, the partial-include plugin, and the generated `sitemap.xml` |

## Development

Requires Node.js 20.19+ or 22.12+, and Microsoft Edge or Google Chrome for the layout check.

```powershell
npm install
npm run dev       # dev server at http://localhost:5173
npm run check     # compare every translation with its English page
npm run build     # that check, a production build into docs/, then the language redirect and layout checks
npm run preview   # serve docs/ at http://localhost:4173
```

Pages include shared markup with `<!-- include: partials/<file>.html -->`. The partials use
`{{name}}` placeholders, such as `{{ui.work}}` for a menu label or `{{year}}` for the current year,
that the build fills in for each page's language. An unknown placeholder stops the build.

## Pictures, diagrams, and charts

Everything that carries text is HTML and CSS, so it is translated like the rest of the page and
follows the light and dark themes. Pictures without text are shared SVG partials, so every language
shows the same drawing.

- **Photo:** `public/images/azizjon-kasimov.jpg` (600 px) and `-thumb.jpg` (300 px), made from the
  saffron-background headshot with `tools/web-images.ps1 -Kind photo`. It sits beside the intro on
  wide screens and above the name on phones, and is hidden in print.
- **Work-card drawings:** `partials/art/<slug>.svg`, one per case study, included at the top of each
  card with `<!-- include: partials/art/<slug>.svg -->`. They are decorative (`aria-hidden`) and
  colored by the `.art-*` classes in `src/styles.css`.
- **Architecture diagrams:** each case study's `<ol class="steps">` gets an icon per step from
  `partials/icons/<name>.svg`. The steps run down the page below 1080px and across the full width
  from 1080px; a step marked `step-optional` is drawn dashed. On wide screens a step is only about
  135px wide, and a word that does not fit makes the layout check fail: give it a break point with
  `&shy;`. German and Korean pages let the browser break any long word, so the check cannot catch
  theirs; look at new German and Korean steps at 1080px, and put `&#8203;` before a bracket that
  follows Korean text.
- **Charts:** bars are `<span class="bar" style="--v: 70">`, where `--v` is the bar's length as a
  percentage of its track. Use only numbers that the page text already states. The translation check
  compares these `style` values, so a chart cannot show different numbers in another language.
- **Screenshots:** `public/screenshots/`, shown in a `.shots` gallery of thumbnails that open the
  full image. Each `<img>` lists the thumbnail, medium, and full image in `srcset`, and its `sizes`
  follows the gallery's columns, so phones get the 960 px image instead of a blurry thumbnail. A
  screenshot alone in its gallery takes the full width and is shown whole. The solar case study
  shows seven screenshots of the Recs Innovation systems, with the plant's name, its location, and
  its sales figures covered.

### Motion

The photo, the hero charts, the work-card drawings, the diagrams, the worked example, the
case-study charts, and the screenshots animate once, when they first scroll into view. The
animations are in `src/motion.css`, and a small script at the end of `partials/head.html` marks each
item as it comes into view.

- An animation only brings a thing into the place it has without motion, so the page looks the same
  once it has played. Nothing moves without JavaScript, for visitors who ask for reduced motion in
  their system settings, or in print.
- Items that come into view together play in turn. A work-card drawing builds up in the order its
  data flows: each shape has a class that says what it does (`draw`, `pop`, `rise`, `grow`, `fade`,
  `wipe`, `turn`, `ring`) and `style="--at: 300ms"` for when. A line that draws itself needs
  `pathLength="1"`.
- While a work card is hovered or focused, its drawing plays a loop: a dash travels along its lines
  (`art-pulse` paths with `pathLength="100"`, started in turn by `--pulse-at`), and parts marked
  `hover-*` move. The loop stops when the pointer leaves.
- Anything new that animates must sit inside one of the items the script watches (listed at the top
  of `src/motion.css`). Otherwise its animation waits forever, what it shows stays hidden, and the
  layout check fails.

### Layout check

`tools/check-layout.mjs` (read-only, run by `npm run build`) opens every built page in every language
in headless Edge or Chrome, with the language menu open, at about 40 screen widths from 320px (the
narrowest phone screen that web accessibility rules require) to 1440px, including both sides of
every width breakpoint in `src/styles.css`. It fails when:

- the page scrolls sideways, or anything reaches past the left or right edge of the screen;
- text sticks out of its box, such as a long word poking out of a card or a button;
- the header does not fit on one row.

It measures these with reduced motion, so every chart and drawing is in its final place. Then it
scrolls through every page with motion on, at 375px and 1280px, and fails when the page scrolls
sideways while things move in, or when an animation still waits at the end, because its item never
counted as scrolled into view.

It measures text in Arial and Courier New, or on Linux their twins Liberation Sans and Liberation
Mono. The twins have identical letter widths, so a PC and GitHub's build server get the same result.
To run it again without rebuilding: `node tools/check-layout.mjs`.

When it fails, fix the CSS or the text; do not weaken the check. If a layout bug ever gets past it,
extend the check so it catches that bug too. The header menu drops links as the screen narrows (five
links on wide screens, three at 860px and narrower, two below 360px), and if the menu still does not
fit, it wraps instead of pushing the page sideways.

## Languages

English pages live at the site root, and each translation has the same paths under its language
folder: `/work/solar-mlops/` in Korean is `/ko/work/solar-mlops/`.

- **Language menu:** a globe button with the current language code (EN, KO, DE, RU, UZ, ZH) sits at the right of the
  header on every page. It opens a list of the site's languages, each linking to the same page in that
  language. It works without JavaScript.
- **Automatic choice:** when a visitor opens an English page from outside the site (a search result,
  LinkedIn, a bookmark), a small script in `partials/head.html` sends them to the same page in their
  language. It uses the language they last picked in the menu, or else the first language in their
  browser settings that the site has. Translated URLs never redirect, so a shared `/ko/` link opens
  in Korean for everyone. Picking a language in the menu is remembered in the browser.
  `tools/check-language-redirect.mjs` (read-only, run by `npm run build`) loads the built pages in
  simulated browsers and checks these rules for every language.
- **Search engines:** every page lists all its language versions with `hreflang` links, with English as
  the default. `sitemap.xml` is generated at build time from the page and language lists.
- **Translation note:** translated pages say in the footer that they are translated from English and
  link to the English page.

### Editing content

Change the English page first, then make the same change in every translation, and run
`npm run check`. The check (`tools/check-translations.mjs`, read-only) fails if a translation's markup,
links, image files, technology tags, code, icons, or numbers differ from English, or if its head tags
are wrong. Links to pages go to the translation's own folder (`/ko/work/...`); links to files, such as
the certificate images, stay exactly as in English.
Numbers are compared by value, so each language can use its own format (`2M+` is `200만+` in Korean,
`2 Mio.+` in German, `2 млн+` in Russian, `2 mln+` in Uzbek, and `200 万+` in Chinese; `4.39` is
`4,39` in German, Russian, and Uzbek). Uzbek text writes oʻ and gʻ with ʻ (U+02BB) and the tutuq
belgisi with ʼ (U+02BC), as in maʼlumot; the check rejects typed apostrophes, which look the same.
Chinese text uses full-width punctuation (，。：（）) next to Chinese characters, and the check rejects
ASCII punctuation there.
`npm run build` runs the check first, so a failing check also stops the deploy.

The check cannot tell whether a sentence still says the same thing, so reread each translated
sentence you change.

### Adding a language

1. Add an entry to `locales` in `site.mjs` (code, HTML lang, Open Graph locale, menu name, short code,
   and the header and footer text).
2. Add its number format, and any words it must never use, to `tools/check-translations.mjs`.
3. Translate every page into `<code>/` and run `npm run check`.
4. If the language needs its own fonts, line breaking, or hyphenation, add `:lang(<code>)` rules to
   `src/styles.css`, as Korean, German, and Chinese have. Run `npm run build`: the layout check tests the new
   pages at every screen width. Also look at the pages on a phone and on desktop, in light and dark
   themes.

## Content rules

- Keep every claim factual and consistent with the resume and LinkedIn profile. Do not invent
  employers, dates, titles, metrics, or outcomes.
- Case studies are simplified and sanitized: no employer code, private data, internal URLs, or
  proprietary implementation details, and third-party data sources are not named.
- No phone number, visa details, or date of birth on public pages, including in certificate scans.
- Translations say the same thing as English: nothing added, dropped, or made stronger. Names,
  company names, and technology names stay as written in English.

## Adding a case study

1. Copy an existing `work/<slug>/index.html` into a new folder and replace the content.
2. Add the page to `pages` in `site.mjs`.
3. Add a card to the Selected work section in `index.html`, and update the previous/next links at the
   bottom of the neighboring case studies.
4. Make the same changes in every language folder, then run `npm run check`.

## Social preview image and touch icon

`public/og-image.png` (1200×630, used by LinkedIn and other link previews) and
`public/apple-touch-icon.png` are rendered from `tools/social-card.html` and `tools/touch-icon.html`
with headless Edge or Chrome:

```powershell
.\tools\render-images.ps1
```

Re-run it after changing the headline or the metrics on the card. All languages share this English
image.

## Certificate scans, screenshots, and the photo

The homepage shows each certificate scan as a small thumbnail next to the entry it proves: the two
diplomas next to the degree, and each award certificate next to its award. Each thumbnail links to
the full scan. The images are in `public/certificates/`, and every language uses the same files.
The original PDFs are kept in the private portfolio repo, and so are the original screenshots and
their covered copies. To add a certificate:

1. Check the scan for private details first, because the site is public, and cover them before
   making the images. The Korean diploma, for example, is shown from a copy with the date of birth
   covered (`education/certificates/woosong-diploma-ko-birthdate-covered.jpg` in the portfolio
   repo).
2. Make the images. The script writes `<name>.jpg` (1240 px wide, to read) and `<name>-thumb.jpg`
   (400 px wide) and drops the scan's metadata:

   ```powershell
   .\tools\web-images.ps1 -Kind certificate -Source <scan.pdf|.jpg|.png> -Name <file-name>
   ```

3. Add the thumbnail to its entry in `index.html` and in every translation, then run
   `npm run check`. An entry with scans is an `<li class="has-scans">`: its text goes in the first
   `<div>`, and the thumbnail links go in `<div class="scans">` (see `.has-scans` in
   `src/styles.css`). Two scans sit side by side and stack on phones. Give each image an `alt` that
   names the document, in the page's language.

The same script makes screenshots (`-Kind screenshot`: `public/screenshots/`, the full image up to
1600 px wide so small text stays readable, a 960 px `-medium` image for phones, and a 480 px
thumbnail) and the photo (`-Kind photo`: `public/images/`, a centered square at 600 and 300 px).
Cover private details in a screenshot, such as a customer's name, before you run it.

## Deployment

Every push to `main` runs `.github/workflows/deploy.yml`: it builds with Node 22 (the build runs the
translation, language-redirect, and layout checks, with the Chrome that GitHub's build server has
installed) and deploys `docs/` to GitHub Pages. A failing check stops the deploy, and the live site
keeps the last good version. The repository's Pages source must be set to **GitHub Actions**. No
secrets or environment variables are needed.

To check a deploy, open the **Actions** tab for the latest "Build & Deploy to GitHub Pages" run, then
load the live site, one case-study page, and one translated page such as `/ko/`.

## Analytics

Google Analytics 4 is loaded from `partials/head.html` (visits, referrers, outbound clicks). Page views
include the language folder in the URL, so visits per language show up in the reports. An English
page that redirects a visitor to a translation does not count a page view, and the translated page
reports the referrer the visitor came from (for example LinkedIn) instead of the English page. The
Google Search Console verification tag is in the English homepage `<head>`.

## License

[MIT](LICENSE)
