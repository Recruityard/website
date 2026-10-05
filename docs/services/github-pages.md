---
service: GitHub Pages
vendor: GitHub, Inc. (Microsoft)
category: infrastructure (necessary)
status: active
owner: GitHub organisation "Recruityard"
added: 2026-10-03
last_reviewed: 2026-10-05
---

# GitHub Pages

**What it does for us:** hosts the static website straight from the `main` branch of this repository.

## Where it is used

- Whole site. Settings: repository → **Settings → Pages** (Deploy from a branch: `main`, `/`).
- `.nojekyll` makes GitHub serve files as they are.
- Custom domain `recruityard.com` (planned): see the go-live checklist in the root `README.md`.

## Data it receives

Every request: IP address, user agent, requested URL. GitHub may log these for security and
operations; we have no access to visitor logs.

## Cookies and browser storage

None.

## Consent

Necessary (hosting).

## Links

- Documentation: https://docs.github.com/pages
- Privacy statement: https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement
- GitHub Pages and personal data: https://docs.github.com/pages/getting-started-with-github-pages/about-github-pages#data-collection

## Notes

GitHub Pages can't set HTTP security headers (CSP, HSTS beyond GitHub's defaults); if those become a
requirement, put a CDN (e.g. Cloudflare) in front or move to a host that supports headers.
