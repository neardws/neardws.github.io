#!/usr/bin/env python3
"""
Remote macOS execution wrapper for darwin-only skills.
Executes commands on a remote macOS machine via SSH.

Usage: remote_exec.py <binary_name> [args...]

Environment Variables:
    SSH_HOST    - Remote macOS host (default: 192.168.31.171)
    SSH_USER    - Remote macOS user (default: neardws)
    SSH_OPTIONS - Additional SSH options (space-separated, default: -o ConnectTimeout=10 -o BatchMode=yes)
"""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from typing import Dict, List, NoReturn

# Default configuration
# NOTE: We default to the current "main Mac" on the LAN.
DEFAULT_SSH_HOST = "192.168.31.114"
DEFAULT_SSH_USER = "neardws"
DEFAULT_SSH_OPTIONS = "-o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=accept-new"

# Installation instructions for each binary
INSTALL_INSTRUCTIONS: Dict[str, str] = {
    "imsg": "brew install steipete/tap/imsg",
    "memo": "brew tap antoniorodr/memo && brew install antoniorodr/memo/memo",
    "remindctl": "brew install steipete/tap/remindctl",
    "grizzly": "go install github.com/tylerwince/grizzly/cmd/grizzly@latest",
    "codexbar": "brew install --cask steipete/tap/codexbar",
    "peekaboo": "brew install steipete/tap/peekaboo",
    "things": "go install github.com/ossianhempel/things3-cli/cmd/things@latest",
    "bird": "brew install steipete/tap/bird (or npm i -g @steipete/bird)",
}

# Environment files to source for specific binaries (remote macOS paths)
# These are sourced with `set -a` to export all variables
ENV_FILES: Dict[str, str] = {
    "bird": "~/User_Services/x/.env",
}


def get_config() -> tuple[str, str, List[str]]:
    """Get SSH configuration from environment or defaults."""
    host = os.environ.get("SSH_HOST", DEFAULT_SSH_HOST)
    user = os.environ.get("SSH_USER", DEFAULT_SSH_USER)
    options_str = os.environ.get("SSH_OPTIONS", DEFAULT_SSH_OPTIONS)
    options = shlex.split(options_str)
    return host, user, options


def build_remote_script(binary: str, args: List[str]) -> str:
    """Build the remote bash script that checks for binary and executes it."""
    install_cmd = INSTALL_INSTRUCTIONS.get(binary, f"Please install '{binary}' on the remote macOS system.")
    
    # Escape arguments for remote execution
    escaped_args = " ".join(shlex.quote(arg) for arg in args)
    
    # Check if this binary needs an env file sourced
    env_file = ENV_FILES.get(binary)
    env_source_line = ""
    if env_file:
        # Use set -a to export all variables from the env file
        env_source_line = f"set -a; source {env_file} 2>/dev/null || true; set +a"
    
    # Ensure Homebrew is on PATH for non-interactive SSH sessions.
    # We cannot rely on zsh init files when running `bash -c` over SSH.
    script = f'''export PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH
{env_source_line}
if ! command -v {shlex.quote(binary)} &>/dev/null; then
    echo "Error: '{binary}' is not installed on this macOS system." >&2
    echo "Install with: {install_cmd}" >&2
    exit 127
fi
exec {shlex.quote(binary)} {escaped_args}
'''
    return script.strip()


def main() -> NoReturn:
    if len(sys.argv) < 2:
        print("Error: No command specified", file=sys.stderr)
        print("Usage: remote_exec.py <binary_name> [args...]", file=sys.stderr)
        sys.exit(1)

    binary = sys.argv[1]
    args = sys.argv[2:]

    host, user, ssh_options = get_config()
    remote_script = build_remote_script(binary, args)

    # Build SSH command - quote the script properly for bash -c
    ssh_cmd = [
        "ssh",
        *ssh_options,
        f"{user}@{host}",
        f"bash -c {shlex.quote(remote_script)}"
    ]

    # Execute SSH
    try:
        result = subprocess.run(ssh_cmd, capture_output=False)
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("Error: 'ssh' command not found. Please install OpenSSH client.", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
