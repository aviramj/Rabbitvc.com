# Podcast, the YouTube version

A verbatim copy of `/podcast/` as it stood at commit `99f498b`, when every
episode played from a YouTube embed and YouTube was listed as a place to
listen. It is kept here so the video version can be put back unchanged once
the channel is sorted out.

Nothing in this folder is published. The site is served by GitHub Pages, which
runs Jekyll, and Jekyll leaves out any directory whose name starts with an
underscore, so `_archive/` is in the repository but not on `rabbitvc.com`.

## What the live pages look like now

The live `/podcast/` is a temporary, audio-only version of the same thing:

- the YouTube iframe is gone from every episode page, and nothing plays in
  its place: an episode is read on the page and heard on Spotify or Apple
  Podcasts through the "Listen on" row. A Spotify embed stood there briefly;
  it was taken out because its cover art is part of the iframe and cannot be
  styled or hidden from our side,
- YouTube is gone from the "Listen on" rows on the index and the episode pages,
- the "Watch" cues on the index read "Listen".

Everything else — copy, artwork, guests, ordering, Spotify and Apple links — is
untouched.

## Putting the video version back

From the repository root:

```sh
./_archive/podcast-youtube/restore.sh
```

That copies these files back over `/podcast/`. Review with `git diff`, then
commit. The archived pages use the `.ep-video` rule in `rv.css`, which was left
in place, so nothing in the stylesheet needs changing to restore.

Same thing straight from git history, if you prefer:

```sh
git checkout 99f498b -- podcast
```
