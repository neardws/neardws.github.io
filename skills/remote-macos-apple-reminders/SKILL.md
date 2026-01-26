---
name: remote-macos-apple-reminders
description: Remote Apple Reminders management via the `remindctl` CLI on macOS through SSH. List, add, edit, complete, delete reminders. Supports lists, date filters, and JSON/plain output.
homepage: https://github.com/steipete/remindctl
metadata: {"clawdbot":{"emoji":"⏰","os":["linux"],"requires":{"bins":["ssh"]}}}
---

# Remote Apple Reminders CLI (remindctl)

Use `remindctl` commands on a remote macOS machine via SSH to manage Apple Reminders directly from the terminal. Supports list filtering, date-based views, and scripting output.

## Requirements
- SSH access to the macOS host (key-based auth recommended)
- On macOS: `remindctl` installed, Reminders permission granted

## Configuration
Environment variables (optional):
- `SSH_HOST` - Remote macOS host (default: 192.168.31.171)
- `SSH_USER` - Remote macOS user (default: neardws)
- `SSH_OPTIONS` - Additional SSH options

## Usage

All commands are executed via the wrapper script:

```bash
# Check permissions
{baseDir}/scripts/remindctl.sh status
{baseDir}/scripts/remindctl.sh authorize

# View reminders (various filters)
{baseDir}/scripts/remindctl.sh today
{baseDir}/scripts/remindctl.sh tomorrow
{baseDir}/scripts/remindctl.sh week
{baseDir}/scripts/remindctl.sh overdue
{baseDir}/scripts/remindctl.sh upcoming
{baseDir}/scripts/remindctl.sh completed
{baseDir}/scripts/remindctl.sh all

# Specific date
{baseDir}/scripts/remindctl.sh 2026-01-04

# Manage lists
{baseDir}/scripts/remindctl.sh list
{baseDir}/scripts/remindctl.sh list Work
{baseDir}/scripts/remindctl.sh list Projects --create
{baseDir}/scripts/remindctl.sh list Work --rename Office
{baseDir}/scripts/remindctl.sh list Work --delete

# Create reminders
{baseDir}/scripts/remindctl.sh add "Buy milk"
{baseDir}/scripts/remindctl.sh add --title "Call mom" --list Personal --due tomorrow

# Edit/complete/delete
{baseDir}/scripts/remindctl.sh edit 1 --title "New title" --due 2026-01-04
{baseDir}/scripts/remindctl.sh complete 1 2 3
{baseDir}/scripts/remindctl.sh delete 4A83 --force

# Output formats
{baseDir}/scripts/remindctl.sh today --json
{baseDir}/scripts/remindctl.sh today --plain
{baseDir}/scripts/remindctl.sh today --quiet
```

## Date Formats
Accepted by `--due` and date filters:
- `today`, `tomorrow`, `yesterday`
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:mm`
- ISO 8601 (`2026-01-04T12:34:56Z`)

## Notes
- Remote macOS must have `remindctl` installed: `brew install steipete/tap/remindctl`
- If access is denied, enable Terminal/remindctl in System Settings → Privacy & Security → Reminders on the Mac
