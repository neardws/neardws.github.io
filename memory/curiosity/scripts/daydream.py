#!/usr/bin/env python3
"""
白日梦引擎 (Daydream Engine)

模拟人类 DMN（默认模式网络）的功能：
1. 从 MEMORY.md 随机抽取两个不相关的条目
2. 尝试找到它们之间的联系
3. 有趣的联想记录到 discoveries.md

触发条件：
- 5% 的心跳随机触发
- 或当 boredom > 0.7 时触发
- 或当 frustration > 0.8 时触发
"""

import json
import random
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
STATE_FILE = BASE_DIR / "state.json"
MEMORY_FILE = BASE_DIR.parent.parent / "MEMORY.md"
DISCOVERIES_FILE = BASE_DIR / "discoveries.md"

# 白日梦触发概率
RANDOM_TRIGGER_PROB = 0.05
BOREDOM_THRESHOLD = 0.7
FRUSTRATION_THRESHOLD = 0.8


def load_state():
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def extract_memory_items():
    """从 MEMORY.md 提取记忆条目"""
    try:
        with open(MEMORY_FILE) as f:
            content = f.read()
    except FileNotFoundError:
        return ["边缘智能", "Neil 研究 HARL", "好奇心内核"]
    
    # 提取标题和列表项
    items = []
    
    # Markdown 标题
    titles = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
    items.extend(titles)
    
    # 列表项
    list_items = re.findall(r'^[-*]\s+(.+)$', content, re.MULTILINE)
    items.extend(list_items)
    
    # 关键句子（包含特定关键词）
    sentences = re.findall(r'[^。！？\n]*[边缘智能|好奇心|HARL|强化学习|系统][^。！？\n]*', content)
    items.extend(sentences[:10])
    
    # 去重并清理
    items = list(set(item.strip() for item in items if len(item.strip()) > 5))
    
    return items if items else ["好奇心系统", "边缘智能研究", "Neil 的工作"]


def should_trigger_daydream(state):
    """判断是否应该触发白日梦"""
    emotion = state.get("emotion", {})
    boredom = emotion.get("boredom", 0)
    frustration = emotion.get("frustration", 0)
    
    # 随机触发
    if random.random() < RANDOM_TRIGGER_PROB:
        return "random"
    
    # 无聊触发
    if boredom > BOREDOM_THRESHOLD:
        return "boredom"
    
    # 挫败触发
    if frustration > FRUSTRATION_THRESHOLD:
        return "frustration"
    
    return None


def generate_association(item1, item2):
    """生成两个条目之间的联想
    
    这是一个简化版本，实际应该调用 LLM 生成。
    这里用模板 + 关键词匹配来模拟。
    """
    
    # 关键词组合 -> 联想模板
    templates = [
        f"**{item1[:20]}** 和 **{item2[:20]}** 的交叉点在哪里？也许可以从资源受限的角度重新思考？",
        f"如果用 {item1[:15]} 的思路去解决 {item2[:15]} 的问题，会发生什么？",
        f"这两个看起来不相关的东西，有没有可能在「系统设计」层面有共同原理？",
        f"从 {item1[:20]} 到 {item2[:20]}，中间缺少了什么环节？",
    ]
    
    return random.choice(templates)


def daydream():
    """执行一次白日梦"""
    state = load_state()
    
    # 检查是否应该触发
    trigger_reason = should_trigger_daydream(state)
    if not trigger_reason:
        return {"triggered": False, "reason": "conditions not met"}
    
    # 提取记忆条目
    items = extract_memory_items()
    
    if len(items) < 2:
        return {"triggered": False, "reason": "not enough memory items"}
    
    # 随机选择两个不相关的条目
    item1, item2 = random.sample(items, 2)
    
    # 生成联想
    association = generate_association(item1, item2)
    
    # 记录到 discoveries
    discovery_record = f"""

## #daydream-{datetime.now().strftime('%Y%m%d-%H%M%S')}

**来源：** 白日梦引擎 (触发原因: {trigger_reason})
**联想：** {association}
**关联条目：**
1. {item1}
2. {item2}
**情感：** boredom={state['emotion'].get('boredom', 0):.2f}
**Neil 评分：** _待评价_
"""
    
    with open(DISCOVERIES_FILE, "a") as f:
        f.write(discovery_record)
    
    # 更新情感状态
    state["emotion"]["boredom"] = max(0, state["emotion"].get("boredom", 0) - 0.1)
    state["emotion"]["interest"] = min(1, state["emotion"].get("interest", 0.5) + 0.05)
    state["stats"]["daydreams"] = state["stats"].get("daydreams", 0) + 1
    save_state(state)
    
    return {
        "triggered": True,
        "reason": trigger_reason,
        "item1": item1[:50],
        "item2": item2[:50],
        "association": association
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python daydream.py <command>")
        print("Commands:")
        print("  run      - attempt to daydream (respects trigger conditions)")
        print("  force    - force a daydream regardless of conditions")
        print("  status   - show daydream stats")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "run":
        result = daydream()
        if result["triggered"]:
            print(f"💭 Daydream triggered ({result['reason']}):")
            print(f"  {result['item1']}")
            print(f"  × {result['item2']}")
            print(f"  → {result['association'][:80]}...")
        else:
            print(f"😴 No daydream ({result['reason']})")
    
    elif cmd == "force":
        # 强制触发：临时降低阈值
        state = load_state()
        old_boredom = state["emotion"].get("boredom", 0)
        state["emotion"]["boredom"] = 0.8
        save_state(state)
        
        result = daydream()
        
        state["emotion"]["boredom"] = old_boredom
        save_state(state)
        
        print(f"💭 Forced daydream:")
        print(f"  {result.get('association', 'N/A')[:100]}...")
    
    elif cmd == "status":
        state = load_state()
        print(f"📊 Daydream Status:")
        print(f"  Total daydreams: {state['stats'].get('daydreams', 0)}")
        print(f"  Current boredom: {state['emotion'].get('boredom', 0):.2f}")
        print(f"  Current frustration: {state['emotion'].get('frustration', 0):.2f}")
        print(f"  Trigger thresholds: boredom>{BOREDOM_THRESHOLD}, frustration>{FRUSTRATION_THRESHOLD}")
