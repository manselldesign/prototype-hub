"""2026-11-23: one underline thickness on every Bloomington prototype. Run: python3 ul_patch.py <prototype-hub>"""
import sys, pathlib
p = pathlib.Path(sys.argv[1])/'_tools'/'bloomington'/'build.py'; s = p.read_text()
old = '''CSS = \'\'\'<style id="bloomington-placeholders">
'''
assert s.count(old) == 1 and 'underline-thickness' not in s
s = s.replace(old, old + '''  /* underline-thickness (2026-11-23, Jenn): every underline (selected,
     current page, hover, focus) is the same 1.5px line. Before, each one
     took its thickness from the font size, so the 14px header label drew a
     thinner line than the 16px side menu title. */
  html body * { text-decoration-thickness: 1.5px !important; }
''')
p.write_text(s); print('ok')
