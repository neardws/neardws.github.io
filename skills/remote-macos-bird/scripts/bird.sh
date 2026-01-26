#!/usr/bin/env bash
# Remote bird wrapper - executes bird on remote macOS via SSH
#
# Usage: bird.sh [bird args...]
#
# Environment Variables:
#   SSH_HOST    - Remote macOS host (default: 192.168.31.171)
#   SSH_USER    - Remote macOS user (default: neardws)
#
# Supported subcommands: whoami, search, read, thread, replies, user-tweets
# Always use --json for structured output

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTE_EXEC="${SCRIPT_DIR}/../../remote-macos-scripts/remote_exec.py"

# Validate that we have at least one argument
if [[ $# -lt 1 ]]; then
    echo "Error: No subcommand specified" >&2
    echo "Usage: bird.sh <subcommand> [args...]" >&2
    echo "" >&2
    echo "Supported subcommands:" >&2
    echo "  whoami       - Show logged-in account" >&2
    echo "  search       - Search tweets" >&2
    echo "  read         - Read a single tweet" >&2
    echo "  thread       - Full conversation thread" >&2
    echo "  replies      - List replies to a tweet" >&2
    echo "  user-tweets  - User's profile timeline" >&2
    echo "" >&2
    echo "Example: bird.sh search \"AI agents\" -n 10 --json" >&2
    exit 1
fi

exec python3 "$REMOTE_EXEC" bird "$@"
