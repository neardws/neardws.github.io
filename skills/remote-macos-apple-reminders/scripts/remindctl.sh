#!/usr/bin/env bash
# Remote remindctl wrapper - executes remindctl on remote macOS via SSH
#
# Usage: remindctl.sh [remindctl args...]
#
# Environment Variables:
#   SSH_HOST    - Remote macOS host (default: 192.168.31.171)
#   SSH_USER    - Remote macOS user (default: neardws)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTE_EXEC="${SCRIPT_DIR}/../../remote-macos-scripts/remote_exec.py"

exec python3 "$REMOTE_EXEC" remindctl "$@"
