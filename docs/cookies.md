# Cookie & browser-storage register

Everything recruityard.com can store on a visitor's device, grouped by the consent categories in
the banner (`assets/consent.js`). Keep this in sync with the Cookie Policy page and the files in
[`services/`](services/).

Last verified: **2026-10-05** (local test of every consent path; see "How to verify" below).

## Necessary — always on

| Name | Provider | Type | Duration | Purpose |
|---|---|---|---|---|
| `ry-consent` | recruityard.com | localStorage | 12 months (then asked again) | Stores the visitor's consent choice: `{"v":1,"ts":<ms timestamp>,"statistics":bool,"marketing":bool}` |
| hCaptcha security cookies (if any) | hcaptcha.com | cookie | varies | Spam protection on the contact form only — [verify](services/hcaptcha.md) |

## Statistics — only after consent

| Name | Provider | Type | Duration | Purpose |
|---|---|---|---|---|
| `_ga` | Google Analytics | cookie (first-party) | 2 years | Distinguishes visitors |
| `_ga_XM9KZGKH6B` | Google Analytics | cookie (first-party) | 2 years | Session state, property G-XM9KZGKH6B |

Loaded by: Google Analytics `G-XM9KZGKH6B` (`gtag.js`) from `assets/consent.js`, after consent. Withdrawing consent deletes these cookies.

## Marketing & media — only after consent (or a click on a single video)

| Name | Provider | Type | Duration | Purpose |
|---|---|---|---|---|
| `VISITOR_INFO1_LIVE`, `YSC`, `yt-remote-*` (approx.) | YouTube (`youtube-nocookie.com`) | cookie / localStorage | session – 6 months | Video playback and preferences, set only after Play — [verify](services/youtube.md) |
| Google advertising cookies (if Google signals is on) | Google (`doubleclick.net`) | cookie (third-party) | up to 13 months | Ad personalisation — only with Marketing consent via Consent Mode |

## Not set anymore

| Was | Removed |
|---|---|
| Framer analytics (`events.framer.com`) | 2026-10 — Framer runtime removed |
| Google Analytics / GTM before consent | 2026-10-05 — now consent-gated |
| YouTube on page load (hidden player) | 2026-10-05 — now loads on Play only |
| CookieYes (`cky-*`) | 2026-10-05 — no longer in the GTM container |
| Old GA property `G-2KLLFFKVXB` (`_ga_2KLLFFKVXB`) and Tag Manager `GTM-K2NX7V7T` | 2026-10-05 — replaced by `G-XM9KZGKH6B` |

## How to verify

1. Open the site in a private window. Before clicking the banner, DevTools → **Application →
   Cookies** should show nothing, and **Network** should show no Google, YouTube or other third-party
   requests (Zoho appears only inside the "Featured jobs" frame).
2. Click **Reject all** → still nothing.
3. **Cookie settings → Accept all** → the Statistics cookies above appear.
4. Play a video in an article → YouTube items appear.
5. Anything not in this table? Add it here and to the matching file in `services/`.

## When adding third-party cookies in the future

- Decide the category first (Statistics or Marketing; "Preferences" can be added as a new category).
- Load the script only from `assets/consent.js` → `apply()` (or listen for `ry:consent`).
- If it changes what visitors agreed to, bump `VERSION` in `assets/consent.js` (everyone is asked again).
- Add rows here, a file in `services/`, and update the Cookie Policy text.
