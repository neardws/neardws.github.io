#!/usr/bin/env python3
"""Read-only server commands for Telegram.

Implements:
- /server status
- /server tmux
- /server disk

This intentionally avoids secrets and destructive actions.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import textwrap
import time

import psutil

TMUXD_SOCKET = "/tmp/clawdbot-tmux-sockets/clawdbot.sock"


def sh(cmd: list[str], timeout: int = 15) -> tuple[int, str, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(timeout=timeout)
    return p.returncode, out.strip(), err.strip()


def fmt_bytes(n: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"


def cmd_status() -> str:
    boot = psutil.boot_time()
    up_s = int(time.time() - boot)

    vm = psutil.virtual_memory()
    load = os.getloadavg() if hasattr(os, "getloadavg") else (0, 0, 0)

    # sample CPU quickly
    cpu = psutil.cpu_percent(interval=0.3)

    lines = []
    lines.append(f"Host: {platform.node()}  ({platform.system()} {platform.release()})")
    lines.append(f"Uptime: {up_s//3600}h{(up_s%3600)//60}m")
    lines.append(f"Load: {load[0]:.2f} {load[1]:.2f} {load[2]:.2f}")
    lines.append(f"CPU: {cpu:.1f}%")
    lines.append(f"Mem: {fmt_bytes(vm.used)}/{fmt_bytes(vm.total)} ({vm.percent:.1f}%)")

    # network quick info
    net = psutil.net_io_counters()
    lines.append(f"Net: sent {fmt_bytes(net.bytes_sent)}, recv {fmt_bytes(net.bytes_recv)}")

    return "\n".join(lines)


def cmd_disk() -> str:
    parts = [p for p in psutil.disk_partitions(all=False) if p.fstype]
    rows = []
    for p in parts:
        try:
            u = psutil.disk_usage(p.mountpoint)
        except PermissionError:
            continue
        rows.append((p.mountpoint, u.used, u.total, u.percent))

    rows.sort(key=lambda r: (r[3], r[2]), reverse=True)
    out = ["Disk usage:"]
    for mnt, used, total, pct in rows[:12]:
        out.append(f"- {mnt}: {fmt_bytes(used)}/{fmt_bytes(total)} ({pct:.1f}%)")
    return "\n".join(out)


def cmd_tmux() -> str:
    if not shutil.which("tmux"):
        return "tmux not found"

    lines = []

    # tmuxd socket sessions
    rc, out, err = sh(["tmux", "-S", TMUXD_SOCKET, "list-sessions"], timeout=5)
    if rc == 0 and out:
        lines.append("tmuxd sessions (/tmp/clawdbot-tmux-sockets/clawdbot.sock):")
        for l in out.splitlines():
            lines.append(f"- {l}")
    else:
        lines.append("tmuxd sessions: <none>")

    # default tmux server
    rc, out, err = sh(["tmux", "list-sessions"], timeout=5)
    if rc == 0 and out:
        lines.append("\ndefault tmux server sessions:")
        for l in out.splitlines():
            lines.append(f"- {l}")
    else:
        lines.append("\ndefault tmux server sessions: <none>")

    return "\n".join(lines).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sub", choices=["status", "disk", "tmux"])
    args = ap.parse_args()

    if args.sub == "status":
        print(cmd_status())
    elif args.sub == "disk":
        print(cmd_disk())
    elif args.sub == "tmux":
        print(cmd_tmux())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
