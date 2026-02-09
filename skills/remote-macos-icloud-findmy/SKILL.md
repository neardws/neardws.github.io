---
name: remote-macos-icloud-findmy
description: Remote iCloud Find My via Clawdbot node. Query device locations and battery status on Mac Mini M4.
metadata: {"clawdbot":{"emoji":"📍","os":["linux"]}}
---

# Remote macOS iCloud Find My

Query Find My device locations on Mac Mini M4 node.

## Requirements
- Mac Mini M4 node connected
- On macOS: Find My app configured, iCloud signed in

## Common Commands

### List devices
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["shortcuts", "run", "Find My Devices"]
}
```

## Notes
- Requires Shortcuts app with "Find My Devices" shortcut configured
- Or use third-party CLI tools for Find My access
