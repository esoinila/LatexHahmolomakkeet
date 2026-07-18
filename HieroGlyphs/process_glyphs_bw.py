#!/usr/bin/env python3
"""
Process GenAI hieroglyph letters (from papyrus reference) into laser B/W glyphs.

Uses the same ink-sketch filter spirit as site emblems: artistic line work,
not solid geometric fills. Y→E and V→F aliases copy the processed masters.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent
COLOR_DIR = ROOT / "glyphs_color"
OUT_DIR = ROOT / "glyphs"
MANIFEST = ROOT / "glyphs_manifest.json"

# raw_N.jpg -> letter (from GenAI batch classification)
RAW_TO_LETTER = {
    22: "C",
    23: "A",
    24: "B",
    25: "F",
    26: "D",
    27: "E",
    28: "G",
    29: "L",
    30: "K",
    31: "H",
    32: "J",
    33: "I",
    34: "P",
    35: "O",
    36: "Q",
    37: "R",
    38: "M",
    39: "N",
    40: "X",
    41: "S",
    42: "U",
    43: "Z",
    44: "W",
    45: "T",
}

ALIASES = {"Y": "E", "V": "F"}


def ink_sketch_bw(im: Image.Image) -> Image.Image:
    rgb = im.convert("RGB")
    gray = ImageOps.grayscale(rgb)
    gray = ImageOps.autocontrast(gray, cutoff=0.5)
    gray = ImageEnhance.Contrast(gray).enhance(1.9)
    gray = ImageEnhance.Sharpness(gray).enhance(1.5)

    paper = gray.point(lambda p: 255 if p >= 205 else p)
    blurred = paper.filter(ImageFilter.GaussianBlur(radius=1.4))
    inv_blur = ImageOps.invert(blurred)
    dodge = ImageChops.screen(paper, inv_blur)
    dodge = ImageEnhance.Contrast(dodge).enhance(1.25)
    mixed = ImageChops.multiply(paper, dodge)
    mixed = ImageEnhance.Contrast(mixed).enhance(1.2)

    def tone(p: int) -> int:
        if p >= 220:
            return 255
        if p <= 35:
            return 0
        return max(0, min(255, int((p - 35) * 255 / 185)))

    out = mixed.point(tone)
    out = out.filter(ImageFilter.MedianFilter(size=3))
    out = ImageEnhance.Sharpness(out).enhance(1.15)
    return out.point(lambda p: 255 if p >= 235 else (0 if p <= 28 else p)).convert("L")


def tight_crop(im: Image.Image, pad_frac: float = 0.06) -> Image.Image:
    mask = im.point(lambda p: 255 if p < 245 else 0)
    mask = mask.filter(ImageFilter.MinFilter(3))
    mask = mask.filter(ImageFilter.MaxFilter(5))
    bbox = mask.getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    w, h = im.size
    pad = max(6, int(min(w, h) * pad_frac))
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(w, x1 + pad), min(h, y1 + pad)
    cropped = im.crop((x0, y0, x1, y1))
    side = max(cropped.size)
    canvas = Image.new("L", (side, side), 255)
    canvas.paste(cropped, ((side - cropped.width) // 2, (side - cropped.height) // 2))
    return canvas


def process_one(src: Path, dst: Path, size: int = 160) -> None:
    im = Image.open(src)
    bw = ink_sketch_bw(im)
    bw = tight_crop(bw)
    bw = bw.resize((size, size), Image.Resampling.LANCZOS)
    bw = bw.point(lambda p: 255 if p >= 230 else (0 if p <= 40 else p))
    bw.save(dst, optimize=True)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    named = COLOR_DIR / "named"
    named.mkdir(parents=True, exist_ok=True)

    manifest: dict = {"sources": {}, "aliases": ALIASES, "style": "genai_from_papyrus + ink_sketch_bw"}
    for n, letter in RAW_TO_LETTER.items():
        src = COLOR_DIR / f"raw_{n}.jpg"
        if not src.exists():
            print(f"MISSING {src}")
            continue
        shutil.copy2(src, named / f"{letter}.jpg")
        dst = OUT_DIR / f"{letter}.png"
        process_one(src, dst)
        manifest["sources"][letter] = {"raw": f"raw_{n}.jpg", "color": f"named/{letter}.jpg", "bw": f"{letter}.png"}
        print(f"  {letter} <- raw_{n}.jpg")

    # aliases: copy PNG
    for alias, target in ALIASES.items():
        src = OUT_DIR / f"{target}.png"
        if src.exists():
            shutil.copy2(src, OUT_DIR / f"{alias}.png")
            print(f"  {alias} -> {target}")

    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote glyphs to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
