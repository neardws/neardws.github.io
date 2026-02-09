#!/bin/bash
# Broadcast message to all team agents

set -e

TEAM_ID="${1:-}"
FROM_AGENT="${2:-}"
MESSAGE="${3:-}"

if [ -z "$TEAM_ID" ] || [ -z "$FROM_AGENT" ] || [ -z "$MESSAGE" ]; then
    echo "Usage: msg-broadcast.sh <team-id> <from-agent> <message>"
    echo ""
    echo "Example:"
    echo "  msg-broadcast.sh my-team droid-auth 'Starting implementation phase'"
    exit 1
fi

WORKSPACE="${HOME}/clawd"
TEAM_DIR="${WORKSPACE}/teams/${TEAM_ID}"

if [ ! -d "$TEAM_DIR" ]; then
    echo "❌ Team '$TEAM_ID' not found"
    exit 1
fi

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
MSG_ID="msg-$(date +%s)-$$"

# Get all agents from team config
AGENTS=$(jq -r '.agents[].name' "${TEAM_DIR}/config.json" 2>/dev/null || echo "")

if [ -z "$AGENTS" ]; then
    echo "⚠️  No agents found in team"
    exit 0
fi

# Send to each agent's inbox
for AGENT in $AGENTS; do
    INBOX_FILE="${TEAM_DIR}/inbox/${AGENT}.json"
    if [ -f "$INBOX_FILE" ]; then
        jq --arg id "$MSG_ID" --arg from "$FROM_AGENT" --arg to "$AGENT" --arg content "$MESSAGE" --arg now "$NOW" '
            .messages += [{
                "id": $id,
                "from": $from,
                "to": $to,
                "type": "broadcast",
                "content": $content,
                "timestamp": $now,
                "read": false
            }]
        ' "$INBOX_FILE" > "${INBOX_FILE}.tmp" && mv "${INBOX_FILE}.tmp" "$INBOX_FILE"
    fi
done

echo "✅ Broadcast sent to all agents in ${TEAM_ID}"
echo "   From: ${FROM_AGENT}"
echo "   Message: ${MESSAGE:0:60}..."
