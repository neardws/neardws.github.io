---
name: remote-macos-peekaboo
description: Remote macOS UI automation via the Peekaboo CLI through SSH. Capture and inspect screens, target UI elements, drive input, and manage apps/windows/menus.
homepage: https://peekaboo.boo
metadata: {"clawdbot":{"emoji":"👀","os":["linux"],"requires":{"bins":["ssh"]}}}
---

# Remote Peekaboo (macOS UI Automation)

Peekaboo is a full macOS UI automation CLI: capture/inspect screens, target UI elements, drive input, and manage apps/windows/menus. Execute commands on a remote macOS machine via SSH.

## Requirements
- SSH access to the macOS host (key-based auth recommended)
- On macOS: `peekaboo` installed, Screen Recording + Accessibility permissions granted

## Configuration
Environment variables (optional):
- `SSH_HOST` - Remote macOS host (default: 192.168.31.171)
- `SSH_USER` - Remote macOS user (default: neardws)
- `SSH_OPTIONS` - Additional SSH options

## Usage

All commands are executed via the wrapper script:

```bash
# Check permissions
{baseDir}/scripts/peekaboo.sh permissions

# List apps
{baseDir}/scripts/peekaboo.sh list apps --json

# Capture annotated screenshot
{baseDir}/scripts/peekaboo.sh see --annotate --path /tmp/peekaboo-see.png

# Click on element
{baseDir}/scripts/peekaboo.sh click --on B1

# Type text
{baseDir}/scripts/peekaboo.sh type "Hello" --return
```

## Core Commands

### Capture & Vision
```bash
{baseDir}/scripts/peekaboo.sh image --mode screen --screen-index 0 --path /tmp/screen.png
{baseDir}/scripts/peekaboo.sh see --app Safari --annotate --path /tmp/safari.png
{baseDir}/scripts/peekaboo.sh capture live --mode region --region 100,100,800,600 --duration 30
```

### Interaction
```bash
{baseDir}/scripts/peekaboo.sh click --on B3 --app Safari
{baseDir}/scripts/peekaboo.sh type "user@example.com" --app Safari
{baseDir}/scripts/peekaboo.sh press tab --count 1 --app Safari
{baseDir}/scripts/peekaboo.sh hotkey --keys "cmd,shift,t"
{baseDir}/scripts/peekaboo.sh scroll --direction down --amount 6 --smooth
```

### App & Window Management
```bash
{baseDir}/scripts/peekaboo.sh app launch "Safari" --open https://example.com
{baseDir}/scripts/peekaboo.sh window focus --app Safari --window-title "Example"
{baseDir}/scripts/peekaboo.sh window set-bounds --app Safari --x 50 --y 50 --width 1200 --height 800
{baseDir}/scripts/peekaboo.sh app quit --app Safari
```

### Menus & Dock
```bash
{baseDir}/scripts/peekaboo.sh menu click --app Safari --item "New Window"
{baseDir}/scripts/peekaboo.sh dock launch Safari
{baseDir}/scripts/peekaboo.sh menubar list --json
```

### Mouse & Gestures
```bash
{baseDir}/scripts/peekaboo.sh move 500,300 --smooth
{baseDir}/scripts/peekaboo.sh drag --from B1 --to T2
{baseDir}/scripts/peekaboo.sh swipe --from-coords 100,500 --to-coords 100,200 --duration 800
```

## Common Flags
- `--json`/`-j` — Output as JSON
- `--verbose`/`-v` — Verbose output
- `--app` — Target app
- `--window-title` — Target window by title
- `--on`/`--id` — Target element by ID (from `see` output)

## Example Workflow: Login Form
```bash
{baseDir}/scripts/peekaboo.sh see --app Safari --window-title "Login" --annotate --path /tmp/see.png
{baseDir}/scripts/peekaboo.sh click --on B3 --app Safari
{baseDir}/scripts/peekaboo.sh type "user@example.com" --app Safari
{baseDir}/scripts/peekaboo.sh press tab --count 1 --app Safari
{baseDir}/scripts/peekaboo.sh type "password" --app Safari --return
```

## Notes
- Use `peekaboo see --annotate` to identify targets before clicking
- Remote macOS must have `peekaboo` installed: `brew install steipete/tap/peekaboo`
- Requires Screen Recording + Accessibility permissions on the macOS host
