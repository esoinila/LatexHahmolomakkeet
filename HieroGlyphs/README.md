# Hieroglyph portal addresses

Portal **network address** tiles for the table. Players decipher site names with your Egypt souvenir papyrus (`Alphabet_for_hieroglyph.jpg`) or the printed Aziz decoder cards.

## Print set

| PDF | Use |
|-----|-----|
| `Output/site_addresses_player.pdf` | Cuttable address tiles (glyphs only) + alphabet reading guide |
| `Output/site_addresses_gm.pdf` | **KEEP SECRET** — tiles + large address strips + Latin codes |
| `Output/hieroglyph_decipher_keys.pdf` | 3 large Aziz Desert Tours decoder cards (1 per A4) |

B/W laser is fine for all three.

## Player experience

1. Print `site_addresses_player.pdf` and cut on the **dashed lines**.
2. Print `hieroglyph_decipher_keys.pdf` and cut out one card per guest (or use the wood papyrus).
3. Bird faces the **start** of the address:
   - faces **left** → read LTR
   - faces **right** → read RTL (glyph order already reversed on the tile)
4. Shared papyrus aliases: **Y** uses **E**; **V** uses **F**.

## GM

Print `site_addresses_gm.pdf` and keep it secret. Same glyphs as the player tiles, with Latin **code** + full site name.

## Rebuild

From repo root (use a Python that has Pillow; project venv may not):

```powershell
# Fast path: current letter masters → assets + all three PDFs
.\build_site_addresses.ps1

# Assets only (no LaTeX):
py -3 HieroGlyphs\rebuild_print_set.py
```

Manual LaTeX after assets:

```powershell
pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_player.tex
pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_gm.tex
pdflatex -interaction=nonstopmode -output-directory=Output site_addresses_gm.tex
pdflatex -interaction=nonstopmode -output-directory=Output hieroglyph_decipher_keys.tex
```

## Data

| File | Role |
|------|------|
| `site_addresses.json` | Codes, directions, icons |
| `alphabet.json` | Glyph file map + Y→E, V→F |
| `glyphs/` | B/W letter glyphs for print |
| `glyphs_color/named/` | Color GenAI masters (source of truth for letter art) |
| `process_glyphs_bw.py` | Color master → laser B/W |
| `addresses/` | Composed glyph address strips |
| `tiles/` | Player card images (icon + address, no Latin) |
| `brand/decipher_key_card.png` | Multi-up decoder card art |

Edit site codes / LTR·RTL in `build_hieroglyph_addresses.py` (`SITES` list), then rebuild.

## Glyph notes

- Letter art is GenAI woodcut masters tuned to `Alphabet_for_hieroglyph.jpg`.
- After changing a master under `glyphs_color/named/`, re-run B/W process + recompose + recompile PDFs.
- Prefer matching the wood papyrus when orienting flips (hand, crook, foot, etc.).
