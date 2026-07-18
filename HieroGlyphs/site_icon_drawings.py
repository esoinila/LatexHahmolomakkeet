#!/usr/bin/env python3
"""
Bold B/W place emblems for portal address tiles (laser-friendly).

Each drawer paints on a 0..100 coordinate square. Motifs are chosen from the
real archaeology / geography each site hints at — not the old GenAI art.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

ICON_SIZE = 420  # large source; tiles downscale


def _canvas() -> tuple[Image.Image, ImageDraw.ImageDraw, float]:
    im = Image.new("L", (ICON_SIZE, ICON_SIZE), 255)
    d = ImageDraw.Draw(im)
    s = ICON_SIZE / 100.0
    return im, d, s


def _xy(s: float, x: float, y: float) -> tuple[float, float]:
    return x * s, y * s


def _poly(d, s, pts, fill=0):
    d.polygon([_xy(s, x, y) for x, y in pts], fill=fill)


def _ellipse(d, s, box, fill=0):
    x0, y0, x1, y1 = box
    d.ellipse([*_xy(s, x0, y0), *_xy(s, x1, y1)], fill=fill)


def _line(d, s, pts, width=5):
    d.line([_xy(s, x, y) for x, y in pts], fill=0, width=max(2, int(width * s / 1.2)))


def _rect(d, s, box, fill=0):
    x0, y0, x1, y1 = box
    d.rectangle([*_xy(s, x0, y0), *_xy(s, x1, y1)], fill=fill)


def _arc(d, s, box, start, end, width=6):
    x0, y0, x1, y1 = box
    d.arc([*_xy(s, x0, y0), *_xy(s, x1, y1)], start=start, end=end, fill=0, width=max(2, int(width * s / 1.2)))


def _finish(im: Image.Image) -> Image.Image:
    """Thicken ink slightly for laser; pure B/W; trim empty margin then re-pad lightly."""
    inv = ImageOps.invert(im)
    inv = inv.filter(ImageFilter.MaxFilter(3))
    im = ImageOps.invert(inv)
    im = im.point(lambda p: 0 if p < 128 else 255)
    # Crop to content, keep ~4% padding so it can fill a box tightly
    bbox = ImageOps.invert(im).getbbox()
    if not bbox:
        return im
    im = im.crop(bbox)
    pad = max(4, int(ICON_SIZE * 0.02))
    im = ImageOps.expand(im, border=pad, fill=255)
    # Fit back into square without shrinking content too much
    side = max(im.size)
    canvas = Image.new("L", (side, side), 255)
    canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
    return canvas.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS).point(
        lambda p: 0 if p < 140 else 255
    )


# --- Site emblems ----------------------------------------------------------


def draw_abydos_osireion(d, s):
    """Osireion: underground pillared hall with water channel around central island."""
    # outer crypt walls
    _rect(d, s, (10, 18, 90, 88))
    _rect(d, s, (16, 24, 84, 82), fill=255)
    # water channel (double frame)
    _rect(d, s, (20, 30, 80, 78))
    _rect(d, s, (28, 38, 72, 70), fill=255)
    # central island platform
    _rect(d, s, (34, 44, 66, 66))
    # ten pillars (5+5 simplified as posts)
    for x in (38, 46, 54, 62):
        _rect(d, s, (x, 40, x + 3, 68), fill=255)
        _rect(d, s, (x + 0.5, 42, x + 2.5, 66))
    # water ripples in channel
    for y in (33, 74):
        _line(d, s, [(24, y), (30, y + 2), (36, y), (42, y + 2), (48, y)], width=2)


def draw_boat_pits(d, s):
    """Solar boat in a rectangular rock-cut pit (Khufu boat pits)."""
    # pit outline
    _rect(d, s, (12, 28, 88, 82))
    _rect(d, s, (18, 34, 82, 76), fill=255)
    # boat hull
    _poly(d, s, [(22, 58), (30, 48), (70, 48), (80, 58), (75, 66), (25, 66)])
    # cabin / shrine
    _rect(d, s, (42, 38, 58, 52))
    # mast + sun disk
    _line(d, s, [(50, 38), (50, 22)], width=4)
    _ellipse(d, s, (42, 12, 58, 28))
    _ellipse(d, s, (46, 16, 54, 24), fill=255)
    # pit floor line
    _line(d, s, [(20, 70), (80, 70)], width=3)


def draw_builders_quarters(d, s):
    """Workers' village: mudbrick house row + copper chisel / mallet."""
    # three house blocks
    for i, x in enumerate((12, 38, 64)):
        _rect(d, s, (x, 42, x + 22, 78))
        _rect(d, s, (x + 4, 50, x + 10, 62), fill=255)  # door
        _rect(d, s, (x + 12, 50, x + 18, 58), fill=255)  # window
        # flat roof beam
        _rect(d, s, (x - 1, 38, x + 23, 44))
    # tools in front: mallet + chisel
    _poly(d, s, [(28, 82), (36, 88), (40, 84), (32, 78)])  # mallet head
    _rect(d, s, (32, 70, 36, 84))
    _rect(d, s, (58, 72, 72, 76))  # chisel blade
    _rect(d, s, (70, 68, 74, 82))


def draw_dendera_temple(d, s):
    """Dendera: Hathor-head columns + temple façade (famous mammisi / main hypostyle)."""
    # podium
    _rect(d, s, (10, 72, 90, 88))
    # façade block
    _rect(d, s, (18, 38, 82, 72))
    # cornice
    _rect(d, s, (14, 32, 86, 40))
    # three Hathor-style columns (face = oval + ears)
    for x in (28, 50, 72):
        _rect(d, s, (x - 4, 48, x + 4, 72), fill=255)
        _rect(d, s, (x - 3, 50, x + 3, 70))
        _ellipse(d, s, (x - 8, 36, x + 8, 54))
        _ellipse(d, s, (x - 5, 40, x + 5, 50), fill=255)
        # cow ears
        _poly(d, s, [(x - 8, 40), (x - 14, 32), (x - 6, 38)])
        _poly(d, s, [(x + 8, 40), (x + 14, 32), (x + 6, 38)])
    # doorway
    _rect(d, s, (44, 54, 56, 72), fill=255)
    # tiny zodiac disk above door (Dendera zodiac nod)
    _ellipse(d, s, (46, 44, 54, 52))


def draw_east_cemetery(d, s):
    """Eastern cemetery: dense mastaba field + small queens' pyramids."""
    # ground
    _line(d, s, [(6, 88), (94, 88)], width=5)
    # two rows of mastabas (bench tombs east of Khufu)
    for y in (38, 62):
        for x in (8, 28, 48):
            _rect(d, s, (x, y, x + 16, y + 22))
            _rect(d, s, (x + 4, y + 5, x + 12, y + 14), fill=255)
    # queens' satellite pyramids
    for x, h in ((70, 40), (82, 28), (70, 22)):
        base = 88
        _poly(d, s, [(x, base), (x + 6, base - h), (x + 12, base)])


def draw_eridu_ruins(d, s):
    """Eridu: first city — temple mound of Enki above the Abzu (fresh waters)."""
    # water / abzu base
    for i, y in enumerate((78, 84, 90)):
        _line(d, s, [(10, y), (20, y - 3), (35, y), (50, y - 3), (65, y), (80, y - 3), (90, y)], width=3)
    # multi-level temple platform (proto-ziggurat mound)
    _poly(d, s, [(18, 78), (28, 58), (72, 58), (82, 78)])
    _poly(d, s, [(28, 58), (36, 40), (64, 40), (72, 58)])
    _rect(d, s, (40, 22, 60, 40))  # shrine
    # doorway
    _rect(d, s, (46, 28, 54, 40), fill=255)
    # reed-bundle poles (Sumerian)
    _line(d, s, [(24, 58), (24, 48)], width=3)
    _line(d, s, [(76, 58), (76, 48)], width=3)
    _ellipse(d, s, (20, 42, 28, 50))
    _ellipse(d, s, (72, 42, 80, 50))


def draw_giza_repository(d, s):
    """Hidden library under Giza: pyramid + open granite vault of scrolls."""
    # great pyramid silhouette
    _poly(d, s, [(12, 78), (50, 12), (88, 78)])
    _poly(d, s, [(28, 78), (50, 32), (72, 78)], fill=255)
    # open vault door
    _rect(d, s, (40, 48, 60, 78))
    _rect(d, s, (44, 52, 56, 74), fill=255)
    # scroll ends inside
    _ellipse(d, s, (45, 56, 49, 70))
    _ellipse(d, s, (51, 56, 55, 70))
    # capstone gleam
    _poly(d, s, [(46, 18), (50, 8), (54, 18)])


def draw_hetepheres_tombs(d, s):
    """Queen Hetepheres: deep shaft tomb + carrying chair / canopy (famous furniture)."""
    # shaft mouth
    _ellipse(d, s, (30, 18, 70, 40))
    _ellipse(d, s, (38, 24, 62, 36), fill=255)
    # shaft going down
    _rect(d, s, (42, 36, 58, 88))
    _rect(d, s, (46, 40, 54, 84), fill=255)
    # canopy chair (side view) next to shaft
    _rect(d, s, (64, 55, 88, 58))  # seat
    _rect(d, s, (66, 45, 70, 72))  # back post
    _rect(d, s, (84, 55, 88, 72))
    _arc(d, s, (64, 38, 88, 58), 200, 340, width=4)  # canopy


def draw_inka_andes(d, s):
    """Gate of the Gods (Aramu Muru style): T-niche false door in Andean cliff + lake."""
    # mountain mass
    _poly(d, s, [(5, 85), (25, 30), (45, 55), (60, 20), (95, 85)])
    # carved face / door slab
    _rect(d, s, (32, 40, 68, 82), fill=255)
    _rect(d, s, (36, 44, 64, 80))
    # T-shaped niche (classic "doorway of the amaru")
    _rect(d, s, (42, 50, 58, 58), fill=255)
    _rect(d, s, (46, 58, 54, 76), fill=255)
    # Lake Titicaca hint
    _line(d, s, [(8, 90), (25, 88), (40, 92), (60, 88), (85, 91), (95, 89)], width=3)


def draw_iran_ziggurat(d, s):
    """Chogha Zanbil: Elamite stepped ziggurat with outer temenos corners."""
    # outer court corners
    _line(d, s, [(8, 88), (8, 70), (18, 70)], width=4)
    _line(d, s, [(92, 88), (92, 70), (82, 70)], width=4)
    # tiers
    _poly(d, s, [(15, 85), (25, 68), (75, 68), (85, 85)])
    _poly(d, s, [(25, 68), (32, 52), (68, 52), (75, 68)])
    _poly(d, s, [(32, 52), (38, 36), (62, 36), (68, 52)])
    _rect(d, s, (42, 22, 58, 36))  # high temple
    _rect(d, s, (46, 26, 54, 36), fill=255)
    # stair ramp
    _poly(d, s, [(48, 85), (52, 36), (56, 85)], fill=255)
    _line(d, s, [(50, 85), (52, 40), (54, 85)], width=2)


def draw_mars_face_mountain(d, s):
    """Cydonia Face: mesa with humanoid face in cliff, thin Mars stars."""
    # mountain body
    _poly(d, s, [(15, 88), (22, 50), (40, 35), (70, 38), (85, 55), (90, 88)])
    # face plane (lighter cut)
    _ellipse(d, s, (38, 42, 72, 78), fill=255)
    # eyes, nose, mouth — bold face reading at table
    _ellipse(d, s, (44, 52, 52, 60))
    _ellipse(d, s, (58, 52, 66, 60))
    _poly(d, s, [(54, 60), (50, 70), (58, 70)])
    _arc(d, s, (46, 68, 64, 80), 20, 160, width=4)
    # stars
    for x, y in ((12, 18), (28, 12), (80, 16), (90, 28)):
        _line(d, s, [(x - 3, y), (x + 3, y)], width=2)
        _line(d, s, [(x, y - 3), (x, y + 3)], width=2)


def draw_ocean_giza_clone(d, s):
    """Sunken Giza clone: three pyramids under waves / force-dome hint."""
    # three pyramids
    _poly(d, s, [(12, 70), (28, 30), (44, 70)])
    _poly(d, s, [(38, 72), (55, 22), (72, 72)])
    _poly(d, s, [(58, 70), (74, 38), (90, 70)])
    # water surface waves over mid height
    for y in (48, 58, 78, 88):
        _line(d, s, [(8, y), (18, y - 4), (32, y), (48, y - 4), (64, y), (80, y - 4), (94, y)], width=3)
    # small dome arc (force field)
    _arc(d, s, (20, 15, 85, 75), 200, 340, width=4)


def draw_office_pyramid_studies(d, s):
    """Modern research office: building block + pyramid logo / files."""
    # office block
    _rect(d, s, (12, 28, 58, 85))
    # windows grid
    for row in (36, 50, 64):
        for col in (18, 30, 42):
            _rect(d, s, (col, row, col + 8, row + 8), fill=255)
    # door
    _rect(d, s, (28, 70, 40, 85), fill=255)
    # pyramid emblem / model on right
    _poly(d, s, [(62, 78), (80, 28), (96, 78)])
    _poly(d, s, [(70, 78), (80, 45), (90, 78)], fill=255)
    # clipboard / notes
    _rect(d, s, (64, 82, 78, 92))
    _line(d, s, [(66, 85), (76, 85)], width=2)
    _line(d, s, [(66, 88), (74, 88)], width=2)


def draw_queen_khentkawes(d, s):
    """Khentkawes: unique stepped 'throne' tomb-pyramid of the queen."""
    # lower square podium (her distinctive form)
    _rect(d, s, (18, 58, 82, 88))
    # upper mastaba / step
    _rect(d, s, (28, 38, 72, 58))
    # tiny pyramidion / chapel
    _poly(d, s, [(40, 38), (50, 18), (60, 38)])
    # doorway on podium
    _rect(d, s, (45, 68, 55, 88), fill=255)
    # queen cartouche-like oval plaque
    _ellipse(d, s, (42, 44, 58, 54), fill=255)
    _ellipse(d, s, (44, 46, 56, 52))


def draw_rock_cut_tombs_khafre(d, s):
    """Rock-cut tombs: cliff face with dark tomb doorways + sun/serpent motif."""
    # cliff
    _poly(d, s, [(8, 20), (20, 12), (90, 12), (95, 88), (8, 88)])
    # rock strata lines
    for y in (30, 45, 60, 75):
        _line(d, s, [(12, y), (90, y)], width=2)
    # three tomb mouths
    for x in (22, 45, 68):
        _rect(d, s, (x, 48, x + 14, 78), fill=255)
        _rect(d, s, (x + 2, 50, x + 12, 76))
    # sun disk + uraeus hint
    _ellipse(d, s, (42, 18, 58, 34))
    _ellipse(d, s, (46, 22, 54, 30), fill=255)
    _poly(d, s, [(58, 24), (70, 20), (68, 28)])


def draw_saqqara_step_pyramid(d, s):
    """Djoser's step pyramid at Saqqara — six clear tiers."""
    tiers = [
        (18, 82, 82, 88),
        (22, 70, 78, 82),
        (28, 56, 72, 70),
        (34, 42, 66, 56),
        (40, 28, 60, 42),
        (44, 16, 56, 28),
    ]
    for box in tiers:
        _rect(d, s, box)
    # enclosure wall hint
    _line(d, s, [(10, 90), (90, 90)], width=4)
    _line(d, s, [(10, 90), (10, 78)], width=3)
    _line(d, s, [(90, 90), (90, 78)], width=3)


def draw_sphinx(d, s):
    """Great Sphinx — bold side profile filling the frame."""
    # haunches / body mass
    _ellipse(d, s, (8, 48, 48, 88))
    _poly(d, s, [(25, 55), (70, 48), (88, 55), (92, 78), (20, 85)])
    # extended paws
    _rect(d, s, (72, 68, 96, 85))
    _rect(d, s, (76, 60, 94, 70))
    # head + nemes headdress
    _poly(d, s, [(58, 50), (60, 12), (88, 12), (92, 35), (86, 52)])
    _ellipse(d, s, (62, 16, 90, 50))
    # eye + brow
    _ellipse(d, s, (72, 26, 84, 38), fill=255)
    _ellipse(d, s, (75, 29, 81, 35))
    # lappet
    _poly(d, s, [(60, 40), (48, 62), (62, 58)])
    # tail curl
    _arc(d, s, (2, 55, 22, 80), 90, 270, width=5)
    # sand base
    _line(d, s, [(4, 90), (98, 90)], width=5)


def draw_sphinx_shadow_chamber(d, s):
    """Shadow chamber: sphinx silhouette + dawn ray + underground vault under paws."""
    # sphinx simplified
    _poly(d, s, [(15, 48), (30, 35), (55, 32), (70, 38), (75, 55), (20, 58)])
    _poly(d, s, [(55, 32), (58, 12), (72, 14), (74, 35)])
    # long dawn shadow / ray from left
    _poly(d, s, [(5, 20), (40, 55), (8, 55)])
    # sun
    _ellipse(d, s, (4, 8, 22, 26))
    _ellipse(d, s, (8, 12, 18, 22), fill=255)
    # underground chamber under ground line
    _line(d, s, [(10, 62), (90, 62)], width=4)
    _rect(d, s, (35, 62, 70, 90))
    _rect(d, s, (40, 68, 65, 85), fill=255)
    # pillar in chamber
    _rect(d, s, (50, 68, 55, 85))


def draw_valley_khafre(d, s):
    """Valley Temple of Khafre: megalithic block temple with square pillars."""
    # massive podium
    _rect(d, s, (10, 70, 90, 88))
    # temple walls
    _rect(d, s, (18, 35, 82, 70))
    # megalith course lines
    for y in (45, 55, 65):
        _line(d, s, [(20, y), (80, y)], width=2)
    # square pillars in front
    for x in (28, 42, 56, 70):
        _rect(d, s, (x, 48, x + 6, 70), fill=255)
        _rect(d, s, (x + 1, 50, x + 5, 68))
    # entrance
    _rect(d, s, (46, 55, 54, 70), fill=255)
    # Anubis / statue plinth hint
    _rect(d, s, (44, 28, 56, 35))
    _poly(d, s, [(46, 28), (50, 18), (54, 28)])


def draw_valley_queens(d, s):
    """Valley of the Queens: cliff tombs + queen's uraeus / lotus."""
    # cliffs
    _poly(d, s, [(5, 85), (15, 25), (40, 35), (55, 15), (85, 30), (95, 85)])
    # tomb doors
    for x, h in ((22, 50), (48, 42), (70, 48)):
        _rect(d, s, (x, h, x + 12, 78), fill=255)
        _rect(d, s, (x + 2, h + 2, x + 10, 76))
    # lotus / queen symbol
    _ellipse(d, s, (42, 80, 58, 94))
    _poly(d, s, [(50, 80), (40, 70), (50, 74), (60, 70)])
    # uraeus curve
    _arc(d, s, (60, 8, 85, 35), 200, 40, width=4)


def draw_western_cemetery(d, s):
    """Western cemetery: vast mastaba grid west of Khufu."""
    # great pyramid edge on right (orientation cue)
    _poly(d, s, [(70, 20), (95, 20), (95, 88), (70, 88), (78, 50)])
    # mastaba grid
    for row, y in enumerate((30, 50, 70)):
        for col, x in enumerate((10, 28, 46)):
            _rect(d, s, (x, y, x + 14, y + 16))
            _rect(d, s, (x + 4, y + 4, x + 10, y + 10), fill=255)
    # path
    _line(d, s, [(18, 90), (65, 90), (72, 50)], width=3)


DRAWERS = {
    "abydos_osireion": draw_abydos_osireion,
    "boat_pits": draw_boat_pits,
    "builders_quarters": draw_builders_quarters,
    "dendera_temple": draw_dendera_temple,
    "east_cemetery": draw_east_cemetery,
    "eridu_ruins": draw_eridu_ruins,
    "giza_repository": draw_giza_repository,
    "hetepheres_tombs": draw_hetepheres_tombs,
    "inka_andes": draw_inka_andes,
    "iran_ziggurat": draw_iran_ziggurat,
    "mars_face_mountain": draw_mars_face_mountain,
    "ocean_giza_clone": draw_ocean_giza_clone,
    "office_pyramid_studies": draw_office_pyramid_studies,
    "queen_khentkawes": draw_queen_khentkawes,
    "rock_cut_tombs_khafre": draw_rock_cut_tombs_khafre,
    "saqqara_step_pyramid": draw_saqqara_step_pyramid,
    "sphinx": draw_sphinx,
    "sphinx_shadow_chamber": draw_sphinx_shadow_chamber,
    "valley_khafre": draw_valley_khafre,
    "valley_queens": draw_valley_queens,
    "western_cemetery": draw_western_cemetery,
}


def build_all_icons(out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for sid, drawer in DRAWERS.items():
        im, d, s = _canvas()
        drawer(d, s)
        im = _finish(im)
        path = out_dir / f"symbol_{sid}.png"
        im.save(path)
        paths[sid] = path
    return paths


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    build_all_icons(root / "site_icons")
    print("Wrote icons to", root / "site_icons")
