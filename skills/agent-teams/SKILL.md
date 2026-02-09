# Agent Teams for OpenClaw

Multi-agent coordination system inspired by Claude Code Agent Teams.

## Features

- ✅ **Task Management** - JSON-based tasks with dependencies (blocked_by/blocks)
- ✅ **Agent Messaging** - Bidirectional communication between agents
- ✅ **Broadcast on Completion** - Auto-notify related agents and Discord channels
- ✅ **Team Dashboard** - Visual overview of all tasks and agent statuses

## Architecture

```
teams/
├── {team-id}/
│   ├── config.json          # Team configuration
│   ├── tasks/
│   │   ├── index.json       # Task registry
│   │   └── {task-id}.json   # Individual tasks
│   ├── inbox/
│   │   └── {agent-id}.json  # Per-agent message inbox
│   └── findings/
│       └── {agent-id}-{timestamp}.md  # Completed work summaries
```

## Quick Start

### 1. Create a Team
```bash
./skills/agent-teams/scripts/team-create.sh my-feature "Implement user authentication"
```

### 2. Add Tasks with Dependencies
```bash
./skills/agent-teams/scripts/task-create.sh my-feature \
  --subject "Design auth API" \
  --owner droid-auth \
  --tags "backend,api"

./skills/agent-teams/scripts/task-create.sh my-feature \
  --subject "Implement login endpoint" \
  --owner codex-backend \
  --blocked-by "task-001" \
  --broadcast discord:1468244824405839894
```

### 3. Spawn Team Agents
```bash
./skills/agent-teams/scripts/team-spawn.sh my-feature droid-auth "Design auth API"
./skills/agent-teams/scripts/team-spawn.sh my-feature codex-backend "Implement login endpoint"
```

### 4. Send Messages Between Agents
```bash
# Direct message
./skills/agent-teams/scripts/msg-send.sh my-feature codex-backend droid-auth \
  "API design ready, check findings/droid-auth-*.md"

# Broadcast to all
./skills/agent-teams/scripts/msg-broadcast.sh my-feature droid-auth \
  "Starting auth flow implementation"
```

### 5. Mark Task Complete (auto-broadcasts)
```bash
./skills/agent-teams/scripts/task-complete.sh my-feature task-002 \
  --findings "Login endpoint implemented with JWT support"
```

## Task Schema

```json
{
  "id": "task-001",
  "subject": "Design auth API",
  "description": "Define endpoints and data models",
  "status": "in_progress",
  "owner": "droid-auth",
  "blocked_by": [],
  "blocks": ["task-002"],
  "tags": ["backend", "api"],
  "broadcast_channels": ["discord:1468244824405839894"],
  "created_at": "2026-02-10T00:00:00Z",
  "updated_at": "2026-02-10T00:00:00Z",
  "completed_at": null,
  "findings": null
}
```

## Message Schema

```json
{
  "messages": [
    {
      "id": "msg-001",
      "from": "droid-auth",
      "to": "codex-backend",
      "type": "direct",
      "content": "API design ready",
      "timestamp": "2026-02-10T00:00:00Z",
      "read": false
    }
  ]
}
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `team-create.sh <id> <description>` | Create new team |
| `team-delete.sh <id>` | Delete team and all data |
| `team-status.sh <id>` | Show team dashboard |
| `task-create.sh <team> [options]` | Create task |
| `task-update.sh <team> <task-id> [options]` | Update task |
| `task-complete.sh <team> <task-id>` | Mark complete + broadcast |
| `team-spawn.sh <team> <agent-name> <task>` | Spawn agent for team |
| `msg-send.sh <team> <from> <to> <message>` | Direct message |
| `msg-broadcast.sh <team> <from> <message>` | Broadcast to all |
| `msg-inbox.sh <team> <agent>` | Check inbox |

## Integration with Discord

When a task is completed, the system:
1. Posts findings to specified Discord channels
2. Notifies blocked tasks' owners that dependencies are ready
3. Updates team status dashboard

Example broadcast:
```
🎯 Task Complete: Implement login endpoint
👤 Agent: codex-backend
⏱️ Duration: 45 minutes
📋 Findings: JWT-based auth with refresh tokens
➡️ Unblocks: task-003 (frontend integration)
```

## Comparison with Claude Code Agent Teams

| Feature | Claude Code | Our Implementation |
|---------|-------------|-------------------|
| Task dependencies | ✅ blocked_by/blocks | ✅ Same |
| Agent messaging | ✅ Inbox system | ✅ sessions_send based |
| Visual dashboard | ✅ teammate-dash-mode | ✅ tmux + status.sh |
| Broadcast | ✅ Built-in | ✅ + Discord integration |
| Local/cloud mix | ❌ | ✅ Ollama + Cloud |
| Cost control | ⚠️ All cloud | ✅ Free local option |
