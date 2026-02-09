#!/bin/bash
# Create a new agent team

set -e

TEAM_ID="${1:-}"
DESCRIPTION="${2:-}"
WORKSPACE="${HOME}/clawd"
TEAMS_DIR="${WORKSPACE}/teams"

if [ -z "$TEAM_ID" ]; then
    echo "Usage: team-create.sh <team-id> [description]"
    echo ""
    echo "Example:"
    echo "  team-create.sh auth-feature 'Implement user authentication'"
    exit 1
fi

TEAM_DIR="${TEAMS_DIR}/${TEAM_ID}"

if [ -d "$TEAM_DIR" ]; then
    echo "❌ Team '$TEAM_ID' already exists"
    exit 1
fi

# Create directory structure
mkdir -p "$TEAM_DIR"/{tasks,inbox,findings}

# Create team config
cat > "${TEAM_DIR}/config.json" << EOF
{
  "id": "${TEAM_ID}",
  "description": "${DESCRIPTION}",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "active",
  "agents": [],
  "tasks_completed": 0,
  "tasks_total": 0
}
EOF

# Create empty task registry
cat > "${TEAM_DIR}/tasks/index.json" << EOF
{
  "tasks": [],
  "last_task_number": 0
}
EOF

echo "✅ Team '${TEAM_ID}' created"
echo ""
echo "Description: ${DESCRIPTION}"
echo "Location: ${TEAM_DIR}"
echo ""
echo "Next steps:"
echo "  1. Add tasks:    task-create.sh ${TEAM_ID} --subject '...' --owner agent-name"
echo "  2. Spawn agents: team-spawn.sh ${TEAM_ID} agent-name 'task description'"
echo "  3. Check status: team-status.sh ${TEAM_ID}"
