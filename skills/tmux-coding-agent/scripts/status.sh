#!/bin/bash
# Check status of a tmux coding agent session
# Usage: ./status.sh <session-name>

SESSION_NAME="$1"

if [ -z "$SESSION_NAME" ]; then
    echo "Usage: $0 <session-name>"
    exit 1
fi

if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "❌ Session '$SESSION_NAME' not found"
    exit 1
fi

# Get session info
SESSION_INFO=$(tmux list-sessions -F "#{session_name}|#{session_activity}|#{session_created}" | grep "^${SESSION_NAME}|")

if [ -z "$SESSION_INFO" ]; then
    echo "❌ Session '$SESSION_NAME' not found"
    exit 1
fi

# Parse info
ACTIVITY=$(echo "$SESSION_INFO" | cut -d'|' -f2)
CREATED=$(echo "$SESSION_INFO" | cut -d'|' -f3)

# Convert timestamps to human-readable
ACTIVITY_HUMAN=$(date -d "@$ACTIVITY" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "$ACTIVITY")
CREATED_HUMAN=$(date -d "@$CREATED" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "$CREATED")

echo "✅ Session '$SESSION_NAME' is running"
echo "   Created:  $CREATED_HUMAN"
echo "   Activity: $ACTIVITY_HUMAN"

# Check if there's a running process
echo ""
echo "Recent output (last 10 lines):"
echo "---"
tmux capture-pane -t "$SESSION_NAME" -p -S "-10"
