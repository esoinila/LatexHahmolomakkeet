#!/usr/bin/env python3
"""
Build Aziz Travel Agency hieroglyph decipher key cards (B/W laser).

Three large keys (one per A4 page) — readable at the table, not the real papyrus.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
HIERO = ROOT / "HieroGlyphs"
GLYPH_DIR = HIERO / "glyphs"
BRAND_DIR = HIERO / "brand"
OUT_CARD = BRAND_DIR / "decipher_key_card.png"
AZIZ_SRC = ROOT / "images" / "Aziz.jpg"

# High-res card for one large print per A4 (~175×248 mm at ~150 dpi)
CARD_W, CARD_H = 1040, 1480
NUM_KEYS = 3

LETTER_ALIASES_NOTE = "Y uses E   ·   V uses F"
ORDER = [
    list("ABC"),
    list("DEF"),
    list("GHI"),
    list("JKL"),
    list("MNO"),
    list("PQR"),
    list("STU"),
    list("WXZ"),
]

SLOGANS = [
    '"For a small fee, I can show you the shortcut."',
    '"For a bigger fee, I can make sure you come back!"',
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf"]
        if bold
        else [r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\segoeui.ttf"]
    )
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def aziz_portrait(size: int = 160) -> Image.Image:
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    if AZIZ_SRC.exists():
        im = Image.open(AZIZ_SRC).convert("RGB")
        w, h = im.size
        side = min(w, h)
        left = (w - side) // 2
        top = max(0, (h - side) // 6)
        im = im.crop((left, top, left + side, top + side))
        g = ImageOps.grayscale(im)
        g = ImageOps.autocontrast(g)
        g = ImageEnhance.Contrast(g).enhance(1.55)
        g = g.point(lambda p: 0 if p < 145 else 255)
        g = g.resize((size, size), Image.Resampling.LANCZOS)
    else:
        g = Image.new("L", (size, size), 230)
        d = ImageDraw.Draw(g)
        d.ellipse([8, 8, size - 8, size - 8], outline=0, width=4)
        d.text((size // 3, size // 3), "A", fill=0, font=font(48, True))
    path = BRAND_DIR / "aziz_bw.png"
    g.save(path)
    return g


def load_glyph(letter: str, box: int) -> Image.Image:
    """Fit glyph inside box×box keeping aspect ratio (same look as address strips)."""
    path = GLYPH_DIR / f"{letter}.png"
    out = Image.new("L", (box, box), 255)
    if not path.exists():
        d = ImageDraw.Draw(out)
        d.text((4, 4), letter, fill=0, font=font(28, True))
        return out
    g = Image.open(path).convert("L")
    g = g.point(lambda p: 0 if p < 140 else 255)
    # Preserve aspect — do not squash horizontal feet (B) etc. into a square
    scale = min(box / g.width, box / g.height)
    nw = max(1, int(g.width * scale))
    nh = max(1, int(g.height * scale))
    g = g.resize((nw, nh), Image.Resampling.LANCZOS)
    out.paste(g, ((box - nw) // 2, (box - nh) // 2))
    return out


def draw_wrapped(d: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], max_w: int, fnt, fill=0, line_gap=3):
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    x, y = xy
    for line in lines:
        d.text((x, y), line, fill=fill, font=fnt)
        bbox = d.textbbox((0, 0), line, font=fnt)
        y += (bbox[3] - bbox[1]) + line_gap
    return y


def build_card() -> Image.Image:
    card = Image.new("L", (CARD_W, CARD_H), 255)
    d = ImageDraw.Draw(card)
    m = 18

    # Outer frames
    d.rectangle([m, m, CARD_W - m - 1, CARD_H - m - 1], outline=0, width=6)
    d.rectangle([m + 8, m + 8, CARD_W - m - 9, CARD_H - m - 9], outline=0, width=2)

    # Header bar
    header_h = 120
    d.rectangle([m + 12, m + 12, CARD_W - m - 13, m + 12 + header_h], fill=0)
    f_title = font(36, True)
    f_sub = font(22, True)
    f_body = font(18)
    f_rule = font(17)
    f_letter = font(22, True)

    header = Image.new("L", (CARD_W - 2 * m - 24, header_h), 0)
    hd = ImageDraw.Draw(header)
    hd.text((14, 14), "AZIZ DESERT TOURS", fill=255, font=f_title)
    hd.text((14, 58), "Official Portal Glyph Decoder", fill=255, font=f_sub)
    hd.text((14, 90), "Complimentary guest souvenir  ·  @DesertTombGuide", fill=255, font=f_body)
    card.paste(header, (m + 12, m + 12))

    # Brand row: portrait + slogans
    y = m + 12 + header_h + 16
    portrait = aziz_portrait(150)
    px, py = m + 22, y
    d.rectangle([px - 3, py - 3, px + portrait.width + 2, py + portrait.height + 2], outline=0, width=3)
    card.paste(portrait, (px, py))

    tx = px + portrait.width + 18
    d.text((tx, y), "Your licensed desert guide", fill=0, font=f_sub)
    y2 = draw_wrapped(d, SLOGANS[0], (tx, y + 32), CARD_W - tx - m - 20, f_body, fill=0, line_gap=3)
    y2 = draw_wrapped(d, SLOGANS[1], (tx, y2 + 8), CARD_W - tx - m - 20, f_body, fill=0, line_gap=3)
    d.text((tx, y2 + 10), "Like · Subscribe · Don't get cursed", fill=0, font=f_body)

    y = max(y + portrait.height, y2 + 36) + 12
    d.line([(m + 22, y), (CARD_W - m - 22, y)], fill=0, width=3)
    y += 14

    # Alphabet title
    d.text((m + 22, y), "HIEROGLYPHIC ALPHABET", fill=0, font=f_sub)
    alias_f = font(16, True)
    alias_w = d.textlength(LETTER_ALIASES_NOTE, font=alias_f)
    d.text((CARD_W - m - 22 - alias_w, y + 4), LETTER_ALIASES_NOTE, fill=0, font=alias_f)
    y += 36

    # Glyph grid
    grid_left = m + 22
    grid_right = CARD_W - m - 22
    grid_w = grid_right - grid_left
    cols, rows = 3, 8
    cell_w = grid_w // cols
    footer_reserve = 210
    grid_bottom = CARD_H - m - footer_reserve
    cell_h = (grid_bottom - y) // rows
    glyph_box = min(cell_w - 48, cell_h - 16)

    for r, row in enumerate(ORDER):
        for c, letter in enumerate(row):
            x0 = grid_left + c * cell_w
            y0 = y + r * cell_h
            d.rectangle([x0, y0, x0 + cell_w - 6, y0 + cell_h - 6], outline=0, width=2)
            g = load_glyph(letter, glyph_box)
            gx = x0 + 8
            gy = y0 + (cell_h - 6 - glyph_box) // 2
            card.paste(g, (gx, gy))
            label = letter
            if letter == "E":
                label = "E/Y"
            elif letter == "F":
                label = "F/V"
            label_w = d.textlength(label, font=f_letter)
            d.text((x0 + cell_w - 12 - label_w, y0 + 6), label, fill=0, font=f_letter)

    y = grid_bottom + 10
    d.line([(m + 22, y), (CARD_W - m - 22, y)], fill=0, width=3)
    y += 12

    # How to read
    d.text((m + 22, y), "HOW TO READ PORTAL ADDRESSES", fill=0, font=f_sub)
    y += 30
    rules = [
        "1. The bird faces the START of the address line.",
        "2. Bird faces LEFT → read left-to-right.",
        "3. Bird faces RIGHT → read right-to-left (follow from the bird).",
        "4. Match each symbol to this chart. Spaces are omitted.",
        "5. Got a code? Ask Aziz which dig site still has a working portal.",
    ]
    for rule in rules:
        d.text((m + 22, y), rule, fill=0, font=f_rule)
        y += 26

    y += 6
    d.rectangle([m + 18, y, CARD_W - m - 19, CARD_H - m - 16], outline=0, width=2)
    d.text((m + 28, y + 8), "AZIZ DESERT TOURS  ·  Ministry of Antiques (tour partner)", fill=0, font=f_body)
    d.text((m + 28, y + 32), "Not responsible for curses, sandstorms, or quantum-locked doors.", fill=0, font=f_body)
    d.text((m + 28, y + 56), "Keep this card. The desert keeps score.  ·  @DesertTombGuide", fill=0, font=f_body)

    return card


def write_tex() -> Path:
    """Three large keys — one per A4 page with cut guides."""
    pages = []
    for i in range(NUM_KEYS):
        if i > 0:
            pages.append(r"\newpage")
        pages.append(
            r"""\centering
{\large\bfseries Aziz Desert Tours --- Portal Glyph Decoder \quad
cut on dashed line \quad B/W laser \quad guest key (not the real papyrus)}\\[2mm]

\decipherkey
"""
        )

    body = "\n".join(pages)
    tex = rf"""\documentclass[a4paper]{{article}}
\usepackage[margin=6mm,top=7mm,bottom=6mm]{{geometry}}
\usepackage{{graphicx}}
\usepackage{{xcolor}}
\definecolor{{cutgray}}{{gray}}{{0.40}}
\usepackage{{tikz}}
\pagestyle{{empty}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0pt}}

% One large key per page — fixed mm sizes for graphicx
\newcommand{{\decipherkey}}{{%
  \begin{{tikzpicture}}
    \node[inner sep=0pt, outer sep=0pt] (k) at (0,0)
      {{\includegraphics[width=175mm,height=248mm,keepaspectratio=false]{{HieroGlyphs/brand/decipher_key_card.png}}}};
    \draw[cutgray, dashed, line width=0.8pt]
      (k.south west) rectangle (k.north east);
    \draw[black, line width=1.0pt]
      (k.south west) -- ++(0,4mm)
      (k.south west) -- ++(4mm,0)
      (k.south east) -- ++(0,4mm)
      (k.south east) -- ++(-4mm,0)
      (k.north west) -- ++(0,-4mm)
      (k.north west) -- ++(4mm,0)
      (k.north east) -- ++(0,-4mm)
      (k.north east) -- ++(-4mm,0);
  \end{{tikzpicture}}%
}}

\begin{{document}}
{body}
\end{{document}}
"""
    path = ROOT / "hieroglyph_decipher_keys.tex"
    path.write_text(tex, encoding="utf-8")
    return path


def main() -> int:
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    if not GLYPH_DIR.exists():
        print("Missing glyphs; run build_hieroglyph_addresses.py first", file=sys.stderr)
        return 1
    card = build_card()
    card.save(OUT_CARD)
    print(f"Wrote {OUT_CARD} ({CARD_W}x{CARD_H})")
    tex = write_tex()
    print(f"Wrote {tex} ({NUM_KEYS} keys)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
