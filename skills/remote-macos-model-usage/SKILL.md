---
name: remote-macos-model-usage
description: Remote CodexBar CLI usage to summarize per-model usage for Codex or Claude via Clawdbot node on Mac Mini M4.
homepage: https://github.com/steipete/codexbar
metadata: {"clawdbot":{"emoji":"📊","os":["linux"]}}
---

# Remote macOS Model Usage (codexbar)

Use `codexbar` commands on Mac Mini M4 node to check model usage stats.

## Requirements
- Mac Mini M4 node connected
- On macOS: `codexbar` installed

## Common Commands

### Get usage summary
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["codexbar", "usage", "--json"]
}
```

## Notes
- Install: `brew install --cask steipete/tap/codexbar`
