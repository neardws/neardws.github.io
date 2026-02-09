---
name: remote-macos-bird
description: Remote X/Twitter CLI for searching, reading tweets/threads, and viewing user timelines via Clawdbot node. Executes bird commands on Mac Mini M4 node.
homepage: https://github.com/steipete/bird
metadata: {"clawdbot":{"emoji":"🐦","os":["linux"]}}
---

# Remote macOS Bird (X/Twitter CLI)

Use `bird` commands on Mac Mini M4 node to search and read X/Twitter content.

## Requirements
- Mac Mini M4 node connected
- On macOS: `bird` installed with valid X API credentials in `~/User_Services/x/.env`

## Usage

Use the `nodes` tool with `action: "run"` and `node: "Mac Mini M4"`:

```json
{
  "action": "run",
  "node": "Mac Mini M4",
  "command": ["bash", "-c", "source ~/User_Services/x/.env && bird search 'query' --limit 10"]
}
```

## Common Commands

### Search tweets
```bash
ssh neardws@192.168.31.114 "/opt/homebrew/bin/bird search 'AI news' -n 10 --json"
```

### Get user timeline
```bash
ssh neardws@192.168.31.114 "/opt/homebrew/bin/bird user-tweets @username -n 10 --json"
```

### Read tweet/thread
```bash
ssh neardws@192.168.31.114 "/opt/homebrew/bin/bird read 1234567890 --json"
```

### Check auth status
```bash
ssh neardws@192.168.31.114 "/opt/homebrew/bin/bird whoami"
```

## Notes
- Uses Safari cookies for authentication (auto-extracted)
- Install: `brew install steipete/tap/bird`
- Binary path: `/opt/homebrew/bin/bird`
