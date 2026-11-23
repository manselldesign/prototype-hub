# Bloomington IA build

Builds `v1.3-bloomington/` from the zoo prototypes in `v1.3/`.

Run from anywhere: `python3 _tools/bloomington/build.py`

## What it does

- Copies each v1.3 prototype (a6, b10–b13, each with a `-gc` version) into `v1.3-bloomington/`.
- Builds A7 from a6 (alt side menu, Children only; CSS in build.py, Figma 14754:4280).
- Builds C1 from b13 / b13-gc (4-column mega menu; pages with nothing under them are stacked
  in the last column used, under a "More in {section}" line).
- Swaps the zoo IA for bloomington.iu.edu's menu tree (`data.txt`).
- Replaces page content with the real headline + breadcrumbs and cream placeholder boxes,
  stacked to the real page's length.
- Header: Campus lockup (Figma `_rvt-logo-lockup`, Type=Campus), Visit and Apply buttons.
- Long mega menus scroll inside themselves.

The hub page `v1.3-bloomington/index.html` is edited by hand, not by this script.

## Important

Design changes go in the **v1.3 zoo files first**, then re-run this script.
Editing files in `v1.3-bloomington/` directly gets overwritten on the next build.

## data.txt

One line per page, in menu order: `depth|path|nav label|headline|page height`

- depth: 0 = main section
- path: relative to the parent's folder
- headline: `=` means the same as the nav label
- page height: px at 1440 wide, measured 2026-11-23 (header + footer, 143px, are subtracted)
