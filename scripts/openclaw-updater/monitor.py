#!/usr/bin/env python3
"""
OpenClaw 源码更新监控与升级系统
- 监控远程仓库更新
- 保留本地新增功能
- 安全合并策略
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置
SOURCE_DIR = Path.home() / "clawdbot"
STATE_FILE = Path.home() / "clawd/scripts/openclaw-updater/state.json"
LOG_FILE = Path.home() / "clawd/scripts/openclaw-updater/monitor.log"

# 本地新增内容（不应被覆盖）
LOCAL_ADDITIONS = [
    "skills/amap-places/",
    "skills/arxiv-researcher/",
    "skills/fact-check/",
    "skills/notebooklm/",
    "skills/paper-manager/",
    "skills/remote-macos-*/",
    "agents/luoxiaohei/",
    "docs/24x7-info-system.md",
    "docs/TELEGRAM_OUTPUT_GUIDE.md",
    "info-monitor/",
]

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {msg}"
    print(log_line)
    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")

def run(cmd, cwd=None, check=True):
    """执行命令并返回输出"""
    result = subprocess.run(
        cmd,
        cwd=cwd or SOURCE_DIR,
        capture_output=True,
        text=True,
        shell=isinstance(cmd, str)
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
    return result.stdout.strip()

def get_current_commit():
    """获取当前本地 commit"""
    return run(["git", "rev-parse", "HEAD"])

def get_remote_commit():
    """获取远程 main 最新 commit"""
    run(["git", "fetch", "origin", "main"])
    return run(["git", "rev-parse", "origin/main"])

def get_commit_message(commit_hash):
    """获取 commit 信息"""
    return run(["git", "log", "-1", "--format=%s", commit_hash])

def get_commit_date(commit_hash):
    """获取 commit 日期"""
    return run(["git", "log", "-1", "--format=%ci", commit_hash])

def get_commits_between(base, head):
    """获取两个 commit 之间的所有提交"""
    output = run(["git", "log", f"{base}..{head}", "--oneline"])
    return output.split("\n") if output else []

def has_local_changes():
    """检查是否有本地未提交修改"""
    status = run(["git", "status", "--porcelain"])
    return bool(status.strip())

def check_updates():
    """检查是否有更新"""
    log("开始检查 OpenClaw 源码更新...")
    
    current = get_current_commit()
    remote = get_remote_commit()
    
    state = load_state()
    last_known_remote = state.get("last_known_remote_commit")
    if not last_known_remote:
        last_known_remote = current
    
    log(f"本地: {current[:8]}")
    log(f"远程: {remote[:8]}")
    
    if current == remote:
        log("✓ 已经是最新版本")
        return {"has_update": False}
    
    # 获取更新列表
    new_commits = get_commits_between(current, remote)
    
    # 只检查上次已知远程之后的更新
    if last_known_remote and last_known_remote != remote:
        try:
            unseen_commits = get_commits_between(last_known_remote, remote)
        except:
            unseen_commits = new_commits
    else:
        unseen_commits = new_commits
    
    result = {
        "has_update": True,
        "current_commit": current,
        "remote_commit": remote,
        "new_commits": new_commits,
        "unseen_commits": unseen_commits,
        "total_commits_behind": len(new_commits),
    }
    
    log(f"发现 {len(new_commits)} 个新提交")
    return result

def load_state():
    """加载状态文件"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "last_check": None,
        "last_known_remote_commit": None,
        "last_update": None,
        "notified_commits": [],
    }

def save_state(state):
    """保存状态文件"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def format_notification(result):
    """格式化更新通知"""
    if not result["has_update"]:
        return None
    
    lines = [
        "🔄 **OpenClaw 源码有更新**",
        f"",
        f"当前: `{result['current_commit'][:8]}`",
        f"远程: `{result['remote_commit'][:8]}`",
        f"落后: **{result['total_commits_behind']}** 个提交",
        f"",
        "**最新提交:**",
    ]
    
    # 显示最新的5个提交
    for commit in result["new_commits"][:5]:
        lines.append(f"- `{commit}`")
    
    if len(result["new_commits"]) > 5:
        lines.append(f"- ... 还有 {len(result['new_commits']) - 5} 个")
    
    lines.extend([
        "",
        "**本地新增内容将被保留:**",
        "- skills/amap-places/",
        "- skills/arxiv-researcher/",
        "- skills/fact-check/",
        "- skills/notebooklm/",
        "- skills/remote-macos-*/",
        "- agents/luoxiaohei/",
        "",
        "**操作:** 运行 `./upgrade.sh` 安全升级",
    ])
    
    return "\n".join(lines)

def main():
    """主函数"""
    os.chdir(SOURCE_DIR)
    
    # 确保在正确的目录
    if not (SOURCE_DIR / ".git").exists():
        log("错误: 不在 git 仓库中")
        sys.exit(1)
    
    state = load_state()
    state["last_check"] = datetime.now().isoformat()
    
    try:
        result = check_updates()
        
        if result["has_update"]:
            state["last_known_remote_commit"] = result["remote_commit"]
            
            # 检查是否有未通知的提交
            unseen = result.get("unseen_commits", [])
            new_unseen = [c for c in unseen if c not in state.get("notified_commits", [])]
            
            if new_unseen:
                state["notified_commits"] = state.get("notified_commits", []) + new_unseen
                save_state(state)
                
                # 输出通知（将被发送给用户）
                notification = format_notification(result)
                print("\n" + "="*50)
                print("UPDATE_FOUND")
                print("="*50)
                print(notification)
                print("="*50)
                return 1  # 返回非零表示发现更新
        else:
            save_state(state)
            
    except Exception as e:
        log(f"检查失败: {e}")
        save_state(state)
        return 2
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
