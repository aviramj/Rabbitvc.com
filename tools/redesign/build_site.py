#!/usr/bin/env python3
"""Generate the live Rabbit Ventures site from the extracted content.

One source of truth per page, so the copy cannot drift between them.
Content and every outbound link come from sitedata.py, which was read
straight off the pages this replaces.
"""
import hashlib, os, re, shutil
from sitedata import (TEAM, PARTNERS, PORTFOLIO, NEWS, PODCAST,
                      DR_GALLERY, DR_PROSE, OFFICES, DR_STORIES)
from episodes import EPISODES
from marks import MARKS

ROOT = "/home/user/Rabbitvc.com"
NAV = [("Home", ""), ("Team", "#team"), ("Fund Partners", "#advisors"),
       ("Portfolio", "portfolio/"), ("News", "news/"),
       ("Desert Rose", "desert-rose/"), ("Podcast", "podcast/")]


def up(depth):
    return "" if depth == 0 else "../" * depth


def href(target, depth):
    """Resolve a nav target from a page nested `depth` folders down."""
    if target.startswith("#"):
        return (target if depth == 0 else up(depth) + target)
    return up(depth) + target


def head(depth, title, desc, canon, extra="", redirect=""):
    u = up(depth)
    REDIRECT = redirect
    return f'''<!doctype html>
<html lang="en-US">
<head>
{REDIRECT}<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover" />
<title>{title}</title>
<meta name="description" content="{desc}" />
<meta name="theme-color" content="#1C222E" />
<meta property="og:locale" content="en_US" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{desc}" />
<meta property="og:url" content="{canon}" />
<meta property="og:site_name" content="Rabbit Ventures" />
<meta property="og:image" content="https://rabbitvc.com/wp-content/uploads/2025/09/rabbit-ventures-og.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="canonical" href="{canon}" />
<link rel="icon" href="{u}wp-content/uploads/2023/08/cropped-rabbit-32x32.png" sizes="32x32" />
<link rel="icon" href="{u}wp-content/uploads/2023/08/cropped-rabbit-192x192.png" sizes="192x192" />
<link rel="apple-touch-icon" href="{u}wp-content/uploads/2023/08/cropped-rabbit-180x180.png" />
<link rel="stylesheet" href="{u}rv.css?v={VER}" />
{extra}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="site d--a d--a3">'''


def nav(depth, active=""):
    u = up(depth)
    links = "".join(
        '<a href="%s"%s>%s</a>' % (href(t, depth) or (u or "./"),
                                   ' aria-current="page"' if n == active else "", n)
        for n, t in NAV)
    mob = "".join('<a href="%s"%s>%s</a>'
                  % (href(t, depth) or (u or "./"),
                     ' aria-current="page"' if n == active else "", n)
                  for n, t in NAV)
    return f'''
<header class="s-nav">
  <a class="s-brand" href="{u or './'}" aria-label="Rabbit Ventures home">
    <img class="mark" src="{u}wp-content/uploads/2025/09/rabbit-mark-white.png" alt="" width="316" height="400" />
    <span class="s-wordmark">Rabbit Ventures</span>
  </a>
  <nav class="s-links" aria-label="Primary">{links}</nav>
  <a class="s-contact" href="{u}contact/">Contact Us</a>
  <button class="s-menu-btn" id="menu-btn" type="button"
          aria-controls="mobile-menu" aria-expanded="false">Menu</button>
</header>
<nav class="s-mobile" id="mobile-menu" aria-label="Primary" hidden>{mob}
  <a href="{u}contact/">Contact Us</a>
</nav>'''


FOOT_TPL = '''
<footer class="s-foot">
  <span class="s-wordmark">Rabbit Ventures</span>
  <span>Copyright &copy; Rabbit Ventures</span>
</footer>
</div>
<script>
(function () {
  var b = document.getElementById('menu-btn'), m = document.getElementById('mobile-menu');
  if (!b || !m) return;
  b.addEventListener('click', function () {
    var open = m.hidden;
    m.hidden = !open;
    b.setAttribute('aria-expanded', String(open));
  });
})();
// Contact: copy the address without leaving the page.
(function () {
  var b = document.getElementById('copy-addr');
  if (!b || !navigator.clipboard) { if (b) b.hidden = true; return; }
  b.addEventListener('click', function () {
    navigator.clipboard.writeText('hello@rabbitvc.com').then(function () {
      var t = b.textContent; b.textContent = 'Copied';
      setTimeout(function () { b.textContent = t; }, 1600);
    });
  });
})();
// Desert Rose: open a frame full size.
(function () {
  var dlg = document.getElementById('lightbox');
  if (!dlg) return;
  var img = null;                            // created on first open, so the
  function frame() {                         // page never holds a srcless <img>
    if (!img) { img = document.createElement('img'); dlg.appendChild(img); }
    return img;
  }
  document.querySelectorAll('.dr-gal button').forEach(function (b) {
    b.addEventListener('click', function () {
      var el = frame();
      el.src = b.dataset.full;
      el.alt = b.querySelector('img').alt;
      dlg.showModal();
    });
  });
  dlg.querySelector('.close').addEventListener('click', function () { dlg.close(); });
  dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener('close', function () { if (img) img.remove(), img = null; });
})();
</script>
</body>
</html>
'''

# Derived from the stylesheet itself: a hand-kept version string was left
# unchanged across a CSS fix once already, so every cached browser and the
# CDN kept serving the stale sheet and the fix was invisible.
VER = hashlib.md5(open("rv.css", "rb").read()).hexdigest()[:8]


def page_head(title, sub):
    return ('<header class="pg-head"><h1 class="pg-h1">%s</h1>'
            '<p class="pg-sub">%s</p></header>' % (title, sub))


def write(path, html):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(html)
    return "%-28s %6d bytes" % (path, len(html))


# ----------------------------------------------------------------- homepage
THESIS = [
    ("Stage", "Pre-seed and seed", "First check, with follow-on"),
    ("Sectors", "Cybersecurity. Defense &amp; military software. AI-native deep tech.", ""),
    ("We look for", "Infrastructure-first companies",
     "Built for global enterprise buyers, with a clear path to U.S. market leadership"),
    ("We bring", "Operator-led GTM and BD",
     "U.S. market access, a CXO and CISO network, strategic guidance"),
]

# No .s-figure block: the chosen direction hides it (`.d--a .s-figure{display:none}`)
# because the photographs were taken out of that part of the page.

MARK = "wp-content/uploads/2025/09/rabbit-mark-white.png"


def slug_of(name):
    return name.split()[0].lower().strip("(")


def home():
    news = "".join(
        '<a class="n-item" href="%s" target="_blank" rel="noopener">'
        '<time>%s</time><span>%s</span></a>' % (n["href"], n["date"], n["title"])
        for n in NEWS[:4])

    thesis = "".join(
        '<div class="t-row"><dt>%s</dt><dd>%s%s</dd></div>'
        % (k, v, ('<small>%s</small>' % s) if s else "")
        for k, v, s in THESIS)

    team = "".join(
        '''<article class="m m--%s">
          <div class="m-photo"><img src="%s" alt="%s" loading="lazy" /></div>
          <div class="m-body">
            <p class="m-role">%s</p>
            <h3 class="m-name">%s</h3>
            <details class="m-det">
              <summary>Background</summary>
              <p class="m-bio">%s</p>
              %s
            </details>
          </div>
        </article>''' % (slug_of(t["name"]), t["img"], t["name"], t["role"], t["name"], t["bio"],
                          ('<a class="m-li" href="%s" target="_blank" rel="noopener">LinkedIn</a>'
                           % t["li"]) if t["li"] else "")
        for t in TEAM)

    partners = "".join(
        '<li><a href="%s" target="_blank" rel="noopener">%s</a></li>' % (h, n)
        for n, h in PARTNERS)

    # the ticker runs the portfolio marks; the one wordmark-only company is skipped
    run = "".join('<img src="%s" alt="%s" />' % (p["img"], p["name"])
                  for p in PORTFOLIO if p["img"])
    ticker = ('<div class="tk-row">%s</div>'
              '<div class="tk-row" aria-hidden="true">%s</div>' % (run, run))

    return head(0, "Rabbit Ventures",
                "The pre-seed and seed partner for cybersecurity, defense software and "
                "AI-native deep tech, across Israel, Korea and Silicon Valley.",
                "https://rabbitvc.com/",
                redirect="<script>if(location.hash===\'#news\')location.replace(\'./news/\');\n"
                         "if(location.hash===\'#portfolio\')location.replace(\'./portfolio/\');</script>\n"
                ) + nav(0, "Home") + '''
<main id="main">

  <section class="s-hero">
    <div class="s-hero-text">
      <h1 class="s-h1">Beyond Capital:<br />Global Reach.<br />Rapid Scale. Day One.</h1>
      <p class="s-lede">The pre-seed and seed partner for cybersecurity, defense software and
      AI-native deep tech, across Israel, Korea and Silicon Valley.</p>
      <div class="s-cta">
        <a class="btn btn-solid" href="portfolio/">View Portfolio</a>
        <a class="btn btn-line" href="#team">Meet the Team</a>
      </div>
    </div>
    <aside class="s-latest">
      <h2 class="s-latest-h">Latest</h2>
      %s
      <a class="n-more" href="news/">All news</a>
    </aside>
  </section>

  <div class="s-ticker" aria-label="Portfolio companies">%s</div>

  <section class="s-vision" id="about">
    <div class="v-lead">
      <h2 class="v-h">The <em>global launchpad</em> from day one</h2>
      <p class="v-p">We are the pre-seed and seed partner for global success, specialized in
      <strong>cybersecurity and defense software</strong> and AI-native, AI-driven deep tech, with
      full-scale execution, focused on startups connected to the Israeli, Korean and Silicon Valley
      ecosystems.</p>
      <p class="v-p">We bring capital and an operational blueprint, <strong>The Rabbit Playbook</strong>:
      hands-on partnership that begins at seed and spans the entire lifecycle of global growth.</p>
    </div>
    <div class="v-thesis">
      <h3 class="v-thesis-h">Our Mission &amp; Thesis</h3>
      <dl class="t-dl">%s</dl>
    </div>
  </section>

  <section class="s-team tv--d" id="team">
    <header class="sec-h"><h2>Our Team</h2></header>
    <div class="team-grid">%s</div>
  </section>

  <section class="s-fp" id="advisors">
    <header class="sec-h"><h2>Fund Partners</h2><span>An extended team of operators who help our founders go global</span></header>
    <h3 class="fp-sub">Mentors and Fund Partners</h3>
    <ul class="fp-list">%s</ul>
  </section>

  <section class="s-pship">
    <header class="sec-h"><h2>Partnership</h2><span></span></header>
    <div class="ps-grid">
      <div class="ps-one">
        <div class="lockup"><img class="mark" src="%s" alt="" /><i>&times;</i><img class="lk-logo" src="logos/j-ventures.png" alt="J-Ventures" /></div>
        <p>Our partnership with <strong>J-Ventures</strong>: a Silicon Valley community-driven fund
        connecting the American and Israeli tech ecosystems, opening Israel&rsquo;s cybersecurity and
        deep-tech bench to the Rabbit playbook, alongside the Korean and Silicon Valley founders we
        already back.</p>
      </div>
      <div class="ps-one">
        <div class="lockup"><img class="mark" src="%s" alt="" /><i>&times;</i><img class="lk-logo lk-technion" src="logos/technion.svg" alt="Technion, Israel Institute of Technology" /></div>
        <p>Our partnership with <strong>Technion</strong>: Cybersecurity and deep-tech teams with
        Technion roots and elite engineering backgrounds, building for global markets from day one.</p>
      </div>
    </div>
  </section>

</main>''' % (news, ticker, thesis, team, partners, MARK, MARK) + FOOT_TPL


# ---------------------------------------------------------------- portfolio
def portfolio():
    cells = ""
    for p in PORTFOLIO:
        if p["img"]:
            mark = ('<img class="pf-mark" src="../%s" alt="%s" loading="lazy"%s />'
                    % (p["img"], p["name"],
                       (' style="%s"' % p["style"]) if p["style"] else ""))
        else:
            mark = '<span class="pc-wm">%s</span>' % p["name"]
        cells += ('<a class="pc" href="%s" target="_blank" rel="noopener" data-name="%s">'
                  '<span class="pc-mark">%s</span>'
                  '<span class="pc-meta"><span class="pc-desc">%s</span></span></a>'
                  % (p["href"], p["name"], mark, p["desc"]))
    return head(1, "Portfolio | Rabbit Ventures",
                "Pre-seed and seed investments across cybersecurity, defense software and "
                "AI-native deep tech.",
                "https://rabbitvc.com/portfolio/") + nav(1, "Portfolio") + '''
<main id="main" class="pg-main">
  %s
  <div class="pf-list">%s</div>
</main>''' % (page_head("The companies we back",
                       "Pre-seed and seed investments across cybersecurity, defense software "
                       "and AI-native deep tech."), cells) + FOOT_TPL


# --------------------------------------------------------------------- news
def news_rows(items, depth):
    return "".join(
        '<a class="nw" href="%s" target="_blank" rel="noopener">'
        '<span class="nw-when"><time>%s</time><em>%s</em></span>'
        '<span class="nw-cover"><img src="%s%s" alt="" loading="lazy" /></span>'
        '<span class="nw-body"><span class="nw-title">%s</span>'
        '<span class="nw-desc">%s</span></span></a>'
        % (n["href"], n["date"], n["kind"], up(depth), n["img"], n["title"], n["desc"])
        for n in items)


def news():
    return head(1, "News | Rabbit Ventures",
                "Portfolio announcements, events and press from Rabbit Ventures.",
                "https://rabbitvc.com/news/") + nav(1, "News") + '''
<main id="main" class="pg-main pg--measure">
  %s
  <div class="nw-list">%s</div>
</main>''' % (page_head("Where we have been showing up",
                       "Portfolio announcements, events and press, most recent first."),
              news_rows(NEWS, 1)) + FOOT_TPL


# -------------------------------------------------------------- desert rose
def desert():
    out, cur, body = "", None, ""
    for b in DR_PROSE:
        if b[0] == "h":
            if cur is not None:
                out += ('<div class="dr-sec"><h2 class="dr-h">%s</h2>'
                        '<div class="dr-copy">%s</div></div>' % (cur, body))
            cur, body = b[1], ""
        elif b[0] == "p":
            body += "<p>%s</p>" % b[1]
        else:
            body += ('<blockquote class="dr-quote"><p>“%s”</p>'
                     '<footer>%s</footer></blockquote>' % (b[1], b[2]))
    out += ('<div class="dr-sec"><h2 class="dr-h">%s</h2>'
            '<div class="dr-copy">%s</div></div>' % (cur, body))

    frames = "".join(
        '<button type="button" class="%s" data-full="./photos/%s">'
        '<img src="./photos/%s" alt="%s" loading="lazy" /></button>' % (c, f, f, a)
        for c, f, a in DR_GALLERY)

    stories = news_rows([n for n in NEWS if n["title"] in DR_STORIES], 1)

    return head(1, "Desert Rose Workation | Rabbit Ventures",
                "A two-week founder workation in the desert, built to give founders the "
                "isolation, time and people to focus on what actually matters.",
                "https://rabbitvc.com/desert-rose/") + nav(1, "Desert Rose") + '''
<main id="main" class="pg-main">
  %s
  <figure class="dr-band">
    <img src="./photos/dr-zion-peaks.jpg" alt="Red rock canyon walls above the road into Zion, southern Utah" />
  </figure>
  <div class="dr-prose">%s</div>
  <h2 class="dr-sub">Two weeks in pictures</h2>
  <div class="dr-gal">%s</div>
  <h2 class="dr-sub">Stories from the desert</h2>
  <div class="nw-list">%s</div>
</main>
<dialog class="dr-lightbox" id="lightbox">
  <button class="close" type="button" aria-label="Close">&times;</button>
</dialog>''' % (page_head("Desert Rose Workation",
                         "A two-week workation in the Arizona desert where Rabbit Ventures "
                         "founders, mentors, and investors step away from the noise and work "
                         "on what actually matters."),
                out, frames, stories) + FOOT_TPL


# ------------------------------------------------------------------ podcast
PLATFORMS = [("Spotify", "https://open.spotify.com/show/2VDaGWArtJPuHOLAzqibW4"),
             ("Apple Podcasts", "https://podcasts.apple.com/us/podcast/startups-with-seoul/id1734893626"),
             ("YouTube", "https://www.youtube.com/@RabbitVentures")]


def podcast():
    lead = PODCAST[0]
    rest = "".join(
        '<a class="pd-ep" href="%s">'
        '<img src="../wp-content/uploads/podcast/%s" alt="%s on The Rabbit Ventures Podcast" loading="lazy" />'
        '<span class="pd-n">%s</span><span class="pd-name">%s</span>'
        '<span class="pd-desc">%s</span><span class="pd-watch">Watch &rarr;</span></a>'
        % (e["href"], e["still"], e["name"], e["num"], e["name"], e["desc"])
        for e in PODCAST[1:])
    plats = '<span class="pd-plats">%s</span>' % "".join(
        '<a class="lo" href="%s" target="_blank" rel="noopener">%s<span>%s</span></a>'
        % (u, mark_for(n), n) for n, u in PLATFORMS)

    return head(1, "Podcast | Rabbit Ventures",
                "Conversations with founders, operators, and investors.",
                "https://rabbitvc.com/podcast/") + nav(1, "Podcast") + '''
<main id="main" class="pg-main">
  %s
  <p class="pd-meta"><b>%d episodes</b><span>Listen on</span>%s</p>
  <a class="pd-lead" href="%s">
    <img src="../wp-content/uploads/podcast/%s" alt="%s on The Rabbit Ventures Podcast" />
    <span>
      <span class="pd-latest">Latest &middot; %s</span>
      <h3>%s</h3><p>%s</p>
      <span class="pd-watch">Watch &rarr;</span>
    </span>
  </a>
  <div class="pd-grid">%s</div>
</main>''' % (page_head("The Rabbit Ventures Podcast",
                       "Conversations with founders, operators, and investors."),
              len(PODCAST), plats, lead["href"], lead["still"], lead["name"],
              lead["num"], lead["name"], lead["desc"], rest) + FOOT_TPL


# ------------------------------------------------------------------ contact
def contact():
    cities = "".join(
        '<a class="cy-city" href="%s" target="_blank" rel="noopener">'
        '<h2>%s</h2><address>%s</address></a>'
        % (m, name, "<br />".join(x.strip() for x in addr))
        for name, m, addr in OFFICES)
    return head(1, "Contact | Rabbit Ventures",
                "Write to Rabbit Ventures. Offices in Silicon Valley, Seoul and Tel Aviv.",
                "https://rabbitvc.com/contact/") + nav(1, "Contact Us") + '''
<main id="main" class="pg-main pg--flush">
  <section class="cy-letter">
    <h1><a class="cy-mail" href="mailto:hello@rabbitvc.com">hello@rabbitvc.com</a></h1>
    <div><button class="cy-copy" id="copy-addr" type="button">Copy address</button></div>
    <div class="cy-strip">%s</div>
  </section>
  <div class="cy-plate">
    <img src="../wp-content/uploads/2023/03/rabbit-website-background-image5-1-1536x1147.jpg"
         srcset="../wp-content/uploads/2023/03/rabbit-website-background-image5-1-1024x765.jpg 1024w,
                 ../wp-content/uploads/2023/03/rabbit-website-background-image5-1-1536x1147.jpg 1536w,
                 ../wp-content/uploads/2023/03/rabbit-website-background-image5-1-2048x1529.jpg 2048w"
         sizes="100vw" width="1536" height="1147" loading="lazy"
         alt="Illustration merging the Tel Aviv seafront, the Silicon Valley hills and the Seoul skyline into one coastline at dusk" />
  </div>
</main>''' % cities + FOOT_TPL


def mark_for(name):
    """The platform's own mark, or nothing if the name is not one we hold."""
    key = ("spotify" if "spotify" in name.lower()
           else "apple" if "apple" in name.lower()
           else "youtube" if "youtube" in name.lower() else None)
    return MARKS.get(key, "")


# ---------------------------------------------------------- podcast episode
def episode(i):
    """One episode page, two folders deep. The order of EPISODES is the
    directory order, so prev/next walk by episode number instead."""
    e = EPISODES[i]
    num = re.match(r"Ep\s*(\d+)", e["title"])
    label = "Ep %s" % num.group(1) if num else ""
    name = e["title"].split(":", 1)[1].strip() if ":" in e["title"] else e["title"]

    copy = "".join("<p>%s</p>" % p for p in e["paras"])

    g = e["guest"]
    guest = ""
    if g and g.get("name"):
        who = ('<a href="%s" target="_blank" rel="noopener">%s</a>' % (g["li"], g["name"])
               if g.get("li") else g["name"])
        guest = ('<section class="ep-guest">'
                 '<p class="ep-guest-cap">The guest</p>'
                 '<p class="ep-guest-name">%s</p>'
                 '%s%s</section>'
                 % (who,
                    ('<p class="ep-guest-role">%s</p>' % g["role"]) if g.get("role") else "",
                    ('<p class="ep-guest-bio">%s</p>' % g["bio"]) if g.get("bio") else ""))

    plat = "".join(
        '<a class="lo" href="%s" target="_blank" rel="noopener">%s<span>%s</span></a>'
        % (u, mark_for(n), n) for n, u in e["links"])
    listen = ('<div class="ep-listen"><b>Listen on</b>%s</div>' % plat) if plat else ""

    def key(x):
        m = re.match(r"Ep\s*(\d+)", x["title"])
        return int(m.group(1)) if m else 0
    order = sorted(range(len(EPISODES)), key=lambda j: key(EPISODES[j]))
    at = order.index(i)
    def link(j, arrow, side):
        if j < 0 or j >= len(order):
            return "<span></span>"
        o = EPISODES[order[j]]
        t = o["title"].split(":", 1)[1].strip() if ":" in o["title"] else o["title"]
        return '<a href="../%s/">%s</a>' % (o["slug"], arrow % t)
    seq = ('<nav class="ep-seq">%s%s</nav>'
           % (link(at - 1, "&larr; %s", "prev"), link(at + 1, "%s &rarr;", "next")))

    desc = e["paras"][0] if e["paras"] else "The Rabbit Ventures Podcast."
    desc = re.sub(r"<[^>]+>", "", desc)[:180]

    return head(2, "%s | The Rabbit Ventures Podcast" % e["title"], desc,
                "https://rabbitvc.com/podcast/%s/" % e["slug"]) + nav(2, "Podcast") + \
        '''
<main id="main" class="pg-main">
  <article class="ep-wrap">
    <a class="ep-back" href="../">&larr; All episodes</a>
    <span class="ep-n">%s</span>
    <h1 class="ep-h1">%s</h1>
    <div class="ep-video">
      <iframe src="https://www.youtube.com/embed/%s" title="%s"
              loading="lazy" allowfullscreen
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              referrerpolicy="strict-origin-when-cross-origin"></iframe>
    </div>
    <div class="ep-copy">%s</div>
    %s
    %s
    %s
  </article>
</main>''' % (label, name, e["yt"], e["title"], copy, guest, listen, seq) + FOOT_TPL


if __name__ == "__main__":
    shutil.copy("rv.css", os.path.join(ROOT, "rv.css"))
    print("rv.css copied")
    for path, fn in [("index.html", home), ("portfolio/index.html", portfolio),
                     ("news/index.html", news), ("desert-rose/index.html", desert),
                     ("podcast/index.html", podcast), ("contact/index.html", contact)]:
        print(write(path, fn()))
    for i, e in enumerate(EPISODES):
        print(write("podcast/%s/index.html" % e["slug"], episode(i)))
