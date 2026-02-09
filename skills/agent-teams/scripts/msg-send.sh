#!/bin/bash
# Send direct message from one agent to another

set -e

TEAM_ID="${1:-}"
FROM_AGENT="${2:-}"
TO_AGENT="${3:-}"
MESSAGE="${4:-}"

if [ -z "$TEAM_ID" ] || [ -z "$FROM_AGENT" ] || [ -z "$TO_AGENT" ] || [ -z "$MESSAGE" ]; then
    echo "Usage: msg-send.sh <team-id> <from-agent> <to-agent> <message>"
    echo ""
    echo "Example:"
    echo "  msg-send.sh my-team droid-auth codex-backend 'API design is ready'"
    exit 1
fi

WORKSPACE="${HOME}/clawd"
TEAM_DIR="${WORKSPACE}/teams/${TEAM_ID}"
INBOX_FILE="${TEAM_DIR}/inbox/${TO_AGENT}.json"

if [ ! -d "$TEAM_DIR" ]; then
    echo "❌ Team '$TEAM_ID' not found"
    exit 1
fi

# Create inbox if it doesn't exist
if [ ! -f "$INBOX_FILE" ]; then
    echo '{"messages": []}' > "$INBOX_FILE"
fi

MSG_ID="msg-$(date +%s)-$$"
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Add message to inbox
jq --arg id "$MSG_ID" --arg from "$FROM_AGENT" --arg to "$TO_AGENT" --arg content "$MESSAGE" --arg now "$NOW" '
    .messages += [{
        "id": $id,
        "from": $from,
        "to": $to,
        "type": "direct",
        "content": $content,
        "timestamp": $now,
        "read": false
    }]
' "$INBOX_FILE" > "${INBOX_FILE}.tmp" && mv "${INBOX_FILE}.tmp" "$INBOX_FILE"

echo "✅ Message sent from ${FROM_AGENT} to ${TO_AGENT}"
echo "   Message: ${MESSAGE:0:60}..."
