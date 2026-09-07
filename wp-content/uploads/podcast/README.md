# Episode thumbnails

Drop the 16:9 episode thumbnails here, named exactly as listed below.
The cards on /podcast/ and the og:image tags already point at these paths, so
dropping the files in is all that is needed - no code change follows. The
filename is the only thing tying an image to an episode.

Until a file lands, its card falls back on its own: video episodes show the
YouTube still, and episodes 1-3 show the rabbit brand plate.

- **Format:** JPG. Upload PNGs if that is what you have and they will be
  converted - the thirteen here started as PNGs averaging 550 KB each, 7.1 MB
  in total, and came down to 1.4 MB as JPEGs at quality 88 with no visible
  loss. PNG is the wrong container for a photograph.
- **Size:** 1920x1080, the same master you upload to YouTube
- **Naming:** zero-padded, `ep-01.jpg` through `ep-13.jpg`. Upload under any
  name and it can be renamed in a follow-up commit; the filename is what ties
  an image to an episode.

| File        | Guest             | Episode page slug                            |
| ----------- | ----------------- | -------------------------------------------- |
| `ep-01.jpg` | Paul Lee          | `startups-with-seoul-episode-1`              |
| `ep-02.jpg` | Chris Chae        | `startups-with-seoul-episode-2`              |
| `ep-03.jpg` | Ryan Lee          | `startups-with-seoul-episode-3`              |
| `ep-04.jpg` | David Yi          | `startups-with-seoul-episode-4-2`            |
| `ep-05.jpg` | Clara Hong        | `startups-with-seoul-episode-4`              |
| `ep-06.jpg` | Jiho Kang         | `startups-with-seoul-episode-6`              |
| `ep-07.jpg` | Jiwon Hong        | `startups-with-seoul-ep-7`                   |
| `ep-08.jpg` | CY Choi           | `startups-with-seoul-ep-8-cy-choi`           |
| `ep-09.jpg` | Sol Eun           | `startups-with-seoul-ep-9-sol-eun`           |
| `ep-10.jpg` | David Lee         | `startups-with-seoul-ep-10-david-lee`        |
| `ep-11.jpg` | John Sung Kim     | `startups-with-seoul-ep-11-john-sung-kim`    |
| `ep-12.jpg` | David Sangmin Lim | `startups-with-seoul-ep-12-david-sangmin-lim`|
| `ep-13.jpg` | Kyum Kim          | `startups-with-seoul-ep-13-kyum-kim`         |

**Careful with 4 and 5.** The slugs disagree with the episode numbers, a
leftover from the WordPress import: episode 4 (David Yi) lives at
`...-episode-4-2` and episode 5 (Clara Hong) lives at `...-episode-4`. Go by
the guest name in this table, not by the slug.
