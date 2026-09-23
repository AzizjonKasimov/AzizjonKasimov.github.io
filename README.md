# Azizjon Kasimov — Portfolio Website

**Live:** [azizjonkasimov.github.io](https://azizjonkasimov.github.io)

A fast, static portfolio for job applications: a homepage that answers "who, what, proof, and how to
reach me" in a few seconds, plus case-study pages for the main projects. There is no backend and no
client-side framework. The pages are plain HTML and CSS, built with Vite and deployed to GitHub Pages
by GitHub Actions.

## Structure

| Path | Purpose |
| --- | --- |
| `index.html` | Homepage: headline metrics, selected work, experience, skills, credentials, contact |
| `work/<slug>/index.html` | Case-study pages (`semantic-search`, `aws-data-pipeline`, `solar-mlops`, `catalog-agent`) |
| `404.html` | Not-found page; GitHub Pages serves it for unknown URLs |
| `partials/` | Shared `<head>` tags, header, and footer, inlined into every page at build time |
| `src/styles.css` | All styles, including the dark theme and print styles |
| `public/` | Files copied as-is: favicon, social preview image, touch icon, `robots.txt`, `sitemap.xml` |
| `tools/` | HTML sources and the render script for the social preview image and touch icon |
| `vite.config.mjs` | The page list and the small partial-include plugin |

## Development

Requires Node.js 20.19+ or 22.12+.

```powershell
npm install
npm run dev       # dev server at http://localhost:5173
npm run build     # production build into docs/
npm run preview   # serve docs/ at http://localhost:4173
```

Pages include shared markup with `<!-- include: partials/<file>.html -->`, and `{{year}}` is replaced
with the current year at build time.

## Content rules

- Keep every claim factual and consistent with the resume and LinkedIn profile. Do not invent
  employers, dates, titles, metrics, or outcomes.
- Case studies are simplified and sanitized: no employer code, private data, internal URLs, or
  proprietary implementation details, and third-party data sources are not named.
- No phone number or visa details on public pages.

## Adding a case study

1. Copy an existing `work/<slug>/index.html` into a new folder and replace the content.
2. Add the page to `pages` in `vite.config.mjs` and a `<url>` entry to `public/sitemap.xml`.
3. Add a card to the Selected work section in `index.html`, and update the previous/next links at the
   bottom of the neighboring case studies.

## Social preview image and touch icon

`public/og-image.png` (1200×630, used by LinkedIn and other link previews) and
`public/apple-touch-icon.png` are rendered from `tools/social-card.html` and `tools/touch-icon.html`
with headless Edge or Chrome:

```powershell
.\tools\render-images.ps1
```

Re-run it after changing the headline or the metrics on the card.

## Deployment

Every push to `main` runs `.github/workflows/deploy.yml`: it builds with Node 22 and deploys `docs/`
to GitHub Pages. The repository's Pages source must be set to **GitHub Actions**. No secrets or
environment variables are needed.

To check a deploy, open the **Actions** tab for the latest "Build & Deploy to GitHub Pages" run, then
load the live site and one case-study page.

## Analytics

Google Analytics 4 is loaded from `partials/head.html` (visits, referrers, outbound clicks). The Google
Search Console verification tag is in the homepage `<head>`.

## License

[MIT](LICENSE)
