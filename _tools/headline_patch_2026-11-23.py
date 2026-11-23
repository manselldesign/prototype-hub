"""2026-11-23: detail-page headline uses the Hero Callout headline style. Run: python3 headline_patch.py <prototype-hub>"""
import sys, pathlib
p = pathlib.Path(sys.argv[1])/'_tools'/'bloomington'/'build.py'; s = p.read_text()
anchor = '''  /* Underlines (2026-11-23, Jenn): every underline'''
assert s.count(anchor) == 1 and 'hero-callout-headline' not in s
s = s.replace(anchor, '''  /* hero-callout-headline (2026-11-23, Jenn): the headline on detail pages
     (every page below a main section) uses the Rivet Hero Callout headline
     style, display/lg/strong (Figma rvt-hero-callout 13491:17647): 29px on
     phones to 48px on desktop, line 32 to 52, Bold 700, width 100. It was
     the same size but heavier (750) and narrower (width 87.5). */
  main .rvt-hero__title.hero-title { font-weight: 700; font-stretch: 100%; }
''' + anchor)
p.write_text(s); print('ok')
