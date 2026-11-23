"""2026-11-23: underlines, round 2: 1px and the same distance from the text everywhere (the side menu's). Run: python3 ul2_patch.py <prototype-hub>"""
import sys, pathlib
p = pathlib.Path(sys.argv[1])/'_tools'/'bloomington'/'build.py'; s = p.read_text()
old = '''  /* underline-thickness (2026-11-23, Jenn): every underline (selected,
     current page, hover, focus) is the same 1.5px line. Before, each one
     took its thickness from the font size, so the 14px header label drew a
     thinner line than the 16px side menu title. */
  html body * { text-decoration-thickness: 1.5px !important; }
'''
new = '''  /* Underlines (2026-11-23, Jenn): every underline (selected, current
     page, hover, focus; header, drop-downs, mega menus, side menu,
     breadcrumbs, footer) is the same 1px line at the same distance from
     the text: the font's own underline spot, as in the side menu. Before,
     the header and menu links sat 2-3px lower and each line took its
     thickness from its text size. */
  html body * {
    text-decoration-thickness: 1px !important;
    text-underline-position: from-font !important;
    text-underline-offset: 0 !important;
  }
'''
assert s.count(old) == 1
p.write_text(s.replace(old, new)); print('ok')
