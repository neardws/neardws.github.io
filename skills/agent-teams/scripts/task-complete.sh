#!/bin/bash
# Complete a task and broadcast to related agents and channels

set -e

TEAM_ID="${1:-}"
TASK_ID="${2:-}"
shift 2 || true

if [ -z "$TEAM_ID" ] || [ -z "$TASK_ID" ]; then
    echo "Usage: task-complete.sh <team-id> <task-id> [options]"
    echo ""
    echo "Options:"
    echo "  --findings <text>    Summary of completed work"
    echo "  --file <path>       Path to findings file to include"
    echo ""
    echo "Example:"
    echo "  task-complete.sh my-team task-001 --findings 'API designed with JWT support'"
    exit 1
fi

WORKSPACE="${HOME}/clawd"
TEAM_DIR="${WORKSPACE}/teams/${TEAM_ID}"
TASKS_DIR="${TEAM_DIR}/tasks"
TASK_FILE="${TASKS_DIR}/${TASK_ID}.json"

if [ ! -f "$TASK_FILE" ]; then
    echo "❌ Task '$TASK_ID' not found in team '$TEAM_ID'"
    exit 1
fi

# Parse arguments
FINDINGS=""
FINDINGS_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --findings) FINDINGS="$2"; shift 2 ;;
        --file) FINDINGS_FILE="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Read findings from file if provided
if [ -n "$FINDINGS_FILE" ] && [ -f "$FINDINGS_FILE" ]; then
    FILE_CONTENT=$(cat "$FINDINGS_FILE")
    FINDINGS="${FINDINGS}

${FILE_CONTENT}"
fi

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
OWNER=$(jq -r '.owner // "unknown"' "$TASK_FILE")
SUBJECT=$(jq -r '.subject' "$TASK_FILE")
BLOCKS=$(jq -r '.blocks | join(", ") // ""' "$TASK_FILE")
BROADCAST_CHANNELS=$(jq -r '.broadcast_channels[]?' "$TASK_FILE")

# Update task status
jq --arg findings "$FINDINGS" --arg now "$NOW" '
  .status = "complete" |
  .completed_at = $now |
  .updated_at = $now |
  .findings = $findings
' "$TASK_FILE" > "${TASK_FILE}.tmp" && mv "${TASK_FILE}.tmp" "$TASK_FILE"

# Update team stats
CONFIG_FILE="${TEAM_DIR}/config.json"
jq '.tasks_completed += 1' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"

echo "✅ Task completed: ${TASK_ID}"
echo "   Subject: ${SUBJECT}"
echo "   Owner: ${OWNER}"
[ -n "$FINDINGS" ] && echo "   Findings: ${FINDINGS:0:100}..."

# Broadcast to Discord channels
if [ -n "$BROADCAST_CHANNELS" ]; then
    echo ""
    echo "📡 Broadcasting to Discord channels..."
    for CHANNEL in $BROADCAST_CHANNELS; do
        # Extract channel ID from discord:channel-id format
        CHANNEL_ID="${CHANNEL#discord:}"
        if [ -n "$CHANNEL_ID" ]; then
            # Build Discord message
            MSG="🎯 **Task Complete: ${SUBJECT}**
👤 Agent: ${OWNER}
⏱️ Completed: ${NOW}
📋 Findings: ${FINDINGS:0:500}"

            # Send to Discord using clawdbot message tool
            echo "   → Channel: ${CHANNEL_ID}"
            # Note: This would need to be called from Clawdbot session with message tool
            # For now, we output the message that should be sent
        fi
    done
fi

# Notify agents waiting on this task
if [ -n "$BLOCKS" ]; then
    echo ""
    echo "📨 Notifying agents waiting on this task..."
    for BLOCKED_TASK_ID in $(echo "$BLOCKS" | tr ',' ' '); do
        BLOCKED_TASK_ID=$(echo "$BLOCKED_TASK_ID" | xargs)
        BLOCKED_FILE="${TASKS_DIR}/${BLOCKED_TASK_ID}.json"
        if [ -f "$BLOCKED_FILE" ]; then
            BLOCKED_OWNER=$(jq -r '.owner // empty' "$BLOCKED_FILE")
            BLOCKED_SUBJECT=$(jq -r '.subject' "$BLOCKED_FILE")
            if [ -n "$BLOCKED_OWNER" ]; then
                # Send message to agent's inbox
                INBOX_FILE="${TEAM_DIR}/inbox/${BLOCKED_OWNER}.json"
                if [ -f "$INBOX_FILE" ]; then
                    MSG_ID="msg-$(date +%s)-$$")
                    jq --arg id "$MSG_ID" --arg from "$OWNER" --arg to "$BLOCKED_OWNER" --arg task "$TASK_ID" --arg blocked "$BLOCKED_TASK_ID" --arg now "$NOW" '
                        .messages += [{
                            "id": $id,
                            "from": $from,
                            "to": $to,
                            "type": "dependency_ready",
                            "content": "Task \($task) completed. You can now start \($blocked): \($blocked_subject)",
                            "task_id": $task,
                            "blocked_task_id": $blocked,
                            "timestamp": $now,
                            "read": false
                        }]
                    ' "$INBOX_FILE" > "${INBOX_FILE}.tmp" && mv "${INBOX_FILE}.tmp" "$INBOX_FILE"
                    echo "   → ${BLOCKED_OWNER}: ${BLOCKED_SUBJECT} is unblocked"
                fi
            fi
        fi
    done
fi

# Broadcast to all team agents
AGENTS=$(jq -r '.agents[].name' "${TEAM_DIR}/config.json" 2>/dev/null || echo "")
if [ -n "$AGENTS" ]; then
    echo ""
    echo "📢 Broadcasting completion to all team agents..."
    for AGENT in $AGENTS; do
        if [ "$AGENT" != "$OWNER" ]; then
            INBOX_FILE="${TEAM_DIR}/inbox/${AGENT}.json"
            if [ -f "$INBOX_FILE" ]; then
                MSG_ID="msg-$(date +%s)-$$-${AGENT}"
                jq --arg id "$MSG_ID" --arg from "$OWNER" --arg to "$AGENT" --arg task "$TASK_ID" --arg subject "$SUBJECT" --arg now "$NOW" '
                    .messages += [{
                        "id": $id,
                        "from": $from,
                        "to": $to,
                        "type": "task_complete",
                        "content": "Task \($task) completed by \($from): \($subject)",
                        "task_id": $task,
                        "timestamp": $now,
                        "read": false
                    }]
                ' "$INBOX_FILE" > "${INBOX_FILE}.tmp" && mv "${INBOX_FILE}.tmp" "$INBOX_FILE"
            fi
        fi
    done
fi

echo ""
echo "✨ Task completion broadcast finished"
