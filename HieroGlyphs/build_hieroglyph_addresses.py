#!/usr/bin/env python3
"""
Build hieroglyph portal-address assets for tabletop use.

Outputs:
  - HieroGlyphs/glyphs/*.png          High-contrast B/W letter glyphs
  - HieroGlyphs/addresses/*.png       Composed address strips (LTR/RTL)
  - HieroGlyphs/tiles/*.png           Player tile images (icon + address)
  - HieroGlyphs/alphabet.json
  - HieroGlyphs/site_addresses.json
  - site_addresses_player.tex
  - site_addresses_gm.tex

Glyphs are clean drawn silhouettes matching the tourist papyrus shapes
(Alphabet_for_hieroglyph.jpg) — B/W laser-friendly, easy to match at the table.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
HIERO = ROOT / "HieroGlyphs"
GLYPH_DIR = HIERO / "glyphs"
ADDR_DIR = HIERO / "addresses"
TILE_DIR = HIERO / "tiles"
ICON_DIR = HIERO / "site_icons"  # new bold B/W place emblems

# Site list: id, full_name, address_code, direction
SITES = [
    ("abydos_osireion", "Osireion (Abydos)", "OSIREION", "LTR"),
    ("boat_pits", "Boat Pits", "BOATPITS", "RTL"),
    ("builders_quarters", "Builders' Quarters", "BUILDERS", "LTR"),
    ("dendera_temple", "Dendera Temple", "DENDERA", "RTL"),
    ("east_cemetery", "Eastern Cemetery", "EASTCEM", "LTR"),
    ("eridu_ruins", "Eridu Ruins", "ERIDU", "RTL"),
    ("giza_repository", "Underground Repository of Knowledge (Giza)", "LIBRARY", "LTR"),
    ("hetepheres_tombs", "Queen Hetepheres' Tombs", "HETEPH", "RTL"),
    ("inka_andes", "Inka Stone Door (Andes)", "ANDES", "LTR"),
    ("iran_ziggurat", "Ancient Ziggurat (Iran)", "ZIGGURAT", "RTL"),
    ("mars_face_mountain", "Face Mountain (Mars)", "MARS", "LTR"),
    ("ocean_giza_clone", "Sunken Giza Clone (Atlantic)", "OCEAN", "RTL"),
    ("office_pyramid_studies", "Office of Pyramid Studies", "OFFICE", "LTR"),
    ("queen_khentkawes", "Tomb of Queen Khentkawes", "KHENT", "RTL"),
    ("rock_cut_tombs_khafre", "Rock Cut Tombs (Khafre)", "ROCKCUT", "LTR"),
    ("saqqara_step_pyramid", "Step Pyramid Complex (Saqqara)", "SAQQARA", "RTL"),
    ("sphinx", "The Great Sphinx", "SPHINX", "LTR"),
    ("sphinx_shadow_chamber", "Sphinx's Shadow Chamber", "SHADOW", "RTL"),
    ("valley_khafre", "Valley Temple of Khafre", "VALLEYK", "LTR"),
    ("valley_queens", "Valley of the Queens", "QUEENS", "RTL"),
    ("western_cemetery", "Western Cemetery", "WESTCEM", "LTR"),
]

LETTER_ALIASES = {"Y": "E", "V": "F"}
SOURCE_LETTERS = list("ABCDEFGHIJKLMNOPQRSTUWXZ")

GLYPH_SIZE = 140
STRIP_HEIGHT = 92
# Compact cuttable cards: ~88×72 mm at print → 6 per A4 (2×3)
TILE_W, TILE_H = 500, 400


def ensure_dirs() -> None:
    for d in (GLYPH_DIR, ADDR_DIR, TILE_DIR, ICON_DIR):
        d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Clean B/W glyph drawings (tourist alphabet shapes from Egypt souvenir)
# Canvas is 0..100 coordinate space, mapped to GLYPH_SIZE.
# ---------------------------------------------------------------------------

def _canvas() -> tuple[Image.Image, ImageDraw.ImageDraw, float]:
    im = Image.new("L", (GLYPH_SIZE, GLYPH_SIZE), 255)
    d = ImageDraw.Draw(im)
    s = GLYPH_SIZE / 100.0
    return im, d, s


def _xy(s: float, x: float, y: float) -> tuple[float, float]:
    return x * s, y * s


def _poly(d: ImageDraw.ImageDraw, s: float, pts: list[tuple[float, float]], fill: int = 0) -> None:
    d.polygon([_xy(s, x, y) for x, y in pts], fill=fill)


def _ellipse(d: ImageDraw.ImageDraw, s: float, box: tuple[float, float, float, float], fill: int = 0) -> None:
    x0, y0, x1, y1 = box
    d.ellipse([*_xy(s, x0, y0), *_xy(s, x1, y1)], fill=fill)


def _line(d: ImageDraw.ImageDraw, s: float, pts: list[tuple[float, float]], width: float = 6) -> None:
    d.line([_xy(s, x, y) for x, y in pts], fill=0, width=max(2, int(width * s / 1.4)))


def _rect(d: ImageDraw.ImageDraw, s: float, box: tuple[float, float, float, float], fill: int = 0) -> None:
    x0, y0, x1, y1 = box
    d.rectangle([*_xy(s, x0, y0), *_xy(s, x1, y1)], fill=fill)


def _arc_line(d: ImageDraw.ImageDraw, s: float, box: tuple[float, float, float, float], start: float, end: float, width: float = 7) -> None:
    x0, y0, x1, y1 = box
    d.arc([*_xy(s, x0, y0), *_xy(s, x1, y1)], start=start, end=end, fill=0, width=max(2, int(width * s / 1.4)))


def draw_A(d, s):
    # Egyptian vulture — bird standing, head left-ish
    _ellipse(d, s, (32, 12, 68, 48))  # body
    _ellipse(d, s, (22, 8, 48, 34))  # head
    _poly(d, s, [(18, 18), (8, 22), (18, 26)])  # beak left
    _poly(d, s, [(40, 44), (30, 88), (42, 88), (48, 50)])  # leg
    _poly(d, s, [(50, 44), (52, 88), (64, 88), (58, 48)])  # leg
    _poly(d, s, [(55, 30), (88, 22), (88, 40), (58, 48)])  # wing
    _ellipse(d, s, (28, 16, 36, 24), fill=255)  # eye hole


def draw_B(d, s):
    # Foot / lower leg (side view)
    _poly(d, s, [
        (25, 30), (55, 28), (70, 35), (78, 48), (75, 58),
        (55, 62), (48, 78), (30, 80), (28, 62), (18, 55), (18, 40),
    ])
    _poly(d, s, [(48, 58), (90, 62), (90, 72), (48, 70)])  # sole forward


def draw_C(d, s):
    # Folded cloth / crook staff (tall hooked shape)
    _rect(d, s, (42, 10, 58, 85))
    _arc_line(d, s, (20, 8, 58, 40), 180, 0, width=12)
    _poly(d, s, [(20, 22), (20, 38), (32, 38), (32, 22)])


def draw_D(d, s):
    # Hand / forearm
    _poly(d, s, [
        (15, 45), (55, 35), (85, 42), (88, 55), (70, 62),
        (55, 58), (50, 72), (38, 72), (40, 58), (20, 60),
    ])
    # fingers
    for fx, fy in [(60, 28), (70, 30), (78, 34), (84, 40)]:
        _ellipse(d, s, (fx - 5, fy - 8, fx + 5, fy + 10))


def draw_E(d, s):
    # Flowering reed (vertical stem + triangular flag leaf) — papyrus E/Y
    _rect(d, s, (46, 28, 54, 90))
    _poly(d, s, [(50, 8), (22, 42), (50, 36)])
    _poly(d, s, [(50, 8), (78, 38), (50, 34)])


def draw_F(d, s):
    # Horned viper (horizontal snake)
    _poly(d, s, [
        (10, 48), (30, 40), (55, 42), (75, 38), (90, 45),
        (92, 55), (75, 58), (55, 55), (30, 58), (12, 55),
    ])
    _ellipse(d, s, (8, 42, 28, 60))  # head
    _line(d, s, [(18, 42), (12, 28)], width=5)
    _line(d, s, [(22, 42), (28, 28)], width=5)  # horns
    _ellipse(d, s, (12, 48, 18, 54), fill=255)


def draw_G(d, s):
    # Jar stand / pot stand (triangular stand with pot)
    _poly(d, s, [(20, 85), (50, 30), (80, 85)])
    _poly(d, s, [(35, 85), (50, 50), (65, 85)], fill=255)  # hollow
    _ellipse(d, s, (32, 18, 68, 48))  # jar
    _rect(d, s, (42, 12, 58, 22))


def draw_H(d, s):
    # Reed shelter / twisted plan (rectangular spiral-ish courtyard)
    _rect(d, s, (22, 18, 78, 82))
    _rect(d, s, (34, 30, 66, 70), fill=255)
    _rect(d, s, (34, 30, 50, 48))
    _rect(d, s, (42, 40, 58, 58), fill=255)


def draw_I(d, s):
    # Two reed leaves / diagonal strokes
    _line(d, s, [(30, 85), (42, 15)], width=11)
    _line(d, s, [(55, 85), (68, 15)], width=11)


def draw_J(d, s):
    # Cobra (rearing)
    _poly(d, s, [
        (55, 15), (70, 25), (72, 45), (60, 55), (58, 85),
        (42, 85), (40, 55), (28, 40), (30, 22), (45, 15),
    ])
    _ellipse(d, s, (48, 12, 68, 32))
    _ellipse(d, s, (54, 18, 60, 24), fill=255)


def draw_K(d, s):
    # Basket with handle (open bowl, no mesh) — distinct from X
    _arc_line(d, s, (18, 28, 82, 88), 0, 180, width=10)
    _line(d, s, [(18, 58), (82, 58)], width=6)
    _arc_line(d, s, (28, 12, 72, 58), 200, 340, width=7)


def draw_L(d, s):
    # Lion reclining
    _ellipse(d, s, (35, 30, 85, 70))  # body
    _ellipse(d, s, (15, 28, 45, 58))  # head/mane
    _poly(d, s, [(75, 50), (92, 42), (95, 55), (80, 58)])  # tail
    _rect(d, s, (40, 65, 50, 88))
    _rect(d, s, (60, 65, 70, 88))
    _ellipse(d, s, (22, 36, 30, 44), fill=255)


def draw_M(d, s):
    # Owl
    _ellipse(d, s, (28, 22, 72, 78))
    _poly(d, s, [(35, 75), (28, 92), (42, 88)])
    _poly(d, s, [(58, 75), (72, 92), (65, 88)])
    _ellipse(d, s, (34, 32, 50, 50))
    _ellipse(d, s, (50, 32, 66, 50))
    _ellipse(d, s, (38, 38, 46, 46), fill=255)
    _ellipse(d, s, (54, 38, 62, 46), fill=255)
    _poly(d, s, [(48, 50), (42, 60), (58, 60)])  # beak
    _poly(d, s, [(25, 40), (15, 55), (28, 58)])  # wing hint
    _poly(d, s, [(75, 40), (85, 55), (72, 58)])


def draw_N(d, s):
    # Water ripple (zigzag)
    pts = []
    for i in range(7):
        x = 12 + i * 12
        y = 40 if i % 2 == 0 else 62
        pts.append((x, y))
    _line(d, s, pts, width=10)
    # second ripple
    pts2 = [(x, y + 12) for x, y in pts]
    _line(d, s, pts2, width=8)


def draw_O(d, s):
    # Lasso / rope loop with tail
    _arc_line(d, s, (25, 12, 75, 62), 0, 360, width=9)
    _poly(d, s, [(55, 55), (70, 90), (58, 92), (48, 62)])


def draw_P(d, s):
    # Stool / reed mat (rectangle with bars)
    _rect(d, s, (28, 18, 72, 85))
    for y in (35, 50, 65):
        _line(d, s, [(32, y), (68, y)], width=4)
    _rect(d, s, (36, 26, 64, 78), fill=255)
    _rect(d, s, (40, 30, 60, 74))


def draw_Q(d, s):
    # Hill slope
    _poly(d, s, [(15, 80), (55, 18), (85, 80)])
    _poly(d, s, [(30, 80), (55, 40), (75, 80)], fill=255)
    _line(d, s, [(15, 80), (85, 80)], width=6)


def draw_R(d, s):
    # Mouth
    _ellipse(d, s, (15, 30, 85, 70))
    _ellipse(d, s, (28, 40, 72, 60), fill=255)
    _line(d, s, [(30, 50), (70, 50)], width=4)


def draw_S(d, s):
    # Door bolt / folded cloth (like a latch / H with bar)
    _rect(d, s, (18, 40, 82, 60))
    _rect(d, s, (28, 28, 42, 72))
    _rect(d, s, (58, 28, 72, 72))


def draw_T(d, s):
    # Bread loaf (solid dome / half-circle on baseline)
    _ellipse(d, s, (18, 30, 82, 92))
    _rect(d, s, (18, 30, 82, 55), fill=255)
    _line(d, s, [(18, 55), (82, 55)], width=7)
    # tiny top bumps to look like loaf, not sieve
    _ellipse(d, s, (30, 42, 42, 55))
    _ellipse(d, s, (44, 38, 56, 55))
    _ellipse(d, s, (58, 42, 70, 55))


def draw_U(d, s):
    # Quail spiral / lasso curl
    _arc_line(d, s, (25, 15, 75, 65), -40, 220, width=10)
    _arc_line(d, s, (38, 28, 62, 52), 0, 360, width=7)
    _poly(d, s, [(55, 55), (72, 88), (60, 90), (48, 60)])


def draw_W(d, s):
    # Quail chick (standing chick)
    _ellipse(d, s, (30, 28, 72, 72))
    _ellipse(d, s, (40, 12, 68, 40))
    _poly(d, s, [(38, 22), (22, 18), (36, 30)])  # beak
    _rect(d, s, (40, 68, 48, 90))
    _rect(d, s, (55, 68, 63, 90))
    _ellipse(d, s, (50, 20, 58, 28), fill=255)
    _poly(d, s, [(65, 40), (88, 32), (88, 48), (68, 50)])  # wing


def draw_X(d, s):
    # Sieve / basket with cross-hatch mesh (papyrus X) — outline + mesh, not solid
    # Outer bowl outline (thick stroke via concentric ellipses)
    _ellipse(d, s, (16, 36, 84, 90))
    _ellipse(d, s, (22, 42, 78, 84), fill=255)
    _line(d, s, [(16, 48), (84, 48)], width=6)
    # Cross-hatch mesh (white interior already)
    for i in range(5):
        x = 28 + i * 11
        _line(d, s, [(x, 50), (x, 82)], width=4)
    for j in range(4):
        y = 54 + j * 8
        _line(d, s, [(26, y), (74, y)], width=4)


def draw_Z(d, s):
    # Door bolt (horizontal bar with ends)
    _rect(d, s, (12, 42, 88, 58))
    _ellipse(d, s, (8, 35, 28, 65))
    _ellipse(d, s, (72, 35, 92, 65))
    _ellipse(d, s, (40, 38, 60, 62))
    _ellipse(d, s, (45, 43, 55, 57), fill=255)


DRAWERS = {
    "A": draw_A, "B": draw_B, "C": draw_C, "D": draw_D, "E": draw_E,
    "F": draw_F, "G": draw_G, "H": draw_H, "I": draw_I, "J": draw_J,
    "K": draw_K, "L": draw_L, "M": draw_M, "N": draw_N, "O": draw_O,
    "P": draw_P, "Q": draw_Q, "R": draw_R, "S": draw_S, "T": draw_T,
    "U": draw_U, "W": draw_W, "X": draw_X, "Z": draw_Z,
}


def build_glyphs() -> None:
    for letter, drawer in DRAWERS.items():
        im, d, s = _canvas()
        drawer(d, s)
        # Thicken for laser: slight max-filter on ink
        inv = ImageOps.invert(im)
        inv = inv.filter(ImageFilter.MaxFilter(3))
        im = ImageOps.invert(inv)
        im = im.point(lambda p: 0 if p < 128 else 255)
        im.save(GLYPH_DIR / f"{letter}.png")


def load_glyph(letter: str) -> Image.Image:
    key = LETTER_ALIASES.get(letter.upper(), letter.upper())
    path = GLYPH_DIR / f"{key}.png"
    if not path.exists():
        raise FileNotFoundError(f"Missing glyph for {letter} ({path})")
    return Image.open(path).convert("L")


def facing_figure(direction: str, height: int) -> Image.Image:
    """Bird silhouette facing the start of reading."""
    h = height
    w = int(h * 0.7)
    im = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(im)
    # body + head + beak pointing left (LTR start)
    d.ellipse([w * 0.25, h * 0.28, w * 0.85, h * 0.78], fill=0)
    d.ellipse([w * 0.12, h * 0.12, w * 0.55, h * 0.48], fill=0)
    d.polygon([(2, h * 0.28), (w * 0.28, h * 0.18), (w * 0.28, h * 0.38)], fill=0)
    d.polygon([(w * 0.45, h * 0.72), (w * 0.35, h * 0.95), (w * 0.52, h * 0.95)], fill=0)
    d.polygon([(w * 0.62, h * 0.72), (w * 0.58, h * 0.95), (w * 0.72, h * 0.95)], fill=0)
    d.ellipse([w * 0.28, h * 0.22, w * 0.40, h * 0.34], fill=255)
    if direction == "RTL":
        im = ImageOps.mirror(im)
    return im


def compose_address(address: str, direction: str) -> Image.Image:
    letters = [c for c in address.upper() if c.isalpha()]
    if direction == "RTL":
        letters = list(reversed(letters))

    face = facing_figure(direction, STRIP_HEIGHT - 8)
    gap = 5
    glyph_h = STRIP_HEIGHT - 12

    scaled: list[Image.Image] = []
    for c in letters:
        g = load_glyph(c)
        scale = glyph_h / g.height
        ng = g.resize((max(1, int(g.width * scale)), glyph_h), Image.Resampling.LANCZOS)
        ng = ng.point(lambda p: 0 if p < 140 else 255)
        scaled.append(ng)

    content_w = face.width + 10 + sum(g.width for g in scaled) + gap * max(0, len(scaled) - 1) + 20
    canvas = Image.new("L", (content_w, STRIP_HEIGHT), 255)
    draw = ImageDraw.Draw(canvas)

    def paste_glyphs(x0: int) -> int:
        x = x0
        for g in scaled:
            canvas.paste(g, (x, (STRIP_HEIGHT - g.height) // 2))
            x += g.width + gap
        return x

    if direction == "LTR":
        x = 6
        canvas.paste(face, (x, (STRIP_HEIGHT - face.height) // 2))
        x += face.width + 6
        draw.rectangle([x, 10, x + 2, STRIP_HEIGHT - 10], fill=0)
        x += 8
        paste_glyphs(x)
    else:
        x = 6
        x = paste_glyphs(x)
        draw.rectangle([x, 10, x + 2, STRIP_HEIGHT - 10], fill=0)
        x += 8
        canvas.paste(face, (x, (STRIP_HEIGHT - face.height) // 2))

    bbox = ImageOps.invert(canvas).getbbox()
    if bbox:
        canvas = canvas.crop((max(0, bbox[0] - 4), 0, min(canvas.width, bbox[2] + 4), canvas.height))
    return canvas


def load_site_icon(site_id: str, max_side: int = 360) -> Image.Image:
    """Load GenAI→B/W place emblem (line art / hatch, not solid fill)."""
    path = ICON_DIR / f"symbol_{site_id}.png"
    if not path.exists():
        print(f"  WARN missing icon {path}")
        return Image.new("L", (max_side, max_side), 255)
    im = Image.open(path).convert("L")
    w, h = im.size
    scale = min(max_side / w, max_side / h)
    im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
    # keep mid-grays for hatching (laser still prints them as toner)
    return im


def build_player_tile(icon: Image.Image, strip: Image.Image) -> Image.Image:
    """Card: large place emblem (fills most of the box) + hieroglyph address. No Latin."""
    card = Image.new("L", (TILE_W, TILE_H), 255)
    d = ImageDraw.Draw(card)
    m = 8
    d.rectangle([m, m, TILE_W - m - 1, TILE_H - m - 1], outline=0, width=4)
    d.rectangle([m + 5, m + 5, TILE_W - m - 6, TILE_H - m - 6], outline=0, width=1)

    # Icon: upper ~72% — fill almost the whole emblem box (minimal padding)
    icon_top = m + 8
    icon_area_h = int(TILE_H * 0.72)
    max_icon_w = TILE_W - 2 * m - 12
    max_icon_h = icon_area_h - 2
    ic = icon.copy()
    iw, ih = ic.size
    scale = min(max_icon_w / iw, max_icon_h / ih)
    # Prefer filling the box; allow slight upscale of source icons
    ic = ic.resize((max(1, int(iw * scale)), max(1, int(ih * scale))), Image.Resampling.LANCZOS)
    ix = (TILE_W - ic.width) // 2
    iy = icon_top + (icon_area_h - ic.height) // 2
    card.paste(ic, (ix, iy))

    div_y = icon_top + icon_area_h
    d.line([(m + 14, div_y), (TILE_W - m - 14, div_y)], fill=0, width=2)

    # Address strip in lower band
    max_strip_w = TILE_W - 2 * m - 16
    max_strip_h = TILE_H - div_y - m - 10
    s = strip
    scale_w = max_strip_w / s.width if s.width else 1.0
    scale_h = max_strip_h / s.height if s.height else 1.0
    scale = min(scale_w, scale_h)
    if abs(scale - 1.0) > 0.01:
        s = s.resize(
            (max(1, int(s.width * scale)), max(1, int(s.height * scale))),
            Image.Resampling.LANCZOS,
        )
        s = s.point(lambda p: 0 if p < 140 else 255)
    sx = (TILE_W - s.width) // 2
    sy = div_y + max(4, (TILE_H - m - 6 - div_y - s.height) // 2)
    card.paste(s, (sx, sy))
    return card


def write_site_json() -> None:
    data = {
        "cipher_notes": {
            "source": "Alphabet_for_hieroglyph.jpg (Egypt tourist papyrus)",
            "aliases": LETTER_ALIASES,
            "direction_rule": (
                "Figures face the beginning of the text. "
                "LTR: bird faces left. RTL: bird faces right; glyph order is reversed on the tile."
            ),
            "spaces": "Omitted from addresses.",
        },
        "sites": [
            {
                "id": sid,
                "full_name": name,
                "address": addr,
                "direction": direction,
                "icon": f"HieroGlyphs/site_icons/symbol_{sid}.png",
            }
            for sid, name, addr, direction in SITES
        ],
    }
    (HIERO / "site_addresses.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_alphabet_json() -> None:
    data = {
        "glyphs": {L: f"glyphs/{L}.png" for L in SOURCE_LETTERS},
        "aliases": LETTER_ALIASES,
        "style": "clean B/W silhouettes matching tourist papyrus shapes",
        "source_reference": "Alphabet_for_hieroglyph.jpg",
    }
    (HIERO / "alphabet.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_reference_alphabet_sheet() -> None:
    """Printable key matching the souvenir layout (compact for one A4 page with rules)."""
    cols, rows = 3, 8
    order = [
        list("ABC"), list("DEF"), list("GHI"), list("JKL"),
        list("MNO"), list("PQR"), list("STU"), list("WXZ"),
    ]
    cell = 96
    pad = 12
    sheet_w = cols * cell + pad * 2
    sheet_h = rows * cell + pad * 2 + 28
    sheet = Image.new("L", (sheet_w, sheet_h), 255)
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 18)
        font_sm = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 12)
    except OSError:
        font = ImageFont.load_default()
        font_sm = font
    d.text((pad, 6), "HIEROGLYPHIC ALPHABET (game key)", fill=0, font=font_sm)
    for r, row in enumerate(order):
        for c, letter in enumerate(row):
            x0 = pad + c * cell
            y0 = pad + 20 + r * cell
            d.rectangle([x0, y0, x0 + cell - 4, y0 + cell - 4], outline=0, width=2)
            g = load_glyph(letter)
            g = g.resize((56, 56), Image.Resampling.LANCZOS)
            g = g.point(lambda p: 0 if p < 140 else 255)
            sheet.paste(g, (x0 + 6, y0 + 24))
            d.text((x0 + cell - 30, y0 + 6), letter, fill=0, font=font)
            if letter == "E":
                d.text((x0 + cell - 30, y0 + 24), "Y", fill=0, font=font_sm)
            if letter == "F":
                d.text((x0 + cell - 30, y0 + 24), "V", fill=0, font=font_sm)
    sheet.save(HIERO / "alphabet_print_key.png")


def write_tex_files() -> None:
    player = r"""\documentclass[a4paper]{article}
\usepackage[margin=7mm,top=8mm,bottom=7mm]{geometry}
\usepackage{graphicx}
\usepackage{xcolor}
\definecolor{cutgray}{gray}{0.35}
\usepackage{tikz}
\usepackage{array}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\setlength{\tabcolsep}{1.2mm}
\renewcommand{\arraystretch}{1.0}

% Fixed grid: 2 x 3 cards per page for easy scissors cutting
\newcommand{\cardw}{94mm}
\newcommand{\cardh}{74mm}

% Draw cut frame around a pre-sized includegraphics
\newcommand{\portaltile}[1]{%
  \begin{tikzpicture}
    \node[inner sep=0pt, outer sep=0pt] (card) at (0,0)
      {\includegraphics[width=\cardw, height=\cardh, keepaspectratio=false]{#1}};
    \draw[cutgray, dashed, line width=0.7pt]
      (card.south west) rectangle (card.north east);
    \draw[black, line width=0.9pt]
      (card.south west) -- ++(0,3.2mm)
      (card.south west) -- ++(3.2mm,0)
      (card.south east) -- ++(0,3.2mm)
      (card.south east) -- ++(-3.2mm,0)
      (card.north west) -- ++(0,-3.2mm)
      (card.north west) -- ++(3.2mm,0)
      (card.north east) -- ++(0,-3.2mm)
      (card.north east) -- ++(-3.2mm,0);
  \end{tikzpicture}%
}

\begin{document}
"""
    pages: list[list[tuple]] = []
    page: list = []
    for site in SITES:
        page.append(site)
        if len(page) == 6:
            pages.append(page)
            page = []
    if page:
        pages.append(page)

    for pi, page_sites in enumerate(pages):
        if pi == 0:
            player += r"""\centering
{\large\bfseries Portal Address Tiles}\\[0.3mm]
{\footnotesize Hieroglyphs only. Bird faces the \emph{start} of the address. Cut on dashed lines. B/W laser OK.}\\[1.2mm]
"""
        else:
            player += "\\centering\n"

        player += "\\begin{tabular}{@{}c@{\\hspace{2mm}}c@{}}\n"
        for i, (sid, name, addr, direction) in enumerate(page_sites):
            tile_path = f"HieroGlyphs/tiles/{sid}.png"
            player += f"% {name} / {addr} / {direction}\n"
            player += f"\\portaltile{{{tile_path}}}"
            if i % 2 == 0 and i + 1 < len(page_sites):
                player += " &\n"
            elif i % 2 == 1 and i + 1 < len(page_sites):
                player += " \\\\[1.0mm]\n"
            else:
                if i % 2 == 0:
                    player += " & \\\\\n"
                else:
                    player += " \\\\\n"
        player += "\\end{tabular}\n"
        if pi < len(pages) - 1:
            player += "\\newpage\n"

    player += r"""
\newpage
\centering
{\Large\bfseries Reading guide (players)}\\[1.5mm]
\includegraphics[height=0.72\textheight,keepaspectratio]{HieroGlyphs/alphabet_print_key.png}\\[2mm]
\begin{minipage}{0.92\textwidth}
\small
\begin{itemize}
  \item The \textbf{bird faces the beginning} of the address line.
  \item Bird faces \textbf{left} $\Rightarrow$ read \textbf{left-to-right}.
  \item Bird faces \textbf{right} $\Rightarrow$ read \textbf{right-to-left}
        (glyphs are already ordered for that direction --- start at the bird and read along the line).
  \item Match each symbol to this key \textbf{or} your wood papyrus from Egypt.
  \item Shared souvenir cells: \textbf{Y} uses \textbf{E}; \textbf{V} uses \textbf{F}.
\end{itemize}
\end{minipage}
\end{document}
"""

    gm = r"""\documentclass[a4paper,9pt]{article}
\usepackage[margin=8mm]{geometry}
\usepackage{graphicx}
\usepackage{longtable}
\usepackage{array}
\usepackage{booktabs}
\pagestyle{plain}
\setlength{\parindent}{0pt}

\begin{document}
\begin{center}
{\Large\bfseries GM Portal Address Key --- KEEP SECRET}\\[1mm]
{\small Latin names for the GM. Glyph strips match the player tiles.}
\end{center}
\vspace{1.5mm}

{\small
\textbf{Cipher:} Tourist papyrus A--Z (\texttt{HieroGlyphs/Alphabet\_for\_hieroglyph.jpg} / print key).
Aliases: Y$\rightarrow$E, V$\rightarrow$F.
Direction: bird faces the start. LTR = left-to-right; RTL = right-to-left (glyphs reversed on tile).
}

\vspace{1.5mm}
\renewcommand{\arraystretch}{1.15}
\begin{longtable}{@{}>{\centering\arraybackslash}p{2.4cm}>{\centering\arraybackslash}p{6.6cm}p{1.9cm}c p{5.0cm}@{}}
\toprule
\textbf{Tile} & \textbf{Address glyphs} & \textbf{Code} & \textbf{Dir} & \textbf{Site} \\
\midrule
\endfirsthead
\toprule
\textbf{Tile} & \textbf{Address glyphs} & \textbf{Code} & \textbf{Dir} & \textbf{Site} \\
\midrule
\endhead
"""
    for sid, name, addr, direction in SITES:
        gm += (
            f"\\includegraphics[width=2.2cm]{{HieroGlyphs/tiles/{sid}.png}}"
            f" & \\includegraphics[height=0.78cm]{{HieroGlyphs/addresses/{sid}.png}}"
            f" & \\texttt{{{addr}}} & {direction} & {name} \\\\\n"
            "\\midrule\n"
        )
    gm += r"""
\end{longtable}

\vspace{1mm}
\section*{Quick lookup}
\begin{tabular}{@{}ll@{\hspace{12mm}}ll@{}}
"""
    half = (len(SITES) + 1) // 2
    left, right = SITES[:half], SITES[half:]
    for i in range(half):
        a = left[i]
        line = f"\\texttt{{{a[2]}}} & {a[1]}"
        if i < len(right):
            b = right[i]
            line += f" & \\texttt{{{b[2]}}} & {b[1]}"
        gm += line + " \\\\\n"
    gm += r"""
\end{tabular}

\vspace{4mm}
{\footnotesize Built by \texttt{HieroGlyphs/build\_hieroglyph\_addresses.py} from \texttt{site\_addresses.json}.}
\end{document}
"""

    (ROOT / "site_addresses_player.tex").write_text(player, encoding="utf-8")
    (ROOT / "site_addresses_gm.tex").write_text(gm, encoding="utf-8")


def main() -> int:
    ensure_dirs()

    print("Processing GenAI place emblems → laser B/W (line art)...")
    sys.path.insert(0, str(HIERO))
    from process_icons_bw import main as process_icons_main  # noqa: E402

    process_icons_main()

    print("Drawing clean B/W glyphs (papyrus-matched shapes)...")
    build_glyphs()
    write_alphabet_json()
    write_site_json()
    write_reference_alphabet_sheet()

    print("Composing addresses and tiles...")
    for sid, name, addr, direction in SITES:
        strip = compose_address(addr, direction)
        strip.save(ADDR_DIR / f"{sid}.png")
        bw_icon = load_site_icon(sid, max_side=380)
        tile = build_player_tile(bw_icon, strip)
        tile.save(TILE_DIR / f"{sid}.png")
        print(f"  {sid}: {addr} ({direction})")

    print("Writing LaTeX...")
    write_tex_files()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
