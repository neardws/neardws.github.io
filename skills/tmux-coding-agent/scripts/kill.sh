#!/bin/bash
# Kill a tmux coding agent session
# Usage: ./kill.sh <session-name> [--force]

SESSION_NAME="$1"
FORCE="$2"

if [ -z "$SESSION_NAME" ]; then
    echo "Usage: $0 <session-name> [--force]"
    echo ""
    echo "  --force   Kill without confirmation"
    exit 1
fi

if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Error: Session '$SESSION_NAME' not found"
    exit 1
fi

# Show recent output before killing
echo "Session '$SESSION_NAME' - Recent output:"
echo "---"
tmux capture-pane -t "$SESSION_NAME" -p -S "-5"
echo "---"
echo ""

if [ "$FORCE" != "--force" ]; then
    read -p "Kill session '$SESSION_NAME'? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled"
        exit 0
    fi
fi

tmux kill-session -t "$SESSION_NAME"
echo "✅ Session '$SESSION_NAME' killed"
