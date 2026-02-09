#!/bin/bash
# Check agent inbox for messages

set -e

TEAM_ID="${1:-}"
AGENT_NAME="${2:-}"

if [ -z "$TEAM_ID" ] || [ -z "$AGENT_NAME" ]; then
    echo "Usage: msg-inbox.sh <team-id> <agent-name>"
    echo ""
    echo "Example:"
    echo "  msg-inbox.sh my-team droid-auth"
    exit 1
fi

WORKSPACE="${HOME}/clawd"
TEAM_DIR="${WORKSPACE}/teams/${TEAM_ID}"
INBOX_FILE="${TEAM_DIR}/inbox/${AGENT_NAME}.json"

if [ ! -f "$INBOX_FILE" ]; then
    echo "📭 Inbox is empty (no messages)"
    exit 0
fi

# Count unread messages
UNREAD_COUNT=$(jq '[.messages[] | select(.read == false)] | length' "$INBOX_FILE")

echo "📬 Inbox for ${AGENT_NAME} (${UNREAD_COUNT} unread)"
echo ""

# Display all messages (unread first)
jq -r '.messages | sort_by(.read) | .[] | 
    "─────────────────────────────\n" +
    "From: " + .from + " | " + .timestamp + "\n" +
    "Type: " + .type + " | " + (if .read then "✓ Read" else "● Unread" end) + "\n" +
    "\n" + .content + "\n"
' "$INBOX_FILE"

# Mark all as read
jq '.messages |= map(.read = true)' "$INBOX_FILE" > "${INBOX_FILE}.tmp" && mv "${INBOX_FILE}.tmp" "$INBOX_FILE"
