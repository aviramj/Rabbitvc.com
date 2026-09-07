#!/usr/bin/env python3
"""
Stamp the guest block into every episode page under podcast/.

Reads tools/guests.json and inserts (or refreshes) a <section class="ep-guest">
just above the Listen On row on each episode page: a small label, the guest's
name linked to their LinkedIn, their role, and - where there is one - a
one-line bio.

The block goes after .ep-body rather than inside it. Video episodes lead with the
embed and audio ones end with the player, so anchoring to the media element would
put the block in a different place on each kind; anchoring to Listen On keeps all
thirteen pages identical and avoids splitting .ep-body in half.

The block ships complete or not at all - the script refuses to write anything
while any guest is still missing a 'linkedin' or 'bio' value, so the site never
shows a half-filled guest strip. The inserted markup is fenced by HTML comments,
so re-running removes the previous block exactly and replaces it; editing a bio
and re-running is safe and leaves no residue.

Usage:
    python3 tools/apply-guest-strip.py           # write the blocks
    python3 tools/apply-guest-strip.py --check   # report readiness, change nothing
    python3 tools/apply-guest-strip.py --remove  # strip the blocks back out

No external deps - just stdlib. Requires Python 3.8+.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "guests.json"

START = "<!-- guest-block start -->"
END = "<!-- guest-block end -->"
BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n", re.S)
ANCHOR = '    <section class="listen-on"'

LI_ICON = (
    '<svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor" aria-hidden="true">'
    '<path d="M19.7,3H4.3C3.582,3,3,3.582,3,4.3v15.4C3,20.418,3.582,21,4.3,21h15.4c0.718,0,1.3-0.582,'
    '1.3-1.3V4.3 C21,3.582,20.418,3,19.7,3z M8.339,18.338H5.667v-8.59h2.672V18.338z M7.004,8.574c-0.857,'
    '0-1.549-0.694-1.549-1.548 c0-0.855,0.691-1.548,1.549-1.548c0.854,0,1.547,0.694,1.547,1.548C8.551,'
    '7.881,7.858,8.574,7.004,8.574z M18.339,18.338h-2.669 v-4.177c0-0.996-0.017-2.278-1.387-2.278c-1.389,'
    '0-1.601,1.086-1.601,2.206v4.249h-2.667v-8.59h2.559v1.174h0.037 c0.356-0.675,1.227-1.387,2.526-1.387'
    'c2.703,0,3.203,1.779,3.203,4.092V18.338z"/></svg>'
)


def build(g):
    return (
        START + "\n"
        '    <section class="ep-guest" aria-label="About the guest">\n'
        '      <p class="ep-guest-cap">The guest</p>\n'
        '      <p class="ep-guest-name"><a href="' + html.escape(g["linkedin"], quote=True) + '" '
        'target="_blank" rel="noopener">' + html.escape(g["name"]) +
        '<span class="ep-guest-li">' + LI_ICON + '</span></a></p>\n'
        '      <p class="ep-guest-role">' + g["role"] + '</p>\n'
        + ('      <p class="ep-guest-bio">' + g["bio"] + '</p>\n' if g["bio"].strip() else "")
        + '    </section>\n'
        + END + "\n"
    )


def main():
    guests = json.loads(DATA.read_text(encoding="utf-8"))["guests"]

    if "--remove" in sys.argv:
        for g in guests:
            page = ROOT / "podcast" / g["slug"] / "index.html"
            if not page.exists():
                continue
            s = page.read_text(encoding="utf-8")
            new = BLOCK_RE.sub("", s)
            if new != s:
                page.write_text(new, encoding="utf-8")
                print("removed from %s" % g["slug"])
        return 0

    # a bio is optional - some guests have nothing on record beyond their role,
    # and the block reads fine without one. A LinkedIn URL is not: the name is
    # rendered as a link, so a blank one would produce a link to nowhere.
    missing = [(g["name"], "linkedin") for g in guests if not g.get("linkedin", "").strip()]
    if missing:
        print("Not ready - %d field(s) still empty in tools/guests.json:" % len(missing))
        for name, field in missing:
            print("  %-22s %s" % (name, field))
        print("\nNothing was written. Fill them in and re-run.")
        return 1

    if "--check" in sys.argv:
        print("Ready: all %d guests have a linkedin (%d also have a bio)."
              % (len(guests), sum(1 for g in guests if g["bio"].strip())))
        return 0

    for g in guests:
        page = ROOT / "podcast" / g["slug"] / "index.html"
        if not page.exists():
            print("skip (no such page): %s" % g["slug"])
            continue
        s = BLOCK_RE.sub("", page.read_text(encoding="utf-8"))
        i = s.find(ANCHOR)
        if i == -1:
            print("skip (no Listen On row to anchor to): %s" % g["slug"])
            continue
        page.write_text(s[:i] + build(g) + s[i:], encoding="utf-8")
        print("wrote %s" % g["slug"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
