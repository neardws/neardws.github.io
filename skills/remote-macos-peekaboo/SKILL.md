---
name: remote-macos-peekaboo
description: Remote macOS UI automation via Clawdbot node. Capture screens, inspect UI elements, drive input on Mac Mini M4.
homepage: https://github.com/steipete/peekaboo
metadata: {"clawdbot":{"emoji":"👀","os":["linux"]}}
---

# Remote macOS Peekaboo (UI Automation)

Use `peekaboo` commands on Mac Mini M4 node for UI automation.

## Requirements
- Mac Mini M4 node connected
- On macOS: `peekaboo` installed, Accessibility permission granted

## Common Commands

### Capture screen
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["peekaboo", "capture", "--format", "png"]
}
```

### List windows
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["peekaboo", "windows", "--json"]
}
```

### Click element
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["peekaboo", "click", "--x", "100", "--y", "200"]
}
```

## Notes
- Install: `brew install steipete/tap/peekaboo`
- Requires Accessibility permission in System Settings
