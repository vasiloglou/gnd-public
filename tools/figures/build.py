"""Regenerate the documentation figures.

    python tools/figures/build.py            # write every SVG into docs/assets
    python tools/figures/build.py --check    # exit 1 if a committed SVG is stale
    python tools/figures/build.py --gif      # also rasterize docs/assets/hero.gif

The GIF needs ``rsvg-convert`` (librsvg) and ``ffmpeg`` on PATH. Rasterized
bytes depend on the local fonts and tool versions, so only the SVGs are
checked for exact regeneration; see README.md for the GIF's provenance.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import hero
import orm_diagrams
from svgkit import LIGHT, bake

ASSETS = HERE.parents[1] / "docs" / "assets"


def figures() -> dict[str, str]:
    out = {name: build() for name, build in orm_diagrams.FIGURES.items()}
    out["hero.svg"] = hero.animated_svg()
    return out


def write_gif(target: Path) -> None:
    for tool in ("rsvg-convert", "ffmpeg"):
        if shutil.which(tool) is None:
            raise SystemExit(f"{tool} is required for --gif")
    with tempfile.TemporaryDirectory(prefix="gnd-hero-") as directory:
        work = Path(directory)
        rendered: dict[str, Path] = {}
        listing: list[str] = []
        count = int(hero.CYCLE * hero.FPS)
        for index in range(count):
            svg = bake(hero.frame_svg(index / hero.FPS), LIGHT)
            key = hashlib.sha256(svg.encode()).hexdigest()[:16]
            if key not in rendered:
                source = work / f"{key}.svg"
                source.write_text(svg, encoding="utf-8")
                png = work / f"{key}.png"
                subprocess.run(["rsvg-convert", "-b", "#fafaf6", "-w", str(hero.WIDTH * 2), "-h", str(hero.HEIGHT * 2),
                                str(source), "-o", str(png)], check=True)
                rendered[key] = png
            listing.append(f"file '{rendered[key]}'\nduration {1 / hero.FPS:.6f}")
        listing.append(f"file '{rendered[key]}'")
        frames = work / "frames.txt"
        frames.write_text("\n".join(listing) + "\n", encoding="utf-8")
        palette = work / "palette.png"
        scale = f"fps={hero.FPS},scale={hero.WIDTH}:-1:flags=lanczos"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(frames),
                        "-vf", f"{scale},palettegen=max_colors=64:stats_mode=full:reserve_transparent=0", str(palette)], check=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(frames),
                        "-i", str(palette), "-lavfi",
                        f"{scale}[x];[x][1:v]paletteuse=dither=none:diff_mode=rectangle",
                        "-loop", "0", str(target)], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="compare instead of writing")
    parser.add_argument("--gif", action="store_true", help="also write docs/assets/hero.gif")
    args = parser.parse_args()
    stale = []
    for name, content in figures().items():
        target = ASSETS / name
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                stale.append(name)
            continue
        target.write_text(content, encoding="utf-8")
        print(f"wrote {target.relative_to(ASSETS.parents[1])}")
    if args.gif and not args.check:
        write_gif(ASSETS / "hero.gif")
        print("wrote docs/assets/hero.gif")
    if stale:
        print("stale figures: " + ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
