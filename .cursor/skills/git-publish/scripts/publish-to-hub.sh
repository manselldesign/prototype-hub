#!/usr/bin/env bash
# Copy a prototype into manselldesign/prototype-hub/<group>/<slug>/ and list it
# on the main hub and that group's page.
#
# Usage:
#   publish-to-hub.sh <folder-with-index.html> <slug> <title> <description> [group]
#
# Group is mega, header, sidebar, drill-down, or breadcrumbs.
# If omitted, it is inferred from the slug (mega-*, header-*, sidebar-*,
# breadcrumb*, drill-*).
#
# Does not create a new GitHub repository.

set -euo pipefail

OWNER="manselldesign"
HUB_REPO="prototype-hub"

usage() {
  echo "Usage: publish-to-hub.sh <folder> <slug> <title> <description> [group]" >&2
  echo "Example: publish-to-hub.sh ./mega-click-icon-simple mega-click-icon-simple \"mega-click-icon-simple\" \"Chevron opens the menu.\" mega" >&2
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 4 || $# -gt 5 ]]; then
  usage
  exit 1
fi

SRC="$1"
SLUG="$2"
TITLE="$3"
DESCRIPTION="$4"
GROUP="${5:-}"

if [[ -z "$GROUP" ]]; then
  case "$SLUG" in
    mega-*) GROUP="mega" ;;
    header-*) GROUP="header" ;;
    sidebar-*) GROUP="sidebar" ;;
    breadcrumb*) GROUP="breadcrumbs" ;;
    drill-*) GROUP="drill-down" ;;
  esac
fi

RESERVED="tools index .cursor mega header sidebar drill-down breadcrumbs"
if [[ " $RESERVED " == *" $SLUG "* ]]; then
  echo "Stopped. \"$SLUG\" is reserved on the hub. Pick another slug." >&2
  exit 1
fi

if [[ -z "$GROUP" ]]; then
  echo "Could not tell which group \"$SLUG\" belongs in." >&2
  echo "Pass one of: mega, header, sidebar, drill-down, breadcrumbs." >&2
  exit 1
fi

case "$GROUP" in
  mega|header|sidebar|drill-down|breadcrumbs) ;;
  *)
    echo "Unknown group \"$GROUP\". Use mega, header, sidebar, drill-down, or breadcrumbs." >&2
    exit 1
    ;;
esac

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

if [[ ! -f "$WORK/hub/$GROUP/index.html" ]]; then
  echo "The $GROUP group page is missing. Add $GROUP/index.html before publishing into it." >&2
  exit 1
fi

DEST="$WORK/hub/$GROUP/$SLUG"
mkdir -p "$DEST"
cp "$SRC/index.html" "$DEST/index.html"

python3 - "$WORK/hub/index.html" "$WORK/hub/$GROUP/index.html" "$GROUP" "$SLUG" "$TITLE" "$DESCRIPTION" <<'PY'
import html, pathlib, re, sys

home_path, group_path, group, slug, title, description = sys.argv[1:]
url = f"https://manselldesign.github.io/prototype-hub/{group}/{slug}/#/"
block = (
    "          <li>\n"
    f"            <h2>{html.escape(title)}</h2>\n"
    f"            <p>{html.escape(description)}</p>\n"
    f"            <a href=\"{html.escape(url, quote=True)}\">{html.escape(url)}</a>\n"
    "          </li>\n"
)
pattern = re.compile(
    r"          <li>\s*<h2>(?:(?!</li>).)*?</h2>\s*<p>(?:(?!</li>).)*?</p>\s*"
    r"<a href=\"[^\"]*(?:/" + re.escape(group) + "/" + re.escape(slug) + r"/|/"
    + re.escape(slug) + r"/#)[^\"]*\">(?:(?!</li>).)*?</a>\s*</li>\n?",
    re.S,
)

def upsert(path):
    file = pathlib.Path(path)
    text = file.read_text()
    marker = f'id="group-{group}"'
    start = text.find(marker)
    if start < 0:
        raise SystemExit(f"{marker} was not found in {path}")
    ul_open = '<ul class="prototype-list">'
    ul = text.find(ul_open, start)
    ul_end = text.find("</ul>", ul)
    next_section = text.find("<section", start + len(marker))
    if ul < 0 or ul_end < 0 or (next_section != -1 and ul > next_section):
        raise SystemExit(f"prototype list for {group} was not found in {path}")
    region = text[ul:ul_end]
    if pattern.search(region):
        region = pattern.sub(block, region, count=1)
        file.write_text(text[:ul] + region + text[ul_end:])
        print(f"updated-card {path}")
        return
    insert = ul + len(ul_open) + 1
    file.write_text(text[:insert] + block + text[insert:])
    print(f"added-card {path}")

upsert(home_path)
upsert(group_path)
PY

REL_HTML="$GROUP/$SLUG/index.html"
if git -C "$WORK/hub" diff --quiet --exit-code && git -C "$WORK/hub" diff --cached --quiet --exit-code; then
  if git -C "$WORK/hub" ls-files --error-unmatch "$REL_HTML" >/dev/null 2>&1; then
    echo "Nothing to publish: hub already has this folder and card."
    echo "https://${OWNER}.github.io/${HUB_REPO}/${GROUP}/${SLUG}/#/"
    exit 0
  fi
fi

git -C "$WORK/hub" add "$REL_HTML" index.html "$GROUP/index.html"
if git -C "$WORK/hub" diff --cached --quiet; then
  echo "Nothing to publish: hub already has this folder and card."
  echo "https://${OWNER}.github.io/${HUB_REPO}/${GROUP}/${SLUG}/#/"
  exit 0
fi

git -C "$WORK/hub" -c user.name="$OWNER" -c user.email="$EMAIL" \
  commit -m "Publish ${TITLE} to prototype-hub/${GROUP}/${SLUG}."

echo "Pushing main..."
git -C "$WORK/hub" push origin HEAD:main

echo ""
echo "Shareable link:"
echo "https://${OWNER}.github.io/${HUB_REPO}/${GROUP}/${SLUG}/#/"
