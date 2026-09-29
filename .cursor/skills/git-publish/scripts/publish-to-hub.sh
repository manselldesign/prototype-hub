#!/usr/bin/env bash
# Copy a prototype into manselldesign/prototype-hub/<slug>/ and list it on the hub.
#
# Usage:
#   publish-to-hub.sh <folder-with-index.html> <slug> <title> <description>
#
# Does not create a new GitHub repository.

set -euo pipefail

OWNER="manselldesign"
HUB_REPO="prototype-hub"

usage() {
  echo "Usage: publish-to-hub.sh <folder> <slug> <title> <description>" >&2
  echo "Example: publish-to-hub.sh ./prototypes/mega-hover mega-hover \"Prototype-Mega-Hover\" \"Mega menu on hover.\"" >&2
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -ne 4 ]]; then
  usage
  exit 1
fi

SRC="$1"
SLUG="$2"
TITLE="$3"
DESCRIPTION="$4"

RESERVED="tools index .cursor"
if [[ " $RESERVED " == *" $SLUG "* ]]; then
  echo "Stopped. \"$SLUG\" is reserved on the hub. Pick another slug." >&2
  exit 1
fi

if [[ ! "$SLUG" =~ ^[a-z0-9][a-z0-9-]{0,99}$ ]]; then
  echo "Slug must be lowercase letters, numbers, and hyphens, and must start with a letter or number." >&2
  exit 1
fi

if [[ ! -d "$SRC" ]]; then
  echo "Folder not found: $SRC" >&2
  exit 1
fi

if [[ ! -f "$SRC/index.html" ]]; then
  echo "Put index.html in the top of that folder, then run this again." >&2
  echo "Looked in: $SRC" >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "The gh command is missing. Install GitHub CLI, then run: gh auth login" >&2
  exit 1
fi

echo "Checking GitHub login..."
if ! LOGIN="$(gh api user --jq .login 2>/dev/null)"; then
  echo "GitHub CLI is not signed in. In this same chat, run: gh auth login" >&2
  echo "Choose GitHub.com, HTTPS, and login with a web browser (device code)." >&2
  exit 1
fi

if [[ "$LOGIN" != "$OWNER" ]]; then
  echo "This login is ${LOGIN}, not ${OWNER}. Publish only as ${OWNER}." >&2
  exit 1
fi

gh auth setup-git >/dev/null 2>&1 || true

EMAIL="$(gh api user --jq '"\(.id)+\(.login)@users.noreply.github.com"')"

WORK="$(mktemp -d)"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

echo "Cloning ${OWNER}/${HUB_REPO}..."
git clone --depth 1 "https://github.com/${OWNER}/${HUB_REPO}.git" "$WORK/hub"

DEST="$WORK/hub/$SLUG"
mkdir -p "$DEST"
cp "$SRC/index.html" "$DEST/index.html"

python3 - "$WORK/hub/index.html" "$SLUG" "$TITLE" "$DESCRIPTION" <<'PY'
import html, pathlib, re, sys

path, slug, title, description = sys.argv[1:]
url = f"https://manselldesign.github.io/prototype-hub/{slug}/#/"
file = pathlib.Path(path)
text = file.read_text()
block = (
    "        <li>\n"
    f"          <h2>{html.escape(title)}</h2>\n"
    f"          <p>{html.escape(description)}</p>\n"
    f"          <a href=\"{html.escape(url, quote=True)}\">{html.escape(url)}</a>\n"
    "        </li>\n"
)
pattern = re.compile(
    r"        <li>\s*<h2>.*?</h2>\s*<p>.*?</p>\s*"
    r"<a href=\"[^\"]*prototype-hub/" + re.escape(slug) + r"/[^\"]*\">.*?</a>\s*</li>\n?",
    re.S,
)
if pattern.search(text):
    text = pattern.sub(block, text, count=1)
    file.write_text(text)
    print("updated-card")
    raise SystemExit(0)

list_at = text.find('id="prototype-list"')
if list_at == -1:
    raise SystemExit("prototype-list was not found in index.html")
comment_end = text.find("-->", list_at)
list_end = text.find("</ul>", list_at)
if list_end == -1:
    raise SystemExit("prototype-list is missing its closing tag")
insert_at = list_end
if comment_end != -1 and comment_end < list_end:
    insert_at = comment_end + len("-->")
    if insert_at < len(text) and text[insert_at] == "\n":
        insert_at += 1
else:
    first_item = text.find("<li>", list_at)
    if first_item != -1 and first_item < list_end:
        insert_at = first_item
text = text[:insert_at] + block + text[insert_at:]
file.write_text(text)
print("added-card")
PY

if git -C "$WORK/hub" diff --quiet --exit-code && git -C "$WORK/hub" diff --cached --quiet --exit-code; then
  # New untracked slug folder still needs adding.
  if git -C "$WORK/hub" ls-files --error-unmatch "$SLUG/index.html" >/dev/null 2>&1; then
    echo "Nothing to publish: hub already has this folder and card."
    echo "https://${OWNER}.github.io/${HUB_REPO}/${SLUG}/#/"
    exit 0
  fi
fi

git -C "$WORK/hub" add "$SLUG/index.html" index.html
if git -C "$WORK/hub" diff --cached --quiet; then
  echo "Nothing to publish: hub already has this folder and card."
  echo "https://${OWNER}.github.io/${HUB_REPO}/${SLUG}/#/"
  exit 0
fi

git -C "$WORK/hub" -c user.name="$OWNER" -c user.email="$EMAIL" \
  commit -m "Publish ${TITLE} to prototype-hub/${SLUG}."

echo "Pushing main..."
git -C "$WORK/hub" push origin HEAD:main

echo ""
echo "Shareable link:"
echo "https://${OWNER}.github.io/${HUB_REPO}/${SLUG}/#/"
