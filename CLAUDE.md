# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`rabbitvc.com` — the Rabbit Ventures marketing site. It is a **plain static site** served by GitHub Pages from the repo root (see `CNAME` → `rabbitvc.com`). There is no framework, no bundler, no package manager, no test suite. Pages are hand-authored HTML, one shared `styles.css`, and one IIFE-style `app.js`.

## Local development

There are no build/lint/test commands. To preview, serve the repo root over HTTP (relative asset paths assume that):

```sh
python3 -m http.server 8000   # then open http://localhost:8000/
```

The `staging/` directory is a separate preview of in-progress changes intended to be reachable at `https://rabbitvc.com/staging/` — it links back to `../wp-content/...` and `../styles.css`, so it must live one level deep from the served root.

Deployment is whatever GitHub Pages does on push to the default branch; do not add CI/build steps unless explicitly requested.

## Architecture: three URL spaces sharing one stylesheet

Understanding why the directory tree looks the way it does requires reading multiple files together:

1. **Live site (`/`, `/podcast/`, `/podcast/<slug>/`)** — the canonical pages. `index.html` is the single-page home (hero / about / team / advisors / portfolio / news / contact, all anchored sections). `podcast/index.html` is the episode index; each episode has its own folder `podcast/<slug>/index.html`.

2. **Legacy WordPress permalinks (`/2023/MM/DD/<slug>/`, `/2024/MM/DD/<slug>/`, `/category/podcast/`)** — these mirror the URL shape of the previous WordPress site. They are **not** real content; they are meta-refresh + `location.replace` redirect stubs that point at the current canonical URL under `/podcast/`. When you add or rename a podcast episode, update the redirect stub at the matching legacy date path so old links keep working. Don't delete the legacy folders.

3. **Staging (`/staging/`, `/staging/news/`)** — a preview clone of pages being iterated on. It uses `../styles.css` and `../wp-content/...` paths and shows a "Staging preview - not yet live" banner (`.staging-banner` in `styles.css`). Promote staging changes to the live pages; don't merge them silently.

All three spaces share the single root `styles.css` and `app.js`, so a CSS/JS change instantly affects every page. Page-specific styling is gated by body classes: `podcast-page`, `podcast-index`, `episode-page`, `news-page`, etc.

## `app.js` invariants

- Single IIFE, no modules, no dependencies. Behaviors: theme toggle (persisted via `localStorage['rv-theme']`), scroll-aware nav (`.scrolled` after 80px), mobile menu, `IntersectionObserver` reveal-on-scroll (`.reveal` → `.in`), hero parallax, and active-section highlighting.
- Active-section highlighting uses a hardcoded list `sectionIds = ['top', 'about', 'team', 'advisors', 'portfolio', 'contact']`. **If you add or rename a top-level section on `index.html`, update this array** or the nav highlight will silently stop working for that section.
- All effects degrade for `prefers-reduced-motion: reduce`.

## `styles.css` invariants

- Theming is driven by CSS custom properties on `:root` and `[data-theme="light"]`. The `data-theme` attribute is set on `<html>` by `app.js` from `localStorage`; default in markup is `dark`. Don't hardcode colors — extend the variable set.
- Layout tokens (`--maxw`, `--pad`, `--section-y`, radii, shadows, easing) are defined once at the top — reuse them.

## Assets and the `wp-content/` tree

`wp-content/uploads/YYYY/MM/...` is the imported WordPress media library. New images can go in `news-images/` (events/press), `logos/` (portfolio companies), or — to match historical paths — `wp-content/uploads/YYYY/MM/`. Many `<img>` tags use full responsive `srcset` with several pre-resized variants of the same source; preserve that pattern when swapping images.

## `tools/` — one-shot helpers, not part of the site

These scripts exist to repopulate assets from external sources; they are not run as part of normal development. Use them only when explicitly needed:

- `tools/download-assets.sh` — re-fetches every image referenced from `index.html` off the live `rabbitvc.com` and zips them. Bash + `curl` + `zip`.
- `tools/download-logos.py` — scrapes portfolio company homepages (apple-touch-icon → og:image → favicon) into `logos/<slug>.<ext>`. **Stdlib only**, Python 3.8+. Editing the portfolio list means editing the `COMPANIES` tuple here and adding a matching `<a class="pf-card">` block in `index.html`.
- `tools/export-podcast.py` — pulls every post in the `podcast` category from the old WordPress install via `wp-json` plus referenced media into `podcast-export/`. Stdlib only. Output paths (`podcast-export/`, `podcast-export.zip`) are gitignored.

## Editing conventions specific to this repo

- Adding a podcast episode: create `podcast/<slug>/index.html` (clone an existing episode page for nav/header boilerplate, mind the `../../` relative paths), add an `<a class="ep-card">` to `podcast/index.html`, and add a redirect stub at the corresponding legacy `YYYY/MM/DD/<slug>/index.html` path.
- Adding a portfolio company: append a `<a class="pf-card">` in the `#portfolio` section of `index.html`, drop a logo in `logos/`, and (if you intend to refresh logos via the script) add the slug + URL to `COMPANIES` in `tools/download-logos.py`. Some logos use inline `style="--logo-zoom:..; --logo-origin:..; --logo-filter:..;"` to fix sizing/contrast — that's intentional, not an inline-style smell.
- Adding a news item: append a `<a class="news-card">` to the `#news` section of `index.html` (and the staging mirror if you're staging it). Cover images go in `news-images/`; cards without an image use the `.news-placeholder` "Photo" block.
- The home `index.html` currently has two "News" links in `.nav-links` — if you touch that nav, deduplicate it.
