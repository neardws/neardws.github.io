#!/bin/bash
# Send Discord notification for task events (used internally by task-complete.sh)
# Can also be used standalone when running inside Clawdbot environment

set -e

CHANNEL_ID="${1:-}"
EVENT_TYPE="${2:-}"  # complete, unblock, start
TEAM_ID="${3:-}"
TASK_ID="${4:-}"

if [ -z "$CHANNEL_ID" ] || [ -z "$EVENT_TYPE" ]; then
    echo "Usage: discord-notify.sh <channel-id> <event-type> [team-id] [task-id]"
    echo ""
    echo "Event types: complete, unblock, start"
    exit 1
fi

# Build message based on event type
case "$EVENT_TYPE" in
    complete)
        if [ -n "$TEAM_ID" ] && [ -n "$TASK_ID" ]; then
            WORKSPACE="${HOME}/clawd"
            TASK_FILE="${WORKSPACE}/teams/${TEAM_ID}/tasks/${TASK_ID}.json"
            if [ -f "$TASK_FILE" ]; then
                SUBJECT=$(jq -r '.subject' "$TASK_FILE")
                OWNER=$(jq -r '.owner // "Unknown"' "$TASK_FILE")
                FINDINGS=$(jq -r '.findings // "No findings provided"' "$TASK_FILE")
                
                MSG="🎯 **Task Complete: ${SUBJECT}**
👤 Completed by: ${OWNER}
📋 Findings: ${FINDINGS:0:800}"
            else
                MSG="🎯 Task completed in team ${TEAM_ID}"
            fi
        else
            MSG="🎯 Task completed"
        fi
        ;;
    unblock)
        if [ -n "$TEAM_ID" ] && [ -n "$TASK_ID" ]; then
            WORKSPACE="${HOME}/clawd"
            TASK_FILE="${WORKSPACE}/teams/${TEAM_ID}/tasks/${TASK_ID}.json"
            if [ -f "$TASK_FILE" ]; then
                SUBJECT=$(jq -r '.subject' "$TASK_FILE")
                MSG="➡️ **Dependency Ready: ${SUBJECT}**
🚀 Tasks that were waiting can now proceed"
            else
                MSG="➡️ Dependencies unblocked in team ${TEAM_ID}"
            fi
        else
            MSG="➡️ Dependencies unblocked"
        fi
        ;;
    start)
        MSG="🚀 **Team Task Started**
Team: ${TEAM_ID}
Task: ${TASK_ID}"
        ;;
    *)
        MSG="📢 Agent Team Update"
        ;;
esac

# Try to use clawdbot message tool if available
if command -v clawdbot >/dev/null 2>&; then
    # Running in Clawdbot environment - use message tool
    echo "📡 Sending to Discord channel ${CHANNEL_ID}..."
    # Note: This would need to be implemented as an actual message tool call
    # For now, we output what would be sent
    echo "Message preview:"
    echo "$MSG"
else
    # Output for manual sending
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "📡 DISCORD NOTIFICATION (Channel: ${CHANNEL_ID})"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "$MSG"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "To send this message, use the message tool:"
    echo "  message --action send --channel discord --target ${CHANNEL_ID} --message '...'"
fi
