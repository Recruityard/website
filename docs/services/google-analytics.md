---
service: Google Analytics 4
vendor: Google Ireland Ltd. / Google LLC
category: statistics
status: active
owner: Recruityard (property "Recruityard website")
added: 2026-10-05
last_reviewed: 2026-10-05
---

# Google Analytics 4 (GA4)

**What it does for us:** visit statistics (pages viewed, traffic sources, devices).

## Where it is used

- Property **Recruityard website**, measurement ID **`G-XM9KZGKH6B`** — the only Google tag on the site.
- All pages, **only after Statistics consent**: `assets/consent.js` → `loadAnalytics()` loads the
  standard `gtag.js` snippet for this ID. Don't paste Google's snippet into the HTML — it would load
  before consent.
- Dashboard: https://analytics.google.com → property *Recruityard website* → Reports → Realtime.

## Data it receives

Page URLs, referrer, device/browser data, approximate location derived from the IP address
(GA4 does not store full IP addresses), interaction events, and a pseudonymous client id.
Data is processed by Google, including in the US (EU–US Data Privacy Framework).

## Cookies and browser storage

| Name | Duration | Purpose |
|---|---|---|
| `_ga` | 2 years | Distinguishes visitors (client id) |
| `_ga_XM9KZGKH6B` | 2 years | Session state for this property |

## Consent

Statistics. Not loaded until consent; Consent Mode v2 signals sent; when a visitor withdraws
consent, `assets/consent.js` deletes the `_ga*` cookies and reloads the page.

## Recommended settings (in the GA4 admin)

- Data retention: 14 months.
- Google signals: off unless advertising features are needed (they'd need Marketing consent).
- Add any other Google products (Ads, Search Console) as *links* in this property, not as extra tags.

## History

- Until 2026-10-05: Google tag `G-DGBC10M59S` sending to property `G-2KLLFFKVXB`, plus an empty Tag
  Manager container `GTM-K2NX7V7T` (which earlier also loaded CookieYes). Replaced by this single
  property; the old ones are being deleted.

## Links

- Documentation: https://support.google.com/analytics
- Cookie usage: https://support.google.com/analytics/answer/11397207
- Privacy: https://policies.google.com/privacy
