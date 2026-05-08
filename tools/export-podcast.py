#!/usr/bin/env python3
"""
Export every post in the 'podcast' category from rabbitvc.com (WordPress)
via the public REST API, plus all referenced media. Produces:

    podcast-export/
      posts.json                 # full post data (title, slug, date, content, etc.)
      media/wp-content/uploads/  # any image / file referenced by a post
    podcast-export.zip           # ready to drop back into the repo

Usage:
    python3 tools/export-podcast.py
    # then push podcast-export.zip to the repo

No external deps — just stdlib. Requires Python 3.8+.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
HOST = "https://rabbitvc.com"
OUT = Path("podcast-export")
MEDIA = OUT / "media"
TIMEOUT = 30

OUT.mkdir(exist_ok=True)
MEDIA.mkdir(exist_ok=True)


def http_get(url: str, want_json: bool = False):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "application/json" if want_json else "*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def fetch_json(url: str):
    return json.loads(http_get(url, want_json=True).decode("utf-8"))


# 1. Find category id for 'podcast'
print("Looking up podcast category…")
cats = fetch_json(f"{HOST}/wp-json/wp/v2/categories?slug=podcast")
if not cats:
    sys.exit("ERROR: no 'podcast' category found")
cat_id = cats[0]["id"]
print(f"  podcast category id = {cat_id}")


# 2. Paginate through all posts in that category
print("Fetching posts…")
posts: list[dict] = []
page = 1
while True:
    url = (
        f"{HOST}/wp-json/wp/v2/posts"
        f"?categories={cat_id}&per_page=100&page={page}&_embed=1"
        f"&orderby=date&order=desc"
    )
    try:
        batch = fetch_json(url)
    except urllib.error.HTTPError as e:
        if e.code in (400, 404):
            break
        raise
    if not batch:
        break
    posts.extend(batch)
    print(f"  page {page}: +{len(batch)} (total {len(posts)})")
    if len(batch) < 100:
        break
    page += 1

print(f"Got {len(posts)} podcast posts")


# 3. Save the full posts JSON
manifest = OUT / "posts.json"
manifest.write_text(json.dumps(posts, indent=2), encoding="utf-8")
print(f"Wrote {manifest}")


# 4. Download every rabbitvc.com /wp-content/uploads/ asset referenced anywhere
url_re = re.compile(
    r'https?://(?:[^\s"\'<>)\\]+\.)?rabbitvc\.com/wp-content/uploads/[^\s"\'<>)\\]+'
)

seen: set[str] = set()


def save_media(url: str) -> str | None:
    if url in seen:
        return None
    seen.add(url)
    parsed = urllib.parse.urlparse(url)
    rel = parsed.path.lstrip("/")
    dest = MEDIA / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = http_get(url)
    except Exception as e:
        print(f"  ! failed {url}: {type(e).__name__}: {e}")
        return None
    dest.write_bytes(data)
    print(f"  saved {rel} ({len(data):,}B)")
    return rel


print("Downloading media…")
for p in posts:
    # featured image (and all its sizes)
    fms = p.get("_embedded", {}).get("wp:featuredmedia") or []
    for fm in fms:
        if fm.get("source_url"):
            save_media(fm["source_url"])
        for sz in (fm.get("media_details", {}).get("sizes", {}) or {}).values():
            if sz.get("source_url"):
                save_media(sz["source_url"])
    # urls embedded directly in post HTML
    content_html = (p.get("content") or {}).get("rendered", "") or ""
    for m in url_re.findall(content_html):
        save_media(m)
    excerpt_html = (p.get("excerpt") or {}).get("rendered", "") or ""
    for m in url_re.findall(excerpt_html):
        save_media(m)


# 5. Zip it up
print()
if any(p.iterdir() for p in [OUT]):
    name = "podcast-export.zip"
    if subprocess.run(["which", "zip"], capture_output=True).returncode == 0:
        subprocess.check_call(["zip", "-qr", name, "podcast-export"])
        print(f"Created {name}")
    else:
        name = "podcast-export.tar.gz"
        subprocess.check_call(["tar", "-czf", name, "podcast-export"])
        print(f"zip not found — created {name} instead")
    print(f"Push {name} to the repo when you're done.")
else:
    print("No data exported.")
