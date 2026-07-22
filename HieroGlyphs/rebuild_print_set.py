#!/usr/bin/env python3
"""
Rebuild print assets from current GenAI letter masters (no icon reprocessing).

  py -3 HieroGlyphs/rebuild_print_set.py
  pdflatex ... (or run build_site_addresses.ps1 after this for icons+full path)
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HIERO = ROOT / "HieroGlyphs"
sys.path.insert(0, str(HIERO))

from process_glyphs_bw import process_one  # noqa: E402
from build_hieroglyph_addresses import (  # noqa: E402
    ADDR_DIR,
    GLYPH_DIR,
    SITES,
    TILE_DIR,
    compose_address,
    load_site_icon,
    build_player_tile,
    write_alphabet_json,
    write_reference_alphabet_sheet,
    write_site_json,
    write_tex_files,
)
from build_decipher_keys import main as decipher_main  # noqa: E402


def main() -> int:
    named = HIERO / "glyphs_color" / "named"
    print("=== Letter masters → B/W glyphs ===")
    for L in list("ABCDEFGHIJKLMNOPQRSTUWXZ"):
        src = named / f"{L}.jpg"
        if not src.exists():
            print(f"  MISSING {src}")
            continue
        process_one(src, GLYPH_DIR / f"{L}.png")
        print(f"  {L}")
    shutil.copy2(GLYPH_DIR / "E.png", GLYPH_DIR / "Y.png")
    shutil.copy2(GLYPH_DIR / "F.png", GLYPH_DIR / "V.png")

    print("=== Addresses + tiles ===")
    for sid, name, addr, direction in SITES:
        strip = compose_address(addr, direction)
        strip.save(ADDR_DIR / f"{sid}.png")
        tile = build_player_tile(load_site_icon(sid, max_side=380), strip)
        tile.save(TILE_DIR / f"{sid}.png")
        print(f"  {sid}: {addr} ({direction})")

    print("=== JSON + alphabet key + TeX ===")
    write_alphabet_json()
    write_site_json()
    write_reference_alphabet_sheet()
    write_tex_files()

    print("=== Decipher key card art + TeX ===")
    decipher_main()

    print("Done. Compile PDFs:")
    print("  pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_player.tex")
    print("  pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_gm.tex")
    print("  pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_gm.tex")
    print("  pdflatex -interaction=nonstopmode -output-directory=Output hieroglyph_decipher_keys.tex")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
