---
name: remote-macos-things-mac
description: Remote Things 3 management via the `things` CLI on macOS through SSH. Add/update projects+todos via URL scheme; read/search/list from the local Things database. Use when a user asks to add a task to Things, list inbox/today/upcoming, search tasks, or inspect projects/areas/tags.
homepage: https://github.com/ossianhempel/things3-cli
metadata: {"clawdbot":{"emoji":"✅","os":["linux"],"requires":{"bins":["ssh"]}}}
---

# Remote Things 3 CLI

Use `things` commands on a remote macOS machine via SSH to read your local Things database (inbox/today/search/projects/areas/tags) and to add/update todos via the Things URL scheme.

## Requirements
- SSH access to the macOS host (key-based auth recommended)
- On macOS: `things` installed, Full Disk Access granted to calling app (Terminal)
- Optional: `THINGS_AUTH_TOKEN` set for update operations

## Configuration
Environment variables (optional):
- `SSH_HOST` - Remote macOS host (default: 192.168.31.171)
- `SSH_USER` - Remote macOS user (default: neardws)
- `SSH_OPTIONS` - Additional SSH options

## Usage

All commands are executed via the wrapper script:

```bash
# Read-only (DB)
{baseDir}/scripts/things.sh inbox --limit 50
{baseDir}/scripts/things.sh today
{baseDir}/scripts/things.sh upcoming
{baseDir}/scripts/things.sh search "query"
{baseDir}/scripts/things.sh projects
{baseDir}/scripts/things.sh areas
{baseDir}/scripts/things.sh tags

# Write (URL scheme)
{baseDir}/scripts/things.sh add "Buy milk"
{baseDir}/scripts/things.sh add "Call mom" --notes "discuss trip" --when today --deadline 2026-01-02
{baseDir}/scripts/things.sh --dry-run add "Title"  # Safe preview
```

## Read-Only Commands (Database)
```bash
{baseDir}/scripts/things.sh inbox --limit 50
{baseDir}/scripts/things.sh today
{baseDir}/scripts/things.sh upcoming
{baseDir}/scripts/things.sh search "meeting"
{baseDir}/scripts/things.sh projects
{baseDir}/scripts/things.sh areas
{baseDir}/scripts/things.sh tags
```

## Write Commands (URL Scheme)

### Add Todos
```bash
# Basic
{baseDir}/scripts/things.sh add "Buy milk"

# With notes
{baseDir}/scripts/things.sh add "Buy milk" --notes "2% + bananas"

# Into a project/area
{baseDir}/scripts/things.sh add "Book flights" --list "Travel"

# With heading
{baseDir}/scripts/things.sh add "Pack charger" --list "Travel" --heading "Before"

# With tags
{baseDir}/scripts/things.sh add "Call dentist" --tags "health,phone"

# With checklist
{baseDir}/scripts/things.sh add "Trip prep" --checklist-item "Passport" --checklist-item "Tickets"

# Safe preview (doesn't execute)
{baseDir}/scripts/things.sh --dry-run add "Title"
```

### Update Todos (requires auth token)
```bash
# First get the ID
{baseDir}/scripts/things.sh search "milk" --limit 5

# Then update (requires THINGS_AUTH_TOKEN on macOS host)
{baseDir}/scripts/things.sh update --id <UUID> --auth-token <TOKEN> "New title"
{baseDir}/scripts/things.sh update --id <UUID> --auth-token <TOKEN> --notes "New notes"
{baseDir}/scripts/things.sh update --id <UUID> --auth-token <TOKEN> --completed
```

## Notes
- Remote macOS must have `things` installed: `go install github.com/ossianhempel/things3-cli/cmd/things@latest`
- `--dry-run` prints the URL and does not open Things
- Full Disk Access must be granted to Terminal/calling app on macOS
- For update operations, set `THINGS_AUTH_TOKEN` on the macOS host
