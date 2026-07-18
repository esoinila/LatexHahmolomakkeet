#!/usr/bin/env python3
"""
Post-process GenAI parchment woodcut emblems into laser-friendly B/W art.

Preserves line work and hatching (not solid Duplo fills). Parchment becomes
pure white; ink becomes high-contrast black/gray suitable for B/W laser.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent
COLOR_DIR = ROOT / "site_icons_color"
OUT_DIR = ROOT / "site_icons"
MANIFEST = ROOT / "site_icons_manifest.json"

# gen_N.jpg -> site id (classified from GenAI batch)
GEN_TO_SITE = {
    1: "boat_pits",
    2: "sphinx",
    3: "abydos_osireion",
    4: "dendera_temple",
    5: "builders_quarters",
    6: "iran_ziggurat",
    7: "giza_repository",
    8: "hetepheres_tombs",
    9: "east_cemetery",
    10: "inka_andes",
    11: "eridu_ruins",
    12: "ocean_giza_clone",
    13: "office_pyramid_studies",
    14: "saqqara_step_pyramid",
    15: "rock_cut_tombs_khafre",
    16: "queen_khentkawes",
    17: "mars_face_mountain",
    18: "valley_queens",
    19: "valley_khafre",
    20: "sphinx_shadow_chamber",
    21: "western_cemetery",
}


def ink_sketch_bw(im: Image.Image) -> Image.Image:
    """
    Woodcut-on-parchment → high-contrast B/W line art for laser.

    Strategy:
    1. Grayscale + contrast (separate brown ink from cream paper)
    2. Soft paper wipe (near-white → pure white)
    3. Color-dodge sketch pass to emphasize edges/hatching
    4. Multiply with darkened original so fills aren't pure black blobs
    5. Final gentle threshold only on the lightest paper, keep mid gray lines
    """
    rgb = im.convert("RGB")
    # Slight desaturation emphasis on darkness of brown ink
    gray = ImageOps.grayscale(rgb)
    gray = ImageOps.autocontrast(gray, cutoff=0.5)
    gray = ImageEnhance.Contrast(gray).enhance(1.85)
    gray = ImageEnhance.Sharpness(gray).enhance(1.4)

    # Paper wipe: parchment to white
    paper_clean = gray.point(lambda p: 255 if p >= 210 else p)

    # Sketch / line emphasis (photocopy-ish)
    blurred = paper_clean.filter(ImageFilter.GaussianBlur(radius=1.6))
    inv_blur = ImageOps.invert(blurred)
    # Color dodge: base / (255 - blend)
    dodge = ImageChops.screen(paper_clean, inv_blur)
    dodge = ImageEnhance.Contrast(dodge).enhance(1.3)

    # Weighted blend: keep structure from original, lines from dodge
    # darker = more ink
    mixed = ImageChops.multiply(paper_clean, dodge)
    mixed = ImageEnhance.Contrast(mixed).enhance(1.25)

    # Ensure true white background, pure-ish black ink; keep mid grays for hatch
    def tone(p: int) -> int:
        if p >= 225:
            return 255
        if p <= 40:
            return 0
        # compress midtones toward ink slightly for laser punch
        return max(0, min(255, int((p - 40) * 255 / 185)))

    out = mixed.point(tone)
    # Optional light despeckle without destroying hatch
    out = out.filter(ImageFilter.MedianFilter(size=3))
    # Re-sharpen lines
    out = ImageEnhance.Sharpness(out).enhance(1.2)
    out = out.point(lambda p: 255 if p >= 240 else (0 if p <= 30 else p))
    return out.convert("L")


def tight_crop(im: Image.Image, pad_frac: float = 0.02) -> Image.Image:
    """Crop to main ink mass; ignore dust speckles so emblems fill tiles."""
    # Binary ink mask
    mask = im.point(lambda p: 255 if p < 245 else 0)
    # Kill isolated speckles (open = erode then dilate)
    mask = mask.filter(ImageFilter.MinFilter(3))
    mask = mask.filter(ImageFilter.MaxFilter(5))
    mask = mask.filter(ImageFilter.MaxFilter(3))
    bbox = mask.getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    w, h = im.size
    # Ignore bbox if it's basically the full frame with one corner speck
    content_w, content_h = x1 - x0, y1 - y0
    if content_w * content_h < (w * h * 0.02):
        return im
    pad = max(4, int(min(w, h) * pad_frac))
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(w, x1 + pad)
    y1 = min(h, y1 + pad)
    cropped = im.crop((x0, y0, x1, y1))
    # Light square pad only if nearly square; else keep aspect for larger fill
    cw, ch = cropped.size
    if abs(cw - ch) / max(cw, ch) < 0.12:
        side = max(cw, ch)
        canvas = Image.new("L", (side, side), 255)
        canvas.paste(cropped, ((side - cw) // 2, (side - ch) // 2))
        return canvas
    return cropped


def process_one(src: Path, dst: Path, size: int = 512) -> None:
    im = Image.open(src)
    bw = ink_sketch_bw(im)
    bw = tight_crop(bw, pad_frac=0.025)
    bw = bw.resize((size, size), Image.Resampling.LANCZOS)
    # re-threshold after resize softens ink
    bw = bw.point(lambda p: 255 if p >= 235 else (0 if p <= 45 else p))
    bw.save(dst, optimize=True)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # also keep named color masters
    color_named = COLOR_DIR / "named"
    color_named.mkdir(parents=True, exist_ok=True)

    manifest = {"sources": {}, "filter": "ink_sketch_bw + tight_crop"}
    for n, site_id in GEN_TO_SITE.items():
        src = COLOR_DIR / f"gen_{n}.jpg"
        if not src.exists():
            print(f"MISSING {src}")
            continue
        named = color_named / f"symbol_{site_id}.jpg"
        shutil.copy2(src, named)
        dst = OUT_DIR / f"symbol_{site_id}.png"
        process_one(src, dst)
        manifest["sources"][site_id] = {
            "color": str(named.relative_to(ROOT)),
            "bw": str(dst.relative_to(ROOT)),
            "gen": f"gen_{n}.jpg",
        }
        print(f"  {site_id} <- gen_{n}.jpg")

    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {len(manifest['sources'])} icons to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
