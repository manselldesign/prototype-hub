"""One-time patch to _tools/bloomington/build.py (2026-11-24, Jenn approved).
A7 only (the side menu with no lines between rows):
  1. Back button sits where it does in every other version; 8px more space
     between Back and the menu title; breadcrumbs stay level with the title.
  2. Menu-change cue: when the side menu shows a different list, the whole
     menu fades in once (500ms, opacity only).
  3. Header drop-down opens in 300ms on the same curve, with no spring.
Kept as a record. Usage: python3 a7_menu_cue_patch_2026-11-24.py path/to/build.py
"""
import sys
f = sys.argv[1]
s = open(f, encoding='utf-8').read()

def once(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70])
    s = s.replace(old, new)

# ---- 1. spacing -----------------------------------------------------------
once("Rail 260px (A6 is 280), 8px above Back, 24px sides and bottom.",
     "Rail 260px (A6 is 280), 20px above Back (the same spot as every other\n"
     "     version; 8px until 2026-11-24), 24px sides and bottom.")
once("Title: 32px under Back, action/lg/strong 16/24, no rule under it.",
     "Title: 28px under Back (the versions with a rule have 20; +8 because no\n"
     "     rule separates them here), action/lg/strong 16/24, no rule under it.")
once("#sidenav#sidenav { padding-top: 8px; padding-bottom: 24px; }",
     "#sidenav#sidenav { padding-top: 20px; padding-bottom: 24px; }")
once("    #sidenav .sidenav-after-back { padding-top: 32px; }\n",
     "    #sidenav .sidenav-after-back { padding-top: 28px; }\n"
     "    /* 2026-11-24: the title is 8px lower than in the other versions, so the\n"
     "       page column follows it (64 -> 72): breadcrumbs, and the heading on\n"
     "       top-level pages, stay level with the menu title. The title is a 24px\n"
     "       line and the breadcrumbs a 20px line, so the breadcrumbs get a 2px\n"
     "       visual shift to sit on the title's exact center (nothing else moves). */\n"
     "    body.has-sidenav .interior-content { padding-top: 72px; }\n"
     "    body.has-sidenav .crumbs-trail { position: relative; top: 2px; }\n")

# ---- 2 + 3. cue and drop-down CSS, at the end of A7_CSS ---------------------
CUE_CSS = """  /* MENU-CHANGE CUE (2026-11-24). Testers did not notice the side menu had
     swapped to a new list. When the side menu shows a different list, the
     whole menu (Back, title and list together) fades in once: 500ms, on the
     curve the mega menus open with. Opacity only: nothing moves, nothing
     blurs, no color change, no layout shift, no row-by-row cascade. The
     page itself appears right away.
     Moving between pages in the SAME menu: no fade. First page load: no fade.
     Reduced motion: the same fade, shortened to 150ms.
     The links are in the page from the start, so keyboard and screen reader
     users never wait on the fade. render() sets data-cue (see A7_JS_SWAPS). */
  @keyframes menu-fade-in { from { opacity: 0; } }
  #sidenav[data-cue] > * { animation: menu-fade-in 500ms cubic-bezier(0.32, 0.08, 0.24, 1); }
  @media (prefers-reduced-motion: reduce) {
    #sidenav[data-cue] > * { animation-duration: 150ms; animation-timing-function: ease-out; }
  }
  /* Header drop-down (2026-11-24): opening slowed from 200ms to 300ms and
     moved off the small spring onto the same curve as the side menu fade,
     so the two read as one family. Still fades in and moves 6px down;
     closing is still instant. Inside no-preference so A6's reduced-motion
     rule (the panel just appears) still wins. */
  @media (prefers-reduced-motion: no-preference) {
    .masthead-nav-item.is-mega-open .nav-dropdown {
      transition:
        opacity 300ms cubic-bezier(0.32, 0.08, 0.24, 1),
        transform 300ms cubic-bezier(0.32, 0.08, 0.24, 1),
        visibility 0s;
    }
  }
"""
once("""    #sidenav ul a.sidenav-item .sidenav-item-label.is-current { font-variation-settings: 'wght' 600, 'wdth' 100; }
  }
</style>
'''
""", """    #sidenav ul a.sidenav-item .sidenav-item-label.is-current { font-variation-settings: 'wght' 600, 'wdth' 100; }
  }
""" + CUE_CSS + """</style>
'''
""")

# ---- 2. cue JS: A7-only swaps in render() ------------------------------------
JS_BLOCK = '''# A7 menu-change cue (2026-11-24): render() remembers which section the side
# menu last showed and sets data-cue on #sidenav only when it differs, so the
# fade in A7_CSS plays for a new menu and not for a new page in the same menu.
A7_JS_SWAPS = [
    (r"""
  function render() {""",
     r"""
  // MENU-CHANGE CUE (A7): which section the side menu last showed, so
  // render() can tell a new menu from a new page in the same menu.
  let cueLastSection = null;
  let cueReady = false; // no cue on the first paint

  function render() {"""),
    (r"""    backAnimating = 0;
    sidenav.innerHTML = isHome ? '' : renderSidenav(slug);""",
     r"""    backAnimating = 0;
    const cueSection = isHome ? null : (hasKids(slug) ? slug : (PAGES[slug].p && PAGES[slug].p !== HOME ? PAGES[slug].p : slug));
    if (cueReady && cueSection && cueSection !== cueLastSection) sidenav.dataset.cue = 'fade';
    else delete sidenav.dataset.cue;
    cueLastSection = cueSection; cueReady = true;
    sidenav.innerHTML = isHome ? '' : renderSidenav(slug);"""),
]

'''
once('\nCTAS = """', '\n' + JS_BLOCK + 'CTAS = """')
once("""        s = s.replace(A7_ITEM_OLD, A7_ITEM_NEW)
""", """        s = s.replace(A7_ITEM_OLD, A7_ITEM_NEW)
        for old, new in A7_JS_SWAPS:
            assert s.count(old) == 1, 'A7: menu cue ' + old[:40]
            s = s.replace(old, new)
""")
open(f, 'w', encoding='utf-8').write(s)
print('build.py patched')
