---
name: remote-macos-apple-photos
description: Remote Apple Photos management via Clawdbot node. List albums, search photos, export on Mac Mini M4.
metadata: {"clawdbot":{"emoji":"📷","os":["linux"]}}
---

# Remote macOS Apple Photos

Query Apple Photos on Mac Mini M4 node using AppleScript.

## Requirements
- Mac Mini M4 node connected
- On macOS: Photos.app configured

## Common Commands

### List albums
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["osascript", "-e", "tell application \"Photos\" to get name of every album"]
}
```

### Get recent photos
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["osascript", "-e", "tell application \"Photos\" to get filename of media items 1 thru 10"]
}
```
