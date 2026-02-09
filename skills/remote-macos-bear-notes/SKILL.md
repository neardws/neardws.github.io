---
name: remote-macos-bear-notes
description: Remote Bear notes management via Clawdbot node. Create, search, and manage Bear notes on Mac Mini M4.
homepage: https://github.com/tylerwince/grizzly
metadata: {"clawdbot":{"emoji":"🐻","os":["linux"]}}
---

# Remote macOS Bear Notes (grizzly)

Use `grizzly` commands on Mac Mini M4 node to manage Bear notes.

## Requirements
- Mac Mini M4 node connected
- On macOS: `grizzly` installed, Bear app configured

## Common Commands

### List notes
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["grizzly", "list", "--json"]
}
```

### Search notes
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["grizzly", "search", "query", "--json"]
}
```

### Create note
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["grizzly", "create", "--title", "Title", "--text", "Content"]
}
```

## Notes
- Install: `go install github.com/tylerwince/grizzly/cmd/grizzly@latest`
