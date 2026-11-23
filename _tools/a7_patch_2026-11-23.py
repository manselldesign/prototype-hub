"""2026-11-23: add A7 (alt side menu, Children only) to the Bloomington build and hub.
Run: python3 a7_patch.py <prototype-hub>"""
import sys, pathlib
ROOT = pathlib.Path(sys.argv[1])
p = ROOT/'_tools'/'bloomington'/'build.py'; s = p.read_text()
if 'A7_CSS' not in s:
    css = r"""A7_CSS = '''<style id="sidenav-a7">
  /* A7 (2026-11-23): alt side menu, Children only. Figma _rvt-sidebar-menu
     14754:4280. Desktop only; the phone menu is A6's.
     Rail 260px (A6 is 280), 8px above Back, 24px sides and bottom.
     Back: 12px arrow, 8px gap, action/sm/strong 14/20.
     Title: 32px under Back, action/lg/strong 16/24, no rule under it.
     Rows: body/xs/regular 14/20, no rules between them, 8px above and below
     (12px above the first), chevron 4px after the label instead of at the
     end of the row. All side menu text is width 100.
     4px grid: Figma overlaps the rows by 1px; here they do not overlap. */
  @media (min-width: 1024px) {
    :root { --sidenav-width: 260px; }
    #sidenav#sidenav { padding-top: 8px; padding-bottom: 24px; }
    #sidenav .nav-btn-back { gap: 8px; }
    #sidenav .t-sidenav-back { font-variation-settings: 'wght' 600, 'wdth' 100; }
    #sidenav .sidenav-after-back { padding-top: 32px; }
    #sidenav a.sidenav-title { border-bottom: 0; padding-bottom: 0; }
    #sidenav a.sidenav-title,
    #sidenav a.sidenav-title .sidenav-title-label { font-size: 16px; line-height: 24px; font-variation-settings: 'wght' 600, 'wdth' 100; }
    #sidenav .sidenav-after-back > ul > li::after { display: none; }
    #sidenav ul a.sidenav-item { padding: 8px 0; gap: 4px; }
    #sidenav ul li:first-child a.sidenav-item { padding-top: 12px; }
    #sidenav ul a.sidenav-item .sidenav-item-label { flex: 0 1 auto; font-variation-settings: 'wght' 350, 'wdth' 100; }
    #sidenav ul a.sidenav-item .sidenav-item-label.is-current { font-variation-settings: 'wght' 600, 'wdth' 100; }
  }
</style>
'''

"""
    a = s.index('CTAS = """'); s = s[:a] + css + s[a:]
    old = "def build(name, src=None, c=False, c_js=None):"
    assert old in s; s = s.replace(old, "def build(name, src=None, c=False, c_js=None, extra_css=''):")
    old = "    (DST/name).mkdir(parents=True, exist_ok=True)\n"
    assert s.count(old) == 1
    s = s.replace(old, "    if extra_css:\n        assert s.count('</body>') == 1\n        s = s.replace('</body>', extra_css + '</body>')\n" + old)
    old = "print('c1', build('c1', 'b13', True));"
    assert old in s; s = s.replace(old, "print('a7', build('a7', 'a6', extra_css=A7_CSS))\n" + old)
    p.write_text(s); print('build.py patched')
p = ROOT/'_tools'/'bloomington'/'README.md'; s = p.read_text()
old = "- Builds C1 from b13"
if 'A7' not in s:
    assert old in s; s = s.replace(old, "- Builds A7 from a6 (alt side menu, Children only; CSS in build.py, Figma 14754:4280).\n" + old); p.write_text(s)
p = ROOT/'v1.3-bloomington'/'index.html'; s = p.read_text()
if 'pair-a7' not in s:
    anchor = '      <section class="group" id="group-mega">'
    assert s.count(anchor) == 1
    new = '''      <section class="group" id="group-header-alt">
        <h2 class="group-title">A - Visible Header (Alt sidenav design)</h2>
        <p>The A6 header and drop-downs with a different side menu: no lines between rows, a larger menu title, and the chevron right after each page name.</p>
        <div class="pair" role="group" aria-labelledby="pair-a7">
          <h3 class="pair-title" id="pair-a7">A7</h3>
          <ul class="prototype-list">
            <li>
              <h2>A7 · Children · Bloomington IA</h2>
              <p>The side menu lists the pages under the current page.</p>
              <a href="https://manselldesign.github.io/prototype-hub/v1.3-bloomington/a7/#/" target="_blank" rel="noopener">https://manselldesign.github.io/prototype-hub/v1.3-bloomington/a7/#/</a>
            </li>
          </ul>
        </div>
      </section>
'''
    p.write_text(s.replace(anchor, new + anchor)); print('hub patched')
