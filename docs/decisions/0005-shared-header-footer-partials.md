# 0005. Keep the header, mobile menu and footer in shared partials

- Status: accepted
- Date: 2026-11-01

## Context

Every page carried its own copy of the header, the mobile menu and the footer (Framer export),
so a change had to be repeated in every page and the copies had drifted apart. Options considered:

- Load the footer with JavaScript (`fetch('footer.html')`): simple, but the footer appears late,
  crawlers may miss its links, and it fails when a page is opened from disk.
- Copy shared fragments into the pages with a small script: the served HTML stays fully static.

## Decision

- The inner markup of each component lives once in `partials/` (header desktop / mobile, mobile
  menu, footer desktop / tablet / phone), taken from `index.html`.
- Each page marks where it goes with `<!-- partial:NAME -->` / `<!-- /partial:NAME -->`. The
  element around the markers stays the page's own, because its classes and size come from that
  page's Framer CSS.
- `tools/build_partials.py` copies the partials in, adds `../` for sub-folders and keeps the
  "current page" link highlight only on the page it points to. Run it after editing a partial.

## Consequences

- One place to edit the header, menu and footer; job pages pick them up from `jobs.html`.
- Edits made between the markers in a page are overwritten on the next run.
- To undo: delete the markers and `partials/`; the pages keep the last copied markup.
