---
name: remote-macos-imsg
description: Remote iMessage/SMS CLI for listing chats, history, watch, and sending via Clawdbot node. Executes imsg commands on Mac Mini M4 node.
homepage: https://imsg.to
metadata: {"clawdbot":{"emoji":"📨","os":["linux"]}}
---

# Remote macOS iMessage (imsg)

Use `imsg` commands on Mac Mini M4 node to read and send Messages.app iMessage/SMS.

## Requirements
- Mac Mini M4 node connected (`clawdbot nodes status`)
- On macOS: `imsg` installed, Messages.app signed in, Full Disk Access, Automation permission

## Usage

Use the `nodes` tool with `action: "run"` and `node: "Mac Mini M4"`:

```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["imsg", "chats", "--limit", "10", "--json"]
}
```

## Common Commands

### List chats
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["imsg", "chats", "--limit", "10", "--json"]
}
```

### Get chat history
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["imsg", "history", "--chat-id", "1", "--limit", "20", "--json"]
}
```

### Send message
```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["imsg", "send", "--to", "+14155551212", "--text", "Hello!"]
}
```

## Notes
- `--service imessage|sms|auto` controls delivery method
- Confirm recipient + message before sending
- Install on Mac: `brew install steipete/tap/imsg`
