---
name: remote-macos-homebrew
description: Remote Homebrew package management via Clawdbot node on Mac Mini M4.
metadata: {"clawdbot":{"emoji":"🍺","os":["linux"]}}
---

# Remote macOS Homebrew

Manage Homebrew packages on Mac Mini M4 node.

## Requirements
- Mac Mini M4 node connected
- On macOS: Homebrew installed at `/opt/homebrew`

## Common Commands

### List installed
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["brew", "list"]
}
```

### Search package
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["brew", "search", "package-name"]
}
```

### Install package
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["brew", "install", "package-name"]
}
```

### Update
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["brew", "update"]
}
```
