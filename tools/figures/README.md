# Documentation figures

The home-page animation and the ORM 2 diagrams are generated from Python so that
they stay consistent, theme-aware and reviewable as text.

| File | Produces |
|---|---|
| `svgkit.py` | deterministic SVG building blocks, theme tokens, glyphs |
| `orm_diagrams.py` | `docs/assets/orm-d1…d7*.svg` |
| `hero.py` | the storyboard for `docs/assets/hero.svg` (animated) and the GIF frames |
| `build.py` | writes the files; `--check` reports stale ones; `--gif` rasterizes the GIF |

```sh
python tools/figures/build.py            # regenerate every SVG
python tools/figures/build.py --check    # exit 1 if a committed SVG is stale
python tools/figures/build.py --gif      # also rasterize docs/assets/hero.gif
```

`tests/test_figures.py` checks that every committed SVG equals its regenerated text,
so edit the generator rather than the SVG.

## Theming

Each SVG carries its own light and dark colour tokens under a zero-specificity
`:where(#id)` rule, used when it is displayed as an image (GitHub follows the operating
system's colour scheme). The site inlines the SVGs with a snippet include inside a raw
`<figure>` or `<div>` without a `markdown` attribute, and `docs/assets/styles.css`
overrides the same tokens per site scheme, so the theme toggle wins. Animations stop
under `prefers-reduced-motion`; the SVG is authored in its final state, which is then
what a reader sees.

## The GIF

`hero.gif` is a light-theme raster of the same storyboard for places that cannot show
an animated SVG, such as social posts. Its bytes depend on local fonts and on the
librsvg and ffmpeg versions, so it is not regenerated in tests. Regenerate it only when
the storyboard changes. It was last generated with librsvg 2.62.3 and ffmpeg 8.1 on
macOS: 800×500, 12 fps, 18 s loop, 64 colours, undithered.
