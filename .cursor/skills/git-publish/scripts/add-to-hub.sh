#!/usr/bin/env bash
# Add one prototype to the top of the list on manselldesign/prototype-hub.
#
# Usage:
#   add-to-hub.sh <repo-name> <title> <one-line description>

set -euo pipefail

OWNER="manselldesign"
API="https://api.github.com"
HUB_REPO="prototype-hub"

if [[ $# -ne 3 ]]; then
  echo "Usage: add-to-hub.sh <repo-name> <title> <one-line description>" >&2
  exit 1
fi

REPO="$1"
TITLE="$2"
DESCRIPTION="$3"

if [[ ! "$REPO" =~ ^[a-z0-9][a-z0-9-]{0,99}$ ]]; then
  echo "Repo name must be lowercase letters, numbers, and hyphens, and must start with a letter or number." >&2
  exit 1
fi

TOKEN_FILE="$(mktemp)"
python3 - "$TOKEN_FILE" <<'PY'
import os, subprocess, sys
out = sys.argv[1]
github_token_name = "GH_" + "TOKEN"
legacy_token_name = "GITHUB_" + "TOKEN"
token = os.environ.get(github_token_name) or os.environ.get(legacy_token_name) or ""
if not token:
    named = os.environ.get("CLOUD_AGENT_ALL_SECRET_NAMES", "")
    if named.startswith(("ghp_", "github_pat_")):
        token = named
if not token:
    for key, value in os.environ.items():
        if key.startswith(("ghp_", "github_pat_")) and value == github_token_name:
            token = key
            break
if not token:
    try:
        result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
        if result.returncode == 0:
            token = result.stdout.strip()
    except FileNotFoundError:
        token = ""
if not token:
    sys.exit(2)
with open(out, "w") as handle:
    handle.write(token)
PY
if [[ $? -ne 0 ]]; then
  echo "No GitHub token is available. Save a Cursor secret named GH_""TOKEN whose value is a personal access token with the repo scope, then run this again." >&2
  rm -f "$TOKEN_FILE"
  exit 1
fi
TOKEN="$(cat "$TOKEN_FILE")"
export TOKEN
rm -f "$TOKEN_FILE"

LOGIN="$(curl -sS -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "$API/user" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("login",""))')"
if [[ "$LOGIN" != "$OWNER" ]]; then
  echo "This token is not signed in as ${OWNER}." >&2
  exit 1
fi

EMAIL="$(curl -sS -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "$API/user" | python3 -c 'import json,sys; u=json.load(sys.stdin); print("%s+%s@users.noreply.github.com" % (u.get("id"), u.get("login")))')"

WORK="$(mktemp -d)"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

BASIC="$(python3 -c 'import os,base64; t=os.environ["TOKEN"]; print(base64.b64encode(("x-access-token:"+t).encode()).decode())')"
GIT_TERMINAL_PROMPT=0 git \
  -c credential.helper= \
  -c "http.extraheader=AUTHORIZATION: basic ${BASIC}" \
  clone --depth 1 "https://github.com/${OWNER}/${HUB_REPO}.git" "$WORK/hub" >/dev/null

python3 - "$WORK/hub/index.html" "$REPO" "$TITLE" "$DESCRIPTION" <<'PY'
import html, pathlib, sys
path, repo, title, description = sys.argv[1:]
url = f"https://manselldesign.github.io/{repo}/"
file = pathlib.Path(path)
text = file.read_text()
if url in text:
    print("already-listed")
    raise SystemExit(0)
block = (
    "        <li>\n"
    f"          <h2>{html.escape(title)}</h2>\n"
    f"          <p>{html.escape(description)}</p>\n"
    f"          <a href=\"{html.escape(url, quote=True)}\">{html.escape(url)}</a>\n"
    "        </li>\n"
)
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
print("added")
PY

if git -C "$WORK/hub" diff --quiet -- index.html; then
  echo "The hub already lists https://${OWNER}.github.io/${REPO}/"
  exit 0
fi

git -C "$WORK/hub" add index.html
git -C "$WORK/hub" -c user.name="$OWNER" -c user.email="$EMAIL" \
  commit -m "List the ${REPO} prototype on the review hub." >/dev/null

GIT_TERMINAL_PROMPT=0 git -C "$WORK/hub" \
  -c credential.helper= \
  -c "http.extraheader=AUTHORIZATION: basic ${BASIC}" \
  push "https://github.com/${OWNER}/${HUB_REPO}.git" HEAD:main >/dev/null
unset BASIC

echo "Added to https://${OWNER}.github.io/${HUB_REPO}/"
echo "https://${OWNER}.github.io/${REPO}/"
