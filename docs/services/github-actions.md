---
service: GitHub Actions
vendor: GitHub, Inc. (Microsoft)
category: infrastructure (no visitor data)
status: active
owner: GitHub organisation "Recruityard"
added: 2026-10-05
last_reviewed: 2026-10-05
---

# GitHub Actions

**What it does for us:** runs `tools/build_jobs.py` every day to refresh the job pages from Zoho
Recruit, commits changes and asks GitHub Pages to rebuild.

## Where it is used

- Workflow: `.github/workflows/jobs.yml` (schedule `15 6 * * *` UTC + manual "Run workflow").
- Permissions: `contents: write`, `pages: write` (built-in `GITHUB_TOKEN`; no secrets stored).
- Runs: repository → **Actions → Refresh job pages**.

## Data it receives

Only job opening data from the Zoho Recruit private API. No visitor data. On failure it emails
the error output to `MAIL_TO` through the SMTP account in the `MAIL_*` secrets.

## Cookies and browser storage

None.

## Links

- Documentation: https://docs.github.com/actions
- Scheduled workflows: https://docs.github.com/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#schedule

## Notes

GitHub disables scheduled workflows in repositories with no activity for 60 days; re-enable from
the Actions tab if that happens.
