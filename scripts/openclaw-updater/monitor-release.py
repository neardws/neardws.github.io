#!/usr/bin/env python3
"""
OpenClaw Release 版本监控脚本
- 仅监控官方发布的 tag 版本（如 v2026.2.9）
- 忽略 main 分支的日常提交
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置
SOURCE_DIR = Path.home() / "clawdbot"
STATE_FILE = Path.home() / "clawd/scripts/openclaw-updater/release-state.json"
LOG_FILE = Path.home() / "clawd/scripts/openclaw-updater/monitor-release.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {msg}"
    print(log_line)
    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")

def run(cmd, cwd=None, check=True):
    result = subprocess.run(
        cmd,
        cwd=cwd or SOURCE_DIR,
        capture_output=True,
        text=True,
        shell=isinstance(cmd, str)
    )
    if check and result.returncode != 0:
        return None
    return result.stdout.strip()

def get_current_tag():
    """获取当前 HEAD 对应的 tag（如果有）"""
    return run(["git", "describe", "--tags", "--exact-match"], check=False)

def get_current_commit():
    """获取当前 commit"""
    return run(["git", "rev-parse", "HEAD"])

def get_latest_release():
    """获取最新的 release tag"""
    # 获取所有版本 tag（v2026.x.x 格式）
    tags = run(["git", "tag", "-l", "v2026.*", "--sort=-v:refname"], check=False)
    if not tags:
        return None
    
    latest = tags.split("\n")[0]
    commit = run(["git", "rev-list", "-n", "1", latest], check=False)
    return {"tag": latest, "commit": commit}

def get_release_notes(tag):
    """获取 release 的变更摘要"""
    # 获取该 tag 的前一个版本
    prev_tag = run(["git", "describe", "--tags", "--abbrev=0", f"{tag}^"], check=False)
    if not prev_tag:
        return "首次发布"
    
    # 获取两个 tag 之间的提交
    commits = run(["git", "log", f"{prev_tag}..{tag}", "--oneline"], check=False)
    if not commits:
        return "无变更记录"
    
    lines = commits.split("\n")[:5]  # 只显示前5个
    return "\n".join([f"- {line}" for line in lines])

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_known_release": None, "notified_releases": []}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def main():
    os.chdir(SOURCE_DIR)
    
    log("=" * 50)
    log("检查 OpenClaw Release 版本...")
    
    # 获取远程 tags
    run(["git", "fetch", "--tags", "origin"], check=False)
    
    current = get_current_commit()
    latest_release = get_latest_release()
    
    if not latest_release:
        log("未找到 Release 版本")
        return 0
    
    log(f"当前 commit: {current[:8]}")
    log(f"最新 Release: {latest_release['tag']} ({latest_release['commit'][:8]})")
    
    state = load_state()
    
    # 检查是否已经在最新 release 上
    if current == latest_release["commit"]:
        log(f"✓ 已是最新 Release: {latest_release['tag']}")
        state["last_known_release"] = latest_release["tag"]
        save_state(state)
        return 0
    
    # 检查是否是新 release
    if latest_release["tag"] in state.get("notified_releases", []):
        log(f"Release {latest_release['tag']} 已通知过")
        return 0
    
    # 发现新 release！
    log(f"🎉 发现新 Release: {latest_release['tag']}")
    
    # 获取变更摘要
    notes = get_release_notes(latest_release["tag"])
    
    # 格式化通知
    notification = f"""
🎉 **OpenClaw 新版本发布: {latest_release['tag']}**

**当前版本**: `{current[:8]}`
**最新 Release**: `{latest_release['tag']}` (`{latest_release['commit'][:8]}`)

**主要变更**:
{notes}

**升级命令**:
```bash
cd ~/clawdbot
git fetch --tags origin
git checkout {latest_release['tag']}
node openclaw.mjs gateway restart
```

**本地功能将被保留**: skills/ 和 agents/ 目录
"""
    
    print("\n" + "="*50)
    print("NEW_RELEASE_FOUND")
    print("="*50)
    print(notification)
    print("="*50)
    
    # 更新状态
    state["last_known_release"] = latest_release["tag"]
    state["notified_releases"] = state.get("notified_releases", []) + [latest_release["tag"]]
    save_state(state)
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
