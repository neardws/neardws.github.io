#!/usr/bin/env python3
"""
发现→分享决策树

决定何时主动汇报发现：
1. 评估发现的价值 (Neil 相关性 × 新颖度 × 可操作性)
2. 检查当前时间
3. 决定：立即汇报 / 缓存到队列 / 丢弃
"""

import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent / "curiosity-kernel"
FEEDBACK_FILE = BASE_DIR / "feedback.json"
QUEUE_FILE = BASE_DIR / "share_queue.json"

# 时间阈值
QUIET_HOURS_START = 23  # 23:00
QUIET_HOURS_END = 8     # 08:00

# 价值阈值
HIGH_VALUE_THRESHOLD = 0.7
MEDIUM_VALUE_THRESHOLD = 0.4


def load_feedback():
    with open(FEEDBACK_FILE) as f:
        return json.load(f)


def is_quiet_hours():
    """检查是否是深夜时段"""
    hour = datetime.now().hour
    return hour >= QUIET_HOURS_START or hour < QUIET_HOURS_END


def calculate_discovery_value(discovery_text, related_topics=None):
    """计算发现的价值"""
    score = 0.5  # 基础分
    
    # Neil 相关性
    neil_keywords = ["HARL", "边缘智能", "Neil", "edge", "reinforcement learning"]
    for kw in neil_keywords:
        if kw.lower() in discovery_text.lower():
            score += 0.15
    
    # 新颖度（基于反馈历史）
    feedback = load_feedback()
    if feedback["learning"]["total_rated"] > 0:
        avg_rating = feedback["learning"]["avg_rating"]
        if avg_rating >= 4:
            score += 0.1  # 之前高分 → 倾向于有价值
    
    # 可操作性
    action_keywords = ["实现", "修复", "优化", "可以", "尝试"]
    for kw in action_keywords:
        if kw in discovery_text:
            score += 0.1
    
    # 研究相关性
    research_keywords = ["论文", "arXiv", "机制", "原理", "研究"]
    for kw in research_keywords:
        if kw in discovery_text:
            score += 0.1
    
    return min(score, 1.0)


def should_share_now(discovery_id, discovery_text, force=False):
    """决定是否立即分享"""
    
    if force:
        return {"decision": "share_now", "reason": "forced"}
    
    # 1. 计算价值
    value = calculate_discovery_value(discovery_text)
    
    # 2. 检查时间
    quiet = is_quiet_hours()
    
    # 3. 决策
    if value >= HIGH_VALUE_THRESHOLD:
        if quiet:
            return {"decision": "queue", "reason": "high_value_but_quiet_hours", "value": value}
        else:
            return {"decision": "share_now", "reason": "high_value", "value": value}
    
    elif value >= MEDIUM_VALUE_THRESHOLD:
        if quiet:
            return {"decision": "queue", "reason": "medium_value_quiet_hours", "value": value}
        else:
            return {"decision": "share_now", "reason": "medium_value_active_hours", "value": value}
    
    else:
        return {"decision": "skip", "reason": "low_value", "value": value}


def add_to_queue(discovery_id, discovery_text, value):
    """添加到待分享队列"""
    try:
        with open(QUEUE_FILE) as f:
            queue = json.load(f)
    except FileNotFoundError:
        queue = {"pending": [], "last_shared": None}
    
    queue["pending"].append({
        "discovery_id": discovery_id,
        "text": discovery_text[:100],
        "value": value,
        "queued_at": datetime.now().isoformat()
    })
    
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)


def get_pending_shares():
    """获取待分享的发现"""
    try:
        with open(QUEUE_FILE) as f:
            queue = json.load(f)
        return queue.get("pending", [])
    except FileNotFoundError:
        return []


def mark_shared(discovery_id):
    """标记已分享"""
    try:
        with open(QUEUE_FILE) as f:
            queue = json.load(f)
        
        queue["pending"] = [p for p in queue["pending"] if p["discovery_id"] != discovery_id]
        queue["last_shared"] = datetime.now().isoformat()
        
        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python share_decision.py <command>")
        print("Commands:")
        print("  evaluate <text>      - evaluate share decision for discovery")
        print("  pending              - show pending shares")
        print("  status               - show current status")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "evaluate":
        if len(sys.argv) < 3:
            print("Usage: python share_decision.py evaluate <discovery_text>")
            sys.exit(1)
        
        text = " ".join(sys.argv[2:])
        result = should_share_now("test", text)
        
        print(f"📊 Discovery Value: {result['value']:.2f}")
        print(f"🌙 Quiet Hours: {is_quiet_hours()}")
        print(f"📢 Decision: {result['decision']}")
        print(f"   Reason: {result['reason']}")
    
    elif cmd == "pending":
        pending = get_pending_shares()
        if pending:
            print(f"📋 Pending shares ({len(pending)}):")
            for p in pending:
                print(f"  - {p['discovery_id']}: {p['text'][:40]}... (value: {p['value']:.2f})")
        else:
            print("No pending shares")
    
    elif cmd == "status":
        pending = get_pending_shares()
        print(f"📊 Share Decision Status:")
        print(f"  Quiet hours: {QUIET_HOURS_START}:00 - {QUIET_HOURS_END}:00")
        print(f"  Current hour: {datetime.now().hour}:00")
        print(f"  Is quiet: {is_quiet_hours()}")
        print(f"  Pending shares: {len(pending)}")
        print(f"  Value thresholds: high>{HIGH_VALUE_THRESHOLD}, medium>{MEDIUM_VALUE_THRESHOLD}")
