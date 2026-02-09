---
name: remote-macos-apple-reminders
description: Remote Apple Reminders management via Clawdbot node. List, add, edit, complete, delete reminders on Mac Mini M4.
homepage: https://github.com/steipete/remindctl
metadata: {"clawdbot":{"emoji":"✅","os":["linux"]}}
---

# Remote macOS Apple Reminders (remindctl)

Use `remindctl` commands on Mac Mini M4 node to manage Apple Reminders.

## Requirements
- Mac Mini M4 node connected
- On macOS: `remindctl` installed, Reminders.app configured

## Common Commands

### List reminders
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["remindctl", "list", "--json"]
}
```

### Add reminder
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["remindctl", "add", "--title", "Task", "--list", "Inbox"]
}
```

### Complete reminder
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["remindctl", "complete", "reminder-id"]
}
```

## Notes
- Install: `brew install steipete/tap/remindctl`
