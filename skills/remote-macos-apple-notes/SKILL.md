---
name: remote-macos-apple-notes
description: Remote Apple Notes management via the `memo` CLI on macOS through SSH. Create, view, edit, delete, search, move, and export notes. Use when a user asks Clawdbot to add a note, list notes, search notes, or manage note folders on the remote macOS.
homepage: https://github.com/antoniorodr/memo
metadata: {"clawdbot":{"emoji":"📝","os":["linux"],"requires":{"bins":["ssh"]}}}
---

# Remote Apple Notes CLI (memo)

Use `memo notes` commands on a remote macOS machine via SSH to manage Apple Notes directly from the terminal. Create, view, edit, delete, search, move notes between folders, and export to HTML/Markdown.

## Requirements
- SSH access to the macOS host (key-based auth recommended)
- On macOS: `memo` installed, Automation access granted to Notes.app

## Configuration
Environment variables (optional):
- `SSH_HOST` - Remote macOS host (default: 192.168.31.171)
- `SSH_USER` - Remote macOS user (default: neardws)
- `SSH_OPTIONS` - Additional SSH options

## Usage

All commands are executed via the wrapper script:

```bash
# List all notes
{baseDir}/scripts/memo.sh notes

# Filter by folder
{baseDir}/scripts/memo.sh notes -f "Folder Name"

# Search notes (fuzzy)
{baseDir}/scripts/memo.sh notes -s "query"

# Add a new note (interactive)
{baseDir}/scripts/memo.sh notes -a

# Quick add with title
{baseDir}/scripts/memo.sh notes -a "Note Title"

# Edit existing note (interactive)
{baseDir}/scripts/memo.sh notes -e

# Delete a note (interactive)
{baseDir}/scripts/memo.sh notes -d

# Move note to folder (interactive)
{baseDir}/scripts/memo.sh notes -m

# Export to HTML/Markdown
{baseDir}/scripts/memo.sh notes -ex
```

## Common Commands

### View Notes
```bash
{baseDir}/scripts/memo.sh notes
{baseDir}/scripts/memo.sh notes -f "Work"
{baseDir}/scripts/memo.sh notes -s "meeting"
```

### Create Notes
```bash
{baseDir}/scripts/memo.sh notes -a "Shopping List"
```

### Edit/Delete Notes
```bash
{baseDir}/scripts/memo.sh notes -e
{baseDir}/scripts/memo.sh notes -d
```

### Move/Export Notes
```bash
{baseDir}/scripts/memo.sh notes -m
{baseDir}/scripts/memo.sh notes -ex
```

## Limitations
- Cannot edit notes containing images or attachments
- Interactive prompts may require terminal access

## Notes
- Remote macOS must have `memo` installed: `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- Requires Apple Notes.app to be accessible on the macOS host
