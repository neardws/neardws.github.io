#!/usr/bin/env python3
"""
预测生成器

基于最近的交互、发现和趋势，自动生成新预测。
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent / "curiosity-kernel"
PREDICTIONS_FILE = BASE_DIR / "predictions.json"
STATE_FILE = BASE_DIR / "state.json"
DISCOVERIES_FILE = BASE_DIR / "discoveries.md"

# 预测模板
PREDICTION_TEMPLATES = {
    "neil_behavior": [
        "Neil 明天会继续讨论 {topic}",
        "Neil 这周会问关于 {topic} 的问题",
        "Neil 会对 {topic} 的实现细节感兴趣",
    ],
    "project_state": [
        "{project} 仓库本周会有新 commit",
        "{project} 的问题会在 {days} 天内被解决",
        "{project} 的文档会被更新",
    ],
    "world_events": [
        "{domain} 领域本周会有重要论文发布",
        "{domain} 社区会讨论 {topic}",
        "会有人问关于 {topic} 的问题",
    ],
    "system_state": [
        "Syncthing 今天不会出问题",
        "好奇心系统今天会探索 {count} 个 gap",
        "今天的工具调用失败率会低于 {rate}%",
    ],
    "self_state": [
        "我明天会生成 {count} 个新发现",
        "我对 {topic} 的理解会增加",
        "白日梦引擎会触发 {count} 次",
    ],
}

# 当前活跃主题
CURRENT_TOPICS = {
    "curiosity_kernel", "gap_generation", "daydream_engine", 
    "feedback_mechanism", "neil_model", "budget_management",
    "edge_intelligence", "HARL", "AgentEvolver"
}

PROJECTS = ["HARL", "clawd", "curiosity-kernel", "ObsidianVault"]
DOMAINS = ["Edge AI", "LLM Agents", "Reinforcement Learning", "Curiosity-driven Learning"]


def load_predictions():
    with open(PREDICTIONS_FILE) as f:
        return json.load(f)["predictions"]


def save_predictions(predictions):
    with open(PREDICTIONS_FILE, "w") as f:
        json.dump({"predictions": predictions}, f, indent=2, ensure_ascii=False)


def generate_prediction():
    """随机生成一个预测"""
    domain = random.choice(list(PREDICTION_TEMPLATES.keys()))
    template = random.choice(PREDICTION_TEMPLATES[domain])
    
    # 填充模板
    topic = random.choice(list(CURRENT_TOPICS))
    project = random.choice(PROJECTS)
    domain_name = random.choice(DOMAINS)
    
    prediction_text = template.format(
        topic=topic,
        project=project,
        domain=domain_name,
        days=random.randint(2, 7),
        count=random.randint(1, 3),
        rate=random.choice([10, 15, 20])
    )
    
    # 设置验证时间
    verify_after = datetime.now() + timedelta(days=random.randint(1, 7))
    
    return {
        "id": f"pred-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "created": datetime.now().isoformat(),
        "domain": domain,
        "prediction": prediction_text,
        "confidence": round(random.uniform(0.3, 0.8), 1),
        "verify_after": verify_after.isoformat(),
        "verified": None,
        "actual": None,
        "surprise_score": None,
        "auto_generated": True
    }


def generate_predictions_from_discoveries():
    """基于最近的发现生成预测"""
    # 读取最近的发现
    with open(DISCOVERIES_FILE) as f:
        content = f.read()
    
    # 提取最近的主题
    recent_topics = []
    for topic in CURRENT_TOPICS:
        if topic.lower() in content.lower():
            recent_topics.append(topic)
    
    predictions = []
    for topic in recent_topics[:2]:  # 最多 2 个
        template = random.choice(PREDICTION_TEMPLATES["self_state"])
        prediction_text = template.format(
            topic=topic,
            count=random.randint(1, 2),
            rate=15
        )
        
        verify_after = datetime.now() + timedelta(days=random.randint(1, 3))
        
        predictions.append({
            "id": f"pred-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{topic[:3]}",
            "created": datetime.now().isoformat(),
            "domain": "self_state",
            "prediction": prediction_text,
            "confidence": round(random.uniform(0.4, 0.7), 1),
            "verify_after": verify_after.isoformat(),
            "verified": None,
            "actual": None,
            "surprise_score": None,
            "auto_generated": True,
            "source": "discovery_driven"
        })
    
    return predictions


def add_predictions(new_predictions):
    """添加新预测"""
    predictions = load_predictions()
    predictions.extend(new_predictions)
    save_predictions(predictions)
    return new_predictions


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python prediction_generator.py <command>")
        print("Commands:")
        print("  generate      - generate random predictions")
        print("  from_discoveries - generate predictions from recent discoveries")
        print("  show          - show all predictions")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "generate":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        new_preds = [generate_prediction() for _ in range(count)]
        added = add_predictions(new_preds)
        print(f"✅ Generated {len(added)} new predictions:")
        for p in added:
            print(f"  - [{p['confidence']:.0%}] {p['prediction'][:50]}...")
    
    elif cmd == "from_discoveries":
        new_preds = generate_predictions_from_discoveries()
        if new_preds:
            added = add_predictions(new_preds)
            print(f"✅ Generated {len(added)} predictions from discoveries")
        else:
            print("No predictions generated (no recent discoveries)")
    
    elif cmd == "show":
        predictions = load_predictions()
        print(f"📋 Total predictions: {len(predictions)}")
        for p in predictions:
            status = "✓" if p.get("verified") else "⏳"
            print(f"  [{status}] {p['prediction'][:60]}...")
