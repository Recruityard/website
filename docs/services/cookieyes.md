---
service: CookieYes
vendor: CookieYes Limited
category: legacy consent tool
status: removed (not in published GTM container as of 2026-10-05)
owner: unknown — check who created the CookieYes account
added: unknown (inside GTM container GTM-K2NX7V7T)
last_reviewed: 2026-10-05
---

# CookieYes (legacy — remove)

**What it was for:** a hosted cookie-consent banner, loaded as a tag inside the Google Tag Manager
container (`https://cdn-cookieyes.com/client_data/9dc6e28b8adb617fef93628f/script.js`).

## Why it should be removed

The site now has its own consent banner (`assets/consent.js`, see
[decision 0004](../decisions/0004-own-consent-banner.md)). Because CookieYes sits *inside* GTM it only
loads after a visitor has already accepted Statistics — too late to ask for consent, and on the live
domain it may show a **second** banner.

## Action

1. In https://tagmanager.google.com → container `GTM-K2NX7V7T` → Tags: pause or delete the CookieYes tag, then **Submit / Publish**.
2. Cancel the CookieYes subscription if one exists.
3. Change `status` above to `removed`.

If you'd rather use CookieYes instead of our own banner, that's possible too: it must then be loaded
directly in each page's `<head>` (not via GTM), and `assets/consent.js` removed.

## Links

- https://www.cookieyes.com/documentation/
