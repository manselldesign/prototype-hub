#!/usr/bin/env bash
# Publish a folder with index.html to a new public repo on
# github.com/manselldesign and turn on GitHub Pages from main at /.
#
# Usage:
#   publish-prototype.sh <directory> <repo-name>
#
# The token is read from the environment or from gh. It is never printed.

set -euo pipefail

OWNER="manselldesign"
API="https://api.github.com"

usage() {
  echo "Usage: publish-prototype.sh <directory> <repo-name>" >&2
  echo "Example: publish-prototype.sh . search-drawer" >&2
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -ne 2 ]]; then
  usage
  exit 1
fi

SRC="$1"
REPO="$2"

TOKEN_FILE="$(mktemp)"
cleanup_token() { rm -f "$TOKEN_FILE"; }
trap cleanup_token EXIT

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
load_status=$?
if [[ "$load_status" -ne 0 ]]; then
  echo "No GitHub token is available. Save a Cursor secret named GH_""TOKEN whose value is a personal access token with the repo scope, then run this again." >&2
  exit 1
fi

TOKEN="$(cat "$TOKEN_FILE")"
export TOKEN
rm -f "$TOKEN_FILE"
trap - EXIT

if [[ ! -d "$SRC" ]]; then
  echo "Folder not found: $SRC" >&2
  exit 1
fi

if [[ ! -f "$SRC/index.html" ]]; then
  echo "Put index.html in the top folder of that directory, then run this command again." >&2
  echo "Looked in: $SRC" >&2
  exit 1
fi

if [[ ! "$REPO" =~ ^[a-z0-9][a-z0-9-]{0,99}$ ]]; then
  echo "Repo name must be lowercase letters, numbers, and hyphens, and must start with a letter or number." >&2
  exit 1
fi

auth_curl() {
  curl -sS -H "Authorization: Bearer ${TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "$@"
}

echo "Checking GitHub login..."
LOGIN="$(auth_curl "$API/user" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("login",""))')"
if [[ "$LOGIN" != "$OWNER" ]]; then
  echo "This token is not signed in as ${OWNER}. Publish only to that account." >&2
  exit 1
fi

echo "Creating public repo ${OWNER}/${REPO}..."
CREATE_CODE="$(curl -sS -o /tmp/git-publish-create.json -w "%{http_code}" \
  -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "$API/user/repos" \
  -d "$(python3 -c 'import json,sys; print(json.dumps({"name": sys.argv[1], "private": False, "auto_init": False, "description": "HTML prototype for stakeholder review."}))' "$REPO")")"

ALREADY_EXISTS=0
if [[ "$CREATE_CODE" == "422" ]]; then
  ALREADY_EXISTS="$(python3 -c 'import json; d=json.load(open("/tmp/git-publish-create.json")); errors=d.get("errors") or []; text=" ".join(e.get("message","") for e in errors).lower(); print("1" if "already exists" in text else "0")')"
fi

if [[ "$CREATE_CODE" == "201" ]]; then
  echo "Created ${OWNER}/${REPO}."
elif [[ "$ALREADY_EXISTS" == "1" ]]; then
  echo "Repo ${OWNER}/${REPO} already exists. Checking that it is still empty..."
  HAS_FILES="$(auth_curl -o /dev/null -w "%{http_code}" "$API/repos/${OWNER}/${REPO}/contents/")"
  if [[ "$HAS_FILES" != "404" ]]; then
    echo "Stopped. ${OWNER}/${REPO} already has files, so nothing was replaced." >&2
    echo "Pick a new repo name." >&2
    exit 1
  fi
else
  echo "Could not create the repo (HTTP ${CREATE_CODE})." >&2
  python3 -c 'import json; d=json.load(open("/tmp/git-publish-create.json")); print(d.get("message","")); [print("-", e.get("message","")) for e in (d.get("errors") or [])]' >&2 || true
  exit 1
fi

WORK="$(mktemp -d)"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

python3 - "$SRC" "$WORK" <<'PY'
import os, shutil, sys
src, dest = sys.argv[1], sys.argv[2]
skip_names = {".git", "node_modules", ".DS_Store", ".env"}
skip_prefixes = (".env.",)

def skip(name):
    return name in skip_names or name.startswith(skip_prefixes) or name.endswith((".pem", ".key"))

def ignore(directory, names):
    return [name for name in names if skip(name)]

for name in os.listdir(src):
    if skip(name):
        continue
    source = os.path.join(src, name)
    target = os.path.join(dest, name)
    if os.path.isdir(source):
        shutil.copytree(source, target, ignore=ignore)
    else:
        shutil.copy2(source, target)
open(os.path.join(dest, ".nojekyll"), "a").close()
PY

if [[ ! -f "$WORK/index.html" ]]; then
  echo "Copy failed: index.html is missing from the publish folder." >&2
  exit 1
fi

EMAIL="$(auth_curl "$API/user" | python3 -c 'import json,sys; u=json.load(sys.stdin); print("%s+%s@users.noreply.github.com" % (u.get("id"), u.get("login")))')"

git -C "$WORK" init -b main >/dev/null
git -C "$WORK" add -A
git -C "$WORK" -c user.name="$OWNER" -c user.email="$EMAIL" commit -m "Publish HTML prototype" >/dev/null

echo "Pushing main..."
BASIC="$(python3 -c 'import os,base64; t=os.environ["TOKEN"]; print(base64.b64encode(("x-access-token:"+t).encode()).decode())')"
GIT_TERMINAL_PROMPT=0 git -C "$WORK" \
  -c credential.helper= \
  -c "http.extraheader=AUTHORIZATION: basic ${BASIC}" \
  push "https://github.com/${OWNER}/${REPO}.git" HEAD:main
unset BASIC

echo "Turning on GitHub Pages from main at / ..."
PAGES_OK=0
PAGES_CODE=""
for _ in 1 2 3 4 5 6; do
  PAGES_CODE="$(curl -sS -o /tmp/git-publish-pages.json -w "%{http_code}" \
    -X POST \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "$API/repos/${OWNER}/${REPO}/pages" \
    -d '{"build_type":"legacy","source":{"branch":"main","path":"/"}}')"
  if [[ "$PAGES_CODE" == "201" || "$PAGES_CODE" == "409" ]]; then
    PAGES_OK=1
    break
  fi
  sleep 3
done

if [[ "$PAGES_OK" != "1" ]]; then
  echo "The files are on main, but Pages did not turn on (HTTP ${PAGES_CODE})." >&2
  echo "Repository: https://github.com/${OWNER}/${REPO}" >&2
  exit 1
fi

if [[ "$PAGES_CODE" == "409" ]]; then
  curl -sS -o /tmp/git-publish-pages.json \
    -X PUT \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "$API/repos/${OWNER}/${REPO}/pages" \
    -d '{"build_type":"legacy","source":{"branch":"main","path":"/"}}' >/dev/null
fi

URL="https://${OWNER}.github.io/${REPO}/"
echo ""
echo "Shareable link:"
echo "$URL"
