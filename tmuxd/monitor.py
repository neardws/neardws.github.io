#!/usr/bin/env python3
import argparse
import subprocess
import sys
import re
from datetime import datetime

ERR_RE = re.compile(r"\b(error|exception|traceback|fatal)\b", re.I)
DONE_RE = re.compile(r"\b(done|completed|success|finished)\b", re.I)


def sh(cmd):
    return subprocess.check_output(cmd, text=True)


def tmux(socket, *args):
    return sh(["tmux", "-S", socket, *args])


def safe_tmux(socket, *args):
    try:
        return tmux(socket, *args)
    except subprocess.CalledProcessError:
        return ""


def last_nonempty_line(text: str) -> str:
    for line in reversed(text.splitlines()):
        s = line.strip("\r")
        if s.strip():
            return s
    return ""


def first_pane_id(socket: str, session: str) -> str:
    out = safe_tmux(socket, "list-panes", "-t", session, "-F", "#{pane_id}")
    for line in out.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--socket", required=True)
    ap.add_argument("--prefix", default="droid-")
    ap.add_argument("--lines", type=int, default=400)
    args = ap.parse_args()

    sessions = safe_tmux(args.socket, "list-sessions", "-F", "#{session_name}")
    sess = [s for s in sessions.splitlines() if s.startswith(args.prefix)]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not sess:
        print(f"[{now}] no sessions with prefix={args.prefix}")
        return

    print(f"[{now}] {len(sess)} instance(s)")

    for s in sess:
        pane = first_pane_id(args.socket, s)
        if not pane:
            print(f"- {s}  [UNKNOWN]\n  last: <no pane>")
            continue

        pane_dead = safe_tmux(args.socket, "display-message", "-p", "-t", pane, "#{pane_dead}").strip()
        out = safe_tmux(args.socket, "capture-pane", "-p", "-J", "-t", pane, "-S", f"-{args.lines}")
        last = last_nonempty_line(out)

        state = "RUNNING"
        if ERR_RE.search(out):
            state = "ERROR"
        elif DONE_RE.search(out):
            state = "DONE"
        elif pane_dead == "1":
            state = "EXITED"

        print(f"- {s}  [{state}]\n  last: {last}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
