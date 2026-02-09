#!/bin/bash
# Create a task in a team

set -e

TEAM_ID="${1:-}"
shift || true

if [ -z "$TEAM_ID" ]; then
    echo "Usage: task-create.sh <team-id> [options]"
    echo ""
    echo "Options:"
    echo "  --subject <text>        Task subject (required)"
    echo "  --description <text>    Task description"
    echo "  --owner <agent-name>    Assigned agent"
    echo "  --blocked-by <ids>      Comma-separated list of blocking task IDs"
    echo "  --tags <tags>           Comma-separated tags"
    echo "  --broadcast <channels>  Comma-separated Discord channel IDs"
    echo ""
    echo "Example:"
    echo "  task-create.sh my-team --subject 'Design API' --owner droid --tags backend"
    exit 1
fi

WORKSPACE="${HOME}/clawd"
TEAM_DIR="${WORKSPACE}/teams/${TEAM_ID}"
TASKS_DIR="${TEAM_DIR}/tasks"

if [ ! -d "$TEAM_DIR" ]; then
    echo "❌ Team '$TEAM_ID' not found"
    exit 1
fi

# Parse arguments
SUBJECT=""
DESCRIPTION=""
OWNER=""
BLOCKED_BY=""
TAGS=""
BROADCAST=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --subject) SUBJECT="$2"; shift 2 ;;
        --description) DESCRIPTION="$2"; shift 2 ;;
        --owner) OWNER="$2"; shift 2 ;;
        --blocked-by) BLOCKED_BY="$2"; shift 2 ;;
        --tags) TAGS="$2"; shift 2 ;;
        --broadcast) BROADCAST="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [ -z "$SUBJECT" ]; then
    echo "❌ --subject is required"
    exit 1
fi

# Generate task ID
INDEX_FILE="${TASKS_DIR}/index.json"
LAST_NUM=$(jq -r '.last_task_number // 0' "$INDEX_FILE")
TASK_NUM=$((LAST_NUM + 1))
TASK_ID=$(printf "task-%03d" $TASK_NUM)

# Build blocked_by array
BLOCKED_BY_JSON="[]"
if [ -n "$BLOCKED_BY" ]; then
    BLOCKED_BY_JSON=$(echo "$BLOCKED_BY" | jq -R 'split(",") | map(gsub("^\\s+|\\s+$"; ""))')
fi

# Build tags array
TAGS_JSON="[]"
if [ -n "$TAGS" ]; then
    TAGS_JSON=$(echo "$TAGS" | jq -R 'split(",") | map(gsub("^\\s+|\\s+$"; ""))')
fi

# Build broadcast channels array
BROADCAST_JSON="[]"
if [ -n "$BROADCAST" ]; then
    BROADCAST_JSON=$(echo "$BROADCAST" | jq -R 'split(",") | map(gsub("^\\s+|\\s+$"; ""))')
fi

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Create task JSON
cat > "${TASKS_DIR}/${TASK_ID}.json" << EOF
{
  "id": "${TASK_ID}",
  "subject": "${SUBJECT}",
  "description": "${DESCRIPTION}",
  "status": "pending",
  "owner": "${OWNER}",
  "blocked_by": ${BLOCKED_BY_JSON},
  "blocks": [],
  "tags": ${TAGS_JSON},
  "broadcast_channels": ${BROADCAST_JSON},
  "created_at": "${NOW}",
  "updated_at": "${NOW}",
  "completed_at": null,
  "findings": null
}
EOF

# Update index
jq --arg id "$TASK_ID" '.tasks += [$id] | .last_task_number += 1' "$INDEX_FILE" > "${INDEX_FILE}.tmp" && mv "${INDEX_FILE}.tmp" "$INDEX_FILE"

# Update blocks references in other tasks
for BLOCKING_ID in $(echo "$BLOCKED_BY" | tr ',' ' '); do
    BLOCKING_ID=$(echo "$BLOCKING_ID" | xargs)
    BLOCKING_FILE="${TASKS_DIR}/${BLOCKING_ID}.json"
    if [ -f "$BLOCKING_FILE" ]; then
        jq --arg id "$TASK_ID" '.blocks += [$id]' "$BLOCKING_FILE" > "${BLOCKING_FILE}.tmp" && mv "${BLOCKING_FILE}.tmp" "$BLOCKING_FILE"
    fi
done

# Update team stats
CONFIG_FILE="${TEAM_DIR}/config.json"
jq '.tasks_total += 1' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"

echo "✅ Task created: ${TASK_ID}"
echo "   Subject: ${SUBJECT}"
[ -n "$OWNER" ] && echo "   Owner: ${OWNER}"
[ -n "$BLOCKED_BY" ] && echo "   Blocked by: ${BLOCKED_BY}"

# Check if blocked tasks are complete
if [ -n "$BLOCKED_BY" ]; then
    for BLOCKING_ID in $(echo "$BLOCKED_BY" | tr ',' ' '); do
        BLOCKING_ID=$(echo "$BLOCKING_ID" | xargs)
        BLOCKING_FILE="${TASKS_DIR}/${BLOCKING_ID}.json"
        if [ -f "$BLOCKING_FILE" ]; then
            BLOCKING_STATUS=$(jq -r '.status' "$BLOCKING_FILE")
            if [ "$BLOCKING_STATUS" != "complete" ]; then
                echo "   ⚠️  Waiting for ${BLOCKING_ID} to complete"
            fi
        fi
    done
fi
