#!/usr/bin/env python3
"""
会话健康检查脚本
检测卡住的会话并尝试恢复
"""

import json
import subprocess
import time
from datetime import datetime

GATEWAY_URL = "http://127.0.0.1:18789"
GATEWAY_TOKEN = "b1b693ff60a1320bae4abcab1f99722b24e576318ef53d0aada23ebd08310cff"
STALE_THRESHOLD_SECONDS = 300  # 5分钟无响应视为卡住

def get_sessions():
    """获取所有会话"""
    cmd = [
        "curl", "-s", 
        "-H", f"Authorization: Bearer {GATEWAY_TOKEN}",
        f"{GATEWAY_URL}/api/sessions"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout) if result.returncode == 0 else {"sessions": []}
    except:
        return {"sessions": []}

def check_stale_sessions(sessions):
    """检查卡住的会话"""
    stale = []
    now = time.time() * 1000  # ms
    
    for s in sessions.get("sessions", []):
        updated = s.get("updatedAt", 0)
        age_seconds = (now - updated) / 1000
        
        # 检查是否有未完成的工具调用
        messages = s.get("messages", [])
        if messages:
            last = messages[-1]
            if last.get("stopReason") == "toolUse":
                if age_seconds > STALE_THRESHOLD_SECONDS:
                    stale.append({
                        "key": s["key"],
                        "displayName": s.get("displayName"),
                        "age_minutes": int(age_seconds / 60),
                        "lastTool": last.get("content", [{}])[-1].get("name")
                    })
    return stale

def main():
    print(f"🔍 检查会话健康状态 - {datetime.now()}")
    sessions = get_sessions()
    stale = check_stale_sessions(sessions)
    
    if stale:
        print(f"\n⚠️ 发现 {len(stale)} 个卡住的会话:")
        for s in stale:
            print(f"  - {s['displayName']}: 卡住 {s['age_minutes']} 分钟")
            print(f"    等待工具: {s['lastTool']}")
    else:
        print("✅ 所有会话正常")

if __name__ == "__main__":
    main()
