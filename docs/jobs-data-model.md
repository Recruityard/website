# Jobs data model — from the ATS to the website

How job openings get from the applicant tracking system (ATS, currently **Zoho Recruit**) onto
recruityard.com, which ATS field fills which part of the site, and what to change when moving to a
different ATS.

Code: [`tools/build_jobs.py`](../tools/build_jobs.py) · Workflow: [`.github/workflows/jobs.yml`](../.github/workflows/jobs.yml)

---

## 1. The pipeline in one picture

```text
 ATS (Zoho Recruit)                    tools/build_jobs.py                                 website
┌──────────────────────┐   ┌──────────────────────────────────────────────┐   ┌─────────────────────────────┐
│ Private API (OAuth)  │──►│ private_records()  ┐                         │   │ jobs.html  (cards + search) │
│  or                  │   │                    ├─► load_jobs() ──► Job ──┼──►│ jobs/<slug>.html (1 per job)│
│ Public careers feed  │──►│ public_records()   ┘   (normalise)    model  │   │ JSON-LD JobPosting (Google) │
└──────────────────────┘   └──────────────────────────────────────────────┘   │ sitemap.xml entries         │
                                                                              └─────────────────────────────┘
```

1. A **source function** fetches raw records from the ATS (`private_records()` or `public_records()`).
2. **`load_jobs()`** converts each raw record into the site's own **Job model** (section 2). This is
   the *only* place where ATS field names appear.
3. Everything after that (cards, job pages, Google structured data, sitemap) reads **only the Job
   model**, never ATS fields.

➡ **Changing ATS = writing a new source function and mapping its fields to the Job model.**
The page templates, styles, search and SEO code don't change.

---

## 2. The Job model (the contract)

Every job on the site is a dictionary with exactly these keys. Any ATS must be able to fill them.

| Key | Type | Required | Meaning |
|---|---|---|---|
| `id` | text | **yes** | Stable unique id of the job in the ATS. Used for de-duplication and as `identifier` for Google. |
| `slug` | text | **yes** (derived) | URL name of the job page: `jobs/<slug>.html`. Built from `title` (see 2.1). |
| `title` | text | **yes** | Job title shown everywhere. |
| `apply` | URL | **yes** | Where "Apply now" sends the candidate (the ATS application form). |
| `description` | HTML | **yes** | Full job description. Cleaned to simple tags (see 2.2). |
| `location` | text | no | Human-readable place, e.g. "Lisboa, Lisboa, Portugal". |
| `city` | text | no | City (structured, for Google). |
| `state` | text | no | Region / district (for Google). |
| `country` | text | no | Country; defaults to "Portugal". |
| `remote` | yes/no | no | Fully remote job. |
| `type` | text | no | Employment type, e.g. "Full time". |
| `experience` | text | no | Experience level, e.g. "1-3 years". |
| `industry` | text | no | Sector, e.g. "Customer Service". |
| `salary` | text | no | Salary as free text, e.g. "1200-2000". Hidden when empty. |
| `opened` | date | no | Date the job was published. Used for sorting (newest first) and "Posted …". |

### 2.1 Derived values
- **`slug`**: `title` → accents removed (Covilhã → Covilha) → lower-case → non-letters become `-` →
  max 80 characters. If two jobs have the same title, the last 6 digits of `id` are appended.
  ⚠ Changing a job's title changes its URL (the old page is deleted on the next run).
- **`location`**: `city, state, country` joined, duplicates removed. If empty and remote → "Portugal".

### 2.2 Description cleaning (`clean_description`)
The ATS HTML is reduced to: paragraphs, headings (`h2`–`h4`), lists, bold, italic, line breaks and
links (http/https/mailto only). Everything else (styles, scripts, `<span>`s) is dropped. Plain-text
ads written as lines with "- " bullets and "**Label:**" lines are turned into real lists and headings.

---

## 3. Field mapping — Zoho Recruit → Job model

| Job model | Zoho private API field (`Job_Openings`) | Zoho public feed field | Transformation |
|---|---|---|---|
| `id` | `id` | `id` | as text |
| `title` | `Posting_Title` (fallback `Job_Opening_Name`) | `Posting_Title` (fallback `Job_Opening_Name`) | trimmed |
| `apply` | — *(not in API)* → looked up by `id` in the public feed's `$url`; if missing, built as `https://recruityard.zohorecruit.eu/jobs/Careers/<id>/<slug>?source=CareerSite` | `$url` | — |
| `description` | `Job_Description` (HTML) | `Job_Description` is plain text → the HTML version is read from each job's public page | `clean_description()` |
| `city` | `City` | `City` | — |
| `state` | `State` | `State` | — |
| `country` | `Country` | `Country` | default "Portugal" |
| `location` | `City` + `State` + `Country` | same | joined, see 2.1 |
| `remote` | `Remote_Job` | `Remote_Job` | true if "Yes"/"true" |
| `type` | `Job_Type` | `Job_Type` | — |
| `experience` | `Work_Experience` | `Work_Experience` | shown as typed in Zoho (e.g. "0-1 ano") |
| `industry` | `Industry` | `Industry` | — |
| `salary` | `Salary` | — → read from each job's public page | trimmed |
| `opened` | `Date_Opened` (`YYYY-MM-DD`) | `Date_Opened` (`MM/DD/YYYY`) | `parse_date()` accepts both |

### Which jobs are published

| Rule | Private API | Public feed |
|---|---|---|
| Must be published on the careers site | `Publish` = true | the feed only contains published jobs |
| Must still be open | `Job_Opening_Status` not in Filled, Cancelled, Declined, Inactive, On-hold, Closed | handled by Zoho |

Zoho fields **not** used today (available if wanted): job owner/recruiter, number of positions,
target date, required skills, client name, custom fields. Ask for a field → add it to the Job model
(section 2) and to the templates (section 4).

---

## 4. Where each field appears on the website

| Job model | Job card (`jobs.html`) | Job page (`jobs/<slug>.html`) | Google JobPosting (JSON-LD) | Other |
|---|---|---|---|---|
| `id` | — | — | `identifier.value` | duplicate-slug suffix |
| `slug` | card link `jobs/<slug>.html` | file name / URL | `url` | `sitemap.xml`, canonical, `og:url` |
| `title` | card heading | hero heading, `<title>`, `og:title` | `title` | search filter |
| `apply` | — | **Apply now** buttons (top and bottom) | — | — |
| `description` | first 180 characters (plain text) | full body | `description` | page meta description (first 155 characters) |
| `location` / `remote` | 📍 line ("Remote · Portugal") | 📍 line | `jobLocationType: TELECOMMUTE` + `applicantLocationRequirements` when remote | search filter, **Remote only** checkbox |
| `city` / `state` / `country` | — | — | `jobLocation.address` (locality, region, country) | — |
| `type` | 🕒 line | 🕒 line | `employmentType` ("Full time" → `FULL_TIME`, "Part time" → `PART_TIME`, "Contract" → `CONTRACTOR`, "Temporary" → `TEMPORARY`, "Internship" → `INTERN`, else `OTHER`) | search filter |
| `experience` | ☆ line | ☆ line | — | — |
| `industry` | — | 🏷 line | — | search filter |
| `salary` | — | 💲 line (hidden if empty) | — *(could be added as `baseSalary`)* | — |
| `opened` | sort order | "Posted 18 Sep 2026" | `datePosted` | sort order |

Rendering code: `render_listing()` (cards), `render_job()` + `meta_items()` (job page),
`job_jsonld()` (Google), `main()` (files, sitemap).

---

## 5. Other places the ATS is used on the site (not via `build_jobs.py`)

| Where | What | ATS-specific? |
|---|---|---|
| `index.html`, `about-us.html`, `find-jobs.html` | "Featured jobs" widget: Zoho embed script (`static.zohocdn.com/.../embed_jobs.js`, page `Hot-Openings`) inside `<iframe srcdoc>` | **yes** — replace with the new ATS widget, or with cards generated like `jobs.html` |
| Footer (most pages) | "RSS Feed" → `recruityard.zohorecruit.eu/jobs/Careers/rss`; "XML Feed" → `recruit.zoho.eu/recruit/downloadjobfeed?clientid=…` | **yes** — point to the new ATS feeds or remove |
| `jobs/*.html` | "Apply now" → Zoho application form | via `apply` |
| `privacy-policy.html` | Legal text naming Zoho as processor | **yes** — legal update needed |
| `docs/services/zoho-recruit.md`, `docs/cookies.md` | Service + cookie registers | **yes** |
| `tools/zoho_token.py` | One-time OAuth helper | **yes** — delete after migration |
| GitHub secrets `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN` | API credentials | **yes** — delete after migration |

---

## 6. Moving to another ATS — checklist

### Before you choose
The new ATS must offer, through an API or public feed:
- [ ] All **required** Job model fields (section 2): id, title, description (ideally HTML), apply URL.
- [ ] A way to tell **published/open** jobs from closed ones.
- [ ] Server-to-server authentication (API key or OAuth client credentials / refresh token) — the
      site has no server, so credentials only live in GitHub Actions secrets.
- [ ] An application form/page per job (for `apply`), hosted by the ATS, with GDPR consent.
- [ ] EU data hosting and a data-processing agreement (GDPR).
- Nice to have: salary, remote flag, structured location, employment type, publish date, a
  "featured" flag (to replace the "Featured jobs" widget), webhooks (to rebuild on change instead of daily).

### Code changes (all in `tools/build_jobs.py`)
1. Write `newats_records()` that returns a list of raw records (copy `private_records()` as a model:
   authenticate → fetch all pages → keep only published/open jobs).
2. In `load_jobs()`, call it instead of the Zoho functions and map its field names to the Job model
   keys — i.e. make a new version of the table in section 3. Nothing outside `load_jobs()` and the
   source function needs to change.
3. If the new ATS sends dates in another format, add it to `parse_date()`.
4. If its employment-type values differ ("Full-Time", "FT", …), extend the `employmentType` mapping
   in `job_jsonld()`.
5. Add the new credentials as GitHub secrets and pass them in `.github/workflows/jobs.yml`
   (`env:` of the "Generate job pages" step).
6. Run `python tools/build_jobs.py` locally and compare: number of jobs, a few job pages, the
   Google [Rich Results Test](https://search.google.com/test/rich-results) on one job page.

### Everything else
- [ ] Replace or remove the "Featured jobs" widget and footer RSS/XML links (section 5).
- [ ] Redirect old apply links? Old Zoho URLs in Google/LinkedIn shares will stop working once Zoho is closed.
- [ ] **Job URLs** (`jobs/<slug>.html`) stay the same if titles stay the same — good for SEO.
- [ ] Update `docs/services/` (new ATS file, mark Zoho removed), `docs/cookies.md`, Privacy Policy.
- [ ] Remove `tools/zoho_token.py`, the Zoho secrets, and revoke the Zoho API client.
- [ ] Export/archive candidate data from Zoho per your retention policy before closing the account.

---

## 7. Verifying the mapping (any ATS)

Run locally, without writing pages:

```bash
python -c "import sys; sys.path.insert(0,'tools'); import build_jobs as b; import pprint; pprint.pprint(b.load_jobs()[0])"
```

This prints the first job **as the website sees it** (the Job model). Check each key against the ATS.
