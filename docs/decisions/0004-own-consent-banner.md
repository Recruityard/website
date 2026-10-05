# 0004. Own cookie-consent banner with Google Consent Mode v2

- Status: accepted
- Date: 2026-10-05

## Context

Google Tag Manager and Google Analytics were loaded on every page and set cookies before any consent,
which the ePrivacy Directive / GDPR (CNPD in Portugal) does not allow. YouTube players also loaded in
the background. A CookieYes banner existed only inside GTM, so it loaded after the tracking it was
meant to control. More third-party cookies may be added in the future.

Options: our own lightweight banner, a hosted consent platform (Cookiebot, CookieYes, iubenda), or
documentation only.

## Decision

Our own banner in `assets/consent.js`:
- Categories: Necessary (always), Statistics (GTM + GA4), Marketing & media (YouTube, ads features).
- Accept all / Reject all / per-category settings; equal prominence for accept and reject.
- Nothing optional loads before consent; Google Consent Mode v2 `default: denied`, `update` on choice.
- Choice stored 12 months in `localStorage`; re-asked when `VERSION` changes.
- Withdrawal deletes GA cookies; "Cookie settings" link in the footer and on the Cookie Policy page.
- YouTube: `youtube-nocookie.com`, loaded on Play, with a notice if Marketing isn't allowed.
- Google Fonts, YouTube thumbnails and the Glassdoor badge are self-hosted.

## Consequences

- No extra vendor or cost; full control of the look.
- Analytics only counts visitors who accept (typically fewer than before).
- No automatic cookie scanning or consent-log storage: keep [`../cookies.md`](../cookies.md) up to
  date by hand. If proof-of-consent records become a requirement, switch to a hosted platform
  (load it directly in `<head>`, not through GTM) and supersede this decision.
- Follow-up: ~~remove CookieYes from GTM~~ (done); ~~pick one GA4 property~~ (G-2KLLFFKVXB, done); update the Cookie Policy text.
