#!/bin/bash
# Send input to a tmux coding agent session
# Usage: ./send.sh <session-name> <text-to-send>

SESSION_NAME="$1"
shift
TEXT="$@"

if [ -z "$SESSION_NAME" ] || [ -z "$TEXT" ]; then
    echo "Usage: $0 <session-name> <text-to-send>"
    echo ""
    echo "Examples:"
    echo "  $0 my-task 'yes'"
    echo "  $0 my-task 'check the tests'"
    echo "  $0 my-task 'Ctrl+C'          # Send Ctrl+C (interrupt)"
    exit 1
fi

if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Error: Session '$SESSION_NAME' not found"
    exit 1
fi

# Handle special keys
case "$TEXT" in
    "Ctrl+C"|"ctrl+c"|"^C")
        tmux send-keys -t "$SESSION_NAME" C-c
        echo "Sent Ctrl+C to '$SESSION_NAME'"
        ;;
    "Ctrl+D"|"ctrl+d"|"^D")
        tmux send-keys -t "$SESSION_NAME" C-d
        echo "Sent Ctrl+D to '$SESSION_NAME'"
        ;;
    "Enter"|"enter")
        tmux send-keys -t "$SESSION_NAME" Enter
        echo "Sent Enter to '$SESSION_NAME'"
        ;;
    *)
        tmux send-keys -t "$SESSION_NAME" "$TEXT" Enter
        echo "Sent '$TEXT' to '$SESSION_NAME'"
        ;;
esac
