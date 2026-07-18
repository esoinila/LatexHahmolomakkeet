# Hieroglyph portal addresses

Portal **network address** tiles for the table. Players decipher site names with your Egypt souvenir papyrus (`Alphabet_for_hieroglyph.jpg`) or the printed game key.

## Player experience

1. Print `Output/site_addresses_player.pdf` (B/W laser OK).
2. Cut on the **dashed lines** (corner ticks help).
3. Put the wood papyrus (or the last page alphabet key) on the table.
4. Bird faces the **start** of the address:
   - faces **left** → read LTR
   - faces **right** → read RTL (glyphs already reversed on the tile)

## GM

Print `Output/site_addresses_gm.pdf` and keep it secret. Same glyphs with Latin **code** + full site name.

## Rebuild

```powershell
python HieroGlyphs\build_hieroglyph_addresses.py
pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_player.tex
pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_gm.tex
pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_gm.tex
```

Or: `.\build_site_addresses.ps1`

## Data

| File | Role |
|------|------|
| `site_addresses.json` | Codes, directions, icons |
| `alphabet.json` | Glyph file map + Y→E, V→F |
| `glyphs/` | GenAI→B/W letter glyphs (from papyrus photo) |
| `glyphs_color/` | Color GenAI masters for each letter |
| `process_glyphs_bw.py` | Letter GenAI → B/W filter |
| `site_icons_color/` | GenAI woodcut masters (cream parchment) |
| `site_icons/` | Laser B/W processed emblems (line art, not solid fill) |
| `process_icons_bw.py` | GenAI → B/W filter + site mapping |
| `addresses/` | Composed glyph strips |
| `tiles/` | Player card images (large icon + address, no Latin) |

Edit address codes / LTR·RTL in `build_hieroglyph_addresses.py` (`SITES` list), then rebuild.
Emblem motifs live in `site_icon_drawings.py` (Osireion water crypt, Eridu temple-mound on the Abzu, Chogha Zanbil tiers, Aramu Muru T-gate, etc.).
