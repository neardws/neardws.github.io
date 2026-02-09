#!/bin/bash
# Delete a team and all its data

set -e

TEAM_ID="${1:-}"

if [ -z "$TEAM_ID" ]; then
    echo "Usage: team-delete.sh <team-id>"
    echo ""
    echo "⚠️  WARNING: This will delete all team data, tasks, and findings!"
    echo ""
    echo "Example:"
    echo "  team-delete.sh my-team"
    exit 1
fi

WORKSPACE="${HOME}/clawd"
TEAM_DIR="${WORKSPACE}/teams/${TEAM_ID}"

if [ ! -d "$TEAM_DIR" ]; then
    echo "❌ Team '$TEAM_ID' not found"
    exit 1
fi

# Check for running tmux sessions
SESSIONS=$(tmux list-sessions -F "#{session_name}" 2>/dev/null | grep "^${TEAM_ID}-" || true)
if [ -n "$SESSIONS" ]; then
    echo "⚠️  Found running sessions for this team:"
    echo "$SESSIONS" | while read session; do
        echo "   - $session"
    done
    echo ""
    echo "Kill these sessions first? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "$SESSIONS" | while read session; do
            tmux kill-session -t "$session" 2>/dev/null && echo "   ✓ Killed $session"
        done
    fi
fi

echo ""
echo "⚠️  Are you sure you want to delete team '${TEAM_ID}'?"
echo "   This will delete: ${TEAM_DIR}"
echo ""
echo "Type 'delete' to confirm:"
read -r confirm

if [ "$confirm" != "delete" ]; then
    echo "Cancelled."
    exit 0
fi

rm -rf "$TEAM_DIR"
echo "✅ Team '${TEAM_ID}' deleted"
