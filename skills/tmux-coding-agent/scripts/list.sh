#!/bin/bash
# List all tmux coding agent sessions

echo "=== Tmux Coding Agent Sessions ==="
echo ""

if ! tmux list-sessions 2>/dev/null | grep -q .; then
    echo "No active sessions"
    exit 0
fi

# List sessions with format
printf "%-20s %-10s %-20s %s\n" "SESSION" "AGENT" "CREATED" "ACTIVITY"
printf "%-20s %-10s %-20s %s\n" "-------" "-----" "-------" "--------"

tmux list-sessions -F "#{session_name}|#{session_created}|#{session_activity}|#{pane_current_command}" | while IFS='|' read -r name created activity cmd; do
    # Try to detect agent from command
    agent="unknown"
    case "$cmd" in
        *claude*) agent="claude" ;;
        *codex*) agent="codex" ;;
        *droid*) agent="droid" ;;
        *opencode*) agent="opencode" ;;
        *gemini*) agent="gemini" ;;
    esac
    
    created_human=$(date -d "@$created" '+%m-%d %H:%M' 2>/dev/null || echo "?")
    activity_human=$(date -d "@$activity" '+%H:%M:%S' 2>/dev/null || echo "?")
    
    printf "%-20s %-10s %-20s %s\n" "$name" "$agent" "$created_human" "$activity_human"
done

echo ""
echo "Commands:"
echo "  Attach:     tmux attach -t <session>"
echo "  Check log:  ./skills/tmux-coding-agent/scripts/log.sh <session>"
echo "  Send input: ./skills/tmux-coding-agent/scripts/send.sh <session> 'text'"
echo "  Kill:       ./skills/tmux-coding-agent/scripts/kill.sh <session>"
