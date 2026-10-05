---
service: YouTube (privacy-enhanced embeds)
vendor: Google Ireland Ltd. / Google LLC
category: marketing
status: active
owner: content / blog editor
added: before 2026 (Framer site)
last_reviewed: 2026-10-05
---

# YouTube

**What it does for us:** video players inside blog articles.

## Where it is used

- `articles/building-your-personal-brand-how-job-seekers-can-impress-employers.html`
- `articles/mastering-your-remote-job-interview-essential-tips-to-stand-out-online.html`
- `articles/thinking-of-a-career-change-expert-advice-for-professionals-ready-to-pivot.html`
- Code: each player is an `<iframe data-ry-src="https://www.youtube-nocookie.com/embed/<id>…">`
  (no `src` until Play). `assets/site.js` (YouTube section) handles the Play click.
- Thumbnails are self-hosted: `assets/media/yt-<video-id>-hqdefault.webp`.

## Data it receives

Nothing until the visitor clicks Play. After that: IP address, device data and viewing behaviour,
under Google's privacy policy.

## Cookies and browser storage

`youtube-nocookie.com` doesn't set cookies until the video is played; after playing, YouTube may set
cookies/local storage such as `VISITOR_INFO1_LIVE`, `YSC` and `yt-remote-*` items (names change over
time — **verify** and update [../cookies.md](../cookies.md)).

## Consent

Marketing & media. With that consent, Play starts the video directly; without it, a notice explains
YouTube may set cookies and offers "Play video" (this video only) or "Cookie settings".

## Adding a new video

Copy an existing embed block, set `data-ry-src` to
`https://www.youtube-nocookie.com/embed/<id>?rel=0&modestbranding=1&playsinline=1&autoplay=1`,
download the thumbnail `https://i.ytimg.com/vi_webp/<id>/hqdefault.webp` into `assets/media/`, and
never use a plain `src` on the iframe.

## Links

- Privacy-enhanced mode: https://support.google.com/youtube/answer/171780
- Privacy: https://policies.google.com/privacy
