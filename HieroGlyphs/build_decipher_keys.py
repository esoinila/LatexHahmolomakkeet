#!/usr/bin/env python3
"""
Build Aziz Travel Agency hieroglyph decipher key cards (B/W laser, multi-up A4).

Players use these instead of the physical Egypt papyrus souvenir.
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

# Card pixel size at ~150 dpi for ~95×138 mm (4 per A4)
CARD_W, CARD_H = 560, 820

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


def aziz_portrait(size: int = 96) -> Image.Image:
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
        d.ellipse([8, 8, size - 8, size - 8], outline=0, width=3)
        d.text((size // 3, size // 3), "A", fill=0, font=font(36, True))
    path = BRAND_DIR / "aziz_bw.png"
    g.save(path)
    return g


def load_glyph(letter: str, box: int) -> Image.Image:
    path = GLYPH_DIR / f"{letter}.png"
    if not path.exists():
        im = Image.new("L", (box, box), 255)
        d = ImageDraw.Draw(im)
        d.text((4, 4), letter, fill=0, font=font(18, True))
        return im
    g = Image.open(path).convert("L")
    g = g.resize((box, box), Image.Resampling.LANCZOS)
    return g.point(lambda p: 0 if p < 140 else 255)


def draw_wrapped(d: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], max_w: int, fnt, fill=0, line_gap=2):
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
    m = 10

    # Outer frames
    d.rectangle([m, m, CARD_W - m - 1, CARD_H - m - 1], outline=0, width=4)
    d.rectangle([m + 5, m + 5, CARD_W - m - 6, CARD_H - m - 6], outline=0, width=1)

    # Header bar
    header_h = 78
    d.rectangle([m + 8, m + 8, CARD_W - m - 9, m + 8 + header_h], fill=0)
    f_title = font(22, True)
    f_sub = font(12, True)
    f_tiny = font(11)
    f_body = font(12)
    f_letter = font(14, True)

    # White text on black header
    # PIL can't draw white easily on L mode with text - use inverse: paste text as mask
    header = Image.new("L", (CARD_W - 2 * m - 16, header_h), 0)
    hd = ImageDraw.Draw(header)
    # white = 255 on black 0, then we need white text - in L mode 255 is white
    hd.text((8, 8), "AZIZ DESERT TOURS", fill=255, font=f_title)
    hd.text((8, 36), "Official Portal Glyph Decoder", fill=255, font=f_sub)
    hd.text((8, 54), "Complimentary guest souvenir  ·  @DesertTombGuide", fill=255, font=f_tiny)
    card.paste(header, (m + 8, m + 8))

    # Brand row: portrait + slogans
    y = m + 8 + header_h + 10
    portrait = aziz_portrait(88)
    # frame portrait
    px, py = m + 14, y
    d.rectangle([px - 2, py - 2, px + portrait.width + 1, py + portrait.height + 1], outline=0, width=2)
    card.paste(portrait, (px, py))

    tx = px + portrait.width + 12
    d.text((tx, y), "Your licensed desert guide", fill=0, font=f_sub)
    y2 = draw_wrapped(d, SLOGANS[0], (tx, y + 20), CARD_W - tx - m - 14, f_tiny, fill=0, line_gap=1)
    y2 = draw_wrapped(d, SLOGANS[1], (tx, y2 + 4), CARD_W - tx - m - 14, f_tiny, fill=0, line_gap=1)
    d.text((tx, y2 + 6), "Like · Subscribe · Don't get cursed", fill=0, font=f_tiny)

    y = max(y + portrait.height, y2 + 28) + 8
    d.line([(m + 14, y), (CARD_W - m - 14, y)], fill=0, width=2)
    y += 8

    # Alphabet title
    d.text((m + 14, y), "HIEROGLYPHIC ALPHABET", fill=0, font=f_sub)
    d.text((CARD_W - m - 170, y), LETTER_ALIASES_NOTE, fill=0, font=f_tiny)
    y += 22

    # Glyph grid
    grid_left = m + 14
    grid_right = CARD_W - m - 14
    grid_w = grid_right - grid_left
    cols, rows = 3, 8
    cell_w = grid_w // cols
    # remaining height for grid + rules footer
    footer_reserve = 118
    grid_bottom = CARD_H - m - footer_reserve
    cell_h = (grid_bottom - y) // rows
    glyph_box = min(cell_w - 28, cell_h - 10)

    for r, row in enumerate(ORDER):
        for c, letter in enumerate(row):
            x0 = grid_left + c * cell_w
            y0 = y + r * cell_h
            d.rectangle([x0, y0, x0 + cell_w - 4, y0 + cell_h - 4], outline=0, width=1)
            g = load_glyph(letter, glyph_box)
            gx = x0 + 4
            gy = y0 + (cell_h - 4 - glyph_box) // 2
            card.paste(g, (gx, gy))
            # letter label top-right of cell
            label = letter
            if letter == "E":
                label = "E/Y"
            elif letter == "F":
                label = "F/V"
            d.text((x0 + cell_w - 36, y0 + 3), label, fill=0, font=f_letter)

    y = grid_bottom + 6
    d.line([(m + 14, y), (CARD_W - m - 14, y)], fill=0, width=2)
    y += 8

    # How to read
    d.text((m + 14, y), "HOW TO READ PORTAL ADDRESSES", fill=0, font=f_sub)
    y += 18
    rules = [
        "1. The bird faces the START of the address line.",
        "2. Bird faces LEFT → read left-to-right.",
        "3. Bird faces RIGHT → read right-to-left (follow from the bird).",
        "4. Match each symbol to this chart. Spaces are omitted.",
        "5. Got a code? Ask Aziz which dig site still has a working portal.",
    ]
    for rule in rules:
        d.text((m + 14, y), rule, fill=0, font=f_tiny)
        y += 14

    y += 4
    d.rectangle([m + 12, y, CARD_W - m - 13, CARD_H - m - 12], outline=0, width=1)
    d.text((m + 18, y + 4), "AZIZ DESERT TOURS  ·  Ministry of Antiques (tour partner)", fill=0, font=f_tiny)
    d.text((m + 18, y + 18), "Not responsible for curses, sandstorms, or quantum-locked doors.", fill=0, font=f_tiny)
    d.text((m + 18, y + 32), "Keep this card. The desert keeps score.  ·  www.youtube.com/@DesertTombGuide", fill=0, font=f_tiny)

    return card


def write_tex() -> Path:
    """4 keys per A4 with scissor cut guides (explicit mm sizes for graphicx)."""
    tex = r"""\documentclass[a4paper]{article}
\usepackage[margin=5mm,top=6mm,bottom=5mm]{geometry}
\usepackage{graphicx}
\usepackage{xcolor}
\definecolor{cutgray}{gray}{0.40}
\usepackage{tikz}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\setlength{\tabcolsep}{1.2mm}

% Fixed mm sizes — do not use macros inside \includegraphics width=
\newcommand{\decipherkey}{%
  \begin{tikzpicture}
    \node[inner sep=0pt, outer sep=0pt] (k) at (0,0)
      {\includegraphics[width=96mm,height=132mm,keepaspectratio=false]{HieroGlyphs/brand/decipher_key_card.png}};
    \draw[cutgray, dashed, line width=0.65pt]
      (k.south west) rectangle (k.north east);
    \draw[black, line width=0.85pt]
      (k.south west) -- ++(0,3mm)
      (k.south west) -- ++(3mm,0)
      (k.south east) -- ++(0,3mm)
      (k.south east) -- ++(-3mm,0)
      (k.north west) -- ++(0,-3mm)
      (k.north west) -- ++(3mm,0)
      (k.north east) -- ++(0,-3mm)
      (k.north east) -- ++(-3mm,0);
  \end{tikzpicture}%
}

\begin{document}
\centering
{\footnotesize\bfseries Aziz Desert Tours --- Portal Glyph Decoders \quad
cut on dashed lines \quad B/W laser \quad 1 card/guest (not the real papyrus)}\\[1mm]

\begin{tabular}{@{}c@{\hspace{2mm}}c@{}}
\decipherkey & \decipherkey \\[1mm]
\decipherkey & \decipherkey \\
\end{tabular}

\newpage
\centering
{\footnotesize\bfseries Aziz Desert Tours --- extra decoder sheet (spares)}\\[1mm]
\begin{tabular}{@{}c@{\hspace{2mm}}c@{}}
\decipherkey & \decipherkey \\[1mm]
\decipherkey & \decipherkey \\
\end{tabular}

\end{document}
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
    print(f"Wrote {OUT_CARD}")
    tex = write_tex()
    print(f"Wrote {tex}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
