#!/usr/bin/env python3
"""
发现评分模块

记录 Neil 对发现的评价，用于学习什么样的探索有价值。
"""

import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent / "curiosity-kernel"
FEEDBACK_FILE = BASE_DIR / "feedback.json"
DISCOVERIES_FILE = BASE_DIR / "discoveries.md"


def load_feedback():
    with open(FEEDBACK_FILE) as f:
        return json.load(f)


def save_feedback(feedback):
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedback, f, indent=2, ensure_ascii=False)


def rate_discovery(discovery_id, rating=None, reaction=None):
    """
    给发现评分
    
    rating: 1-5 分
    reaction: emoji 反应 (👍/💡/🤔/❌)
    """
    feedback = load_feedback()
    
    if discovery_id not in feedback["ratings"]:
        feedback["ratings"][discovery_id] = {
            "neil_rating": None,
            "neil_reaction": None,
            "auto_score": 0.5,
            "rated_at": None
        }
    
    if rating is not None:
        feedback["ratings"][discovery_id]["neil_rating"] = rating
        feedback["ratings"][discovery_id]["rated_at"] = datetime.now().isoformat()
    
    if reaction is not None:
        feedback["ratings"][discovery_id]["neil_reaction"] = reaction
        if feedback["ratings"][discovery_id]["rated_at"] is None:
            feedback["ratings"][discovery_id]["rated_at"] = datetime.now().isoformat()
    
    # 更新学习统计
    update_learning_stats(feedback)
    save_feedback(feedback)
    
    return feedback["ratings"][discovery_id]


def update_learning_stats(feedback):
    """更新学习统计"""
    ratings = [r["neil_rating"] for r in feedback["ratings"].values() if r["neil_rating"]]
    reactions = [r["neil_reaction"] for r in feedback["ratings"].values() if r["neil_reaction"]]
    
    if ratings:
        feedback["learning"]["avg_rating"] = sum(ratings) / len(ratings)
        feedback["learning"]["total_rated"] = len(ratings)
    
    # 分析高分和低分模式
    high_rated = [rid for rid, r in feedback["ratings"].items() 
                  if r["neil_rating"] and r["neil_rating"] >= 4]
    low_rated = [rid for rid, r in feedback["ratings"].items() 
                 if r["neil_rating"] and r["neil_rating"] <= 2]
    
    feedback["learning"]["high_value_patterns"] = high_rated
    feedback["learning"]["low_value_patterns"] = low_rated


def reaction_to_score(reaction):
    """将 emoji 反应转换为分数"""
    mapping = {
        "👍": 4,  # 有用
        "💡": 5,  # 启发
        "🤔": 3,  # 一般
        "❌": 1   # 无价值
    }
    return mapping.get(reaction, 3)


def get_unrated_discoveries():
    """获取未评分的发现"""
    feedback = load_feedback()
    return [did for did, r in feedback["ratings"].items() if r["neil_rating"] is None]


def get_discovery_score(discovery_id):
    """获取发现的综合分数"""
    feedback = load_feedback()
    if discovery_id not in feedback["ratings"]:
        return 0.5
    
    r = feedback["ratings"][discovery_id]
    
    # 综合分数 = Neil 评分优先，否则用 auto_score
    if r["neil_rating"]:
        return r["neil_rating"] / 5.0
    elif r["neil_reaction"]:
        return reaction_to_score(r["neil_reaction"]) / 5.0
    else:
        return r["auto_score"]


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python feedback.py <command> [args]")
        print("Commands:")
        print("  rate <id> <1-5>     - rate a discovery")
        print("  react <id> <emoji>  - react with emoji")
        print("  unrated             - show unrated discoveries")
        print("  stats               - show learning stats")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "rate":
        if len(sys.argv) < 4:
            print("Usage: python feedback.py rate <discovery_id> <1-5>")
            sys.exit(1)
        
        discovery_id = sys.argv[2]
        rating = int(sys.argv[3])
        
        if rating < 1 or rating > 5:
            print("Rating must be 1-5")
            sys.exit(1)
        
        result = rate_discovery(discovery_id, rating=rating)
        print(f"✅ Rated {discovery_id}: {rating}/5")
    
    elif cmd == "react":
        if len(sys.argv) < 4:
            print("Usage: python feedback.py react <discovery_id> <emoji>")
            sys.exit(1)
        
        discovery_id = sys.argv[2]
        reaction = sys.argv[3]
        
        result = rate_discovery(discovery_id, reaction=reaction)
        print(f"✅ Reacted to {discovery_id}: {reaction}")
    
    elif cmd == "unrated":
        unrated = get_unrated_discoveries()
        for did in unrated:
            print(f"- {did}")
    
    elif cmd == "stats":
        feedback = load_feedback()
        stats = feedback["learning"]
        print(f"Total rated: {stats['total_rated']}")
        print(f"Average rating: {stats['avg_rating']:.2f}" if stats['avg_rating'] else "N/A")
        print(f"High value: {stats['high_value_patterns']}")
        print(f"Low value: {stats['low_value_patterns']}")
