#!/usr/bin/env bash
# Publish a single-folder HTML prototype to a new public repo on
# github.com/manselldesign and turn on GitHub Pages from main at /.
#
# Usage:
#   ./tools/publish-prototype.sh <directory> <repo-name>
#
# The directory must contain index.html at its top level.
# Set GH_TOKEN (or GITHUB_TOKEN) to a GitHub personal access token
# that can create public repos, push code, and enable Pages.
# The token is never written into the repo.

set -euo pipefail

OWNER="manselldesign"
API="https://api.github.com"

usage() {
  echo "Usage: ./tools/publish-prototype.sh <directory> <repo-name>" >&2
  echo "Example: ./tools/publish-prototype.sh ~/Desktop/search-drawer search-drawer" >&2
  echo "GH_TOKEN or GITHUB_TOKEN must be set to a GitHub personal access token." >&2
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

if [[ -z "${GH_TOKEN:-}" && -n "${GITHUB_TOKEN:-}" ]]; then
  GH_TOKEN="$GITHUB_TOKEN"
fi

# Cloud setups store the PAT as the secret name in this variable.
if [[ -z "${GH_TOKEN:-}" && -n "${CLOUD_AGENT_ALL_SECRET_NAMES:-}" ]]; then
  GH_TOKEN="$CLOUD_AGENT_ALL_SECRET_NAMES"
fi

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "Set GH_TOKEN to your GitHub personal access token, then run this command again." >&2
  exit 1
fi
export GH_TOKEN

if [[ ! -d "$SRC" ]]; then
  echo "Folder not found: $SRC" >&2
  exit 1
fi

if [[ ! -f "$SRC/index.html" ]]; then
  echo "Put index.html in the top folder of that directory, then run this command again." >&2
  echo "Looked in: $SRC" >&2
  exit 1
fi

if [[ ! "$REPO" =~ ^[A-Za-z0-9_][A-Za-z0-9._-]{0,99}$ ]]; then
  echo "Repo name must use letters, numbers, periods, underscores, or hyphens, and must start with a letter, number, or underscore." >&2
  exit 1
fi

auth_curl() {
  curl -sS -H "Authorization: Bearer ${GH_TOKEN}" \
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
CREATE_CODE="$(curl -sS -o /tmp/publish-prototype-create.json -w "%{http_code}" \
  -X POST \
  -H "Authorization: Bearer ${GH_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "$API/user/repos" \
  -d "$(python3 -c 'import json,sys; print(json.dumps({"name": sys.argv[1], "private": False, "auto_init": False, "description": "HTML prototype for stakeholder review."}))' "$REPO")")"

ALREADY_EXISTS=0
if [[ "$CREATE_CODE" == "422" ]]; then
  ALREADY_EXISTS="$(python3 -c 'import json; d=json.load(open("/tmp/publish-prototype-create.json")); errors=d.get("errors") or []; text=" ".join(e.get("message","") for e in errors).lower(); print("1" if "already exists" in text else "0")')"
fi

if [[ "$CREATE_CODE" == "201" ]]; then
  echo "Created ${OWNER}/${REPO}."
elif [[ "$ALREADY_EXISTS" == "1" ]]; then
  echo "Repo ${OWNER}/${REPO} already exists. Checking that it is still empty..."
  HAS_FILES="$(auth_curl -o /dev/null -w "%{http_code}" "$API/repos/${OWNER}/${REPO}/contents/")"
  if [[ "$HAS_FILES" != "404" ]]; then
    echo "Stopped. ${OWNER}/${REPO} already has files, so nothing was replaced." >&2
    echo "Pick a new repo name, or update that repo yourself." >&2
    exit 1
  fi
else
  echo "Could not create the repo (HTTP ${CREATE_CODE})." >&2
  python3 -c 'import json; d=json.load(open("/tmp/publish-prototype-create.json")); print(d.get("message","")); [print("-", e.get("message","")) for e in (d.get("errors") or [])]' >&2 || true
  exit 1
fi

WORK="$(mktemp -d)"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

python3 - "$SRC" "$WORK" <<'PY'
import os, shutil, sys
src, dest = sys.argv[1], sys.argv[2]
skip = {".git", "node_modules", ".DS_Store"}
for name in os.listdir(src):
    if name in skip:
        continue
    s = os.path.join(src, name)
    d = os.path.join(dest, name)
    if os.path.isdir(s):
        shutil.copytree(s, d, ignore=shutil.ignore_patterns(".git", "node_modules", ".DS_Store"))
    else:
        shutil.copy2(s, d)
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
# GitHub's git endpoint expects basic auth. The token stays out of the remote URL.
BASIC="$(python3 -c 'import os,base64; t=os.environ["GH_TOKEN"]; print(base64.b64encode(("x-access-token:"+t).encode()).decode())')"
GIT_TERMINAL_PROMPT=0 git -C "$WORK" \
  -c credential.helper= \
  -c "http.extraheader=AUTHORIZATION: basic ${BASIC}" \
  push "https://github.com/${OWNER}/${REPO}.git" HEAD:main
unset BASIC

echo "Turning on GitHub Pages from main at / ..."
PAGES_OK=0
for _ in 1 2 3 4 5 6; do
  PAGES_CODE="$(curl -sS -o /tmp/publish-prototype-pages.json -w "%{http_code}" \
    -X POST \
    -H "Authorization: Bearer ${GH_TOKEN}" \
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
  echo "In the repo, set Pages to branch main and folder / (root)." >&2
  exit 1
fi

# If Pages was already on, make sure the source is main at /.
if [[ "$PAGES_CODE" == "409" ]]; then
  curl -sS -o /tmp/publish-prototype-pages.json -w "" \
    -X PUT \
    -H "Authorization: Bearer ${GH_TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "$API/repos/${OWNER}/${REPO}/pages" \
    -d '{"build_type":"legacy","source":{"branch":"main","path":"/"}}' >/dev/null
fi

URL="https://${OWNER}.github.io/${REPO}/"
echo ""
echo "Shareable link:"
echo "$URL"
echo "Add this prototype to the hub by editing index.html in ${OWNER}/prototype-hub (the list with id prototype-list)."
