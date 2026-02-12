#!/bin/bash
# Attach to a tmux coding agent session interactively
# Usage: ./attach.sh <session-name>

SESSION_NAME="$1"

if [ -z "$SESSION_NAME" ]; then
    echo "Usage: $0 <session-name>"
    echo ""
    echo "To detach from session: Press Ctrl+B, then D"
    exit 1
fi

if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Error: Session '$SESSION_NAME' not found"
    echo ""
    echo "Available sessions:"
    ./skills/tmux-coding-agent/scripts/list.sh
    exit 1
fi

echo "Attaching to session: $SESSION_NAME"
echo ""
echo "To detach: Press Ctrl+B, then D (session continues running)"
echo "To exit: Type 'exit' or press Ctrl+D (may end session)"
echo ""

tmux attach -t "$SESSION_NAME"
