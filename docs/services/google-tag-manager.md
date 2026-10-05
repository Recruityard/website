---
service: Google Tag Manager
vendor: Google Ireland Ltd. / Google LLC
category: statistics
status: removed (2026-10-05)
owner: Recruityard marketing (Google account that owns container GTM-K2NX7V7T)
added: before 2026 (Framer site)
last_reviewed: 2026-10-05
---

# Google Tag Manager (GTM) — removed

> **Not used anymore (2026-10-05).** The container was empty; Google Analytics is loaded directly
> (see [google-analytics.md](google-analytics.md)). Delete container `GTM-K2NX7V7T` and both Tag Manager
> accounts (6274180528, 6250290378) in https://tagmanager.google.com. Kept for history; if Tag Manager is
> needed again, load it from `assets/consent.js` after consent and never also load GA directly.

**What it does for us:** a container that loads marketing/analytics tags configured in the GTM web
interface, without changing the site code.

## Where it is used

- All pages, **only after Statistics consent**.
- Code: `assets/consent.js` → `loadAnalytics()` (container id `GTM-K2NX7V7T`).
- Dashboard: https://tagmanager.google.com (container `GTM-K2NX7V7T`).

## What the container currently loads (observed 2026-10-05)

**Nothing** — the published container is empty (no tags). Google Analytics is loaded directly by `assets/consent.js` (see [google-analytics.md](google-analytics.md)). Earlier it contained:

| Tag | Seen as | Note |
|---|---|---|
| CookieYes consent banner | `cdn-cookieyes.com/client_data/9dc6e28b8adb617fef93628f/script.js` | Removed — no longer in the published container ([cookieyes.md](cookieyes.md)). |
| Google advertising features | requests to `stats.g.doubleclick.net`, `www.google.pt` | Come from the Google tag / GA4 "Google signals" setting, not from GTM. Advertising use needs Marketing consent; Consent Mode tells Google whether it was given. |

Tags live in the GTM web interface, not in this repo: after changing them, update this table.

## Data it receives

GTM itself only serves the container; the tags it fires receive page URL, IP address, device data
and any events configured.

## Cookies and browser storage

GTM sets none; the tags it loads do (see [google-analytics.md](google-analytics.md), [../cookies.md](../cookies.md)).

## Consent

Statistics. `assets/consent.js` loads GTM only after consent and sends Google Consent Mode v2
signals (`analytics_storage`, `ad_storage`, `ad_user_data`, `ad_personalization`). For tags added
in GTM later, configure **Consent settings** on each tag (Built-in consent checks) to match their
category.

## Links

- Documentation: https://developers.google.com/tag-platform/tag-manager
- Consent Mode: https://developers.google.com/tag-platform/security/guides/consent
- Privacy: https://policies.google.com/privacy · Data processing terms: https://business.safety.google/processorterms/
