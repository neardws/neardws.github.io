---
name: remote-macos-things-mac
description: Remote Things 3 management via Clawdbot node. Add/update projects+todos, read/search/list from Things database on Mac Mini M4.
homepage: https://github.com/ossianhempel/things3-cli
metadata: {"clawdbot":{"emoji":"📋","os":["linux"]}}
---

# Remote macOS Things 3 (things)

Use `things` commands on Mac Mini M4 node to manage Things 3 tasks.

## Requirements
- Mac Mini M4 node connected
- On macOS: `things` CLI installed, Things 3 app configured

## Common Commands

### List inbox
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["things", "inbox", "--json"]
}
```

### List today
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["things", "today", "--json"]
}
```

### Add task
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["things", "add", "--title", "New Task", "--list", "Inbox"]
}
```

## Notes
- Install: `go install github.com/ossianhempel/things3-cli/cmd/things@latest`
