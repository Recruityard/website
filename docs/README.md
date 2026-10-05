# Website documentation

Documentation for the third-party services, cookies and key decisions behind recruityard.com.
It follows a "docs as code" approach: plain Markdown kept next to the code, reviewed and versioned
with it.

| Folder / file | What it is | Based on |
|---|---|---|
| [`services/`](services/) | One file per external service: what it does, what data it receives, where it is configured, links to its docs and legal terms | Vendor register (GDPR Art. 30 *records of processing* + Art. 28 *processors*) |
| [`cookies.md`](cookies.md) | Every cookie / browser-storage item the site can create, by consent category | ePrivacy Directive; cookie categories used by most consent tools (necessary, preferences, statistics, marketing) |
| [`decisions/`](decisions/) | Short records of *why* things are the way they are | [Architecture Decision Records](https://adr.github.io/) |

## Current services

| Service | Purpose | Consent category | Sets cookies |
|---|---|---|---|
| [GitHub Pages](services/github-pages.md) | Hosting | Necessary | No |
| [GitHub Actions](services/github-actions.md) | Daily job-page refresh | n/a (no visitor data) | No |
| [Zoho Recruit](services/zoho-recruit.md) | Job openings, applications, "Featured jobs" widget | Necessary | Only on Zoho's own pages |
| [Web3Forms](services/web3forms.md) | Contact form delivery | Necessary | No |
| [hCaptcha](services/hcaptcha.md) | Contact form spam protection | Necessary | Possibly (security) |
| [Google Analytics 4](services/google-analytics.md) | Visit statistics (`G-XM9KZGKH6B`) | Statistics | Yes |
| [Google Tag Manager](services/google-tag-manager.md) | Removed — was an empty container | — | — |
| [CookieYes](services/cookieyes.md) | Legacy consent tool — removed | — | — |
| [YouTube](services/youtube.md) | Videos in blog articles | Marketing & media | Yes, after Play |
| [Glassdoor](services/glassdoor.md) | Footer badge + link (badge image self-hosted) | None needed | No |

Not used anymore: Framer (site builder and runtime), Framer CDN, Google Fonts CDN, LinkedIn
follow widget, the Zoho job-board widget on `jobs.html`. See [decisions](decisions/).

## How consent works on the site

`assets/consent.js` shows the banner and stores the choice in `localStorage` (`ry-consent`).
Nothing in **Statistics** or **Marketing & media** loads before the visitor allows it; Google
Consent Mode v2 signals are sent too. Visitors can change their choice from **Cookie settings**
in the footer or the button on the Cookie Policy page. Details: [cookies.md](cookies.md).

## Checklist: adding or changing a third-party service

1. **Document it**: copy [`services/_template.md`](services/_template.md) to
   `services/<service>.md` and fill it in (purpose, data sent, cookies, legal terms, owner).
2. **Find its cookies**: open the site in a private window, accept all, then check
   DevTools → *Application* → *Cookies* / *Local storage*, and the *Network* tab for its domains.
   Add each item to [cookies.md](cookies.md).
3. **Pick the consent category** and gate it in code:
   - Statistics/marketing scripts must only load from `assets/consent.js` (`apply()`), or listen
     for the `ry:consent` event / check `window.ryConsent.get()`.
   - Never paste a tracking snippet straight into the HTML `<head>`.
   - Use one Google tag only (`G-XM9KZGKH6B`); link other Google products inside Analytics instead of adding tags.
4. **New category or vendor that changes what visitors agreed to?** Bump `VERSION` in
   `assets/consent.js` so everyone is asked again, then run `python tools/version_assets.py`.
5. **Update the legal texts** (Cookie Policy, Privacy Policy) to list the service.
6. **Check the data-processing terms** (DPA) and where data is stored (EU / international transfers).
7. If it was a real choice between options, add a [decision record](decisions/).
8. Update the table above and the `last_reviewed` date in the service file.

Review this folder at least **once a year** and whenever a vendor changes its terms.
