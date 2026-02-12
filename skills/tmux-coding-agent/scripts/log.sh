#!/bin/bash
# Get recent output from a tmux coding agent session
# Usage: ./log.sh <session-name> [number-of-lines]

SESSION_NAME="$1"
LINES="${2:-50}"

if [ -z "$SESSION_NAME" ]; then
    echo "Usage: $0 <session-name> [number-of-lines]"
    echo ""
    echo "Examples:"
    echo "  $0 my-task        # Show last 50 lines"
    echo "  $0 my-task 100    # Show last 100 lines"
    exit 1
fi

if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Error: Session '$SESSION_NAME' not found"
    echo ""
    echo "Available sessions:"
    tmux list-sessions 2>/dev/null | grep -v "^tmux" || echo "  (none)"
    exit 1
fi

echo "=== Session: $SESSION_NAME (last $LINES lines) ==="
echo ""
tmux capture-pane -t "$SESSION_NAME" -p -S "-$LINES"
