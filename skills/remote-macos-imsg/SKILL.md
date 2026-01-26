---
name: remote-macos-imsg
description: Remote iMessage/SMS CLI for listing chats, history, watch, and sending via SSH to macOS. Proxy skill that executes imsg commands on a remote macOS machine.
homepage: https://imsg.to
metadata: {"clawdbot":{"emoji":"📨","os":["linux"],"requires":{"bins":["ssh"]}}}
---

# Remote macOS iMessage (imsg)

Use `imsg` commands on a remote macOS machine via SSH to read and send Messages.app iMessage/SMS.

## Requirements
- SSH access to the macOS host (key-based auth recommended)
- On macOS: `imsg` installed, Messages.app signed in, Full Disk Access for terminal, Automation permission

## Configuration
Environment variables (optional):
- `SSH_HOST` - Remote macOS host (default: 192.168.31.171)
- `SSH_USER` - Remote macOS user (default: neardws)
- `SSH_OPTIONS` - Additional SSH options

## Usage

All commands are executed via the wrapper script:

```bash
# List chats
{baseDir}/scripts/imsg.sh chats --limit 10 --json

# Get chat history
{baseDir}/scripts/imsg.sh history --chat-id 1 --limit 20 --attachments --json

# Watch for new messages
{baseDir}/scripts/imsg.sh watch --chat-id 1 --attachments

# Send a message
{baseDir}/scripts/imsg.sh send --to "+14155551212" --text "hi"

# Send with attachment
{baseDir}/scripts/imsg.sh send --to "+14155551212" --text "hi" --file /path/pic.jpg
```

## Common Commands

### List chats
```bash
{baseDir}/scripts/imsg.sh chats --limit 10 --json
```

### Get history
```bash
{baseDir}/scripts/imsg.sh history --chat-id 1 --limit 20 --attachments --json
```

### Watch for messages
```bash
{baseDir}/scripts/imsg.sh watch --chat-id 1 --attachments
```

### Send message
```bash
{baseDir}/scripts/imsg.sh send --to "+14155551212" --text "Hello!"
```

## Notes
- `--service imessage|sms|auto` controls delivery method
- Confirm recipient + message before sending
- Remote macOS must have `imsg` installed: `brew install steipete/tap/imsg`
