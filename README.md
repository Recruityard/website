# Recruityard website

Static marketing site for [Recruityard](https://www.recruityard.com), served with GitHub Pages.
No build step: every page is a plain HTML file.

## Structure

```text
index.html                Home
about-us.html             About
hire-talent.html          Employers
find-jobs.html            Candidates (embeds Zoho Recruit job listings)
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

## Deploy

Push to `main`. GitHub Pages publishes the repository root.
