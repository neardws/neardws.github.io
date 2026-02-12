---
name: tmux-coding-agent
description: Run coding agents in tmux sessions with full PTY support. Combines tmux persistence with fine-grained process control.
metadata:
  clawdbot:
    emoji: "🖥️"
    requires:
      bins: ["tmux"]
---

# Tmux Coding Agent

Run coding agents in **persistent tmux sessions** with **full PTY support**.

Combines the best of both worlds:
- ✅ **tmux persistence**: Sessions survive Clawdbot restarts
- ✅ **PTY support**: Full interactive terminal for coding agents
- ✅ **Fine-grained control**: Check logs, send input, kill sessions
- ✅ **Multiple agents**: Run Claude, Codex, Droid, Opencode in parallel

## Quick Start

### Spawn an agent

```bash
# Spawn with default agent (claude)
./skills/tmux-coding-agent/scripts/spawn.sh my-task "Fix the login bug"

# Spawn specific agent
./skills/tmux-coding-agent/scripts/spawn.sh refactor "Refactor auth module" droid
./skills/tmux-coding-agent/scripts/spawn.sh debug "Debug API error" codex
./skills/tmux-coding-agent/scripts/spawn.sh docs "Write documentation" gemini
./skills/tmux-coding-agent/scripts/spawn.sh quick "Quick fix" opencode
```

### Check progress without attaching

```bash
# Get recent output
./skills/tmux-coding-agent/scripts/log.sh my-task

# Check if still running
./skills/tmux-coding-agent/scripts/status.sh my-task
```

### Interactive control

```bash
# Attach to interact (Ctrl+B then D to detach)
tmux attach -t my-task

# Send input without attaching
tmux send-keys -t my-task "yes" Enter

# Kill when done
tmux kill-session -t my-task
```

## Available Agents

| Agent | Command | Best For |
|-------|---------|----------|
| **claude** | Claude Code | Complex reasoning, careful edits |
| **codex** | OpenAI Codex | Quick iterations, debugging |
| **droid** | Factory Droid | Large refactoring, full features |
| **opencode** | OpenCode + MiniMax | Fast, cheap tasks |
| **gemini** | Google Gemini | Long context, documentation |

## Advanced Usage

### Interactive mode (recommended for complex tasks)

```bash
# 1. Spawn in background
./skills/tmux-coding-agent/scripts/spawn.sh feature "Build new feature" claude

# 2. Check progress periodically
./skills/tmux-coding-agent/scripts/log.sh feature

# 3. When agent asks a question, send input
tmux send-keys -t feature "yes" Enter

# 4. Or attach to have a conversation
tmux attach -t feature
# ... do interactive work ...
# Press Ctrl+B, then D to detach (session keeps running)

# 5. Check final result
./skills/tmux-coding-agent/scripts/log.sh feature

# 6. Clean up
tmux kill-session -t feature
```

### Batch processing (multiple agents)

```bash
# Launch multiple agents in parallel
./skills/tmux-coding-agent/scripts/spawn.sh backend "Implement API" droid
./skills/tmux-coding-agent/scripts/spawn.sh frontend "Build UI" codex
./skills/tmux-coding-agent/scripts/spawn.sh tests "Write tests" opencode

# Check all status
./skills/tmux-coding-agent/scripts/list.sh

# Get logs from all
for session in backend frontend tests; do
  echo "=== $session ==="
  ./skills/tmux-coding-agent/scripts/log.sh $session
done
```

### Working directory

All agents start in the **current working directory**:

```bash
cd ~/my-project
./skills/tmux-coding-agent/scripts/spawn.sh fix "Fix the bug" claude
# Agent sees only my-project, not your entire home
```

## Commands Reference

### Scripts

| Script | Purpose |
|--------|---------|
| `spawn.sh <name> <task> [agent]` | Spawn a new agent session |
| `log.sh <name> [lines]` | Get recent output (default: 50 lines) |
| `status.sh <name>` | Check if session is running |
| `list.sh` | List all tmux-coding-agent sessions |
| `attach.sh <name>` | Attach to session interactively |
| `send.sh <name> <text>` | Send input to session |
| `kill.sh <name>` | Kill a session |

### Direct tmux commands

```bash
# List all sessions
tmux list-sessions

# Attach to session
tmux attach -t session-name

# Send keys to session
tmux send-keys -t session-name "your input" Enter

# Capture pane output
tmux capture-pane -t session-name -p

# Kill session
tmux kill-session -t session-name
```

## Differences from Original Skills

| Feature | coding-agent | tmux-agents | tmux-coding-agent |
|---------|-------------|-------------|-------------------|
| Persistence | ❌ Restart loses it | ✅ tmux persists | ✅ tmux persists |
| PTY support | ✅ `pty:true` | ⚠️ Limited | ✅ Full PTY |
| Process control | `process` tool | tmux commands | Both options |
| Interactive | Direct | Attach | Attach or send keys |
| Best for | Quick tasks | Long background | Interactive long tasks |

## Tips

1. **Naming**: Use descriptive names like `fix-auth-bug`, `refactor-user-model`
2. **Cleanup**: Kill sessions when done to free resources
3. **Logs**: Use `log.sh` to check progress without interrupting
4. **Parallel**: Spawn multiple agents for different tasks
5. **Recovery**: If Clawdbot restarts, your sessions are still there!

## Troubleshooting

### Session not found
```bash
# List all tmux sessions
tmux list-sessions

# List only tmux-coding-agent sessions
./skills/tmux-coding-agent/scripts/list.sh
```

### Agent not responding
```bash
# Check if process is running
./skills/tmux-coding-agent/scripts/status.sh my-task

# Attach to see what's happening
tmux attach -t my-task

# Or send interrupt
./skills/tmux-coding-agent/scripts/send.sh my-task "Ctrl+C"
```

### Kill stuck session
```bash
./skills/tmux-coding-agent/scripts/kill.sh my-task
# Or force kill
tmux kill-session -t my-task
```
