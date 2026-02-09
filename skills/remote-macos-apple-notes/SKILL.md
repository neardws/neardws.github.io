---
name: remote-macos-apple-notes
description: Remote Apple Notes management via Clawdbot node. Create, view, edit, delete, search, move, and export notes on Mac Mini M4.
homepage: https://github.com/antoniorodr/memo
metadata: {"clawdbot":{"emoji":"📝","os":["linux"]}}
---

# Remote macOS Apple Notes (memo)

Use `memo` commands on Mac Mini M4 node to manage Apple Notes.

## Requirements
- Mac Mini M4 node connected
- On macOS: `memo` installed, Notes.app configured

## Common Commands

### List notes
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["memo", "list", "--limit", "10", "--json"]
}
```

### Search notes
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["memo", "search", "query", "--json"]
}
```

### Create note
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["memo", "create", "--title", "Note Title", "--body", "Content here"]
}
```

### View note
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["memo", "show", "note-id", "--json"]
}
```

## Notes
- Install: `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
