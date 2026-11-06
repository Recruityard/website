"""Copy the shared header, mobile menu and footer from partials/ into every page.

    python tools/build_partials.py

Edit the header, menu or footer only in partials/*.html, then run this. Each page marks where a
partial goes with <!-- partial:NAME --> ... <!-- /partial:NAME --> (NAME = file name without
.html); everything between the two markers is replaced. The element around the markers stays
the page's own, because its classes and size come from that page's Framer CSS.

Links in partials are written from the site root (./about-us.html, and ./ for the home page);
pages in a sub-folder get ../ instead. Page links carry data-framer-page-link-current="true" in the partial (Framer colours
the current page's link); each page keeps it only on links to itself. Leave it off links that
should never be highlighted, such as placeholders pointing at the home page.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTIALS = ROOT / "partials"
BLOCK = re.compile(r"(<!-- partial:([\w-]+) -->).*?(<!-- /partial:\2 -->)", re.S)
CURRENT = ' data-framer-page-link-current="true"'
NAV_LINK = re.compile(r'<a\s[^>]*' + CURRENT + r'[^>]*href="\./([^"]*)"[^>]*>')


def render(partial: str, page: Path) -> str:
    rel = page.relative_to(ROOT).as_posix()
    html = NAV_LINK.sub(lambda m: m.group(0) if (m.group(1) or "index.html") == rel else m.group(0).replace(CURRENT, ""), partial)
    depth = len(page.relative_to(ROOT).parts) - 1
    if depth:
        html = re.sub(r'(?<=["\'(,\s])\./', "../" * depth, html)
    return html


def main() -> int:
    partials = {p.stem: p.read_text(encoding="utf-8").strip("\n") for p in PARTIALS.glob("*.html")}
    changed = 0
    for page in sorted(ROOT.rglob("*.html")):
        if ".git" in page.parts or PARTIALS in page.parents:
            continue
        text = page.read_text(encoding="utf-8")
        missing = {m.group(2) for m in BLOCK.finditer(text)} - partials.keys()
        if missing:
            print(f"{page.relative_to(ROOT)}: no partials/{', '.join(sorted(missing))}.html", file=sys.stderr)
            return 1
        new = BLOCK.sub(lambda m: m.group(1) + render(partials[m.group(2)], page) + m.group(3), text)
        if new != text:
            page.write_text(new, encoding="utf-8", newline="")
            changed += 1
    print(f"{len(partials)} partials, {changed} pages updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
