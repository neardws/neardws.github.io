#!/usr/bin/env bash
set -euo pipefail

# bin-proxy.sh — run a command locally if available, otherwise run it on the Mac via SSH.
#
# Usage:
#   remote-mac/bin-proxy.sh <command> [args...]
#
# Examples:
#   remote-mac/bin-proxy.sh ffmpeg -version
#   remote-mac/bin-proxy.sh memo list
#
# Notes:
# - This is intentionally dumb/simple: it checks local PATH, then falls back to Mac.
# - For macOS-only tools (memo/remindctl/imsg/peekaboo/things), you may prefer always-remote.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTE="$SCRIPT_DIR/remote-mac.sh"

if [[ $# -lt 1 ]]; then
  echo "Usage: $(basename "$0") <command> [args...]" >&2
  exit 1
fi

cmd="$1"; shift

if command -v "$cmd" >/dev/null 2>&1; then
  exec "$cmd" "$@"
else
  exec "$REMOTE" run "$cmd" "$@"
fi
