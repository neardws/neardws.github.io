#!/usr/bin/env python3
"""
Curiosity Loop - Main Integration Script

整合所有好奇心组件的主循环，设计为每次心跳调用一次。

Usage:
    python3 curiosity_loop.py           # 正常执行
    python3 curiosity_loop.py --force   # 强制探索（忽略 tension）
    python3 curiosity_loop.py --dry-run # 只打印计划，不执行

Returns:
    0 - 正常完成
    1 - 有重要发现（建议主动汇报）
    2 - 执行错误
"""

import json
import random
import sys
import argparse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
STATE_FILE = BASE_DIR / "state.json"
HEARTBEAT_STATE = BASE_DIR.parent / "heartbeat-state.json"

def load_state():
    """加载当前状态"""
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_state(state):
    """保存状态"""
    state['last_updated'] = datetime.now().isoformat()
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def load_heartbeat_state():
    """加载心跳状态"""
    if HEARTBEAT_STATE.exists():
        with open(HEARTBEAT_STATE, 'r') as f:
            return json.load(f)
    return {'curiosity_loop_count': 0}

def save_heartbeat_state(state):
    """保存心跳状态"""
    with open(HEARTBEAT_STATE, 'w') as f:
        json.dump(state, f, indent=2)

def select_gap(knowledge_gaps):
    """选择要探索的 gap（importance × uncertainty）"""
    if not knowledge_gaps:
        return None
    
    # 计算分数并排序
    scored = []
    for gap in knowledge_gaps:
        score = gap.get('importance', 0.5) * gap.get('uncertainty', 0.5)
        # 惩罚最近探索过的
        if gap.get('last_touched'):
            score *= 0.8
        scored.append((score, gap))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1] if scored else None

def check_tension(state, force=False):
    """检查是否需要探索"""
    if force:
        return True, "forced"
    
    tension = state.get('tension', {}).get('index', 0)
    threshold = state.get('tension', {}).get('threshold', 0.5)
    
    if tension >= threshold:
        return True, f"tension {tension:.2f} >= threshold {threshold}"
    
    return False, f"tension {tension:.2f} < threshold {threshold}"

def run_daydream_check(state):
    """检查是否应该触发白日梦"""
    boredom = state.get('emotion', {}).get('boredom', 0)
    frustration = state.get('emotion', {}).get('frustration', 0)
    
    # 5% 随机触发或高无聊/挫败
    if random.random() < 0.05:
        return True, "random trigger (5%)"
    if boredom > 0.7:
        return True, f"high boredom ({boredom:.2f})"
    if frustration > 0.8:
        return True, f"high frustration ({frustration:.2f})"
    
    return False, None

def print_summary(state, action, target_gap=None, daydream=False):
    """打印执行摘要"""
    print("\n" + "="*50)
    print("🧠 CURIOSITY LOOP SUMMARY")
    print("="*50)
    print(f"Action: {action}")
    print(f"Tension: {state.get('tension', {}).get('index', 0):.2f} " +
          f"(threshold: {state.get('tension', {}).get('threshold', 0.5)})")
    print(f"Emotion: interest={state.get('emotion', {}).get('interest', 0):.2f}, " +
          f"boredom={state.get('emotion', {}).get('boredom', 0):.2f}")
    print(f"Stats: {state.get('stats', {}).get('total_explorations', 0)} explorations, " +
          f"{state.get('stats', {}).get('total_discoveries', 0)} discoveries")
    
    if target_gap:
        print(f"\n🎯 Target Gap: {target_gap.get('question', 'N/A')[:60]}...")
        print(f"   Score: {target_gap.get('importance', 0) * target_gap.get('uncertainty', 0):.2f} " +
              f"(I={target_gap.get('importance', 0):.2f}, U={target_gap.get('uncertainty', 0):.2f})")
    
    if daydream:
        print(f"\n💭 Daydream: Triggered")
    
    print(f"\nKnowledge Gaps: {len(state.get('knowledge_gaps', []))} total")
    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Curiosity Loop - Main Integration')
    parser.add_argument('--force', action='store_true', help='Force exploration')
    parser.add_argument('--dry-run', action='store_true', help='Dry run')
    args = parser.parse_args()
    
    try:
        # 加载状态
        state = load_state()
        hb_state = load_heartbeat_state()
        
        # 检查是否需要执行
        should_explore, reason = check_tension(state, args.force)
        
        if not should_explore and not args.dry_run:
            print(f"⏸️  Skipping exploration: {reason}")
            print_summary(state, f"skipped ({reason})")
            return 0
        
        # 选择目标 gap
        target_gap = select_gap(state.get('knowledge_gaps', []))
        
        # 检查白日梦
        daydream_triggered, daydream_reason = run_daydream_check(state)
        
        if args.dry_run:
            print(f"📝 DRY RUN - Would explore: {target_gap.get('question', 'N/A')[:50] if target_gap else 'None'}")
            print_summary(state, f"dry-run ({reason})", target_gap, daydream_triggered)
            return 0
        
        # 执行探索
        print(f"🔍 Exploring: {target_gap.get('question', 'N/A')[:50]}..." if target_gap else "🔍 No target gap")
        
        # TODO: 实际探索逻辑（1-2 次工具调用）
        # 这里应该调用搜索/读文件等工具
        # 为简化，先只更新统计
        
        stats = state.get('stats', {})
        stats['total_explorations'] = stats.get('total_explorations', 0) + 1
        state['stats'] = stats
        
        # 更新 gap 的 last_touched
        if target_gap:
            target_gap['last_touched'] = datetime.now().isoformat()
        
        # 生成新 gap（简化版）
        print("🆕 Generating new knowledge gap...")
        # 实际应该调用 gap_generator.py
        
        # 触发白日梦
        if daydream_triggered:
            print(f"💭 Daydream triggered: {daydream_reason}")
            # 实际应该调用 daydream.py
        
        # 更新心跳状态
        hb_state['curiosity_loop_count'] = hb_state.get('curiosity_loop_count', 0) + 1
        hb_state['last_curiosity_loop'] = datetime.now().isoformat()
        hb_state['tension_after'] = state.get('tension', {}).get('index', 0)
        
        # 保存状态
        save_state(state)
        save_heartbeat_state(hb_state)
        
        print_summary(state, f"explored ({reason})", target_gap, daydream_triggered)
        
        # 返回码：1 表示有重要发现（这里简化处理）
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
