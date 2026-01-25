#!/usr/bin/env python3
"""tmuxd watcher

Poll tmuxd status and emit notifications when something changes.

State file: ~/.clawdbot/tmuxd/watch-state.json

Notifications:
- state transitions (RUNNING/NEEDS_INPUT/DONE/ERROR/EXITED)
- QUIET: running too long with no observable output change

Designed to be called periodically (e.g., every minute) by Clawdbot cron.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass

DEFAULT_SOCKET_DIR = os.environ.get("CLAWDBOT_TMUX_SOCKET_DIR") or f"{os.environ.get('TMPDIR') or '/tmp'}/clawdbot-tmux-sockets"
DEFAULT_SOCKET = os.environ.get("TMUXD_SOCKET") or f"{DEFAULT_SOCKET_DIR}/clawdbot.sock"
DEFAULT_PREFIX = os.environ.get("TMUXD_PREFIX") or "droid-"
STATE_DIR = os.path.expanduser(os.environ.get("TMUXD_STATE_DIR") or "~/.clawdbot/tmuxd")
STATE_PATH = os.path.join(STATE_DIR, "watch-state.json")

ERR_RE = re.compile(r"\b(error|exception|traceback|fatal)\b", re.I)
NEEDS_INPUT_RE = re.compile(r"\b(enter to send|press\s+enter|login|authorize|auth|open\s+browser|device\s+code)\b", re.I)
PROMPT_RE = re.compile(r"^\s*>\s+", re.M)

DROID_JSON_DONE_RE = re.compile(r'"type"\s*:\s*"result"')
DROID_JSON_ERROR_RE = re.compile(r'"is_error"\s*:\s*true|"subtype"\s*:\s*"error"')


def sh(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True)


def safe_sh(cmd: list[str]) -> str:
    try:
        return sh(cmd)
    except subprocess.CalledProcessError:
        return ""


def tmux(socket: str, *args: str) -> str:
    return sh(["tmux", "-S", socket, *args])


def safe_tmux(socket: str, *args: str) -> str:
    try:
        return tmux(socket, *args)
    except subprocess.CalledProcessError:
        return ""


def ensure_state_dir() -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    try:
        os.chmod(STATE_DIR, 0o700)
    except Exception:
        pass


def load_state() -> dict:
    ensure_state_dir()
    if not os.path.exists(STATE_PATH):
        return {"instances": {}}
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"instances": {}}


def save_state(state: dict) -> None:
    ensure_state_dir()
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, STATE_PATH)


@dataclass
class Snapshot:
    session: str
    pane: str
    pane_dead: str
    exit_status: str
    last_line: str
    out_hash: str
    state: str


def last_nonempty_line(text: str) -> str:
    for line in reversed(text.splitlines()):
        s = line.strip("\r")
        if s.strip():
            return s
    return ""


def out_digest(text: str) -> str:
    # keep it cheap: hash last 2000 chars
    tail = text[-2000:]
    return hashlib.sha256(tail.encode("utf-8", errors="ignore")).hexdigest()[:16]


def classify(out: str, pane_dead: str, exit_status: str) -> str:
    if pane_dead == "1":
        if exit_status == "0":
            return "DONE"
        if exit_status:
            return f"ERROR({exit_status})"
        return "EXITED"

    # JSON result wins (avoid false positives)
    if DROID_JSON_DONE_RE.search(out):
        if DROID_JSON_ERROR_RE.search(out):
            return "ERROR"
        return "DONE"

    if ERR_RE.search(out):
        return "ERROR"
    if NEEDS_INPUT_RE.search(out) or PROMPT_RE.search(out):
        return "NEEDS_INPUT"
    return "RUNNING"


def get_snapshots(socket: str, prefix: str, lines: int) -> list[Snapshot]:
    sessions = safe_tmux(socket, "list-sessions", "-F", "#{session_name}")
    sess = [s.strip() for s in sessions.splitlines() if s.strip().startswith(prefix)]
    snaps: list[Snapshot] = []
    for s in sess:
        pane = safe_tmux(socket, "list-panes", "-t", s, "-F", "#{pane_id}").splitlines()
        pane = next((p.strip() for p in pane if p.strip()), "")
        if not pane:
            continue
        pane_dead = safe_tmux(socket, "display-message", "-p", "-t", pane, "#{pane_dead}").strip()
        exit_status = safe_tmux(socket, "display-message", "-p", "-t", pane, "#{pane_exit_status}").strip()
        out = safe_tmux(socket, "capture-pane", "-p", "-J", "-t", pane, "-S", f"-{lines}")
        last = last_nonempty_line(out)
        snaps.append(
            Snapshot(
                session=s,
                pane=pane,
                pane_dead=pane_dead,
                exit_status=exit_status,
                last_line=last,
                out_hash=out_digest(out),
                state=classify(out, pane_dead, exit_status),
            )
        )
    return snaps


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--socket", default=DEFAULT_SOCKET)
    ap.add_argument("--prefix", default=DEFAULT_PREFIX)
    ap.add_argument("--lines", type=int, default=800)
    ap.add_argument("--quiet-seconds", type=int, default=600, help="alert if output hash unchanged for this long while RUNNING")
    ap.add_argument("--now", type=int, default=0)
    args = ap.parse_args()

    now = int(args.now or time.time())
    state = load_state()
    inst_state: dict = state.setdefault("instances", {})

    snaps = get_snapshots(args.socket, args.prefix, args.lines)
    current_names = set()
    notes: list[str] = []

    for sn in snaps:
        current_names.add(sn.session)
        prev = inst_state.get(sn.session)
        if prev is None:
            inst_state[sn.session] = {
                "firstSeen": now,
                "lastSeen": now,
                "lastState": sn.state,
                "lastHash": sn.out_hash,
                "lastChange": now,
                "lastLine": sn.last_line,
            }
            notes.append(f"[tmuxd] {sn.session} started → {sn.state}\n{sn.last_line}")
            continue

        prev_state = prev.get("lastState")
        prev_hash = prev.get("lastHash")

        prev["lastSeen"] = now

        changed = (sn.out_hash != prev_hash)
        if changed:
            prev["lastHash"] = sn.out_hash
            prev["lastChange"] = now
            prev["lastLine"] = sn.last_line

        if sn.state != prev_state:
            prev["lastState"] = sn.state
            prev["lastLine"] = sn.last_line
            prev["lastChange"] = now
            notes.append(f"[tmuxd] {sn.session} {prev_state} → {sn.state}\n{sn.last_line}")
            continue

        # quiet detection (only if RUNNING)
        if sn.state == "RUNNING":
            last_change = int(prev.get("lastChange") or now)
            if now - last_change >= args.quiet_seconds:
                # throttle: emit at most once per quiet window
                last_quiet = int(prev.get("lastQuietAlert") or 0)
                if now - last_quiet >= args.quiet_seconds:
                    prev["lastQuietAlert"] = now
                    notes.append(f"[tmuxd] {sn.session} QUIET ≥ {args.quiet_seconds}s\n{sn.last_line}")

    # detect disappeared sessions
    for name in list(inst_state.keys()):
        if name.startswith(args.prefix) and name not in current_names:
            prev = inst_state[name]
            notes.append(f"[tmuxd] {name} disappeared (was {prev.get('lastState')})")
            del inst_state[name]

    save_state(state)

    # print notifications (cron can decide to send)
    out = "\n\n".join(notes).strip()
    if out:
        print(out)
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
