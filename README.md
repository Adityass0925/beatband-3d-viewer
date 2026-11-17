# BeatBand V1 – interactive 3D model

A single-page viewer for the BeatBand V1 concept design. Visitors can drag to rotate the band, scroll or pinch to zoom, switch between Charcoal and Heather grey, and turn the part labels on or off.

It is a fully static site: `index.html` plus a local copy of three.js r160 in `lib/`. There is no build step, and the only outside request is for Google Fonts.

## Run it locally

```bash
python serve.py
```

This opens http://localhost:8765. Any static file server pointed at this folder also works. Opening `index.html` directly from disk will not work, because browsers block ES modules on `file://`.

## Put it live on a BeatBand subdomain

1. Deploy this repo as a static site with no build command and `/` as the output folder. Cloudflare Pages, Netlify and Vercel all work with a private repo. GitHub Pages works only if the repo is public, or on a paid plan.
2. Add the subdomain you want (for example `3d.beatband.in`) in the host's custom-domain settings.
3. At the DNS provider for `beatband.in`, add the `CNAME` record the host gives you (for example `3d` → `your-project.pages.dev`).
4. Update the "Open interactive 3D model" link on slide 8 of the pitch deck to the new URL.

## Files

| Path | What it is |
| --- | --- |
| `index.html` | The viewer: page, styles and the procedural 3D model |
| `lib/` | three.js r160 and the three add-ons used (OrbitControls, RoomEnvironment, CSS2DRenderer), MIT licence |
| `serve.py` | Small local server for previewing (not needed on a host) |
