# Staging

Preview work. Nothing in here is linked from the live site, and nothing here
changes it: `index.html`, `styles.css` and `app.js` at the repository root are
untouched by this branch.

| Path | What it is |
| --- | --- |
| `index.html` | The staged homepage. The current homepage with the new hero in place of the illustrated cityscape. Loads `../styles.css` first, then `hero.css`. |
| `hero.css` | Styles for the new hero only. Loaded by the staged page alone, so the live homepage is unaffected. |
| `hero-review/` | The partner review page: the chosen direction, what it is made of, and the open questions. Also published as a Claude artifact. Self-contained apart from Google Fonts. |
| `hero-options/` | Round one. Four takes on a large statement over navy. Superseded, kept for reference. |
| `hero-options-2/` | Round two. Five distinct directions: Index, Meridian, Ticker, Broadsheet, Monogram. The chosen hero came from Ticker plus Broadsheet's Latest column. |
| `contact-options/` | Four directions for `/contact/`: Skyline, Letterhead, Three windows, Quiet letter. Loads `../../styles.css`, so every option is judged in the site's real tokens and type. |

## The contact page

`contact-options/` shows four ways to lay out `/contact/`. All four carry the
same content, the address and the three offices, and all four use the 2023
cityscape painting, differing in what they ask it to do:

| Option | The painting is | Reads as |
| --- | --- | --- |
| A. Skyline | the banner, behind the headline | a conventional interior page. This is what is built at `/contact/`. |
| B. Letterhead | a tall panel beside the details, washed into the ground at the seam | a letterhead. Addresses are a list, so a fourth office is one more row. |
| C. Three windows | cut into three, one slice per office | the offices *are* the artwork. Cards run Tel Aviv, Valley, Seoul, the order the painting is composed in. |
| D. Quiet letter | a closing band, fading up out of the ground | a printed letter. Type only above the fold; closest to the three-city strip from the old banner. |

C leans on the painting being composed left to right as Tel Aviv, then the
Valley, then Seoul. Each frame is one `background-position` on a single file
at `background-size: 400%`, so there are no new image assets and no crops to
maintain.

Two review conveniences, not part of any option: `?only=c` isolates one
direction and `?theme=light` opens on the cream ground.

## The hero

Headline is the motto, `Beyond Capital: Global Reach. Rapid Scale. Day One.`,
set across three lines with the phrases held together so none splits across a
line break. Latest sits on the right, the eighteen portfolio companies move
along the bottom.

Neither content block is hardcoded:

- The **ticker** reads company names out of the page's own portfolio section,
  so adding a company adds it to the hero. Cards carrying a logo image are read
  from its `alt`; the SecuXR card has no logo, so it carries `data-name`.
- **Latest** fetches the newest items from `../news/` on load and falls back to
  the four shipped in the HTML if that request fails.

Motion pauses on hover and stops under `prefers-reduced-motion`. The nav keeps
the hero's colouring while the hero is behind it, so it never turns pale over
navy in light mode.

## Colours

Sampled from the Fund II deck, the business cards and the banners:

| Token | Hex | Source |
| --- | --- | --- |
| navy | `#0A0E27` | deck ground |
| indigo | `#2E2A6E` | banner glow |
| blue | `#3B8EFF` | deck accent |
| cream | `#F5F4EE` | card stock |
| gold | `#B4924F` | card rule |
| ink | `#1B1B3A` | card type |

Two things are still open, both outside the hero:

1. The site ground is `#0E151F` (H 215, S 38) against the hero's `#0A0E27`
   (H 232, S 59). Same lightness, different hue, so there is a faint band at
   the seam. Pointing `--bg` at the deck navy closes it; `--bg-soft` and
   `--bg-elev` should follow the same hue.
2. The site still runs on teal `#0BB4AA` and orange `#FF8A5B`, neither of which
   appears in any brand asset. They should move to the deck blue.
