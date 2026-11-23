"""2026-11-23: A7 round 2, from Figma 14755:4462. Run: python3 a7_round2_patch.py <prototype-hub>"""
import sys, pathlib
p = pathlib.Path(sys.argv[1])/'_tools'/'bloomington'/'build.py'; s = p.read_text()
reps = [
("""     Rows: body/xs/regular 14/20, no rules between them, 8px above and below
     (12px above the first), chevron 4px after the label instead of at the
     end of the row. All side menu text is width 100.
     4px grid: Figma overlaps the rows by 1px; here they do not overlap. */""",
 """     Rows: body/xs/regular 14/20, no rules between them, chevron 4px after
     the label instead of at the end of the row. All side menu text is
     width 100.
     Round 2 (Figma 14755:4462): the title is underlined when it is the
     page you are on (as before; underline now from-font); 16px from the
     title to the first row; rows are one 20px line with 12px between them
     (each link's click area still reaches 6px above and below, 32px in
     all); the chevron sits 0.75px low (Figma: 1.5px above it in a centered
     box) so it reads centered on the text. */"""),
("""    #sidenav ul a.sidenav-item { padding: 8px 0; gap: 4px; }
    #sidenav ul li:first-child a.sidenav-item { padding-top: 12px; }
""",
 """    #sidenav a.sidenav-title .sidenav-title-label { text-underline-position: from-font; }
    #sidenav .sidenav-after-back > ul { display: flex; flex-direction: column; gap: 12px; padding-top: 16px; }
    #sidenav ul a.sidenav-item { position: relative; padding: 0; gap: 4px; }
    #sidenav ul a.sidenav-item::before { content: ''; position: absolute; inset: -6px 0; }
"""),
("""       aligned and the chevron's box is one 20px line tall). Optical: the
       line box centers it on the capitals; 1px lower puts it on the visual
       middle of mixed-case text (a shift only, the layout does not move). */
    #sidenav ul a.sidenav-item .sidenav-chevron { transform: translateY(1px); }""",
 """       aligned and the chevron's box is one 20px line tall). Optical: the
       line box centers it on the capitals; 0.75px lower (Figma) puts it on
       the visual middle of mixed-case text (a shift only, the layout does
       not move). */
    #sidenav ul a.sidenav-item .sidenav-chevron { transform: translateY(0.75px); }"""),
]
for a, b in reps:
    assert s.count(a) == 1, a[:50]
    s = s.replace(a, b)
p.write_text(s); print('ok')
