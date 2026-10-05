---
service: Zoho Recruit
vendor: Zoho Corporation (EU data centre: zohorecruit.eu)
category: necessary
status: active
owner: Recruityard recruitment team
added: before 2026 (Framer site)
last_reviewed: 2026-10-05
---

# Zoho Recruit

**What it does for us:** our applicant tracking system. Job openings are managed there; the website
mirrors them and candidates apply on Zoho's careers pages.

## Where it is used

| Feature | Where | How |
|---|---|---|
| Job pages + listing | `jobs.html`, `jobs/*.html` | Generated daily by `tools/build_jobs.py` from the public feed `https://recruityard.zohorecruit.eu/recruit/v2/public/Job_Openings?pagename=Careers&source=CareerSite` and each job's public page (formatted description, salary). No visitor data involved. |
| "Apply now" buttons | `jobs/*.html` | Link to the job's page on `recruityard.zohorecruit.eu` (application form) |
| "Featured jobs" widget | `index.html`, `find-jobs.html` | Zoho embed script (`static.zohocdn.com/recruit/embed_careers_site/…/embed_jobs.js`) inside an isolated `<iframe srcdoc>`, page `Hot-Openings` |
| RSS / XML job feeds | footer links | Links only |

Dashboard: https://recruit.zoho.eu (careers site settings, "Publish" / "Hot openings" flags).

## Data it receives

- Visitors viewing "Featured jobs": the widget loads from Zoho's CDN and API, so Zoho receives IP
  address and browser details.
- Applicants: everything they submit on Zoho's application form (CV, contact details) — governed by
  Zoho Recruit's careers-site privacy settings, not by this website.
- Data location: Zoho EU data centre (`.eu` domains).

## Cookies and browser storage

The embed widget did not set cookies on our domain in testing (2026-10-05). Zoho's own careers pages
(after clicking Apply) set their own cookies under Zoho's consent banner. **Verify** after any widget
change and list findings in [../cookies.md](../cookies.md).

## Consent

Necessary / functional: the job listings are core content of a recruitment site.

## Links

- Careers site embed docs: https://help.zoho.com/portal/en/kb/recruit/career-site
- Privacy policy: https://www.zoho.com/privacy.html
- DPA / GDPR: https://www.zoho.com/gdpr.html

## Notes

- Job fields such as *Work Experience* are shown as typed in Zoho (some are in Portuguese, e.g.
  "0-1 ano", "Mais recente").
- If the public feed format changes, `tools/build_jobs.py` stops without deleting pages.
