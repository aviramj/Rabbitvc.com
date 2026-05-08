#!/usr/bin/env python3
"""
Fetch the best available logo for each portfolio company.

For each company homepage, parses the HTML and picks the highest-quality
icon in this priority order:
  1. <link rel="apple-touch-icon">  (usually 180x180 PNG)
  2. <meta property="og:image">     (often a 1200x630 banner, decent fallback)
  3. <link rel="icon"> / favicon.ico (largest size attribute wins)

Saves results into ./logos/<slug>.<ext> and zips them.

Usage:
    python3 tools/download-logos.py

Requires: Python 3.8+, no external deps. zip (or tar) on PATH.
"""

from __future__ import annotations
import html.parser
import mimetypes
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# (slug, homepage URL) — slugs match how we'll reference them in index.html
COMPANIES: list[tuple[str, str]] = [
    ("work-onward", "https://www.workonward.com/"),
    ("jigo-ai",     "https://jigo.ai/"),
    ("teiren",      "https://teiren.io/"),
    ("sortielab",   "https://sortielab.com/"),
    ("wordbricks",  "https://www.wordbricks.ai/"),
    ("phyxup",      "https://phyxup.com/"),
    ("sociable",    "https://www.sociable.how/"),
    ("secuxr",      "https://www.secuxr.com/"),
    ("tribe-money", "https://www.tribe.money/"),
    ("nurie",       "https://www.nurie.ai/"),
    ("miraflow",    "https://miraflow.ai/"),
    ("spotlite",    "https://spotlite.global/en"),
    ("bizcrush",    "https://bizcrush.app/"),
    ("provally",    "https://provally.io/"),
    ("guide-ai",    "https://www.getguide.ai/"),
]


class IconParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.icons: list[tuple[str, str, str]] = []  # (rel, href, sizes)
        self.og_image: str | None = None

    def handle_starttag(self, tag: str, attrs):
        a = dict(attrs)
        if tag == "link":
            rel = (a.get("rel") or "").lower()
            href = a.get("href") or ""
            if href and any(r in rel for r in ("icon", "apple-touch-icon", "apple-touch-icon-precomposed", "shortcut")):
                self.icons.append((rel, href, a.get("sizes", "")))
        elif tag == "meta":
            prop = (a.get("property") or a.get("name") or "").lower()
            if prop == "og:image" and a.get("content"):
                self.og_image = a["content"]

    handle_startendtag = handle_starttag  # treat <link/> too


def fetch(url: str, timeout: int = 20) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(8_000_000), (r.headers.get("Content-Type") or "")


def parse_size(s: str) -> int:
    if not s:
        return 0
    m = re.search(r"(\d+)\s*x\s*(\d+)", s)
    return int(m.group(1)) if m else 0


def candidates_for(home_url: str) -> list[tuple[int, str, str]]:
    """Returns [(score, full_url, why), ...] sorted best-first."""
    body, _ = fetch(home_url)
    p = IconParser()
    try:
        p.feed(body.decode("utf-8", errors="ignore"))
    except Exception:
        pass

    out: list[tuple[int, str, str]] = []
    for rel, href, sizes in p.icons:
        full = urllib.parse.urljoin(home_url, href)
        sz = parse_size(sizes)
        if "apple-touch-icon" in rel:
            score = max(sz, 180) + 1000  # prefer apple-touch-icon
        elif "icon" in rel:
            score = sz if sz else 32
        else:
            score = sz
        out.append((score, full, rel))

    if p.og_image:
        out.append((500, urllib.parse.urljoin(home_url, p.og_image), "og:image"))

    # always try /favicon.ico as a final fallback
    out.append((10, urllib.parse.urljoin(home_url, "/favicon.ico"), "favicon.ico"))

    out.sort(key=lambda c: -c[0])
    # de-duplicate by URL preserving order
    seen, dedup = set(), []
    for c in out:
        if c[1] in seen:
            continue
        seen.add(c[1])
        dedup.append(c)
    return dedup


def ext_from(content_type: str, url: str) -> str:
    ct = content_type.split(";", 1)[0].strip().lower()
    fixed = {
        "image/svg+xml": ".svg",
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/x-icon": ".ico",
        "image/vnd.microsoft.icon": ".ico",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "image/avif": ".avif",
    }
    if ct in fixed:
        return fixed[ct]
    guess = mimetypes.guess_extension(ct) if ct else None
    if guess:
        return ".jpg" if guess == ".jpe" else guess
    # fall back to url extension
    p = urllib.parse.urlparse(url).path
    _, e = os.path.splitext(p)
    return e.lower() if e else ".png"


def save_one(slug: str, home: str, out_dir: Path) -> str | None:
    print(f"  {slug:14s} {home}")
    try:
        cands = candidates_for(home)
    except Exception as e:
        print(f"    ! could not fetch homepage: {e}")
        return None
    for score, url, why in cands:
        try:
            data, ct = fetch(url, timeout=15)
            if not data or len(data) < 64:
                continue
            ext = ext_from(ct, url)
            path = out_dir / f"{slug}{ext}"
            path.write_bytes(data)
            print(f"    {why:30s} {url}  →  {path.name}  ({len(data):,}B)")
            return path.name
        except Exception as e:
            print(f"    skip {url} ({type(e).__name__}: {e})")
    print(f"    ! no logo could be downloaded for {slug}")
    return None


def main() -> int:
    out_dir = Path("logos")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir()

    manifest: dict[str, str] = {}
    for slug, url in COMPANIES:
        fn = save_one(slug, url, out_dir)
        if fn:
            manifest[slug] = f"logos/{fn}"

    print()
    print(f"Got {len(manifest)} / {len(COMPANIES)} logos.")
    if len(manifest) < len(COMPANIES):
        missing = [s for s, _ in COMPANIES if s not in manifest]
        print("Missing:", ", ".join(missing))

    # write a manifest so we know what was saved
    (out_dir / "manifest.txt").write_text(
        "\n".join(f"{k}\t{v}" for k, v in manifest.items()) + "\n",
        encoding="utf-8",
    )

    # zip it up
    if shutil.which("zip"):
        os.system("rm -f logos.zip && zip -qr logos.zip logos")
        print("Created logos.zip")
    else:
        os.system("tar -czf logos.tar.gz logos")
        print("zip not found — created logos.tar.gz instead")
    return 0


if __name__ == "__main__":
    sys.exit(main())
