---
service: Google Maps (Maps Embed API)
vendor: Google Ireland Ltd. / Google LLC
category: marketing
status: active
owner: website
added: 2026-11-01
last_reviewed: 2026-11-01
---

# Google Maps

**What it does for us:** shows the office location (São Brás de Alportel) in the footer of every
page, with a "Get directions" button that opens Google Maps.

## Where it is used

- Footer of every page (desktop, tablet and phone layouts), from `partials/footer-*.html`: map,
  address and "Get directions" button, after the page links.
- Code: `<iframe data-ry-map-src="https://www.google.com/maps/embed/v1/place?key=…">` (no `src`
  until allowed). `assets/site.js` (Office map section) loads it.
- API key: Google Cloud Console → APIs & Services → Credentials. Restricted to the Maps Embed API
  and to the referrers `https://recruityard.com/*`, `https://www.recruityard.com/*` and
  `http://localhost:3000/*`. The Maps Embed API is free with no usage limit.

## Data it receives

Nothing until the map loads. After that: IP address, device data and map interactions, under
Google's privacy policy. The "Get directions" link only sends data when the visitor clicks it.

## Cookies and browser storage

The embed may set Google cookies (for example `NID`) once loaded. Names change over time —
**verify** and update [../cookies.md](../cookies.md).

## Consent

Marketing & media. With that consent the map loads straight away; without it, a notice explains
Google may set cookies and offers "Show map" (this visit only) or "Cookie settings".

## Changing the location

Edit the coordinates in the three `partials/footer-*.html` files (map `q=` and the directions
`destination=`) and the address text, then run `python tools/build_partials.py`.

## Links

- Maps Embed API: https://developers.google.com/maps/documentation/embed/get-started
- Google privacy policy: https://policies.google.com/privacy
