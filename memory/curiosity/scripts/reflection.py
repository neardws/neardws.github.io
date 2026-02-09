#!/usr/bin/env python3
"""
每周反思系统 (Phase 4)

定期回顾本周的探索，分析选择偏好，调整参数。
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent / "memory/curiosity"
STATE_FILE = BASE_DIR / "state.json"
DISCOVERIES_FILE = BASE_DIR / "discoveries.md"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

REFLECTIONS_FILE = BASE_DIR / "reflections.md"


def load_state():
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def load_feedback():
    with open(FEEDBACK_FILE) as f:
        return json.load(f)


def count_discoveries_this_week():
    """统计本周的发现数量"""
    with open(DISCOVERIES_FILE) as f:
        content = f.read()
    
    # 简化：数 ## # 的数量
    week_start = datetime.now() - timedelta(days=7)
    week_str = week_start.strftime("%Y-%m-%d")
    
    # 统计所有发现
    import re
    discoveries = re.findall(r'## #(\d+|daydream-[\d-]+)[^#]*?(\d{4}-\d{2}-\d{2})', content)
    
    recent = [d for d in discoveries if d[1] >= week_str]
    return len(recent)


def analyze_exploration_patterns():
    """分析探索模式"""
    state = load_state()
    gaps = state.get("knowledge_gaps", [])
    
    # 统计已探索的 gap
    explored = [g for g in gaps if g.get("last_touched")]
    unexplored = [g for g in gaps if not g.get("last_touched")]
    
    # 按领域分组
    domains = {}
    for gap in gaps:
        domain = gap.get("domain", "unknown")
        domains[domain] = domains.get(domain, 0) + 1
    
    # 计算平均张力
    tensions = [g.get("importance", 0.5) * g.get("uncertainty", 0.5) for g in gaps]
    avg_tension = sum(tensions) / len(tensions) if tensions else 0
    
    return {
        "total_gaps": len(gaps),
        "explored": len(explored),
        "unexplored": len(unexplored),
        "domains": domains,
        "avg_tension": round(avg_tension, 2)
    }


def analyze_feedback_patterns():
    """分析反馈模式"""
    feedback = load_feedback()
    stats = feedback.get("learning", {})
    
    high_value = stats.get("high_value_patterns", [])
    low_value = stats.get("low_value_patterns", [])
    
    return {
        "total_rated": stats.get("total_rated", 0),
        "avg_rating": stats.get("avg_rating"),
        "high_value_count": len(high_value),
        "low_value_count": len(low_value)
    }


def generate_reflection():
    """生成反思报告"""
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    
    # 收集数据
    exploration = analyze_exploration_patterns()
    feedback = analyze_feedback_patterns()
    discovery_count = count_discoveries_this_week()
    
    # 生成反思问题
    questions = []
    
    if exploration["explored"] == 0:
        questions.append("- ⚠️ 本周没有探索任何 gap，为什么？")
    elif exploration["unexplored"] > exploration["explored"]:
        questions.append("- 🤔 大部分 gap 未被探索，是张力阈值太高吗？")
    
    if feedback["total_rated"] == 0:
        questions.append("- 📊 没有收到反馈，Neil 不知道哪些发现有价值")
    
    if feedback["avg_rating"] and feedback["avg_rating"] < 3:
        questions.append("- ⬇️ 平均评分低于 3，探索方向可能需要调整")
    
    # 生成建议
    suggestions = []
    
    if exploration["avg_tension"] < 0.5:
        suggestions.append("- 考虑降低 tension threshold，增加探索频率")
    
    # 写入反思文件
    reflection = f"""# 每周反思 — {now.strftime("%Y-%m-%d")}

## 📊 本周统计

| 指标 | 值 |
|------|-----|
| 发现数量 | {discovery_count} |
| 已探索 gap | {exploration["explored"]}/{exploration["total_gaps"]} |
| 平均张力 | {exploration["avg_tension"]} |
| 收到评分 | {feedback["total_rated"]} |
| 平均评分 | {feedback["avg_rating"] or "N/A"} |

## 🧠 自我问题

{chr(10).join(questions) if questions else "- ✅ 系统运行正常，继续保持"}

## 💡 改进建议

{chr(10).join(suggestions) if suggestions else "- 当前参数合理，无需调整"}

## 📈 领域分布

"""
    
    for domain, count in exploration["domains"].items():
        reflection += f"- {domain}: {count} gaps\n"
    
    reflection += f"""
---

*下次反思时间: {(now + timedelta(days=7)).strftime("%Y-%m-%d")}*
"""
    
    with open(REFLECTIONS_FILE, "w") as f:
        f.write(reflection)
    
    return {
        "generated": True,
        "questions": len(questions),
        "suggestions": len(suggestions),
        "file": str(REFLECTIONS_FILE)
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python reflection.py <command>")
        print("Commands:")
        print("  generate    - generate weekly reflection")
        print("  stats       - show current statistics")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "generate":
        result = generate_reflection()
        print(f"✅ Reflection generated: {result['file']}")
        print(f"   Questions: {result['questions']}")
        print(f"   Suggestions: {result['suggestions']}")
    
    elif cmd == "stats":
        exploration = analyze_exploration_patterns()
        feedback = analyze_feedback_patterns()
        
        print("📊 Current Statistics:")
        print(f"  Gaps: {exploration['total_gaps']} ({exploration['explored']} explored)")
        print(f"  Avg tension: {exploration['avg_tension']}")
        print(f"  Feedback: {feedback['total_rated']} rated, avg {feedback['avg_rating'] or 'N/A'}")
