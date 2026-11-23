"""2026-11-23: A7 round 3, chevrons on the left (Figma 14755:4462). Run: python3 a7_round3_patch.py <prototype-hub>"""
import sys, pathlib
p = pathlib.Path(sys.argv[1])/'_tools'/'bloomington'/'build.py'; s = p.read_text()
# 1. the wrap-fit script is not needed with the chevron in front of the name
a = s.index('<script id="sidenav-a7-fit">'); e = s.index('</script>\n', a) + len('</script>\n')
s = s[:a] + s[e:]
reps = [
("    #sidenav ul a.sidenav-item .sidenav-item-label { flex: 0 1 auto; font-variation-settings: 'wght' 350, 'wdth' 100; }",
 """    #sidenav ul a.sidenav-item .sidenav-item-label { font-variation-settings: 'wght' 350, 'wdth' 100; }
    /* Round 3 (Jenn, Figma 14755:4462): the chevron sits in front of the
       page name, 4px before it. Rows with no pages under them keep the same
       16px indent (Figma: a hidden chevron), so every name starts on the
       same line; the menu title stays flush left. */
    #sidenav ul a.sidenav-item > span[aria-hidden="true"] { order: -1; }
    #sidenav ul a.sidenav-item:not(.has-subpages) { padding-left: 16px; }"""),
("    /* Chevron: stays on the first line when a name wraps (the row is top", "    /* Chevron: stays on the first line when a name wraps (the row is top"),
("     Rows: body/xs/regular 14/20, no rules between them, chevron 4px after\n     the label instead of at the end of the row. All side menu text is\n     width 100.",
 "     Rows: body/xs/regular 14/20, no rules between them, chevron 4px in\n     front of the label (round 3; it was after the label). All side menu\n     text is width 100."),
]
for x, y in reps:
    assert s.count(x) == 1, x[:60]
    s = s.replace(x, y)
p.write_text(s); print('ok')
