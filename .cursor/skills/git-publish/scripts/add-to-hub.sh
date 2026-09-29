#!/usr/bin/env bash
# add-to-hub.sh is no longer a list-only helper.
# Prototypes must be copied into prototype-hub/<slug>/index.html in the same publish.

set -euo pipefail

echo "Do not add a homepage card without copying the prototype into the hub." >&2
echo "Use:" >&2
echo "  bash .cursor/skills/git-publish/scripts/publish-to-hub.sh <folder> <slug> \"<title>\" \"<description>\"" >&2
exit 1
