---
name: remote-macos-model-usage
description: Remote CodexBar CLI usage to summarize per-model usage for Codex or Claude via SSH to macOS. Trigger when asked for model-level usage/cost data from codexbar.
metadata: {"clawdbot":{"emoji":"📊","os":["linux"],"requires":{"bins":["ssh"]}}}
---

# Remote Model Usage (CodexBar)

Get per-model usage cost from CodexBar's local cost logs on a remote macOS machine via SSH. Supports "current model" (most recent daily entry) or "all models" summaries for Codex or Claude.

## Requirements
- SSH access to the macOS host (key-based auth recommended)
- On macOS: `codexbar` installed

## Configuration
Environment variables (optional):
- `SSH_HOST` - Remote macOS host (default: 192.168.31.171)
- `SSH_USER` - Remote macOS user (default: neardws)
- `SSH_OPTIONS` - Additional SSH options

## Usage

All commands are executed via the wrapper script:

```bash
# Get current model usage (Codex)
{baseDir}/scripts/codexbar.sh cost --format json --provider codex

# Get current model usage (Claude)
{baseDir}/scripts/codexbar.sh cost --format json --provider claude

# Get all models
{baseDir}/scripts/codexbar.sh cost --format json --provider codex
```

## Direct CLI Examples

```bash
# Fetch raw cost data
{baseDir}/scripts/codexbar.sh cost --format json --provider codex

# Get model breakdown
{baseDir}/scripts/codexbar.sh cost --format json --provider claude
```

## Current Model Logic
- Uses the most recent daily row with `modelBreakdowns`
- Picks the model with the highest cost in that row
- Falls back to the last entry in `modelsUsed` when breakdowns are missing

## Output
- Text (default) or JSON (`--format json`)
- Values are cost-only per model; tokens are not split by model in CodexBar output

## Notes
- Remote macOS must have `codexbar` installed: `brew install --cask steipete/tap/codexbar`
- CodexBar GUI must have been run at least once to populate cost data
