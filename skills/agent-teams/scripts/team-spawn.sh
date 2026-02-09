#!/bin/bash
# Spawn an agent for a team with team context

set -e

TEAM_ID="${1:-}"
AGENT_NAME="${2:-}"
TASK_DESC="${3:-}"
AGENT_TYPE="${4:-claude}"

if [ -z "$TEAM_ID" ] || [ -z "$AGENT_NAME" ] || [ -z "$TASK_DESC" ]; then
    echo "Usage: team-spawn.sh <team-id> <agent-name> <task-description> [agent-type]"
    echo ""
    echo "Agent types: claude, droid, codex, gemini, opencode, ollama-claude, ollama-codex"
    echo ""
    echo "Example:"
    echo "  team-spawn.sh auth-team droid-auth 'Design auth API' droid"
    exit 1
fi

WORKSPACE="${HOME}/clawd"
TEAM_DIR="${WORKSPACE}/teams/${TEAM_ID}"

if [ ! -d "$TEAM_DIR" ]; then
    echo "❌ Team '$TEAM_ID' not found"
    exit 1
fi

# Create inbox for this agent
INBOX_FILE="${TEAM_DIR}/inbox/${AGENT_NAME}.json"
if [ ! -f "$INBOX_FILE" ]; then
    echo '{"messages": []}' > "$INBOX_FILE"
fi

# Register agent in team config
CONFIG_FILE="${TEAM_DIR}/config.json"
jq --arg name "$AGENT_NAME" --arg type "$AGENT_TYPE" '.agents += [{"name": $name, "type": $type, "status": "active", "started_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}]' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"

# Build team context for the agent
TEAM_CONTEXT="You are part of Agent Team '${TEAM_ID}'. 

Team workspace: ${TEAM_DIR}
Your inbox: ${INBOX_FILE}
Findings directory: ${TEAM_DIR}/findings/

RULES:
1. When you complete your task, write findings to: ${TEAM_DIR}/findings/${AGENT_NAME}-$(date +%s).md
2. Check your inbox regularly for messages from other agents: ${INBOX_FILE}
3. To message another agent, create a JSON entry in their inbox file
4. Mark tasks complete using: task-complete.sh ${TEAM_ID} <task-id> --findings '...'

CURRENT TASK: ${TASK_DESC}"

# Use existing spawn script but inject team context
SESSION_NAME="${TEAM_ID}-${AGENT_NAME}"

# Create session with team context
./skills/tmux-agents/scripts/spawn.sh "$SESSION_NAME" "$TEAM_CONTEXT $TASK_DESC" "$AGENT_TYPE"

echo ""
echo "✅ Team agent spawned: ${AGENT_NAME}"
echo "   Team: ${TEAM_ID}"
echo "   Session: ${SESSION_NAME}"
echo "   Type: ${AGENT_TYPE}"
echo ""
echo "Commands:"
echo "  Watch:   tmux attach -t ${SESSION_NAME}"
echo "  Inbox:   msg-inbox.sh ${TEAM_ID} ${AGENT_NAME}"
echo "  Status:  team-status.sh ${TEAM_ID}"
