---
name: remote-macos-apple-contacts
description: Remote Apple Contacts management via Clawdbot node. Query contacts by name, phone, or email on Mac Mini M4.
metadata: {"clawdbot":{"emoji":"👥","os":["linux"]}}
---

# Remote macOS Apple Contacts

Query Apple Contacts on Mac Mini M4 node using AppleScript.

## Requirements
- Mac Mini M4 node connected
- On macOS: Contacts.app configured

## Common Commands

### Search by name
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["osascript", "-e", "tell application \"Contacts\" to get name of every person whose name contains \"John\""]
}
```

### Get all contacts
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["osascript", "-e", "tell application \"Contacts\" to get {name, phones} of every person"]
}
```
