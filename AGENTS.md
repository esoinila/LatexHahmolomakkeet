# Agent rules — LatexHahmolomakkeet

## Print typography (MANDATORY)

**NEVER use unreadable small fonts in print PDFs or LaTeX print materials.**

This project is for **tabletop handouts** players and GMs read in real light, often after cutting. Tiny type is a defect.

### Forbidden for body text / messages / cards

Do **not** use:

- LaTeX: `\tiny`, `\scriptsize`, `\footnotesize` for **message body** or anything meant to be **read aloud**
- HTML/CSS: `font-size` under **11pt** for printable body copy
- Packing so dense that you “solve” overflow by shrinking type

### Minimum sizes

| Role | Minimum |
|------|---------|
| Body / poem / message (player or GM) | **`\\normalsize`** (≈10–11pt) or larger; prefer **11–12pt** document class |
| Card code / title | **`\\small`** or larger (`\\normalsize` / `\\large` preferred for titles) |
| Page footer / cut hint only | `\\small` allowed; never the only readable line of a clue |
| Headers on GM sheets | `\\large` or bigger when space allows |

### Layout rule

If text does not fit: **use fewer cards per page**, larger page count, or shorter copy — **not** smaller fonts.

### Where this applies

- `Output/NewClues2026/` clue PDFs
- `messages_all_fi.tex`, character sheets, item cards, site address PDFs
- Any future print generator

### Related

- Player clue cards: only code (T1/K1/U1) + message — no faction spoilers
- GM clue cards: metadata OK, but **must stay readable** (see above)
