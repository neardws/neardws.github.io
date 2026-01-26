---
name: remote-macos-bird
description: Remote X/Twitter CLI for searching, reading tweets/threads, and viewing user timelines via SSH to macOS. Proxy skill that executes bird commands on a remote macOS machine.
homepage: https://bird.fast
metadata: {"clawdbot":{"emoji":"🐦","os":["linux"],"requires":{"bins":["ssh"]}}}
---

# Remote macOS Bird (X/Twitter CLI)

Use `bird` commands on a remote macOS machine via SSH to search and read X/Twitter content.

## Trigger Words

Use this skill when the user mentions:
- X 搜索、X search、搜索 X
- 推特搜索、Twitter search、搜索推特
- 推文、tweet、read tweet
- X thread、Twitter thread、推特帖子
- X replies、推特回复
- user tweets、用户推文
- Twitter timeline、X timeline

## Requirements
- SSH access to the macOS host (key-based auth recommended)
- On macOS: `bird` installed with valid cookie auth configured

## Configuration
Environment variables (optional):
- `SSH_HOST` - Remote macOS host (default: 192.168.31.171)
- `SSH_USER` - Remote macOS user (default: neardws)
- `SSH_OPTIONS` - Additional SSH options

## Usage

All commands are executed via the wrapper script:

```bash
# Check authentication status
{baseDir}/scripts/bird.sh whoami

# Search tweets
{baseDir}/scripts/bird.sh search "query" -n 10 --json

# Read a single tweet
{baseDir}/scripts/bird.sh read <url-or-id> --json

# Get full conversation thread
{baseDir}/scripts/bird.sh thread <url-or-id> --json

# List replies to a tweet
{baseDir}/scripts/bird.sh replies <url-or-id> -n 10 --json

# Get user's tweets
{baseDir}/scripts/bird.sh user-tweets @handle -n 20 --json
```

## Common Commands

### Check Auth
```bash
{baseDir}/scripts/bird.sh whoami
```

### Search
```bash
# Basic search
{baseDir}/scripts/bird.sh search "AI agents" -n 10 --json

# Search from specific user
{baseDir}/scripts/bird.sh search "from:steipete" --all --max-pages 3 --json
```

### Read Tweet
```bash
# By URL
{baseDir}/scripts/bird.sh read https://x.com/user/status/123456789 --json

# By ID
{baseDir}/scripts/bird.sh read 123456789 --json
```

### Thread
```bash
{baseDir}/scripts/bird.sh thread <url-or-id> --json
```

### Replies
```bash
{baseDir}/scripts/bird.sh replies <url-or-id> -n 20 --json
```

### User Tweets
```bash
{baseDir}/scripts/bird.sh user-tweets @steipete -n 20 --json
```

## Output Options

Always prefer `--json` for structured output:
```bash
--json          # JSON output (recommended)
--json-full     # JSON with raw API response
--plain         # No emoji, no color (script-friendly)
```

## Security Notes

- AUTH_TOKEN and CT0 values are never printed by this skill
- Cookie auth is configured on the remote macOS machine
- All sensitive credentials stay on the remote host

## Supported Subcommands

| Command     | Description              |
| ----------- | ------------------------ |
| `whoami`      | Show logged-in account   |
| `search`      | Search tweets            |
| `read`        | Read a single tweet      |
| `thread`      | Full conversation thread |
| `replies`     | List replies to a tweet  |
| `user-tweets` | User's profile timeline  |

## Notes
- Remote macOS must have `bird` installed: `brew install steipete/tap/bird` or `npm i -g @steipete/bird`
- Cookie auth must be configured on the macOS host (via browser cookies or config file)
- Use `--json` output for all queries to get structured data
