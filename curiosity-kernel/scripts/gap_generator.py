#!/usr/bin/env python3
"""
Gap 自动生成模块

从发现中自动提取新的知识缺口：
1. 提取发现中的关键词和主题
2. 搜索 supermemory 找到相关但不理解的点
3. 生成新的 knowledge_gap
"""

import json
import re
from datetime import datetime
from pathlib import Path
import uuid

BASE_DIR = Path(__file__).parent.parent.parent / "curiosity-kernel"
STATE_FILE = BASE_DIR / "state.json"
DISCOVERIES_FILE = BASE_DIR / "discoveries.md"

# 关键词提取的简单规则
TOPIC_PATTERNS = {
    "edge_intelligence": r"边缘智能|edge\s*intelligence|资源受限|计算预算",
    "curiosity": r"好奇心|curiosity|探索|tension|张力",
    "system_design": r"系统设计|架构|模块|subsystem|子系统",
    "learning": r"学习|learning|预测|prediction|惊讶|surprise",
    "neil_research": r"HARL|强化学习|边缘|vehicle|vehicular",
    "self_improvement": r"自我|反思|优化|改进|meta",
}


def load_state():
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def extract_topics(text):
    """从文本中提取主题"""
    topics = []
    text_lower = text.lower()
    
    for topic, pattern in TOPIC_PATTERNS.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            topics.append(topic)
    
    return topics


def extract_key_phrases(text):
    """提取关键短语（简化版：引号内容和问号句子）"""
    phrases = []
    
    # 引号内容
    quoted = re.findall(r'[""「」『』]([^""「」『』]+)[""「」『』]', text)
    phrases.extend(quoted)
    
    # 问号句子
    questions = re.findall(r'([^。！？\n]+\?)', text)
    phrases.extend(questions)
    
    return phrases


def generate_gap_from_discovery(discovery_text, discovery_id):
    """从发现生成新的 knowledge gap"""
    topics = extract_topics(discovery_text)
    phrases = extract_key_phrases(discovery_text)
    
    # 基于 topic 组合生成问题
    if len(topics) >= 2:
        gap_question = f"{topics[0].replace('_', ' ')} 和 {topics[1].replace('_', ' ')} 的结合点在哪里？"
    elif len(topics) == 1:
        gap_question = f"{topics[0].replace('_', ' ')} 这个方向还有哪些我没理解的？"
    elif phrases:
        gap_question = f"关于 \"{phrases[0][:30]}\" 背后的原理是什么？"
    else:
        return None  # 无法生成有意义的 gap
    
    return {
        "id": f"gap-{uuid.uuid4().hex[:8]}",
        "domain": topics[0] if topics else "general",
        "question": gap_question,
        "importance": 0.6,
        "uncertainty": 0.8,
        "created": datetime.now().isoformat(),
        "source": "discovery_driven",
        "related_discovery": discovery_id
    }


def generate_gaps_from_recent_discoveries(limit=3):
    """从最近的发现生成新的 gap"""
    state = load_state()
    
    # 读取 discoveries.md
    with open(DISCOVERIES_FILE) as f:
        content = f.read()
    
    # 提取最近的发现
    discovery_pattern = r'## (#\d+)[^#]*?(\d{4}-\d{2}-\d{2})[^#]*?\*\*发现[：:]\*\*\s*([^\n]+)'
    matches = re.findall(discovery_pattern, content)
    
    new_gaps = []
    existing_questions = [g["question"] for g in state["knowledge_gaps"]]
    
    for discovery_id, date, discovery_text in matches[:limit]:
        gap = generate_gap_from_discovery(discovery_text, discovery_id)
        
        if gap and gap["question"] not in existing_questions:
            new_gaps.append(gap)
            existing_questions.append(gap["question"])
    
    # 添加到 state
    if new_gaps:
        state["knowledge_gaps"].extend(new_gaps)
        save_state(state)
    
    return new_gaps


def generate_gap_from_surprise(prediction, surprise):
    """从高惊讶度预测生成新 gap"""
    return {
        "id": f"gap-{uuid.uuid4().hex[:8]}",
        "domain": prediction.get("domain", "general"),
        "question": f"为什么我对 '{prediction['prediction'][:50]}...' 的预测错了？置信度 {prediction['confidence']:.0%}",
        "importance": min(surprise + 0.3, 1.0),
        "uncertainty": 0.9,
        "created": datetime.now().isoformat(),
        "source": "surprise_driven",
        "related_prediction": prediction["id"]
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python gap_generator.py <command>")
        print("Commands:")
        print("  generate    - generate gaps from recent discoveries")
        print("  show        - show current knowledge gaps")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "generate":
        new_gaps = generate_gaps_from_recent_discoveries()
        if new_gaps:
            print(f"✅ Generated {len(new_gaps)} new gaps:")
            for gap in new_gaps:
                print(f"  - {gap['id']}: {gap['question'][:50]}...")
        else:
            print("No new gaps generated (all topics already covered)")
    
    elif cmd == "show":
        state = load_state()
        print(f"📋 Current knowledge gaps ({len(state['knowledge_gaps'])}):")
        for gap in state["knowledge_gaps"]:
            importance = gap.get("importance", 0.5)
            uncertainty = gap.get("uncertainty", 0.5)
            tension_score = importance * uncertainty
            print(f"  [{tension_score:.2f}] {gap['question'][:60]}...")
