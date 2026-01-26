#!/usr/bin/env bash
# Remote macOS execution wrapper for darwin-only skills
# Executes commands on a remote macOS machine via SSH
#
# Usage: remote_exec.sh <binary_name> [args...]
#
# Environment Variables:
#   SSH_HOST    - Remote macOS host (default: 192.168.31.171)
#   SSH_USER    - Remote macOS user (default: neardws)
#   SSH_OPTIONS - Additional SSH options (default: -o ConnectTimeout=10 -o BatchMode=yes)

set -euo pipefail

# Default configuration
: "${SSH_HOST:=192.168.31.171}"
: "${SSH_USER:=neardws}"
: "${SSH_OPTIONS:=-o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=accept-new}"

if [[ $# -lt 1 ]]; then
    echo "Error: No command specified" >&2
    echo "Usage: remote_exec.sh <binary_name> [args...]" >&2
    exit 1
fi

BINARY="$1"
shift

# Build the remote command with proper escaping
# We need to check if the binary exists first, then execute it
REMOTE_CMD=$(cat <<'EOFSCRIPT'
check_and_run() {
    local bin="$1"
    shift
    
    # Try to find the binary
    if ! command -v "$bin" &>/dev/null; then
        echo "Error: '$bin' is not installed on this macOS system." >&2
        case "$bin" in
            imsg)
                echo "Install with: brew install steipete/tap/imsg" >&2
                ;;
            memo)
                echo "Install with: brew tap antoniorodr/memo && brew install antoniorodr/memo/memo" >&2
                ;;
            remindctl)
                echo "Install with: brew install steipete/tap/remindctl" >&2
                ;;
            grizzly)
                echo "Install with: go install github.com/tylerwince/grizzly/cmd/grizzly@latest" >&2
                ;;
            codexbar)
                echo "Install with: brew install --cask steipete/tap/codexbar" >&2
                ;;
            peekaboo)
                echo "Install with: brew install steipete/tap/peekaboo" >&2
                ;;
            things)
                echo "Install with: go install github.com/ossianhempel/things3-cli/cmd/things@latest" >&2
                ;;
            *)
                echo "Please install '$bin' on the remote macOS system." >&2
                ;;
        esac
        return 127
    fi
    
    # Execute the command
    exec "$bin" "$@"
}
check_and_run
EOFSCRIPT
)

# Execute on remote macOS
# shellcheck disable=SC2086
exec ssh ${SSH_OPTIONS} "${SSH_USER}@${SSH_HOST}" "$(printf '%s %q' "$REMOTE_CMD" "$BINARY")" "$@"
