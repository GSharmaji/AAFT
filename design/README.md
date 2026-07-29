# Post designs

Coded social graphics (1080×1350, 4:5 — great for both LinkedIn and Instagram),
rendered from a locked brand template so all posts share one identity and the
headline text is always pixel-crisp (never AI-misspelled).

- **Type:** Anton (display), Archivo Black (wordmark), Poppins (body)
- **Signature accent:** electric lime `#C8FF00`
- **Themes:** `ink` (dark), `cream` (light), `lime` (punch) — assigned per post
  for grid rhythm.

The rendered PNGs live in `../assets/` and are referenced by `content/posts.yaml`,
so the scheduler posts each caption together with its graphic.

## Regenerate

```bash
bash design/install-fonts.sh          # one time — installs display fonts
npm i -g playwright                    # if not already available
NODE_PATH="$(npm root -g)" node design/build.js        # all posts -> design/out/
NODE_PATH="$(npm root -g)" node design/build.js 3      # just post #3 (preview)
cp design/out/post-*.png assets/       # publish to what the scheduler posts
```

## Editing content

Headline / kicker / sub / theme for each graphic live in the `POSTS` array in
`build.js`. Wrap the word you want highlighted in `<mark>…</mark>`. The headline
auto-shrinks to fit, so you don't have to hand-tune sizes.

## Why system fonts, not @font-face

The bundled Chromium in this environment cannot rasterize `@font-face` web fonts
(it reports them "loaded" but paints a serif fallback) and rejects *subset*
TTFs. So the template references fonts by their **system family name**, and
`install-fonts.sh` installs the **full** TTFs (in `design/fonts/`) into the
font path where fontconfig — and therefore Chromium — will find them.
