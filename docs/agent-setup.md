# Agent Setup Guide

Complete configuration for coding agents.

---

## Agent 配置 (via LiteLLM Gateway)

| Agent | Config File | Model | Endpoint |
|-------|-------------|-------|----------|
| Claude Code | `~/.claude/config.json` | claude-opus-4-6 | http://localhost:4000 |
| **Droid** | `~/.factory/settings.json` | [LiteLLM] Claude Opus 4.6 | http://localhost:4000/v1 |
| **Codex CLI** | `~/.codex/config.toml` | foxcode-gpt-5.3-codex | http://localhost:4000 |
| Opencode | `~/.config/opencode/config.json` | litellm models | http://localhost:4000 |

---

## Claude Code (v2.1.9)

**Config** (`~/.claude/config.json`)
```json
{
  "anthropic": {
    "baseUrl": "http://localhost:4000",
    "apiKey": "sk-litellm-neardws-1770801720"
  },
  "defaults": {
    "model": "claude-opus-4-6"
  }
}
```

**Launch**
```bash
cd ~/clawd/skills/tmux-coding-agent
./scripts/spawn.sh <session> "<task>" claude
./scripts/status.sh <session>
./scripts/log.sh <session>
./scripts/kill.sh <session>
tmux attach -t <session>
```

**Key Commands**
| Command | Function |
|---------|----------|
| `/help` | Show help |
| `/model` | Switch model |
| `/init` | Create CLAUDE.md |
| `/commit` | Git commit |
| `?` | Shortcuts help |
| `!` | Bash mode |
| `Shift+Tab` | Auto-accept edits |

**Docs**
- https://code.claude.com/docs/en/overview
- https://github.com/anthropics/claude-code/issues

---

## Codex CLI (v0.98.0)

**Config** (`~/.codex/config.toml`)
```toml
[settings]
model = "foxcode-gpt-5.3-codex"
model_provider = "openai"
base_url = "http://localhost:4000/v1"
api_key = "sk-litellm-neardws-1770801720"
personality = "pragmatic"
```

**Launch**
```bash
export OPENAI_API_KEY="sk-litellm-neardws-1770801720"
export OPENAI_BASE_URL="http://localhost:4000/v1"
codex -m foxcode-gpt-5.3-codex
```

**Key Commands**
| Command | Function |
|---------|----------|
| `/model` | Switch model |
| `/permissions` | Set permission level |
| `/skills` | Use skills |
| `?` | Shortcuts |
| `!` | Shell command |
| `Ctrl+V` | Paste image |

**GitHub**: https://github.com/openai/codex

---

## Droid

**Launch**
```bash
cd ~/clawd/skills/tmux-coding-agent
./scripts/spawn.sh <name> "<task>" droid --interactive
```

**Commands**
- `/help`, `/model`, `/mcp`, `/status`, `/cost`, `/sessions`, `/skills`

**Shortcuts**
- `shift+tab` — toggle auto/spec mode
- `ctrl+L` — clear screen
- `ctrl+N` — switch model

**Auto Levels**
- `low` — safe edits only
- `medium` — development work
- `high` — deployment ops

---

## Claude Code vs Droid

| Feature | Claude Code | Droid |
|---------|-------------|-------|
| UI | Simple two-pane | Rich TUI |
| Skills | Built-in | Rich `/skills` |
| MCP | Built-in | `/mcp` managed |
| Git | Recommended | Not required |
| Execution | Auto Bash | Confirmation |

---

## Claude Code vs Codex CLI

| Feature | Claude Code | Codex CLI |
|---------|-------------|-----------|
| Model | Claude | GPT/Codex |
| API | Anthropic | OpenAI |
| UI | TUI | Single-line |
| Images | ❌ | ✅ |
| Skills | Built-in | `/skills` |

---

## Sub-agent Delegation Matrix

| Task Type | Agent | Model |
|-----------|-------|-------|
| Programming | Droid (interactive) | Claude Code |
| Search/Fact-check | Sub-agent | Grok (`GrokCheck`) |
| Batch text | Sub-agent | MiniMax (`cheap`) |
| Long docs | Sub-agent | Kimi K2.5 (256K) |
| Planning | Main agent | Opus |
| Debug | Sub-agent | Codex |

**Main agent role**: Project manager — plan, spawn, supervise, report. Don't write code.

---

## API Limitations

Current key **cannot** access `foxcode-*` models.

**Available:**
- ✅ `claude-opus-4-6` (current)
- ✅ `claude-opus-4-5-20251101`
- ✅ `claude-sonnet-4-5-20251001`

---

## Automation Boundaries

- ✅ Docker/services (run/rebuild/pause)
- ✅ Write configs/files
- ⚠️ Ask before destructive deletions
- ⚠️ Ask before public exposure

---

## Service Management

- Logs: `~/User_Services/services-logs`
- Docs naming: `XXX_SERVICE.md`
- Check ports via Services Log before allocation
