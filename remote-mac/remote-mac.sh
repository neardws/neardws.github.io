#!/usr/bin/env bash
set -euo pipefail

# remote-mac.sh — run macOS-side tools over SSH.
#
# Default setup expects your existing mac-remote service at:
#   ~/User_Services/mac-remote
# containing:
#   - .env (MAC_USER, MAC_HOST)
#   - mac-remote.sh
#
# You can override with:
#   MAC_REMOTE_DIR=... ./remote-mac.sh ...

MAC_REMOTE_DIR="${MAC_REMOTE_DIR:-$HOME/User_Services/mac-remote}"
MAC_REMOTE_ENTRY="$MAC_REMOTE_DIR/mac-remote.sh"

usage() {
  cat <<'EOF'
Usage:
  remote-mac.sh doctor
  remote-mac.sh bins
  remote-mac.sh brew-install <pkg...>

  # Convenience wrappers (run on Mac):
  remote-mac.sh notify <title> <message>
  remote-mac.sh reminders <subcommand> ...
  remote-mac.sh notes <subcommand> ...
  remote-mac.sh imsg <args...>
  remote-mac.sh peekaboo <args...>
  remote-mac.sh things <args...>
  remote-mac.sh ffmpeg <args...>
  remote-mac.sh gifgrep <args...>
  remote-mac.sh whisper <args...>

  # Escape hatch (run arbitrary command on Mac):
  remote-mac.sh run <command...>

Notes:
- This script delegates to ~/User_Services/mac-remote/mac-remote.sh.
- brew installs modify the Mac. Use intentionally.
EOF
}

need_entry() {
  if [[ ! -x "$MAC_REMOTE_ENTRY" ]]; then
    echo "Error: missing executable: $MAC_REMOTE_ENTRY" >&2
    echo "Expected your mac-remote service at: $MAC_REMOTE_DIR" >&2
    exit 1
  fi
}

main() {
  [[ $# -ge 1 ]] || { usage; exit 1; }
  need_entry

  cmd="$1"; shift
  case "$cmd" in
    doctor)
      "$MAC_REMOTE_ENTRY" run "set -e; echo HOST:\$(hostname); sw_vers -productVersion; echo BREW:\$(command -v brew); brew --version | head -n 1;"
      ;;

    bins)
      # Presence-only checks (avoid commands that hang on --version)
      "$MAC_REMOTE_ENTRY" run 'set -e; echo "BINS:"; for b in ffmpeg whisper gifgrep memo remindctl imsg peekaboo things brew; do if command -v "$b" >/dev/null 2>&1; then echo "$b OK $(command -v "$b")"; else echo "$b MISSING"; fi; done'
      ;;

    brew-install)
      [[ $# -ge 1 ]] || { echo "Usage: remote-mac.sh brew-install <pkg...>" >&2; exit 1; }
      # shellcheck disable=SC2029
      "$MAC_REMOTE_ENTRY" run "set -e; brew update; brew install $*"
      ;;

    notify)
      [[ $# -ge 2 ]] || { echo "Usage: remote-mac.sh notify <title> <message>" >&2; exit 1; }
      "$MAC_REMOTE_ENTRY" notify "$1" "$2"
      ;;

    reminders)
      [[ $# -ge 1 ]] || { echo "Usage: remote-mac.sh reminders <list|show|done|lists> ..." >&2; exit 1; }
      sub="$1"; shift
      case "$sub" in
        list|lists) "$MAC_REMOTE_ENTRY" reminder-list ;;
        show) if [[ $# -ge 1 ]]; then "$MAC_REMOTE_ENTRY" reminder-show "$1"; else "$MAC_REMOTE_ENTRY" reminder-show; fi ;;
        done) [[ $# -ge 2 ]] || { echo "Usage: remote-mac.sh reminders done <list> <title>" >&2; exit 1; }
              "$MAC_REMOTE_ENTRY" reminder-done "$1" "$2" ;;
        add)  [[ $# -ge 2 ]] || { echo "Usage: remote-mac.sh reminders add <list> <title> [due]" >&2; exit 1; }
              list="$1"; title="$2"; due="${3:-}";
              if [[ -n "$due" ]]; then "$MAC_REMOTE_ENTRY" reminder "$list" "$title" "$due"; else "$MAC_REMOTE_ENTRY" reminder "$list" "$title"; fi
              ;;
        *) echo "Unknown reminders subcommand: $sub" >&2; exit 1 ;;
      esac
      ;;

    notes)
      # memo CLI runs on Mac; we forward arbitrary args
      [[ $# -ge 1 ]] || { echo "Usage: remote-mac.sh notes <memo-args...>" >&2; exit 1; }
      "$MAC_REMOTE_ENTRY" run "memo $*"
      ;;

    imsg|peekaboo|things|ffmpeg|gifgrep|whisper)
      [[ $# -ge 1 ]] || { echo "Usage: remote-mac.sh $cmd <args...>" >&2; exit 1; }
      "$MAC_REMOTE_ENTRY" run "$cmd $*"
      ;;

    run)
      [[ $# -ge 1 ]] || { echo "Usage: remote-mac.sh run <command...>" >&2; exit 1; }
      "$MAC_REMOTE_ENTRY" run "$*"
      ;;

    -h|--help|help)
      usage
      ;;

    *)
      echo "Unknown command: $cmd" >&2
      usage
      exit 1
      ;;
  esac
}

main "$@"
