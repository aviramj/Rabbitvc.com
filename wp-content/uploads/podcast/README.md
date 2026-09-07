# Episode thumbnails

Drop the 16:9 episode thumbnails here, named exactly as listed below.
`tools/apply-thumbnails.py` wires them into the cards on /podcast/ by this
name, so the filename is the only thing tying an image to an episode.

- **Format:** JPG (PNG is fine if the file stays under ~400 KB)
- **Size:** 1920x1080, the same master you upload to YouTube
- **Naming:** zero-padded, `ep-01` through `ep-13`

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
