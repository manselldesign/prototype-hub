#!/usr/bin/env bash
# Wrapper so a clone of this hub can publish without copying the skill path.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
exec bash "$HERE/../.cursor/skills/git-publish/scripts/publish-to-hub.sh" "$@"
