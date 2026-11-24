"""One-time patch to v1.3-bloomington/index.html (2026-11-24, Jenn approved).
1. Cards: the printed URL is removed; the card title is the link and the
   whole card is still the click area.
2. A7 group description rewritten as a short list.
Kept as a record. Usage: python3 hub_cards_patch_2026-11-24.py path/to/index.html
"""
import sys, re
f = sys.argv[1]
s = open(f, encoding='utf-8').read()
def once(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70])
    s = s.replace(old, new)

# 1. Cards: the title is the link; the printed URL is gone.
pat = re.compile(r'(\n\s*)<h2>([^<]+)</h2>(\n\s*<p>.*?</p>)\n\s*<a href="([^"]+)" target="_blank" rel="noopener">\4</a>')
s, n = pat.subn(lambda m: f'{m.group(1)}<h2><a href="{m.group(4)}" target="_blank" rel="noopener">{m.group(2)}</a></h2>{m.group(3)}', s)
assert n == 13, n
once("""    .prototype-list a {
      margin-top: auto;
      padding-top: 24px;
      font-family: var(--font-mono);
      font-stretch: normal;
      font-size: 12px;
      line-height: 16px;
      letter-spacing: 1px;
      color: var(--text);
      text-decoration: none;
    }
""", """    /* 2026-11-24: the printed URL was removed from each card. The title is
       the link, and its ::after still makes the whole card the click area. */
    .prototype-list a { color: inherit; text-decoration: inherit; }
""")

# 2. A7 group description.
once("""        <p>The A6 header and drop-downs with a different side menu: no lines between rows, a larger menu title, and the chevron right after each page name.</p>
""", """        <p>The A6 header and drop-downs with a different side menu.</p>
        <ul class="notes">
          <li><strong>No lines between rows.</strong> With a larger menu title, the hierarchy is clearer.</li>
          <li><strong>Chevron next to each page name.</strong> It stays in view with the name when the screen is magnified.</li>
          <li><strong>Subtle fade.</strong> The side menu fades in when it changes, so the change is easier to notice. The drop-downs open with the same easing.</li>
        </ul>
""")
open(f, 'w', encoding='utf-8').write(s)
print('hub page patched', n, 'cards')
