#!/bin/bash
# Show team status dashboard

set -e

TEAM_ID="${1:-}"

if [ -z "$TEAM_ID" ]; then
    echo "Usage: team-status.sh <team-id>"
    echo ""
    echo "Example:"
    echo "  team-status.sh my-team"
    exit 1
fi

WORKSPACE="${HOME}/clawd"
TEAM_DIR="${WORKSPACE}/teams/${TEAM_ID}"
TASKS_DIR="${TEAM_DIR}/tasks"
CONFIG_FILE="${TEAM_DIR}/config.json"

if [ ! -d "$TEAM_DIR" ]; then
    echo "❌ Team '$TEAM_ID' not found"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════"
echo "                    🚀 TEAM: ${TEAM_ID}"
echo "═══════════════════════════════════════════════════════════"

# Team info
if [ -f "$CONFIG_FILE" ]; then
    DESCRIPTION=$(jq -r '.description // "No description"' "$CONFIG_FILE")
    CREATED=$(jq -r '.created_at // "Unknown"' "$CONFIG_FILE")
    COMPLETED=$(jq -r '.tasks_completed // 0' "$CONFIG_FILE")
    TOTAL=$(jq -r '.tasks_total // 0' "$CONFIG_FILE")
    
    echo ""
    echo "📋 Description: ${DESCRIPTION}"
    echo "🕐 Created: ${CREATED}"
    echo "📊 Progress: ${COMPLETED}/${TOTAL} tasks completed"
fi

# Agents
if [ -f "$CONFIG_FILE" ]; then
    echo ""
    echo "👥 AGENTS"
    echo "───────────────────────────────────────────────────────────"
    jq -r '.agents[] | "  • " + .name + " (" + .type + ") - " + .status' "$CONFIG_FILE" 2>/dev/null || echo "  No agents"
fi

# Tasks
echo ""
echo "📋 TASKS"
echo "───────────────────────────────────────────────────────────"

if [ -f "${TASKS_DIR}/index.json" ]; then
    for TASK_ID in $(jq -r '.tasks[]' "${TASKS_DIR}/index.json"); do
        TASK_FILE="${TASKS_DIR}/${TASK_ID}.json"
        if [ -f "$TASK_FILE" ]; then
            SUBJECT=$(jq -r '.subject' "$TASK_FILE")
            STATUS=$(jq -r '.status' "$TASK_FILE")
            OWNER=$(jq -r '.owner // "Unassigned"' "$TASK_FILE")
            BLOCKED_BY=$(jq -r '.blocked_by | if length > 0 then " [⛔ " + join(",") + "]" else "" end' "$TASK_FILE")
            
            # Status emoji
            case "$STATUS" in
                complete) ICON="✅" ;;
                in_progress) ICON="▶️" ;;
                pending) ICON="⏸️" ;;
                *) ICON="⚪" ;;
            esac
            
            printf "  %s %-10s | %-20s | %s%s\n" "$ICON" "[$TASK_ID]" "$OWNER" "$SUBJECT" "$BLOCKED_BY"
        fi
    done
else
    echo "  No tasks yet"
fi

# Recent findings
echo ""
echo "📝 RECENT FINDINGS"
echo "───────────────────────────────────────────────────────────"
if [ -d "${TEAM_DIR}/findings" ]; then
    ls -lt "${TEAM_DIR}/findings" 2>/dev/null | head -6 | tail -5 | awk '{print "  📄 " $9}' || echo "  No findings yet"
else
    echo "  No findings yet"
fi

# Unread messages summary
echo ""
echo "📬 UNREAD MESSAGES"
echo "───────────────────────────────────────────────────────────"
UNREAD_TOTAL=0

if ls "${TEAM_DIR}/inbox"/*.json 1>/dev/null 2>&1; then
    for INBOX in "${TEAM_DIR}/inbox"/*.json; do
        if [ -f "$INBOX" ]; then
            AGENT=$(basename "$INBOX" .json)
            COUNT=$(jq '[.messages[] | select(.read == false)] | length' "$INBOX")
            if [ "$COUNT" -gt 0 ]; then
                echo "  ● ${AGENT}: ${COUNT} unread"
                UNREAD_TOTAL=$((UNREAD_TOTAL + COUNT))
            fi
        fi
    done
fi

[ "$UNREAD_TOTAL" -eq 0 ] && echo "  No unread messages"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Commands:"
echo "  task-create.sh ${TEAM_ID} --subject '...' --owner agent"
echo "  team-spawn.sh ${TEAM_ID} agent-name 'task' claude"
echo "  msg-inbox.sh ${TEAM_ID} <agent-name>"
echo "═══════════════════════════════════════════════════════════"
