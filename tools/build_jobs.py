"""Generate the job pages from Zoho Recruit.

    python tools/build_jobs.py

Data source:
  * Zoho Recruit private API (OAuth) when ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET and ZOHO_REFRESH_TOKEN
    are set (GitHub Actions secrets). Get the refresh token once with tools/zoho_token.py.
  * Otherwise the public careers feed (no credentials).

Writes:
  jobs.html          job cards between the JOBS markers (the rest of the page is left alone)
  jobs/<slug>.html   one page per open position (closed positions are removed)
  sitemap.xml        job URLs refreshed

Uses only the Python standard library. Run daily by .github/workflows/jobs.yml.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZOHO = "https://recruityard.zohorecruit.eu"
FEED = f"{ZOHO}/recruit/v2/public/Job_Openings?pagename=Careers&source=CareerSite"
BASE = "https://recruityard.com"
LISTING = ROOT / "jobs.html"
JOBS_DIR = ROOT / "jobs"
START, END = "<!-- JOBS:START -->", "<!-- JOBS:END -->"
UA = {"User-Agent": "Mozilla/5.0 (compatible; RecruityardSiteBuilder/1.0)"}


# ---------------------------------------------------------------- fetching

def get(url: str) -> str:
    url = urllib.parse.quote(url, safe=":/?&=%#+,;@!$'()*~")  # Zoho URLs can contain accents (Francês)
    req = urllib.request.Request(url, headers={**UA, "Accept": "application/json, text/html"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def js_unescape(s: str) -> str:
    """Decode a JavaScript string literal body (without quotes). Never evaluates anything."""
    simple = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c != "\\":
            out.append(c)
            i += 1
            continue
        n = s[i + 1]
        if n == "x":
            out.append(chr(int(s[i + 2:i + 4], 16)))
            i += 4
        elif n == "u":
            out.append(chr(int(s[i + 2:i + 6], 16)))
            i += 6
        else:
            out.append(simple.get(n, n))
            i += 2
    return "".join(out)


def job_details(url: str) -> dict:
    """Rich description + salary, embedded in the Zoho job page as jobs = JSON.parse('…')."""
    page = get(url)
    marker = "jobs = JSON.parse('"
    a = page.index(marker) + len(marker)
    b = a
    while not (page[b] == "'" and page[b - 1] != "\\"):
        b += 1
    data = json.loads(js_unescape(page[a:b]))
    return data[0] if isinstance(data, list) else data


# ---------------------------------------------------------------- sanitising

ALLOWED = {"p", "h2", "h3", "h4", "ul", "ol", "li", "strong", "b", "em", "i", "br", "a"}
RENAME = {"h1": "h2", "b": "strong", "i": "em"}


class Sanitizer(HTMLParser):
    """Keep simple formatting tags only; drop attributes (except safe link hrefs) and wrappers."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.skip = 0  # inside <head>/<script>/<style>

    def handle_starttag(self, tag, attrs):
        if tag in ("head", "script", "style"):
            self.skip += 1
            return
        tag = RENAME.get(tag, tag)
        if self.skip or tag not in ALLOWED:
            return
        if tag == "a":
            href = dict(attrs).get("href", "")
            if not re.match(r"^(https?:|mailto:)", href or ""):
                return
            self.out.append(f'<a href="{html.escape(href)}" rel="noopener" target="_blank">')
        else:
            self.out.append(f"<{tag}>")

    def handle_endtag(self, tag):
        if tag in ("head", "script", "style"):
            self.skip = max(0, self.skip - 1)
            return
        tag = RENAME.get(tag, tag)
        if not self.skip and tag in ALLOWED and tag != "br":
            self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(html.escape(data, quote=False))


def clean_description(raw: str) -> str:
    p = Sanitizer()
    p.feed(raw or "")
    s = "".join(p.out)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"(<br>\s*)+(</(?:p|li|h2|h3|h4)>)", r"\2", s)          # Zoho's trailing <br>s
    s = re.sub(r"<(p|li|h2|h3|h4|strong|em)>\s*</\1>", "", s)           # empty blocks
    s = re.sub(r"<a [^>]*>\s*</a>", "", s)
    s = re.sub(r"\s*(</?(?:p|ul|ol|li|h2|h3|h4)>)\s*", r"\1", s)
    # Loose <br>-separated text between block elements gets real structure.
    parts = re.split(r"(<(p|ul|ol|h2|h3|h4)>.*?</\2>)", s)
    out = []
    for i in range(0, len(parts), 3):
        loose = parts[i].strip()
        if loose:
            out.append(structure_lines(loose))
        if i + 1 < len(parts):
            out.append(parts[i + 1])
    s = "".join(out)
    # A paragraph that is only a bold label ("<strong>What you'll do?</strong>") is a heading.
    s = re.sub(r"<p><strong>\s*([^<]{2,80}?[:?])\s*</strong></p>", lambda m: f"<h3>{m.group(1).rstrip(':')}</h3>", s)
    return s.strip()


def structure_lines(s: str) -> str:
    """Some ads are plain lines joined by <br> ("<strong>Label:</strong><br>- item<br>- item").
    Turn bold labels into headings, dash lines into lists and the rest into paragraphs."""
    out = []
    for block in re.split(r"(?:<br>\s*){2,}", s):
        lines = [ln.strip() for ln in block.split("<br>") if ln.strip()]
        para, items = [], []
        def flush():
            if para:
                out.append("<p>" + "<br>".join(para) + "</p>")
                para.clear()
            if items:
                out.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
                items.clear()
        for ln in lines:
            label = re.fullmatch(r"<strong>\s*([^<]{2,80}?)\s*</strong>:?", ln)
            if label and re.search(r"[:?]\s*(</strong>)?:?$", ln):
                flush()
                out.append(f"<h3>{label.group(1).strip().rstrip(':')}</h3>")
            elif re.match(r"^[-•–]\s+", ln):
                if para:
                    flush()
                items.append(re.sub(r"^[-•–]\s+", "", ln))
            else:
                if items:
                    flush()
                para.append(ln)
        flush()
    return "".join(out)


def plain(text: str, limit: int) -> str:
    t = re.sub(r"<[^>]+>", " ", text)
    t = re.sub(r"\s+", " ", html.unescape(t)).strip()
    return t if len(t) <= limit else t[: limit - 1].rsplit(" ", 1)[0] + "…"


# ---------------------------------------------------------------- job model

def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()  # Covilhã -> Covilha
    s = re.sub(r"[^a-z0-9]+", "-", text.lower().replace("'", ""))
    return s.strip("-")[:80].strip("-")


# ---- source 1: Zoho Recruit private API (OAuth, used when the ZOHO_* environment variables are set)

ZOHO_ACCOUNTS = os.environ.get("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.eu")   # EU data centre
ZOHO_API = os.environ.get("ZOHO_API_URL", "https://recruit.zoho.eu/recruit/v2")
CLOSED_STATUSES = {"filled", "cancelled", "declined", "inactive", "on-hold", "on hold", "closed"}


def zoho_access_token() -> str:
    """Exchange the long-lived refresh token for a 1-hour access token."""
    body = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": os.environ["ZOHO_REFRESH_TOKEN"],
        "client_id": os.environ["ZOHO_CLIENT_ID"],
        "client_secret": os.environ["ZOHO_CLIENT_SECRET"],
    }).encode()
    req = urllib.request.Request(f"{ZOHO_ACCOUNTS}/oauth/v2/token", data=body, method="POST", headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if "access_token" not in data:
        raise RuntimeError(f"Zoho token refresh failed: {data.get('error', data)}")  # never print secrets
    return data["access_token"]


def private_records() -> list[dict]:
    token = zoho_access_token()
    records, page = [], 1
    while True:
        url = f"{ZOHO_API}/Job_Openings?page={page}&per_page=200"
        req = urllib.request.Request(url, headers={**UA, "Authorization": f"Zoho-oauthtoken {token}"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw) if raw.strip() else {}          # 204 No Content when there are no records
        records += data.get("data") or []
        if not (data.get("info") or {}).get("more_records"):
            break
        page += 1
    # Only what the careers site shows: published and still open.
    open_jobs = [r for r in records
                 if r.get("Publish") and str(r.get("Job_Opening_Status") or "").strip().lower() not in CLOSED_STATUSES]
    # Apply links: the public careers URL (looked up by id; built from the id if the feed is down).
    try:
        public_urls = {j["id"]: j["$url"] for j in json.loads(get(FEED)).get("data") or []}
    except Exception:
        public_urls = {}
    for r in open_jobs:
        title = r.get("Posting_Title") or r.get("Job_Opening_Name") or ""
        r["$url"] = public_urls.get(str(r["id"])) or \
            f"{ZOHO}/jobs/Careers/{r['id']}/{slugify(title)}?source=CareerSite"
    print(f"Zoho private API: {len(records)} job openings, {len(open_jobs)} published and open")
    return open_jobs


# ---- source 2: public careers feed (no credentials; description/salary scraped from each job page)

def public_records() -> list[dict]:
    records = []
    for j in json.loads(get(FEED)).get("data") or []:
        if not j.get("Publish", True):
            continue
        try:
            detail = job_details(j["$url"])
            j["Job_Description"] = detail.get("Job_Description") or ""
            j["Salary"] = detail.get("Salary") or ""
        except Exception as e:  # keep the feed's plain-text description
            print(f"  ! detail page failed for {j.get('Posting_Title')}: {e}", file=sys.stderr)
            j["Job_Description"] = f"<p>{html.escape(j.get('Job_Description') or '')}</p>"
        records.append(j)
    print(f"Zoho public feed: {len(records)} published jobs")
    return records


def parse_date(value) -> dt.date | None:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):  # API: 2026-09-18, public feed: 09/18/2026
        try:
            return dt.datetime.strptime(str(value), fmt).date()
        except ValueError:
            continue
    return None


def load_jobs() -> list[dict]:
    use_api = all(os.environ.get(k) for k in ("ZOHO_CLIENT_ID", "ZOHO_CLIENT_SECRET", "ZOHO_REFRESH_TOKEN"))
    records = private_records() if use_api else public_records()
    jobs, seen = [], set()
    for j in records:
        jid = str(j["id"])
        title = (j.get("Posting_Title") or j.get("Job_Opening_Name") or "").strip()
        slug = slugify(title) or jid
        if slug in seen:
            slug = f"{slug}-{jid[-6:]}"
        seen.add(slug)
        remote = str(j.get("Remote_Job") or "").lower() in ("yes", "true")
        place = ", ".join(dict.fromkeys(x for x in (j.get("City"), j.get("State"), j.get("Country")) if x))
        salary = j.get("Salary") or ""
        jobs.append({
            "id": jid, "slug": slug, "title": title, "apply": j["$url"],
            "description": clean_description(j.get("Job_Description") or ""),
            "salary": str(salary).strip(), "remote": remote,
            "location": place or ("Portugal" if remote else ""),
            "city": j.get("City") or "", "state": j.get("State") or "", "country": j.get("Country") or "Portugal",
            "type": j.get("Job_Type") or "", "experience": j.get("Work_Experience") or "",
            "industry": j.get("Industry") or "", "opened": parse_date(j.get("Date_Opened")),
        })
    jobs.sort(key=lambda x: (x["opened"] or dt.date.min, x["title"]), reverse=True)
    return jobs


# ---------------------------------------------------------------- rendering

ICON = {  # small inline icons (Phosphor-style strokes)
    "pin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11Z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "star": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9Z"/></svg>',
    "tag": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12V4h8l10 10-8 8Z"/><circle cx="7.5" cy="7.5" r="1.5"/></svg>',
    "cal": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
    "coin": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M15 9.5c-.5-1-1.6-1.5-3-1.5-1.7 0-3 .8-3 2s1.3 1.7 3 2 3 .8 3 2-1.3 2-3 2c-1.4 0-2.5-.5-3-1.5M12 6v12"/></svg>',
}
_P = '<p class="framer-text framer-styles-preset-ohmaut" data-styles-preset="FcXhOVzsL" dir="auto">'
INTRO = (  # listing page only (the job pages show the job instead)
    '<div class="framer-1k58ohx" data-framer-component-type="RichTextContainer" data-framer-name="Intro">'
    f"{_P}Find the right career opportunity for you. Browse our current openings below, search by title, "
    "language or location, and open a role to read the full description and apply.</p>"
    f'{_P}Don’t see the right fit? <a class="framer-text framer-styles-preset-1dvgqtt" href="./contact-us.html">'
    "Get in touch</a> and tell us what you’re looking for.</p></div>"
)
esc = lambda s: html.escape(str(s), quote=True)
fmt_date = lambda d: d.strftime("%d %b %Y") if d else ""


def meta_items(j: dict, full: bool) -> str:
    items = [("pin", ("Remote · " if j["remote"] else "") + j["location"] if j["location"] else ("Remote" if j["remote"] else ""))]
    items += [("clock", j["type"]), ("star", j["experience"])]
    if full:
        items += [("tag", j["industry"]), ("coin", j["salary"]), ("cal", f"Posted {fmt_date(j['opened'])}" if j["opened"] else "")]
    return "".join(f'<li>{ICON[i]}<span>{esc(t)}</span></li>' for i, t in items if t)


def render_listing(jobs: list[dict]) -> str:
    cards = []
    for j in jobs:
        search = " ".join([j["title"], j["location"], j["industry"], j["type"], "remote" if j["remote"] else ""]).lower()
        cards.append(
            f'<li class="ry-job-card" data-search="{esc(search)}" data-remote="{str(j["remote"]).lower()}">'
            f'<a href="./jobs/{j["slug"]}.html">'
            f'<h2 class="ry-job-card-title">{esc(j["title"])}</h2>'
            f'<ul class="ry-job-meta">{meta_items(j, full=False)}</ul>'
            f'<p class="ry-job-card-text">{esc(plain(j["description"], 180))}</p>'
            f'<span class="ry-job-card-more">View job <span aria-hidden="true">→</span></span>'
            "</a></li>"
        )
    count = f'{len(jobs)} open position{"s" if len(jobs) != 1 else ""}'
    return (
        INTRO +
        '<section class="ry-jobs" aria-label="Job openings">'
        '<form class="ry-jobs-filter" role="search" onsubmit="return false">'
        '<label class="ry-visually-hidden" for="ry-job-q">Search jobs</label>'
        '<input id="ry-job-q" type="search" placeholder="Search by job title, language or location" autocomplete="off"/>'
        '<label class="ry-jobs-remote"><input id="ry-job-remote" type="checkbox"/> Remote only</label>'
        "</form>"
        f'<p class="ry-jobs-count" aria-live="polite" data-total="{len(jobs)}">{count}</p>'
        f'<ul class="ry-job-list">{"".join(cards)}</ul>'
        '<p class="ry-jobs-empty" hidden>No positions match your search. '
        '<a href="./contact-us.html">Get in touch</a> and tell us what you’re looking for.</p>'
        "</section>"
    )


def job_jsonld(j: dict) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "JobPosting",
        "title": j["title"],
        "description": j["description"],
        "identifier": {"@type": "PropertyValue", "name": "Recruityard", "value": j["id"]},
        "hiringOrganization": {"@type": "Organization", "name": "Recruityard", "sameAs": BASE + "/",
                               "logo": f"{BASE}/assets/media/bPPqciueo2HHJROfIlp9nEAfJ8-d8c7a1-512.png"},
        "employmentType": {"full time": "FULL_TIME", "part time": "PART_TIME", "contract": "CONTRACTOR",
                           "temporary": "TEMPORARY", "internship": "INTERN"}.get(j["type"].lower(), "OTHER"),
        "url": f"{BASE}/jobs/{j['slug']}.html",
    }
    if j["opened"]:
        data["datePosted"] = j["opened"].isoformat()
    address = {"@type": "PostalAddress", "addressCountry": j["country"] or "Portugal"}
    if j["city"]:
        address["addressLocality"] = j["city"]
    if j["state"]:
        address["addressRegion"] = j["state"]
    if j["remote"]:
        data["jobLocationType"] = "TELECOMMUTE"
        data["applicantLocationRequirements"] = {"@type": "Country", "name": j["country"] or "Portugal"}
    if j["city"] or not j["remote"]:
        data["jobLocation"] = {"@type": "Place", "address": address}
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def render_job(j: dict) -> str:
    apply = (f'<a class="ry-btn" href="{esc(j["apply"])}" rel="noopener">Apply now</a>')
    return (
        '<article class="ry-job">'
        '<a class="ry-job-back" href="../find-jobs.html"><span aria-hidden="true">←</span> All open positions</a>'
        f'<ul class="ry-job-meta">{meta_items(j, full=True)}</ul>'
        f'<div class="ry-job-actions">{apply}</div>'
        f'<div class="ry-job-body">{j["description"]}</div>'
        f'<div class="ry-job-actions ry-job-actions-end">{apply}'
        '<a class="ry-btn ry-btn-ghost" href="../contact-us.html">Ask us a question</a></div>'
        "</article>"
    )


def to_subdir(page: str) -> str:
    """Rewrite ./relative links of a root page for a page one folder down."""
    return re.sub(r'(?<=["\'(,\s])\./', "../", page)


def set_head(page: str, title: str, desc: str, url: str, extra: str = "") -> str:
    page = re.sub(r"<title>[^<]*</title>", f"<title>{esc(title)}</title>", page, count=1)
    page = re.sub(r'<meta content="[^"]*" (name="description"|property="og:description"|name="twitter:description")/>',
                  lambda m: f'<meta content="{esc(desc)}" {m.group(1)}/>', page)
    page = re.sub(r'<meta content="[^"]*" (property="og:title"|name="twitter:title")/>',
                  lambda m: f'<meta content="{esc(title)}" {m.group(1)}/>', page)
    page = re.sub(r'<link href="[^"]*" rel="canonical"/>', f'<link href="{url}" rel="canonical"/>', page)
    page = re.sub(r'<meta content="[^"]*" property="og:url"/>', f'<meta content="{url}" property="og:url"/>', page)
    page = re.sub(r'<script type="application/ld\+json">.*?</script>', "", page, flags=re.S)
    return page.replace("</head>", extra + "</head>", 1)


def replace_block(page: str, block: str) -> str:
    a, b = page.index(START), page.index(END)
    return page[: a + len(START)] + block + page[b:]


def main() -> int:
    template = LISTING.read_text(encoding="utf-8")
    if START not in template or END not in template:
        print("jobs.html is missing the JOBS:START / JOBS:END markers", file=sys.stderr)
        return 1

    jobs = load_jobs()
    if not jobs:
        print("Zoho returned no jobs; leaving existing pages untouched.", file=sys.stderr)
        return 1
    print(f"{len(jobs)} jobs")

    LISTING.write_text(replace_block(template, render_listing(jobs)), encoding="utf-8", newline="")

    JOBS_DIR.mkdir(exist_ok=True)
    keep = set()
    for j in jobs:
        url = f"{BASE}/jobs/{j['slug']}.html"
        page = replace_block(template, render_job(j))
        page = page.replace(">Open Positions<", f">{esc(j['title'])}<")
        page = set_head(page, f"{j['title']} | Recruityard Jobs", plain(j["description"], 155), url,
                        f'<script type="application/ld+json">{job_jsonld(j)}</script>')
        out = JOBS_DIR / f"{j['slug']}.html"
        out.write_text(to_subdir(page), encoding="utf-8", newline="")
        keep.add(out.name)
        print("  ", out.relative_to(ROOT))
    for old in JOBS_DIR.glob("*.html"):
        if old.name not in keep:
            old.unlink()
            print("  removed", old.relative_to(ROOT))

    sitemap = ROOT / "sitemap.xml"
    sm = re.sub(r"  <url><loc>https://recruityard\.com/jobs/[^<]*</loc>.*?</url>\n", "", sitemap.read_text(encoding="utf-8"))
    today = dt.date.today().isoformat()
    entries = "".join(f"  <url><loc>{BASE}/jobs/{j['slug']}.html</loc><lastmod>{today}</lastmod></url>\n" for j in jobs)
    sm = sm.replace("</urlset>", entries + "</urlset>")
    sitemap.write_text(sm, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
