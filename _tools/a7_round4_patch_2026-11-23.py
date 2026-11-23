"""2026-11-23: A7 round 4, chevron back after the page name, riding inline with the last word.
Run: python3 a7_round4_patch.py <prototype-hub> [mask-y-offset-px]"""
import sys, pathlib
OFF = sys.argv[2] if len(sys.argv) > 2 else '0.75'
p = pathlib.Path(sys.argv[1])/'_tools'/'bloomington'/'build.py'; s = p.read_text()
a = s.index("    /* Round 3 (Jenn, Figma 14755:4462): the chevron sits in front of the")
b = s.index("  }\n</style>\n", a)
new = """    /* Round 4 (Jenn): the chevron is back after the page name and hugs the
       text: it rides inline, 4px after the last word, and can never drop
       to a line of its own (the build swaps A6's end-of-row chevron for an
       inline one, see A7_ITEM_NEW). On a name that wraps it follows the
       last word. Optical: its middle sits 0.75px below the middle of the
       capitals (Figma 14755:4462), the visual middle of mixed-case text. */
    #sidenav ul a.sidenav-item { display: block; }
    #sidenav ul a.sidenav-item .sidenav-item-label { display: inline; }
    #sidenav ul a.sidenav-item .sidenav-item-label.is-current { font-variation-settings: 'wght' 600, 'wdth' 100; }
    #sidenav ul a.sidenav-item .sidenav-chevron-inline { margin-left: 0; -webkit-mask-position: right calc(50% + @@OFF@@px); mask-position: right calc(50% + @@OFF@@px); }
"""
s = s[:a] + new + s[b:]
old = "  @media (min-width: 1024px) {\n    :root { --sidenav-width: 260px; }"
assert s.count(old) == 1
s = s.replace(old, """  /* The chevron drawing (Rivet rvt-chevron-right-12) as a mask, so it takes
     the link's color in every state. */
  #sidenav ul a.sidenav-item .sidenav-chevron-inline {
    padding-left: 16px; margin-left: auto; background-color: currentColor;
    -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12'%3E%3Cpath d='M9.09668 6L4.42578 11.5205L2.89844 10.2295L6.47656 6L2.89844 1.77051L4.42578 0.479492L9.09668 6Z'/%3E%3C/svg%3E") no-repeat right center / 12px 12px;
    mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12'%3E%3Cpath d='M9.09668 6L4.42578 11.5205L2.89844 10.2295L6.47656 6L2.89844 1.77051L4.42578 0.479492L9.09668 6Z'/%3E%3C/svg%3E") no-repeat right center / 12px 12px;
  }
""" + old)
s = s.replace('@@OFF@@', OFF)
for x, y in [
 ("     Rows: body/xs/regular 14/20, no rules between them, chevron 4px in\n     front of the label (round 3; it was after the label). All side menu\n     text is width 100.",
  "     Rows: body/xs/regular 14/20, no rules between them, chevron 4px after\n     the label (round 3 tried it in front; round 4 put it back). All side\n     menu text is width 100."),
 ("</style>\n'''\n\nCTAS = ", """</style>
'''
# A7 swaps A6's end-of-row chevron for one that rides inline after the name.
# The word joiner (&#8288;) inside it has no width and cannot start a line,
# so the chevron always stays with the last word.
A7_ITEM_OLD = '''          (kids
            ? `<span class="sr-only">, has subpages</span>` +
              `<span class="flex h-5 w-3 shrink-0 items-center" aria-hidden="true">` +
              `<span class="sidenav-chevron block size-3">${SIDENAV_CHEVRON}</span></span>`
            : '') +
'''
A7_ITEM_NEW = '''          (kids
            ? `<span class="sidenav-chevron-inline" aria-hidden="true">&#8288;</span>` +
              `<span class="sr-only">, has subpages</span>`
            : '') +
'''

CTAS = """),
 ("    if extra_css:\n", "    if name == 'a7':\n        assert s.count(A7_ITEM_OLD) == 1, 'A7: side menu row'\n        s = s.replace(A7_ITEM_OLD, A7_ITEM_NEW)\n    if extra_css:\n"),
]:
    assert s.count(x) == 1, x[:50]
    s = s.replace(x, y)
p.write_text(s); print('ok')
