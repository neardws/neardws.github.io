# Agent Teams

Multi-agent coordination system for OpenClaw with task management, agent messaging, and Discord integration.

## Overview

Agent Teams allows you to:
- Create teams of agents working on related tasks
- Manage tasks with dependencies (blocked_by/blocks)
- Send messages between agents
- Broadcast task completions to Discord channels
- Visualize team status and progress

## Installation

The skill is already installed at `/home/neardws/clawd/skills/agent-teams/`.

## Quick Start

### 1. Create a Team

```bash
./skills/agent-teams/scripts/team-create.sh auth-feature "Implement user authentication system"
```

### 2. Add Tasks

```bash
# Task 1: Design API (no dependencies)
./skills/agent-teams/scripts/task-create.sh auth-feature \
  --subject "Design authentication API" \
  --owner droid-design \
  --tags "api,design" \
  --broadcast "discord:1468244824405839894"

# Task 2: Implement backend (depends on Task 1)
./skills/agent-teams/scripts/task-create.sh auth-feature \
  --subject "Implement auth backend" \
  --owner codex-backend \
  --blocked-by "task-001" \
  --tags "backend,implementation" \
  --broadcast "discord:1468244824405839894"

# Task 3: Frontend integration (depends on Task 2)
./skills/agent-teams/scripts/task-create.sh auth-feature \
  --subject "Build login UI" \
  --owner gemini-frontend \
  --blocked-by "task-002" \
  --tags "frontend,ui"
```

### 3. Spawn Team Agents

```bash
# Spawn agents for each task
./skills/agent-teams/scripts/team-spawn.sh auth-feature droid-design "Design auth API" droid
./skills/agent-teams/scripts/team-spawn.sh auth-feature codex-backend "Implement auth backend" codex
./skills/agent-teams/scripts/team-spawn.sh auth-feature gemini-frontend "Build login UI" gemini
```

### 4. Monitor Progress

```bash
# View team dashboard
./skills/agent-teams/scripts/team-status.sh auth-feature

# Check an agent's inbox
./skills/agent-teams/scripts/msg-inbox.sh auth-feature codex-backend
```

### 5. Agents Communicate

From within an agent session (or manually):

```bash
# Send direct message
./skills/agent-teams/scripts/msg-send.sh auth-feature \
  droid-design codex-backend \
  "API spec is ready in findings/droid-design-*.md"

# Broadcast to all team members
./skills/agent-teams/scripts/msg-broadcast.sh auth-feature \
  droid-design \
  "Starting OAuth2 implementation phase"
```

### 6. Complete Task (Auto-Broadcast)

```bash
# Mark task complete - automatically broadcasts to:
# - Discord channels configured for this task
# - Agents waiting on this task (unblocks them)
# - All other team agents
./skills/agent-teams/scripts/task-complete.sh auth-feature task-001 \
  --findings "API designed with JWT + refresh token support. Endpoints: POST /auth/login, POST /auth/refresh, POST /auth/logout"
```

## Directory Structure

```
teams/
├── auth-feature/
│   ├── config.json          # Team metadata
│   ├── tasks/
│   │   ├── index.json       # Task registry
│   │   ├── task-001.json    # Individual tasks
│   │   └── task-002.json
│   ├── inbox/
│   │   ├── droid-design.json      # Per-agent message inbox
│   │   ├── codex-backend.json
│   │   └── gemini-frontend.json
│   └── findings/
│       ├── droid-design-1739145600.md
│       └── codex-backend-1739149200.md
```

## Task Schema

```json
{
  "id": "task-001",
  "subject": "Design authentication API",
  "description": "Define endpoints and data models for auth system",
  "status": "complete",
  "owner": "droid-design",
  "blocked_by": [],
  "blocks": ["task-002"],
  "tags": ["api", "design"],
  "broadcast_channels": ["discord:1468244824405839894"],
  "created_at": "2026-02-10T00:00:00Z",
  "updated_at": "2026-02-10T01:30:00Z",
  "completed_at": "2026-02-10T01:30:00Z",
  "findings": "API designed with JWT + refresh token support..."
}
```

## Message Schema

```json
{
  "messages": [
    {
      "id": "msg-1234567890",
      "from": "droid-design",
      "to": "codex-backend",
      "type": "direct",
      "content": "API spec is ready",
      "timestamp": "2026-02-10T01:00:00Z",
      "read": false
    }
  ]
}
```

## Command Reference

| Command | Description |
|---------|-------------|
| `team-create.sh <id> [description]` | Create new team |
| `team-delete.sh <id>` | Delete team (with confirmation) |
| `team-status.sh <id>` | Show team dashboard |
| `task-create.sh <team> [options]` | Create task with dependencies |
| `task-update.sh <team> <task> [options]` | Update task properties |
| `task-complete.sh <team> <task> [options]` | Mark complete + broadcast |
| `team-spawn.sh <team> <agent> <task> [type]` | Spawn agent for team |
| `msg-send.sh <team> <from> <to> <msg>` | Direct message |
| `msg-broadcast.sh <team> <from> <msg>` | Broadcast to all |
| `msg-inbox.sh <team> <agent>` | Check inbox |

### Task Create Options

```
--subject <text>        Task title (required)
--description <text>    Detailed description
--owner <agent>         Assigned agent name
--blocked-by <ids>      Comma-separated blocking task IDs
--tags <tags>           Comma-separated tags
--broadcast <channels>  Comma-separated Discord channel IDs
```

### Task Update Options

```
--status <status>       pending|in_progress|complete|deleted
--owner <agent>         Reassign to agent
--subject <text>        Update title
--description <text>    Update description
--add-tag <tag>         Add a tag
--remove-tag <tag>      Remove a tag
```

### Task Complete Options

```
--findings <text>       Summary of completed work
--file <path>           Path to findings file to include
```

## Discord Integration

When a task is completed, the system:

1. Posts to configured Discord channels with format:
```
🎯 Task Complete: {subject}
👤 Agent: {owner}
⏱️ Completed: {timestamp}
📋 Findings: {findings}
➡️ Unblocks: {blocked_tasks}
```

2. Sends messages to agents whose tasks were blocked by this one
3. Broadcasts to all team agents about the completion

## Comparison with Claude Code Agent Teams

| Feature | Claude Code | OpenClaw Agent Teams |
|---------|-------------|----------------------|
| Task dependencies | ✅ blocked_by/blocks | ✅ Same |
| Agent messaging | ✅ Inbox system | ✅ JSON-based inbox |
| Visual dashboard | ✅ teammate-dash-mode | ✅ tmux + team-status.sh |
| Discord broadcast | ❌ | ✅ Native integration |
| Local/cloud mix | ❌ Cloud only | ✅ Ollama + Cloud |
| Cost control | ⚠️ All paid | ✅ Free local option |

## Advanced Usage

### Parallel Debugging with Multiple Hypotheses

```bash
# Create team for debugging
./skills/agent-teams/scripts/team-create.sh debug-session "Investigate production issue"

# Create tasks for different investigation paths
./skills/agent-teams/scripts/task-create.sh debug-session \
  --subject "Check database connections" --owner agent-db
./skills/agent-teams/scripts/task-create.sh debug-session \
  --subject "Analyze memory leaks" --owner agent-memory
./skills/agent-teams/scripts/task-create.sh debug-session \
  --subject "Review recent deployments" --owner agent-git

# Spawn all agents to investigate in parallel
./skills/agent-teams/scripts/team-spawn.sh debug-session agent-db "Check DB pool settings" claude
./skills/agent-teams/scripts/team-spawn.sh debug-session agent-memory "Profile memory usage" claude
./skills/agent-teams/scripts/team-spawn.sh debug-session agent-git "Check recent commits" claude

# Agents share findings via messages
# When each completes, findings are broadcast
```

### Dependency Chain Example

```bash
# Backend → Frontend → Testing chain
./skills/agent-teams/scripts/task-create.sh feature \
  --subject "Design schema" --owner droid --tags design

./skills/agent-teams/scripts/task-create.sh feature \
  --subject "Implement backend" --owner codex \
  --blocked-by task-001 --tags backend

./skills/agent-teams/scripts/task-create.sh feature \
  --subject "Build frontend" --owner gemini \
  --blocked-by task-002 --tags frontend

./skills/agent-teams/scripts/task-create.sh feature \
  --subject "Write tests" --owner opencode \
  --blocked-by task-003 --tags testing
```

When task-001 completes, task-002 is notified it can start, and so on.

## Tips

- Use descriptive team IDs (kebab-case): `auth-refactor`, `api-v2`, `bug-1234`
- Tag tasks for filtering: `backend`, `frontend`, `urgent`, `blocked`
- Always broadcast to relevant Discord channels for visibility
- Check `msg-inbox.sh` regularly when working in a team
- Use `team-status.sh` to get a quick overview of all work

