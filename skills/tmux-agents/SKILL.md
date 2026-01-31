---
name: tmux-agents
description: Manage background coding agents in tmux sessions. Spawn Claude Code or other agents, check progress, get results.
version: 1.0.0
author: Jose Munoz
homepage: https://clawdhub.com/skills/tmux-agents
triggers:
  - spawn agent
  - coding task
  - background task
  - tmux session
  - run codex
  - run gemini
  - local agent
  - ollama agent
metadata:
  clawdbot:
    emoji: "🖥️"
    requires:
      bins: ["tmux"]
    install:
      - id: brew-tmux
        kind: brew
        formula: tmux
        bins: ["tmux"]
        label: "Install tmux (brew)"
---

# Tmux Agents

Run coding agents in persistent tmux sessions. They work in the background while you do other things.

## Available Agents

### ☁️ Cloud Agents (API credits)

| Agent | Command | Best For |
|-------|---------|----------|
| **droid** | Factory Droid | 复杂编程项目、大型重构、完整功能开发 |
| **codex** | OpenAI Codex | Debug、快速调试、错误修复 |
| **gemini** | Google Gemini | 超大文档处理、长上下文分析 |
| **opencode** | OpenCode + MiniMax | 简单任务、小改动、快速编辑 |
| **claude** | Claude Code | 通用编程、代码审查 |

### 🦙 Local Agents (FREE via Ollama)

| Agent | Command | Best For |
|-------|---------|----------|
| **ollama-claude** | Claude Code + Ollama | Long experiments, heavy refactoring |
| **ollama-codex** | Codex + Ollama | Extended coding sessions |

Local agents use your Mac's GPU — no API costs, great for experimentation!

## Quick Commands

### Spawn a new agent session
```bash
./skills/tmux-agents/scripts/spawn.sh <name> <task> [agent]

# Cloud (uses API credits)
./skills/tmux-agents/scripts/spawn.sh fix-bug "Fix login validation" claude
./skills/tmux-agents/scripts/spawn.sh refactor "Refactor the auth module" codex
./skills/tmux-agents/scripts/spawn.sh research "Research caching strategies" gemini

# Local (FREE - uses Ollama)
./skills/tmux-agents/scripts/spawn.sh experiment "Rewrite entire test suite" ollama-claude
./skills/tmux-agents/scripts/spawn.sh big-refactor "Refactor all services" ollama-codex
```

### List running sessions
```bash
tmux list-sessions
# or
./skills/tmux-agents/scripts/status.sh
```

### Check on a session
```bash
./skills/tmux-agents/scripts/check.sh session-name
```

### Attach to watch live
```bash
tmux attach -t session-name
# Detach with: Ctrl+B, then D
```

### Send additional instructions
```bash
tmux send-keys -t session-name "additional instruction here" Enter
```

### Kill a session when done
```bash
tmux kill-session -t session-name
```

## When to Use Local vs Cloud

| Scenario | Recommendation |
|----------|----------------|
| Quick fix, time-sensitive | ☁️ Cloud (faster) |
| Expensive task, budget matters | 🦙 Local |
| Long experiment, might fail | 🦙 Local |
| Production code review | ☁️ Cloud (smarter) |
| Learning/exploring | 🦙 Local |
| Heavy refactoring | 🦙 Local |

## Parallel Agents

Run multiple agents simultaneously:

```bash
# Mix and match cloud + local
./scripts/spawn.sh backend "Implement user API" claude           # Cloud
./scripts/spawn.sh frontend "Build login form" ollama-codex      # Local
./scripts/spawn.sh docs "Write API documentation" gemini         # Cloud
./scripts/spawn.sh tests "Write all unit tests" ollama-claude    # Local
```

Check all at once:
```bash
./skills/tmux-agents/scripts/status.sh
```

## Ollama Setup

Local agents require Ollama with a coding model:

```bash
# Pull recommended model
ollama pull glm-4.7-flash

# Configure tools (one-time)
ollama launch claude --model glm-4.7-flash --config
ollama launch codex --model glm-4.7-flash --config
```

## Tips

- Sessions persist even if Clawdbot restarts
- Use local agents for risky/experimental work
- Use cloud for production-critical tasks
- Check `tmux ls` to see all active work
- Kill sessions when done to free resources
