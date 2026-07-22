#!/usr/bin/env python3
"""
Build printable clue PDFs:

  PLAYER — only code (T1/K1/U1) + message text (read aloud, mysterious)
  GM     — multi-up with full titles + usage metadata

PRINT FONT RULE (see repo AGENTS.md):
  NEVER use \\tiny / \\scriptsize / \\footnotesize for body text.
  Prefer \\normalsize for messages; fewer cards/page if needed.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent

# --- Typography floor (do not lower) ---
# Body must be \normalsize or larger. No \footnotesize/\scriptsize/\tiny on body.
PLAYER_BODY_FONT = r"\normalsize"  # read aloud at table
PLAYER_CODE_FONT = r"\large\ttfamily\bfseries"
GM_BODY_FONT = r"\normalsize"
GM_CODE_FONT = r"\large\ttfamily\bfseries"
GM_TITLE_FONT = r"\normalsize\bfseries"
GM_META_FONT = r"\small"  # meta only — still ≥ small, never scriptsize

# Player: dense 4-up. GM: stack full-width cards (no fixed empty box height).
PLAYER_COLS, PLAYER_ROWS = 2, 2
PLAYER_PER_PAGE = PLAYER_COLS * PLAYER_ROWS
# How many GM cards we group before a soft page break hint (natural height, no min-height padding)
GM_PER_PAGE = 3


def escape_tex(s: str) -> str:
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "—": r"---",
        "–": r"--",
        "“": "``",
        "”": "''",
        "‘": "`",
        "’": "'",
        "…": r"\ldots{}",
    }
    return "".join(repl.get(ch, ch) for ch in s)


def parse_cards(md_path: Path) -> list[tuple[str, str, str]]:
    """Return (code, full_title, body). code = T1 / K1 / U1 only."""
    text = md_path.read_text(encoding="utf-8")
    # Only match markers at line start (not inside backticks in intro text)
    blocks = re.findall(
        r"(?m)^---KORTTI---\s*\n(.*?)^---/KORTTI---\s*$",
        text,
        flags=re.DOTALL,
    )
    cards: list[tuple[str, str, str]] = []
    for block in blocks:
        lines = [ln.rstrip() for ln in block.strip().splitlines()]
        full_title = ""
        body_lines: list[str] = []
        for ln in lines:
            if not ln.strip():
                if full_title:
                    body_lines.append("")
                continue
            if not full_title and ln.strip().startswith("**"):
                full_title = re.sub(r"^\*\*(.+?)\*\*\s*$", r"\1", ln.strip())
                continue
            body_lines.append(ln)
        while body_lines and not body_lines[-1].strip():
            body_lines.pop()
        cleaned: list[str] = []
        for ln in body_lines:
            s = ln.strip()
            if re.match(r"^[—\-]\s*", s) and re.search(
                r"Toth|Kotka|Thoth|Eagle|Huolenpid|Brändi|Terveys|Turvallisuus|Järjestyksen",
                s,
                re.I,
            ):
                continue
            if re.match(r"^\*\(ja jos joku", s):
                continue
            cleaned.append(ln)
        while cleaned and not cleaned[-1].strip():
            cleaned.pop()
        code_m = re.match(r"^([TKU]\d+)\b", full_title.strip())
        code = code_m.group(1) if code_m else full_title.split()[0]
        cards.append((code, full_title, "\n".join(cleaned)))
    return cards


def _format_inline(s: str) -> str:
    s = re.sub(
        r"\*\*(.+?)\*\*",
        lambda m: r"\textbf{" + escape_tex(m.group(1)) + "}",
        s,
    )
    if "\\textbf{" in s:
        return s
    return escape_tex(s)


def body_to_tex(body: str, blank_vspace: str = r"\vspace{0.22em}") -> str:
    """Player layout: one poem line per printed line."""
    parts: list[str] = []
    raw_lines = body.splitlines()
    for i, ln in enumerate(raw_lines):
        s = ln.strip()
        if not s:
            parts.append(blank_vspace)
            continue
        is_last = i == len(raw_lines) - 1 or all(
            not x.strip() for x in raw_lines[i + 1 :]
        )
        end = "" if is_last else r" \\"
        parts.append(_format_inline(s) + end)
    return "\n".join(parts)


def body_to_tex_gm_compact(body: str) -> str:
    """
    GM compact: join player line-breaks with ' --- ' into flowing paragraphs.
    Blank lines in the source start a new paragraph (stanza).
    Big font, minimal vertical space.
    """
    stanzas: list[list[str]] = []
    cur: list[str] = []
    for ln in body.splitlines():
        s = ln.strip()
        if not s:
            if cur:
                stanzas.append(cur)
                cur = []
            continue
        cur.append(s)
    if cur:
        stanzas.append(cur)

    paras: list[str] = []
    for stanza in stanzas:
        joined = " --- ".join(_format_inline(s) for s in stanza)
        paras.append(joined)
    # Paragraph break between stanzas only
    return "\n\n".join(paras)


def card_box_player(code: str, body: str) -> str:
    """Player: only T1/K1/U1 + message. No descriptive title."""
    return rf"""\begin{{tikzpicture}}
  \node[
    draw=black!55, dashed, line width=0.65pt,
    inner sep=2.6mm,
    text width=0.92\linewidth,
    align=left,
    minimum height=0.40\textheight,
    anchor=north
  ] {{
    {{{PLAYER_CODE_FONT} {escape_tex(code)}}}\\[0.45em]
    {PLAYER_BODY_FONT}
    {body_to_tex(body)}
  }};
\end{{tikzpicture}}"""


def card_box_gm(code: str, full_title: str, body: str, meta: str, color: str) -> str:
    """GM: big type, compact prose (--- between poem lines), height = content only."""
    return rf"""\noindent
\begin{{tcolorbox}}[
  colframe={color},
  colback=white,
  boxrule=0.8pt,
  arc=0pt,
  outer arc=0pt,
  left=2.5mm, right=2.5mm, top=2mm, bottom=2mm,
  boxsep=0.5mm,
  sharp corners,
  enhanced,
  breakable=false
]
{{{GM_CODE_FONT} {escape_tex(code)}}}~~
{{{GM_TITLE_FONT} {escape_tex(full_title)}}}\\[0.2em]
{{{GM_META_FONT}\color{{black!65}} {escape_tex(meta)}}}\\[0.35em]
{{{GM_BODY_FONT}\raggedright {body_to_tex_gm_compact(body)}}}
\end{{tcolorbox}}
"""


def grid_pages_player(cards: list[tuple[str, str, str]]) -> str:
    chunks: list[str] = []
    for page_i in range(0, len(cards), PLAYER_PER_PAGE):
        page_cards = cards[page_i : page_i + PLAYER_PER_PAGE]
        if page_i > 0:
            chunks.append(r"\newpage")
        rows_tex: list[str] = []
        for r in range(PLAYER_ROWS):
            cells: list[str] = []
            for c in range(PLAYER_COLS):
                idx = r * PLAYER_COLS + c
                if idx < len(page_cards):
                    code, _full, body = page_cards[idx]
                    cells.append(
                        r"\begin{minipage}[t]{0.48\textwidth}"
                        + "\n"
                        + card_box_player(code, body)
                        + "\n"
                        + r"\end{minipage}"
                    )
                else:
                    cells.append(
                        r"\begin{minipage}[t]{0.48\textwidth}\strut\end{minipage}"
                    )
            rows_tex.append(" &\n".join(cells))
        chunks.append(
            r"\noindent\begin{tabular}{@{}c@{\hspace{2.5mm}}c@{}}"
            + "\n"
            + (r" \\" + "\n" + r"\vspace{1.8mm}" + "\n").join(rows_tex)
            + "\n"
            + r"\end{tabular}"
        )
    return "\n".join(chunks)


def grid_pages_gm(
    cards: list[tuple[str, str, str]],
    series: str,
    meta: str,
    color: str,
) -> str:
    """Stack GM cards tightly; natural height only (compact --- line joins)."""
    chunks: list[str] = []
    chunks.append(
        rf"""\begin{{center}}
{{\Large\bfseries GM · {escape_tex(series)}}}\\[0.1em]
{{\small {escape_tex(meta)} \ · \ EI pelaajille}}
\end{{center}}
\vspace{{0.8mm}}
"""
    )
    for j, (code, full, body) in enumerate(cards):
        if j > 0:
            chunks.append(r"\vspace{0.9mm}")
        chunks.append(card_box_gm(code, full, body, meta, color))
        chunks.append(r"\filbreak")
    return "\n".join(chunks)


def preamble() -> str:
    return r"""\documentclass[a4paper,11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[finnish]{babel}
\usepackage{lmodern}
\usepackage[margin=7mm,top=8mm,bottom=7mm]{geometry}
\usepackage{tikz}
\usepackage{xcolor}
\usepackage{array}
\usepackage{microtype}
\usepackage{tcolorbox}
\tcbuselibrary{skins,breakable}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.35em}
\setlength{\tabcolsep}{0pt}
\definecolor{tothcol}{RGB}{40,40,90}
\definecolor{eaglecol}{RGB}{120,40,40}
\definecolor{unicol}{RGB}{40,80,60}
"""


def compile_tex(tex_path: Path) -> Path:
    pdf = DIR / (tex_path.stem + ".pdf")
    r = subprocess.run(
        [
            "pdflatex",
            "-interaction=nonstopmode",
            f"-output-directory={DIR}",
            str(tex_path.name),
        ],
        cwd=str(DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if not pdf.exists():
        print(r.stdout[-2500:] if r.stdout else "")
        raise SystemExit(f"pdflatex failed for {tex_path.name}")
    log = DIR / (tex_path.stem + ".log")
    pages = "?"
    if log.exists():
        m = re.search(
            r"Output written on .*?\((\d+) pages?",
            log.read_text(encoding="utf-8", errors="replace"),
        )
        if m:
            pages = m.group(1)
    print(f"Wrote {pdf.name} ({pages} pages)")
    return pdf


def write_and_compile(name: str, body: str) -> None:
    path = DIR / name
    path.write_text(
        preamble() + "\\begin{document}\n" + body + "\n\\end{document}\n",
        encoding="utf-8",
    )
    compile_tex(path)


def main() -> int:
    # Remove stale titled previews so they are not used by mistake
    for stale in DIR.glob("clues_*.pdf"):
        stale.unlink(missing_ok=True)
        print(f"removed stale {stale.name}")
    for stale in DIR.glob("clues_*.tex"):
        stale.unlink(missing_ok=True)

    jobs = [
        (
            "Toth_univiestit.md",
            "player_T",
            "gm_Toth",
            "Toth · uni / huume / jooga / rajutila",
            "Vie Eriduun, Sfinksin varjoon, repoon; 3 lukkoa; akut+zenith",
            "tothcol",
        ),
        (
            "Kotkavaki_viestit.md",
            "player_K",
            "gm_Kotkavaki",
            "Kotkaväki · gaslighting / some / varoitukset",
            "Patronisoiva; suokaasu, huumeet; estä etsintä",
            "eaglecol",
        ),
        (
            "Universumi_yhteys.md",
            "player_U",
            "gm_Universumi",
            "Universumi · kytkeytyminen",
            "Lue kun jooga/huume/meditaatio/yhteys",
            "unicol",
        ),
    ]

    all_player: list[tuple[str, str, str]] = []
    all_gm: list[tuple[str, str, str, str, str]] = []

    for md_name, player_stem, gm_stem, series, meta, col in jobs:
        cards = parse_cards(DIR / md_name)
        print(f"{md_name}: {len(cards)} cards, first code={cards[0][0] if cards else '?'}")
        if not cards:
            continue
        write_and_compile(f"{player_stem}.tex", grid_pages_player(cards))
        write_and_compile(f"{gm_stem}.tex", grid_pages_gm(cards, series, meta, col))
        for c in cards:
            all_player.append(c)
            all_gm.append((c[0], c[1], c[2], series + " · " + meta, col))

    write_and_compile("player_ALL.tex", grid_pages_player(all_player))

    # player_ALL also as the only "preview" name people might open
    write_and_compile("clues_ALL_preview.tex", grid_pages_player(all_player))

    chunks: list[str] = [
        r"""\begin{center}
{\Large\bfseries GM · kaikki vihjekortit}\\[0.1em]
{\small metadata \ · \ EI pelaajille \ · \ runot tiivistetty --- välein}
\end{center}
\vspace{0.8mm}
"""
    ]
    for j, (code, full, body, meta, col) in enumerate(all_gm):
        if j > 0:
            chunks.append(r"\vspace{0.9mm}")
        chunks.append(card_box_gm(code, full, body, meta, col))
        chunks.append(r"\filbreak")
    write_and_compile("gm_ALL.tex", "\n".join(chunks))

    print("\nPLAYER (code + message only):")
    for p in sorted(DIR.glob("player_*.pdf")):
        print(f"  {p.name}")
    print("  clues_ALL_preview.pdf  (same as player_ALL — mysterious)")
    print("GM (full titles + meta):")
    for p in sorted(DIR.glob("gm_*.pdf")):
        print(f"  {p.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
