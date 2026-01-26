# Remote macOS Execution Scripts

Shared execution wrapper scripts for all `remote-macos-*` proxy skills that execute darwin-only commands on a remote macOS machine via SSH.

## Files

- `remote_exec.py` - Python-based remote execution wrapper (recommended)
- `remote_exec.sh` - Bash-based remote execution wrapper

## Configuration

Environment variables (all optional, with defaults):

| Variable    | Default                                                                   | Description                      |
| ----------- | ------------------------------------------------------------------------- | -------------------------------- |
| `SSH_HOST`    | `192.168.31.171`                                                            | Remote macOS host IP or hostname |
| `SSH_USER`    | `neardws`                                                                   | Remote macOS username            |
| `SSH_OPTIONS` | `-o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=accept-new` | Additional SSH options           |

## Usage

```bash
# Direct usage
./remote_exec.py imsg chats --limit 10 --json
./remote_exec.py memo notes -s "meeting"
./remote_exec.py remindctl today --json

# With custom host
SSH_HOST=192.168.1.100 ./remote_exec.py imsg chats

# With custom user
SSH_USER=john ./remote_exec.py memo notes
```

## Requirements

- `ssh` client installed on Linux
- SSH key-based authentication configured to the macOS host
- Respective binary installed on the macOS host (imsg, memo, remindctl, etc.)

## Supported Binaries

| Binary    | macOS Install Command                                            |
| --------- | ---------------------------------------------------------------- |
| `imsg`      | `brew install steipete/tap/imsg`                                   |
| `memo`      | `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`  |
| `remindctl` | `brew install steipete/tap/remindctl`                              |
| `grizzly`   | `go install github.com/tylerwince/grizzly/cmd/grizzly@latest`      |
| `codexbar`  | `brew install --cask steipete/tap/codexbar`                        |
| `peekaboo`  | `brew install steipete/tap/peekaboo`                               |
| `things`    | `go install github.com/ossianhempel/things3-cli/cmd/things@latest` |
| `bird`      | `brew install steipete/tap/bird` or `npm i -g @steipete/bird`        |

## Error Handling

If a binary is not installed on the remote macOS, the script will output a friendly error message with installation instructions:

```
Error: 'imsg' is not installed on this macOS system.
Install with: brew install steipete/tap/imsg
```
