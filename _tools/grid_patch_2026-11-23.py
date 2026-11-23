"""2026-11-23: put the v1.3 prototypes on a true 4px grid (Jenn).
1px rules no longer add to heights: each rule sits inside the last/first
pixel of the padding next to it. Run: python3 grid_patch.py <prototype-hub>"""
import sys, pathlib, re
ROOT = pathlib.Path(sys.argv[1])
NAMES = ['a6', 'a6-gc', 'b10', 'b10-gc', 'b11', 'b11-gc', 'b12', 'b12-gc', 'b13', 'b13-gc']
def rep(s, old, new, name, n=None, optional=False):
    c = s.count(old)
    if c == 0 and (optional or new in s): return s
    assert c >= 1 and (n is None or c == n), f'{name}: found {c}'
    return s.replace(old, new)
for nm in NAMES:
    p = ROOT/'v1.3'/nm/'index.html'; s = p.read_text(); o = s
    s = rep(s, "--header-h: 121px;     /* 20 top + 44 lockup + 16 + 24 nav + 16 + 1px rule */",
               "--header-h: 120px;     /* 20 top + 44 lockup + 16 + 24 nav + 16 (the 1px rule is the last pixel of that 16) */", 'header-h', 1)
    s = rep(s, "below) with 16px under it. Header stays 121px (120 + the 1px rule). */\n      padding: 0 var(--chrome-gutter) 16px;",
               "below) with 16px under it: 15px + the header's 1px rule, so the\n         header is 120px in all (4px grid, 2026-11-23). */\n      padding: 0 var(--chrome-gutter) 15px;", 'nav pad', 1)
    s = rep(s, "  #sidenav a.sidenav-title {\n    padding-bottom: 12px;\n  }",
               "  #sidenav a.sidenav-title {\n    padding-bottom: 11px; /* + the 1px rule = 12 (4px grid) */\n  }", 'title pad', 1)
    s = rep(s, "    margin-top: 16px;\n    padding: 16px 0;\n    border-top: 1px solid #6D0808;",
               "    margin-top: 16px;\n    padding: 15px 0 16px; /* 15 + the 1px rule = 16 (4px grid) */\n    border-top: 1px solid #6D0808;", 'footer legal', 1)
    s = rep(s, 'class="flex items-center gap-2 border-y border-cream py-3 t15 text-ink lg:hover:underline"',
               'class="flex items-center gap-2 border-t border-cream pt-[11px] pb-3 shadow-[0_1px_0_#EDDDC4] t15 text-ink lg:hover:underline"', 'popular rows')
    s = rep(s, '<li class="-mb-px">', '<li>', 'popular li')
    if nm.endswith('-gc'):
        s = rep(s, "#sidenav .sidenav-after-back > ul.sg-list { padding: 0; margin: -1px 0 0; display: flex;", "#sidenav .sidenav-after-back > ul.sg-list { padding: 0; margin: 0; display: flex;", 'sg-list', 1)
        s = rep(s, "  #sidenav .sg-group + .sg-group { margin-top: -1px; }\n", "", 'sg-group', 1)
        s = rep(s, "cream rule above it (none under the last), rules collapsed by 1px. */", "cream rule above it (none under the last). The rule is drawn inside the\n     group's top padding, so every group stays on the 4px grid. */", 'sg comment', 1)
    s = rep(s, "top: calc(100% - 1px);", "top: 100%; /* header is 120px with its rule inside (was 121 - 1) */", 'mega top', 1)
    s = rep(s, ".crumbs-spacer { display: block; height: 0; margin-bottom: -2px; }",
               ".crumbs-spacer { display: block; height: 0; }\n    /* 4px grid (2026-11-23): the 2px optical pull is now a visual shift of\n       the heading only, so nothing under it leaves the grid. */\n    .crumbs-spacer + * { position: relative; top: -2px; }", 'crumbs spacer', 1)
    # Fluid text: line heights step in 4px between the phone and desktop sizes.
    if 'line-height:round(' not in s:
        s, k = re.subn(r'^(\s*)line-height:(clamp\([^;]+\));$', lambda m: f"{m.group(1)}line-height:{m.group(2)};\n{m.group(1)}line-height:round({m.group(2)}, 4px); /* 4px grid */", s, flags=re.M)
        assert k == 4, f'fluid line heights: {k}'
    if s != o: p.write_text(s)
    print(nm, 'patched' if s != o else 'unchanged')

# Bloomington build: placeholder boxes on the 4px grid.
p = ROOT/'_tools'/'bloomington'/'build.py'; s = p.read_text(); o = s
for old, new in [
    (".ph { box-sizing: border-box; overflow: hidden; background: #FAF6EF; padding: 24px; display: flex; flex-direction: column; gap: 14px; }",
     ".ph { box-sizing: border-box; overflow: hidden; background: #FAF6EF; padding: 24px; display: flex; flex-direction: column; gap: 16px; }"),
    (".ph-bar { display: block; height: 10px; background: #EDDDC4; flex: none; }", ".ph-bar { display: block; height: 8px; background: #EDDDC4; flex: none; }"),
    (".ph-bar--head { height: 16px; margin-bottom: 6px; }", ".ph-bar--head { height: 16px; margin-bottom: 8px; }"),
    (".ph-row { display: flex; align-items: center; gap: 12px; height: 10px; flex: none; }", ".ph-row { display: flex; align-items: center; gap: 12px; height: 8px; flex: none; }"),
    (".ph-card { display: flex; flex-direction: column; gap: 14px; padding: 20px;", ".ph-card { display: flex; flex-direction: column; gap: 16px; padding: 20px;"),
    ("const kinds = [['text', 228], ['media', 360], ['list', 178], ['cards', 264], ['text', 180], ['list', 226]];", "const kinds = [['text', 228], ['media', 360], ['list', 180], ['cards', 264], ['text', 180], ['list', 228]];"),
    ("h = Math.max(48, left - (first ? 0 : gap)); left = 0;", "h = Math.max(48, Math.round((left - (first ? 0 : gap)) / 4) * 4); left = 0;"),
    ("class=\"flex items-center gap-2 border-y border-cream py-3 t15 text-ink lg:hover:underline\">", "class=\"flex items-center gap-2 border-t border-cream pt-[11px] pb-3 shadow-[0_1px_0_#EDDDC4] t15 text-ink lg:hover:underline\">"),
    ("Math.floor((h - 48 - 36) / 24)", "Math.floor((h - 48 - 40) / 24)"),
    ("Math.floor((h - 48 + 14) / 24)", "Math.floor((h - 48 + 16) / 24)"),
    ("'          <li class=\"-mb-px\">\\n'", "'          <li>\\n'"),
]:
    s = rep(s, old, new, 'build.py ' + old[:30], 1)
if s != o: p.write_text(s)
print('build.py', 'patched' if s != o else 'unchanged')
