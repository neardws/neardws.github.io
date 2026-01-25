# remote-mac

Wrapper utilities to run macOS-side tools over SSH.

This workspace delegates to your existing mac-remote service:

- `~/User_Services/mac-remote/.env` (defines `MAC_USER`, `MAC_HOST`)
- `~/User_Services/mac-remote/mac-remote.sh`

## Quick start

```bash
cd /home/neardws/clawd
chmod +x remote-mac/remote-mac.sh

# sanity check
remote-mac/remote-mac.sh doctor
remote-mac/remote-mac.sh bins

# safe test
remote-mac/remote-mac.sh notify "Clawdbot" "Remote Mac is connected"
```

## Install packages on the Mac

```bash
remote-mac/remote-mac.sh brew-install ffmpeg gifgrep openai-whisper
```

## Convenience commands

- Reminders:
  - `remote-mac/remote-mac.sh reminders lists`
  - `remote-mac/remote-mac.sh reminders show [list]`
  - `remote-mac/remote-mac.sh reminders add <list> <title> [due]`
  - `remote-mac/remote-mac.sh reminders done <list> <title>`

- Notes (memo CLI):
  - `remote-mac/remote-mac.sh notes <memo args...>`

- Escape hatch:
  - `remote-mac/remote-mac.sh run <command...>`

## Security

This folder does **not** store Mac credentials. It relies on the `.env` managed in `~/User_Services/mac-remote/`.
