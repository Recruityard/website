# 0003. Generate job pages from Zoho Recruit daily

- Status: accepted
- Date: 2026-10-05

## Context

Jobs are managed in Zoho Recruit. The Zoho embed widget looked off-brand, overlapped on narrow
screens, and kept job content off our domain (bad for SEO and Google for Jobs).

## Decision

`tools/build_jobs.py` reads Zoho's public careers feed and each job's public page, and writes
`jobs.html` (cards + search) and `jobs/<slug>.html` (one page per job with JobPosting structured
data). A GitHub Action runs it daily. "Apply" links go to Zoho's application form.

## Consequences

- Job content lives on recruityard.com; applications still land in Zoho.
- Changes in Zoho appear on the site within a day (or immediately via "Run workflow").
- Depends on Zoho's public feed format; the script fails safe (no deletions) if it changes.
