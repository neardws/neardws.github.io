---
name: remote-macos-bear-notes
description: Remote Bear notes management via grizzly CLI on macOS through SSH. Create, search, and manage Bear notes.
homepage: https://bear.app
metadata: {"clawdbot":{"emoji":"🐻","os":["linux"],"requires":{"bins":["ssh"]}}}
---

# Remote Bear Notes (grizzly)

Use `grizzly` commands on a remote macOS machine via SSH to create, read, and manage notes in Bear.

## Requirements
- SSH access to the macOS host (key-based auth recommended)
- On macOS: `grizzly` installed, Bear app installed and running
- For some operations: Bear app token stored in `~/.config/grizzly/token`

## Configuration
Environment variables (optional):
- `SSH_HOST` - Remote macOS host (default: 192.168.31.171)
- `SSH_USER` - Remote macOS user (default: neardws)
- `SSH_OPTIONS` - Additional SSH options

## Getting a Bear Token (on macOS)

For operations that require a token (add-text, tags, open-note --selected):
1. Open Bear → Help → API Token → Copy Token
2. Save it: `echo "YOUR_TOKEN" > ~/.config/grizzly/token`

## Usage

All commands are executed via the wrapper script:

```bash
# Create a note
echo "Note content here" | {baseDir}/scripts/grizzly.sh create --title "My Note" --tag work
{baseDir}/scripts/grizzly.sh create --title "Quick Note" --tag inbox < /dev/null

# Open/read a note by ID
{baseDir}/scripts/grizzly.sh open-note --id "NOTE_ID" --enable-callback --json

# Append text to a note
echo "Additional content" | {baseDir}/scripts/grizzly.sh add-text --id "NOTE_ID" --mode append --token-file ~/.config/grizzly/token

# List all tags
{baseDir}/scripts/grizzly.sh tags --enable-callback --json --token-file ~/.config/grizzly/token

# Search notes (via open-tag)
{baseDir}/scripts/grizzly.sh open-tag --name "work" --enable-callback --json
```

## Common Flags
- `--dry-run` — Preview the URL without executing
- `--print-url` — Show the x-callback-url
- `--enable-callback` — Wait for Bear's response (needed for reading data)
- `--json` — Output as JSON (when using callbacks)
- `--token-file PATH` — Path to Bear API token file

## Remote Configuration

Grizzly reads config from (in priority order on macOS):
1. CLI flags
2. Environment variables (`GRIZZLY_TOKEN_FILE`, `GRIZZLY_CALLBACK_URL`, `GRIZZLY_TIMEOUT`)
3. `.grizzly.toml` in current directory
4. `~/.config/grizzly/config.toml`

Example `~/.config/grizzly/config.toml` on the macOS host:
```toml
token_file = "~/.config/grizzly/token"
callback_url = "http://127.0.0.1:42123/success"
timeout = "5s"
```

## Notes
- Bear must be running on the macOS host for commands to work
- Note IDs are Bear's internal identifiers (visible in note info or via callbacks)
- Use `--enable-callback` when you need to read data back from Bear
- Remote macOS must have `grizzly` installed: `go install github.com/tylerwince/grizzly/cmd/grizzly@latest`
