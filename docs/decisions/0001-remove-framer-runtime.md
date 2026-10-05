# 0001. Remove the Framer runtime and self-host all assets

- Status: accepted
- Date: 2026-10-04

## Context

The site was exported from Framer. Its pages loaded Framer's JavaScript runtime, fonts and images from
`framerusercontent.com`, plus Framer analytics. That made the site depend on a Framer project/account,
broke when served from a sub-path, and sent visitor data to Framer.

## Decision

- Remove all Framer scripts. Rebuild the interactive parts (menu, FAQ, slideshow, tabs, form,
  icons) in `assets/site.js` / `assets/site.css`.
- Download every image and font into `assets/media/` and reference them relatively.
- Keep Framer's generated CSS and markup (layout) as is.

## Consequences

- No runtime dependency on Framer; works on any static host.
- Editing is done in HTML, not in Framer's editor. Many sections exist three times (desktop / tablet /
  phone layouts).
- Content that only existed in Framer's JavaScript (FAQ answers, "For Candidates" tab, mobile menu)
  was captured once and is now stored in the pages.
