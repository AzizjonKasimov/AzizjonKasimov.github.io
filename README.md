# Azizjon Kasimov — Portfolio Website

**Live:** [azizjonkasimov.github.io](https://azizjonkasimov.github.io)

A fast, static portfolio for job applications: a homepage that answers "who, what, proof, and how to
reach me" in a few seconds, plus case-study pages for the main projects. There is no backend and no
client-side framework. The pages are plain HTML and CSS, built with Vite and deployed to GitHub Pages
by GitHub Actions. The site is in English, Korean, and German. Russian, Uzbek, and Chinese will be
added one at a time.

## Structure

| Path | Purpose |
| --- | --- |
| `index.html` | Homepage: headline metrics, selected work, experience, skills, credentials, contact |
| `work/<slug>/index.html` | Case-study pages (`semantic-search`, `aws-data-pipeline`, `solar-mlops`, `catalog-agent`) |
| `ko/`, `de/` | The same pages in Korean and German; each new language gets its own folder |
| `404.html` | Not-found page (English only); GitHub Pages serves it for unknown URLs |
| `partials/` | Shared `<head>` tags, header (with the language menu), and footer, inlined into every page at build time |
| `site.mjs` | The page list, the languages, and the translated header and footer text |
| `src/styles.css` | All styles, including the dark theme and print styles |
| `public/` | Files copied as-is: favicon, social preview image, touch icon, certificate scans (`certificates/`), `robots.txt` |
| `tools/` | The translation and language-redirect checks, the certificate image script, and the sources and render script for the social preview image and touch icon |
| `vite.config.mjs` | The build: one entry per page and language, the partial-include plugin, and the generated `sitemap.xml` |

## Development

Requires Node.js 20.19+ or 22.12+.

```powershell
npm install
npm run dev       # dev server at http://localhost:5173
npm run check     # compare every translation with its English page
npm run build     # that check, a production build into docs/, then the language redirect check
npm run preview   # serve docs/ at http://localhost:4173
```

Pages include shared markup with `<!-- include: partials/<file>.html -->`. The partials use
`{{name}}` placeholders, such as `{{ui.work}}` for a menu label or `{{year}}` for the current year,
that the build fills in for each page's language. An unknown placeholder stops the build.

## Languages

English pages live at the site root, and each translation has the same paths under its language
folder: `/work/solar-mlops/` in Korean is `/ko/work/solar-mlops/`.

- **Language menu:** a globe button with the current language code (EN, KO, DE) sits at the right of the
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
Numbers are compared by value, so each language can use its own format (`2M+` is `200만+` in Korean
and `2 Mio.+` in German, and `4.39` is `4,39` in German).
`npm run build` runs the check first, so a failing check also stops the deploy.

The check cannot tell whether a sentence still says the same thing, so reread each translated
sentence you change.

### Adding a language

1. Add an entry to `locales` in `site.mjs` (code, HTML lang, Open Graph locale, menu name, short code,
   and the header and footer text).
2. Add its number format, and any words it must never use, to `tools/check-translations.mjs`.
3. Translate every page into `<code>/` and run `npm run check`.
4. If the language needs its own fonts, line breaking, or hyphenation, add `:lang(<code>)` rules to
   `src/styles.css`, as Korean and German have. Check the pages on a phone and on desktop, in light
   and dark themes.

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

## Certificate scans

The homepage shows the two diplomas and the award certificates as a gallery of thumbnails, each
linking to the full scan. The images are in `public/certificates/`, and every language uses the
same files. The original PDFs are kept in the private portfolio repo. To add a certificate:

1. Check the scan for private details first, because the site is public, and cover them before
   making the images. The Korean diploma, for example, is shown from a copy with the date of birth
   covered (`education/certificates/woosong-diploma-ko-birthdate-covered.jpg` in the portfolio
   repo).
2. Make the images. The script writes `<name>.jpg` (1240 px wide, to read) and `<name>-thumb.jpg`
   (400 px wide) and drops the scan's metadata:

   ```powershell
   .\tools\certificate-images.ps1 -Source <scan.pdf|.jpg|.png> -Name <file-name>
   ```

3. Add a card to the certificate gallery in `index.html` and in every translation, then run
   `npm run check`. The gallery has 6 columns on desktop, 3 on tablets, and 2 on phones (see
   `.cert-gallery` in `src/styles.css`), so the six scans fill even rows; change the column counts
   if the number of scans changes.

## Deployment

Every push to `main` runs `.github/workflows/deploy.yml`: it builds with Node 22 (the build runs the
translation and language-redirect checks) and deploys `docs/` to GitHub Pages. The repository's Pages source must be
set to **GitHub Actions**. No secrets or environment variables are needed.

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
