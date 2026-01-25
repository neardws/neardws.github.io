#!/usr/bin/env python3
"""Service status helper.

Reads services/services.yaml and prints a concise status summary.

This is intentionally conservative: read-only checks by default.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass

try:
    import yaml  # type: ignore
except Exception:
    yaml = None


def sh(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(timeout=20)
    return p.returncode, out.strip(), err.strip()


@dataclass
class Service:
    name: str
    spec: dict


def load_services(path: str) -> list[Service]:
    if yaml is None:
        raise RuntimeError("PyYAML not installed. Install: pip install pyyaml")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    services = (data or {}).get("services") or {}
    return [Service(name=k, spec=v or {}) for k, v in services.items()]


def check_python_service(svc: Service) -> tuple[str, str]:
    cwd = svc.spec.get("cwd")
    vpy = svc.spec.get("venvPython")
    if not vpy or not os.path.exists(vpy):
        return "MISSING", f"venv python not found: {vpy}"

    # If entry is provided, try a lightweight import/run.
    entry = svc.spec.get("entry")
    if entry == "-c":
        code = svc.spec.get("checkCmd") or "print('ok')"
        rc, out, err = sh([vpy, "-c", code], cwd=cwd)
        if rc == 0:
            return "OK", out or "ok"
        return "ERROR", err or out

    if entry:
        # Do a syntax check if possible: python -m py_compile main.py
        target = os.path.join(cwd, entry) if cwd else entry
        if os.path.exists(target):
            rc, out, err = sh([vpy, "-m", "py_compile", target], cwd=cwd)
            if rc == 0:
                return "OK", f"py_compile ok ({entry})"
            return "ERROR", err or out
        return "UNKNOWN", f"entry not found: {entry}"

    return "OK", "configured"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default=os.path.join(os.path.dirname(__file__), "services.yaml"))
    ap.add_argument("--name", default="")
    args = ap.parse_args()

    svcs = load_services(args.registry)
    if args.name:
        svcs = [s for s in svcs if s.name == args.name]

    lines: list[str] = []
    for s in sorted(svcs, key=lambda x: x.name):
        kind = s.spec.get("kind")
        if kind == "python":
            status, detail = check_python_service(s)
        else:
            status, detail = "UNKNOWN", f"kind={kind}"
        lines.append(f"- {s.name}: {status} — {detail}")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
