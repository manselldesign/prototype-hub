import re, json, os, pathlib, html
HERE = pathlib.Path(__file__).resolve().parent
H = HERE.parents[1]  # the prototype-hub folder
SRC = H/'v1.3'; DST = H/'v1.3-bloomington'
SITE_NAME = 'Indiana University Bloomington'
CHROME = 143  # real page header + footer, taken off the measured total

# ---------- data ----------
rows = [l.split('|') for l in open(HERE/'data.txt', encoding='utf8').read().rstrip('\n').split('\n')]
pages = {'index': {'t': SITE_NAME, 'l': 'Home', 'v': 0, 'c': [], 'h': 'Where impact takes shape', 'n': 9771 - CHROME, 'u': '/'}}
stack = [('index', '/')]  # (slug, dir)
for d, rel, label, h1, total in rows:
    d = int(d); stack = stack[:d + 1]
    pslug, pdir = stack[-1]
    path = pdir + rel
    slug = path.strip('/').replace('.html', '').replace('/', '-')
    assert slug not in pages, slug
    pages[slug] = {'t': f'{label} - {SITE_NAME}', 'l': label, 'v': d + 1, 'p': pslug, 'h': label if h1 == '=' else h1, 'n': int(total) - CHROME, 'u': path}
    pages[pslug].setdefault('c', []).append(slug)
    stack.append((slug, path if path.endswith('/') else pdir))
for p in pages.values():
    if 'c' in p and not p['c']: del p['c']
SITE = {'home': 'index', 'pages': pages}
TOP = pages['index']['c']
print(len(pages), 'pages;', TOP)

POPULAR = ['admissions-apply', 'cost-aid-cost-attendance', 'academics-calendars', 'admissions-visit', 'campus-life-housing-dining']
for s in POPULAR: assert s in pages, s

JS_FUNCS = r'''
  /* =========================================================================
     Bloomington IA (2026-11-23). The navigation is bloomington.iu.edu's own
     menu tree. Page content is not reproduced: each page keeps its real
     headline and breadcrumbs, and the rest of the column is cream
     placeholder boxes stacked to the real page's length (PAGES[slug].n,
     measured at 1440px wide).
     ========================================================================= */
  function renderPlaceholderPage(slug, p) {
    const stack = `<p class="sr-only">Page content is not shown in this prototype.</p>` +
                  `<div class="ph-stack" aria-hidden="true"></div>`;
    if (slug === HOME) {
      return (
        `<div class="rvt-hero rvt-hero--statement bg-white pb-16">` +
        `<div class="mx-auto max-w-[1600px] px-4 lg:px-20">` +
        `<div class="flex flex-col items-center pb-8 pt-16 text-center lg:pt-[108px]">` +
        `<h1 class="rvt-hero__title hero-title-display text-crimson">${esc(p.h)}</h1>` +
        `</div>${stack}</div></div>`
      );
    }
    const h1Class = p.v <= 1 ? 'hero-title-display' : 'hero-title';
    return (
      `<div class="rvt-hero rvt-hero--feature interior-content px-4 pb-10 pt-6 lg:pb-12 lg:pl-[60px] lg:pr-10">` +
      renderBreadcrumbs(slug) +
      `<h1 class="rvt-hero__title ${h1Class} text-crimson">${esc(p.h)}</h1>` +
      stack +
      `</div>`
    );
  }
  function placeholderBlock(kind, h) {
    const bar = (w) => `<span class="ph-bar" style="width:${w}%"></span>`;
    let inner = '';
    if (kind === 'text') {
      const n = Math.max(0, Math.floor((h - 48 - 40) / 24));
      const widths = [100, 96, 100, 92, 98, 64];
      inner = `<span class="ph-bar ph-bar--head" style="width:38%"></span>` +
        Array.from({ length: n }, (_, i) => bar(i === n - 1 ? 58 : widths[i % widths.length])).join('');
    } else if (kind === 'list') {
      const n = Math.max(1, Math.floor((h - 48 + 16) / 24));
      inner = Array.from({ length: n }, (_, i) => {
        const sub = i % 4 >= 2;
        return `<span class="ph-row${sub ? ' ph-row--sub' : ''}"><span class="ph-dot"></span>${bar(sub ? 56 : 70)}</span>`;
      }).join('');
    } else if (kind === 'cards') {
      inner = `<span class="ph-cards">` + [0, 1, 2].map(() =>
        `<span class="ph-card"><span class="ph-bar ph-bar--head" style="width:60%"></span>${bar(100)}${bar(82)}</span>`).join('') + `</span>`;
    }
    return `<div class="ph ph--${kind}" style="height:${h}px">${inner}</div>`;
  }
  function fillPlaceholders(slug) {
    const stack = main.querySelector('.ph-stack');
    if (!stack) return;
    const target = PAGES[slug].n || 1200;
    stack.innerHTML = '';
    // main is stretched by the page layout, so measure its content instead.
    let left = target - main.firstElementChild.offsetHeight;
    let seed = 0;
    for (const ch of slug) seed = (seed * 31 + ch.charCodeAt(0)) >>> 0;
    const kinds = [['text', 228], ['media', 360], ['list', 180], ['cards', 264], ['text', 180], ['list', 228]];
    const gap = 32;
    let out = '';
    let i = seed % kinds.length;
    let first = true;
    while (left > 0) {
      let [k, h] = kinds[i % kinds.length];
      i += 1;
      // Right under the headline the first box is always plain lines.
      if (first) { k = 'text'; h = 228; }
      const need = h + (first ? 0 : gap);
      if (left - need < 120) { h = Math.max(48, Math.round((left - (first ? 0 : gap)) / 4) * 4); left = 0; if (h < 150 && !first) k = 'media'; }
      else left -= need;
      out += placeholderBlock(k, h);
      first = false;
    }
    stack.innerHTML = out;
  }

'''

CSS = '''<style id="bloomington-placeholders">
  /* Long mega menus: the open menu is never taller than the screen below
     the header, and scrolls inside itself so every link can be reached. */
  .mega-panel {
    max-height: calc(100vh - var(--header-h));
    max-height: calc(100dvh - var(--header-h));
    overflow-y: auto;
    overscroll-behavior: contain;
  }
  /* Header lockup = Figma _rvt-logo-lockup, Type=Campus, Color=Default:
     44px mark, 6px gap, then two lines 2px apart (1px above).
     component/lockup/campus-title 16/16, wght 600, wdth 40, +0.25px, caps.
     component/lockup/campus-name  14/14, wght 350, wdth 40, caps. */
  .lockup-text { display: flex; flex-direction: column; gap: 2px; padding-top: 1px; color: #000000; text-transform: uppercase; white-space: nowrap; }
  .lockup-campus-title { font-size: 16px; line-height: 16px; letter-spacing: 0.25px; font-variation-settings: 'wght' 600, 'wdth' 40; }
  .lockup-campus-name { font-size: 14px; line-height: 14px; letter-spacing: 0; font-variation-settings: 'wght' 350, 'wdth' 40; }
  /* Cream placeholder boxes that stand in for page content. */
  .ph-stack { display: flex; flex-direction: column; gap: 32px; margin-top: 32px; max-width: 54rem; }
  .rvt-hero--statement .ph-stack { max-width: none; margin-top: 0; }
  .ph { box-sizing: border-box; overflow: hidden; background: #FAF6EF; padding: 24px; display: flex; flex-direction: column; gap: 16px; }
  .ph-bar { display: block; height: 8px; background: #EDDDC4; flex: none; }
  .ph-bar--head { height: 16px; margin-bottom: 8px; }
  .ph-row { display: flex; align-items: center; gap: 12px; height: 8px; flex: none; }
  .ph-row--sub { padding-left: 32px; }
  .ph-dot { width: 8px; height: 8px; border-radius: 50%; background: #EDDDC4; flex: none; }
  .ph-row--sub .ph-dot { background: transparent; box-shadow: inset 0 0 0 1.5px #EDDDC4; }
  .ph-cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px; height: 100%; }
  .ph-card { display: flex; flex-direction: column; gap: 16px; padding: 20px; box-shadow: inset 0 0 0 1px #EDDDC4; background: #fff; }
  @media (max-width: 639px) { .ph-cards { grid-template-columns: 1fr; } .ph-card:nth-child(n+2) { display: none; } }
</style>
'''

C_JS = r'''    /* C1: four columns. Column 1 is Overview and Close, as in
       B13. Pages with pages under them are sorted by how many they have
       (most first, ties A to Z) and fill the next columns row by row.
       Pages with nothing under them are stacked A to Z in the column right
       after the last one used in the first row, never further right.
       2026-11-23: that stack sits under a "More in {section}" line (left
       out when the stack is the only thing in the menu). */
    const count = (s) => (PAGES[s].c || []).filter((g) => PAGES[g]).length;
    const all = (PAGES[sectionSlug].c || []).filter((s) => PAGES[s]);
    const byName = (a, b) => PAGES[a].l.localeCompare(PAGES[b].l);
    const groups = all.filter((s) => count(s) > 0).sort((a, b) => count(b) - count(a) || byName(a, b));
    const leaves = all.filter((s) => count(s) === 0).sort(byName);
    const per = leaves.length ? Math.min(groups.length, 2) : 3;
    /* The groups sit in their own grid, so a long stack beside them cannot
       stretch their rows off the 4px grid. */
    const cells = groups.length
      ? `<div class="mega-groups" style="grid-column:1 / span ${per};grid-template-columns:repeat(${per},minmax(0,1fr))">${groups.map(col).join('')}</div>`
      : '';
    const more = groups.length
      ? `<p class="mega-more" id="mega-more-label">More in ${esc(sectionNavLabel(sectionSlug))}</p>`
      : '';
    const side = leaves.length
      ? `<div class="mega-leaves"${more ? ' role="group" aria-labelledby="mega-more-label"' : ''} style="grid-column:${per + 1}">${more}${leaves.map(col).join('')}</div>`
      : '';
    return `<div class="mega-layout mega-c-layout">${overview}<div class="mega-grid">${cells}${side}</div></div>`;
'''

C_CSS = '''<style id="mega-c">
  /* C1: Overview and Close in column 1 (B13), then three equal columns.
     Spacing (4px grid, 2026-11-23): 12px from a heading to its list (from
     B13); in the stack of pages with nothing under them, 12px from the
     "More in" line to the first link and 12px between links.
     "More in" line: 14/20 regular, body #343C42, same as the page links, in
     a 24px row (2px above and below) so it sits level with the headings
     beside it and the first link starts level with their first page link. */
  .mega-c-layout .mega-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); column-gap: 48px; row-gap: 40px; justify-content: stretch; }
  .mega-c-layout .mega-groups { display: grid; column-gap: 48px; row-gap: 40px; align-content: start; min-width: 0; }
  .mega-c-layout .mega-leaves { display: flex; flex-direction: column; align-items: flex-start; gap: 12px; min-width: 0; }
  .mega-c-layout .mega-more { margin: 0; padding: 2px 0; font-size: 14px; line-height: 20px; font-weight: 350; font-variation-settings: 'wght' 350, 'wdth' 115; color: #343C42; }
  @media (max-width: 1279px) { .mega-c-layout .mega-grid, .mega-c-layout .mega-groups { column-gap: 24px; } }
</style>
'''

A7_CSS = '''<style id="sidenav-a7">
  /* A7 (2026-11-23): alt side menu, Children only. Figma _rvt-sidebar-menu
     14754:4280. Desktop only; the phone menu is A6's.
     Rail 260px (A6 is 280), 8px above Back, 24px sides and bottom.
     Back: 12px arrow, 8px gap, action/sm/strong 14/20.
     Title: 32px under Back, action/lg/strong 16/24, no rule under it.
     Rows: body/xs/regular 14/20, no rules between them, chevron 4px after
     the label (round 3 tried it in front; round 4 put it back). All side
     menu text is width 100.
     Round 2 (Figma 14755:4462): the title is underlined when it is the
     page you are on (as before; underline now from-font); 16px from the
     title to the first row; rows are one 20px line with 12px between them
     (each link's click area still reaches 6px above and below, 32px in
     all); the chevron sits 0.75px low (Figma: 1.5px above it in a centered
     box) so it reads centered on the text. */
  /* The chevron drawing (Rivet rvt-chevron-right-12) as a mask, so it takes
     the link's color in every state. */
  #sidenav ul a.sidenav-item .sidenav-chevron-glyph {
    display: inline-block; width: 12px; height: 12px; margin-left: 4px;
    background-color: currentColor;
    -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12'%3E%3Cpath d='M9.09668 6L4.42578 11.5205L2.89844 10.2295L6.47656 6L2.89844 1.77051L4.42578 0.479492L9.09668 6Z'/%3E%3C/svg%3E") no-repeat center / 12px 12px;
    mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12'%3E%3Cpath d='M9.09668 6L4.42578 11.5205L2.89844 10.2295L6.47656 6L2.89844 1.77051L4.42578 0.479492L9.09668 6Z'/%3E%3C/svg%3E") no-repeat center / 12px 12px;
    /* Visual middle of the words: halfway between the middle of the
       capitals and the middle of the lowercase letters. vertical-align puts
       the box's middle on the middle of the capitals (browsers snap it to
       whole pixels); the 0.75px shift lowers it to the visual middle (the
       same 0.75px as Figma 14755:4462). */
    vertical-align: -1px;
    transform: translateY(0.75px);
  }
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
    #sidenav a.sidenav-title .sidenav-title-label { text-underline-position: from-font; }
    #sidenav .sidenav-after-back > ul { display: flex; flex-direction: column; gap: 12px; padding-top: 16px; }
    #sidenav ul a.sidenav-item { position: relative; padding: 0; gap: 4px; }
    #sidenav ul a.sidenav-item::before { content: ''; position: absolute; inset: -6px 0; }
    #sidenav ul a.sidenav-item .sidenav-item-label { font-variation-settings: 'wght' 350, 'wdth' 100; }
    /* Round 4 (Jenn): the chevron is back after the page name and hugs the
       text: it rides inline, 4px after the last word, and can never drop
       to a line of its own (the build swaps A6's end-of-row chevron for an
       inline one, see A7_ITEM_NEW). On a name that wraps it follows the
       last word. Its middle sits halfway between the middle of the
       capitals and the middle of the lowercase (see .sidenav-chevron-glyph). */
    #sidenav ul a.sidenav-item { display: block; }
    #sidenav ul a.sidenav-item .sidenav-item-label { display: inline; }
    #sidenav ul a.sidenav-item .sidenav-item-label.is-current { font-variation-settings: 'wght' 600, 'wdth' 100; }
  }
</style>
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
            ? `<span class="sidenav-chevron-inline" aria-hidden="true">&#8288;<span class="sidenav-chevron-glyph"></span></span>` +
              `<span class="sr-only">, has subpages</span>`
            : '') +
'''

CTAS = """
              <a data-nav href="#/admissions-visit" class="masthead-cta">
                <span class="t16">Visit</span>
                <span data-icon="arrow-right" class="block size-3 shrink-0"></span>
              </a>
              <a data-nav href="#/admissions-apply" class="masthead-cta">
                <span class="t16">Apply</span>
                <span data-icon="arrow-right" class="block size-3 shrink-0"></span>
              </a>"""
DRAWER_CTAS = """
          <a data-nav href="#/admissions-visit"
             class="nav-btn nav-btn-cta w-full border border-crimson text-crimson sm:flex-1">
            <span class="t14 flex-1">Visit</span>
            <span data-icon="arrow-right" class="block size-4 shrink-0"></span>
          </a>
          <a data-nav href="#/admissions-apply"
             class="nav-btn nav-btn-cta w-full border border-crimson text-crimson sm:flex-1">
            <span class="t14 flex-1">Apply</span>
            <span data-icon="arrow-right" class="block size-4 shrink-0"></span>
          </a>"""

def sub1(s, pat, rep, name, flags=0, count=1):
    s2, n = re.subn(pat, lambda m: rep if isinstance(rep, str) else rep(m), s, count=count, flags=flags)
    assert n >= 1, f'missing: {name}'
    return s2

def popular_li(slug):
    return ('          <li>\n'
            f'            <a data-nav href="#/{slug}"\n'
            '               class="flex items-center gap-2 border-t border-cream pt-[11px] pb-3 shadow-[0_1px_0_#EDDDC4] t15 text-ink lg:hover:underline">\n'
            f'              <span class="min-w-0 flex-1">{html.escape(pages[slug]["l"])}</span>\n'
            '              <span data-icon="arrow-right" class="block size-4 shrink-0" aria-hidden="true"></span>\n'
            '            </a>\n          </li>\n')

def build(name, src=None, c=False, c_js=None, extra_css=''):
    s = (SRC/(src or name)/'index.html').read_text()
    # data
    s = sub1(s, r'const SITE = \{.*\};?\n', '    const SITE = ' + json.dumps(SITE, ensure_ascii=False, separators=(',', ':')).replace('\\', '\\\\') + ';\n', 'SITE')
    s = s.replace('const SITE =     const SITE', 'const SITE')
    s = re.sub(r'^ *    const SITE = ', '    const SITE = ', s, count=1, flags=re.M)
    nav = '  const HEADER_NAV = [\n' + ''.join(f"    [{json.dumps(t)}, {json.dumps(pages[t]['l'])}],\n" for t in TOP) + '  ].filter(([slug]) => PAGES[slug]);\n'
    s = sub1(s, r'  const HEADER_NAV = \[.*?\]\.filter\(\(\[slug\]\) => PAGES\[slug\]\);\n', nav, 'HEADER_NAV', re.S)
    s = sub1(s, r'  const TB_COPY = \{.*?\n  \};\n(?=  function copyFor)', '  const TB_COPY = {};\n', 'TB_COPY', re.S)
    # content
    s = sub1(s, r'(?=  /\*\* Home hero)', JS_FUNCS, 'insert funcs')
    s = sub1(s, r'  function renderHome\(p\) \{\n', '  function renderHome(p) {\n    return renderPlaceholderPage(HOME, p);\n', 'renderHome')
    s = sub1(s, r'  function renderInterior\(slug, p\) \{\n', '  function renderInterior(slug, p) {\n    return renderPlaceholderPage(slug, p);\n', 'renderInterior')
    s = sub1(s, r"(      if \(typeof fitCrumbs === 'function'\) fitCrumbs\(\);\n)", lambda m: m.group(1) + "      { const sl = currentSlug(); if (sl !== null) fillPlaceholders(sl); }\n", 'refill')
    s = sub1(s, r'(    main\.innerHTML = isHome \? renderHome\(p\) : renderInterior\(slug, p\);\n)', lambda m: m.group(1) + '    fillPlaceholders(slug);\n', 'fill')
    # A6 drop-downs: with 8 sections the last menus would run off the right
    # edge while closed and add a sideways scroll, so place them all up front.
    if 'function placeDropdown(item)' in s:
        place = "document.querySelectorAll('.masthead-nav-item').forEach((it) => placeDropdown(it));"
        s = sub1(s, r"(    renderHeaderNav\(slug\);\n    closeMega\(\);\n)", lambda m: m.group(1) + "    " + place + "\n", 'place on render')
        s = sub1(s, r"(      \{ const sl = currentSlug\(\); if \(sl !== null\) fillPlaceholders\(sl\); \}\n)", lambda m: m.group(1) + "      " + place + "\n", 'place on remeasure')
        s = sub1(s, r"(  window\.addEventListener\('load', remeasureLayout\);\n)", lambda m: m.group(1) + "  window.addEventListener('resize', remeasureLayout);\n", 'resize')
    # chrome
    # Header buttons: Visit and Apply, in the same button design as v1.3.
    s = sub1(s, r'(<div class="masthead-ctas">).*?(\s*</div>\n)', lambda m: m.group(1) + CTAS + m.group(2), 'ctas', re.S)
    s = sub1(s, r'(<div class="drawer-ctas[^>]*>).*?(\s*</div>\n)', lambda m: m.group(1) + DRAWER_CTAS + m.group(2), 'drawer ctas', re.S)
    s = sub1(s, r'(<h2 id="popular-searches-heading"[^>]*>Popular searches</h2>\n\s*<ul class="pt-2">\n).*?(        </ul>)', lambda m: m.group(1) + ''.join(popular_li(x) for x in POPULAR) + m.group(2), 'popular', re.S)
    n = s.count('Indiana Zooniversity'); assert n >= 5, n
    s = s.replace('Indiana Zooniversity', SITE_NAME)
    old = '<span class="rvt-lockup__title t1">' + SITE_NAME + '</span>'
    assert s.count(old) == 1, 'lockup'
    s = s.replace(old, '<span class="lockup-text"><span class="lockup-campus-title">Indiana University</span>'
                       '<span class="lockup-campus-name">Bloomington</span></span>')
    s = s.replace('</body>\n</html>', CSS + '</body>\n</html>') if '</body>\n</html>' in s else s.replace('</body>', CSS + '</body>')
    assert 'bloomington-placeholders' in s
    if c:
        old = "    return `<div class=\"mega-layout\">${overview}<div class=\"mega-grid\">${megaColumnOrder(sectionSlug).map(col).join('')}</div></div>`;\n"
        assert s.count(old) == 1, 'C: mega return'
        s = s.replace(old, c_js or C_JS)
        s = s.replace('<style id="bloomington-placeholders">', C_CSS + '<style id="bloomington-placeholders">')
        assert 'mega-c-layout' in s
    if name == 'a7':
        assert s.count(A7_ITEM_OLD) == 1, 'A7: side menu row'
        s = s.replace(A7_ITEM_OLD, A7_ITEM_NEW)
    if extra_css:
        assert s.count('</body>') == 1
        s = s.replace('</body>', extra_css + '</body>')
    (DST/name).mkdir(parents=True, exist_ok=True)
    (DST/name/'index.html').write_text(s)
    return len(s)

for n in ['a6', 'a6-gc', 'b10', 'b10-gc', 'b11', 'b11-gc', 'b12', 'b12-gc', 'b13', 'b13-gc']:
    print(n, build(n))
print('a7', build('a7', 'a6', extra_css=A7_CSS))
print('c1', build('c1', 'b13', True)); print('c1-gc', build('c1-gc', 'b13-gc', True))
