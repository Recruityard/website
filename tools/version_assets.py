"""Stamp assets/site.css and assets/site.js references with a content hash (?v=…).

    python tools/version_assets.py

Browsers (especially on phones) cache these files; the hash changes whenever a file changes,
so visitors always get the current version. Run it after editing site.css or site.js.
"""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

versions = {
    name: hashlib.sha1((ROOT / "assets" / name).read_bytes()).hexdigest()[:8]
    for name in ("site.css", "site.js", "consent.js")
}
pattern = re.compile(r'(assets/(site\.(?:css|js)|consent\.js))(?:\?v=[0-9a-f]+)?(?=")')

changed = 0
for page in sorted(ROOT.rglob("*.html")):
    if ".git" in page.parts or "node_modules" in page.parts:
        continue
    text = page.read_text(encoding="utf-8")
    new = pattern.sub(lambda m: f"{m.group(1)}?v={versions[m.group(2)]}", text)
    if new != text:
        page.write_text(new, encoding="utf-8", newline="")
        changed += 1
print("  ".join(f"{n}?v={v}" for n, v in versions.items()), f"({changed} pages updated)")
