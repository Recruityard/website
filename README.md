# Recruityard website

Static marketing site for [Recruityard](https://www.recruityard.com), served with GitHub Pages.
No build step: every page is a plain HTML file.

## Structure

```text
index.html                Home
about-us.html             About
hire-talent.html          Employers
find-jobs.html            Candidates (embeds Zoho Recruit job listings)
jobs.html                 Open positions: job cards + search (all "Find Jobs" links)   [generated]
jobs/*.html               One page per open position, Apply → Zoho Recruit             [generated]
tools/build_jobs.py       Builds the two above from the public Zoho Recruit careers site
.github/workflows/jobs.yml  Runs build_jobs.py daily and commits changes
blog-articles.html        Blog index
articles/*.html           Blog posts
contact-us.html           Contact form (Web3Forms)
privacy-policy.html, cookie-policy.html, terms-and-conditions.html
404.html                  Shown by GitHub Pages for unknown URLs

assets/
  site.css                Interactive styles: menu, FAQ, slideshow, form
  site.js                 Interactive behaviour: menu, FAQ, slideshow, form, button links
  media/                  Images and fonts (self-hosted)

robots.txt                Crawler rules
.nojekyll                 Tells GitHub Pages to serve files as-is
```

The pages were originally exported from Framer. Layout and typography live in the inline
`<style>` blocks inside each page (Framer's generated CSS); the `framer-*` class names come from
there. Framer's JavaScript runtime is **not** used. Everything interactive is in `assets/site.js`.

## Run locally

```bash
npx serve .
```

Then open <http://localhost:3000>. You can also open the HTML files directly from disk; all
internal links point at real `.html` files.

## Editing tips

- **Text**: search the page for the text and edit it in place. Many sections exist three
  times (desktop, tablet, phone layouts, wrapped in `ssr-variant hidden-*` divs), so update
  every copy.
- **Links**: internal links are relative (`./about-us.html`, or `../about-us.html` from `articles/`).
- **Images**: add files to `assets/media/` and reference them relatively. Keep photos at or below
  2560px on the long side and compress them (JPEG quality ~80).
- **Contact form**: submissions go to [Web3Forms](https://web3forms.com). The public access key
  is the `access_key` input in `contact-us.html`. hCaptcha is required by the Web3Forms settings.
- **FAQ answers / mobile menu**: FAQ answers are inline in `index.html`; the open mobile-menu
  layout is the `<template id="ry-menu">` at the end of each page.

## Job pages

Jobs are managed in Zoho Recruit; the site mirrors them.

- **Automatic**: the *Refresh job pages* GitHub Action runs every day at 06:15 UTC. It adds
  pages for new openings, updates changed ones and deletes pages of closed ones. Run it any
  time from **Actions → Refresh job pages → Run workflow**.
- **Manual**: `python tools/build_jobs.py` (Python 3.9+, no dependencies), then commit.
- Only the area between `<!-- JOBS:START -->` and `<!-- JOBS:END -->` in `jobs.html` is
  generated; edit the rest of `jobs.html` normally (it is also the template for every job page).
- If Zoho returns no jobs (outage), the script stops without deleting anything.

## Deploy

Push to `main`. GitHub Pages publishes the repository root.

Canonical URLs, Open Graph tags, structured data and `sitemap.xml` already point at the final
domain, `https://recruityard.com`, while the site is being tested on
`https://recruityard.github.io/website/`.

## Go-live checklist (switching to recruityard.com)

1. **DNS** at the domain registrar: four `A` records for `recruityard.com` →
   `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`, and a `CNAME`
   for `www` → `recruityard.github.io`.
2. **GitHub → Settings → Pages → Custom domain**: enter `recruityard.com` (this commits a
   `CNAME` file), wait for the DNS check, then tick **Enforce HTTPS**.
3. **404 page**: GitHub serves `404.html` at any missing path, so switch its relative
   `./…` links and asset paths to root-absolute `/…`.
4. **Web3Forms**: if you restrict the access key to a domain, set it to `recruityard.com`.
5. **Search Console**: add the domain and submit `https://recruityard.com/sitemap.xml`.
6. Bump the `<lastmod>` dates in `sitemap.xml` whenever pages change.
