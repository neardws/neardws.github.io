#!/bin/bash
# Update task properties

set -e

TEAM_ID="${1:-}"
TASK_ID="${2:-}"
shift 2 || true

if [ -z "$TEAM_ID" ] || [ -z "$TASK_ID" ]; then
    echo "Usage: task-update.sh <team-id> <task-id> [options]"
    echo ""
    echo "Options:"
    echo "  --status <status>       pending|in_progress|complete|deleted"
    echo "  --owner <agent>         Assign to agent"
    echo "  --subject <text>        Update subject"
    echo "  --description <text>    Update description"
    echo "  --add-tag <tag>         Add tag"
    echo "  --remove-tag <tag>      Remove tag"
    echo ""
    echo "Example:"
    echo "  task-update.sh my-team task-001 --status in_progress --owner droid"
    exit 1
fi

WORKSPACE="${HOME}/clawd"
TEAM_DIR="${WORKSPACE}/teams/${TEAM_ID}"
TASK_FILE="${TEAM_DIR}/tasks/${TASK_ID}.json"

if [ ! -f "$TASK_FILE" ]; then
    echo "❌ Task '$TASK_ID' not found"
    exit 1
fi

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Parse and apply updates
while [[ $# -gt 0 ]]; do
    case $1 in
        --status)
            jq --arg status "$2" --arg now "$NOW" '.status = $status | .updated_at = $now' "$TASK_FILE" > "${TASK_FILE}.tmp" && mv "${TASK_FILE}.tmp" "$TASK_FILE"
            echo "✓ Status updated to: $2"
            shift 2
            ;;
        --owner)
            jq --arg owner "$2" --arg now "$NOW" '.owner = $owner | .updated_at = $now' "$TASK_FILE" > "${TASK_FILE}.tmp" && mv "${TASK_FILE}.tmp" "$TASK_FILE"
            echo "✓ Owner assigned to: $2"
            shift 2
            ;;
        --subject)
            jq --arg subject "$2" --arg now "$NOW" '.subject = $subject | .updated_at = $now' "$TASK_FILE" > "${TASK_FILE}.tmp" && mv "${TASK_FILE}.tmp" "$TASK_FILE"
            echo "✓ Subject updated"
            shift 2
            ;;
        --description)
            jq --arg desc "$2" --arg now "$NOW" '.description = $desc | .updated_at = $now' "$TASK_FILE" > "${TASK_FILE}.tmp" && mv "${TASK_FILE}.tmp" "$TASK_FILE"
            echo "✓ Description updated"
            shift 2
            ;;
        --add-tag)
            jq --arg tag "$2" --arg now "$NOW" '.tags |= (. // []) | .tags += [$tag] | .updated_at = $now' "$TASK_FILE" > "${TASK_FILE}.tmp" && mv "${TASK_FILE}.tmp" "$TASK_FILE"
            echo "✓ Tag added: $2"
            shift 2
            ;;
        --remove-tag)
            jq --arg tag "$2" --arg now "$NOW" '.tags -= [$tag] | .updated_at = $now' "$TASK_FILE" > "${TASK_FILE}.tmp" && mv "${TASK_FILE}.tmp" "$TASK_FILE"
            echo "✓ Tag removed: $2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo ""
echo "✅ Task ${TASK_ID} updated"
