# Curiosity Kernel 整合完成

## ✅ 整合摘要

**原位置:** `~/clawd/curiosity-kernel/`  
**新位置:** `~/clawd/memory/curiosity/`  
**状态:** ✅ 已整合进主记忆系统

## 📁 新文件结构

```
memory/
├── curiosity/                    # 🧠 好奇心内核（已整合）
│   ├── state.json               # 当前状态（tension=0.50, interest=0.85）
│   ├── discoveries.md           # 发现日志
│   ├── predictions.json         # 预测列表
│   ├── open-questions.md        # 开放问题
│   ├── neil_model.json          # Neil 建模
│   ├── DESIGN.md                # 完整设计文档
│   ├── budget.json              # Token 预算
│   ├── feedback.json            # 反馈记录
│   └── scripts/                 # 执行脚本
│       ├── curiosity_loop.py    # 🆕 主循环（心跳调用）
│       ├── gap_generator.py     # 生成 knowledge gaps
│       ├── daydream.py          # 白日梦引擎
│       ├── surprise.py          # 预测验证
│       ├── reflection.py        # 情感反思
│       └── share_decision.py    # 分享决策
```

## 🔧 核心变化

### 1. 路径更新
所有脚本已更新为使用新路径 `memory/curiosity/`

```python
# 之前
BASE_DIR = Path("/home/neardws/clawd/curiosity-kernel")

# 现在
BASE_DIR = Path("/home/neardws/clawd/memory/curiosity")
```

### 2. 新增主循环脚本

**`curiosity_loop.py`** - 每次心跳调用的入口：

```bash
# 正常执行（根据 tension 决定是否探索）
python3 memory/curiosity/scripts/curiosity_loop.py

# 强制探索
python3 memory/curiosity/scripts/curiosity_loop.py --force

# 测试运行（只打印计划）
python3 memory/curiosity/scripts/curiosity_loop.py --dry-run
```

**返回码:**
- 0 - 正常完成
- 1 - 有重要发现（建议主动汇报）
- 2 - 执行错误

### 3. 更新 HEARTBEAT.md

心跳清单第 3 步已更新为：

```bash
# 🧠 好奇心循环（核心组件 - 每次心跳必须执行）
python3 memory/curiosity/scripts/curiosity_loop.py
```

流程简化：
1. 读取 `memory/curiosity/state.json`
2. 检查 tension ≥ threshold（当前 0.5）
3. 选择最高 `importance × uncertainty` 的 gap
4. 执行轻量探索（1-2 次工具调用）
5. 自动生成新 gap
6. 白日梦检查（5% 概率或 boredom > 0.7）
7. 验证预测
8. 更新状态

## 📊 当前状态

| 指标 | 值 |
|------|-----|
| **Tension** | 0.50 (刚好达到阈值) |
| **Interest** | 0.85 |
| **Boredom** | 0.00 |
| **Knowledge Gaps** | 7 个 |
| **Total Explorations** | 2 |
| **Total Discoveries** | 3 |

### 当前 Knowledge Gaps（按优先级排序）

| 排名 | Gap | 分数 (I×U) | 领域 |
|------|-----|-----------|------|
| 1 | Neil 的 HARL 项目当前状态和进展如何？ | 0.72 | neil_research |
| 2 | AgentEvolver 论文中的 self-questioning 机制具体怎么实现的？ | 0.51 | self_evolution |
| 3 | 边缘智能领域最近有什么突破性进展？ | 0.72 | edge_intelligence |
| 4 | Neil 今晚为什么突然对 AI 意识和好奇心感兴趣？ | 0.67 | neil_motivation |
| 5 | 我的 Learned Rules 机制实际上改变了我多少行为？ | 0.42 | self_understanding |

## 🎯 心跳整合

### 完整流程

```bash
# 1. 读取状态
cat memory/heartbeat-state.json
cat memory/curiosity/state.json

# 2. 执行好奇心循环
python3 memory/curiosity/scripts/curiosity_loop.py
# 输出：探索摘要、选择的 gap、情感状态

# 3. 分享决策（如果发现有价值的内容）
python3 memory/curiosity/scripts/share_decision.py

# 4. 更新心跳状态
# 自动更新 memory/heartbeat-state.json
```

### 自动化集成

可以在 `~/.clawdbot/scripts/check-emails.py` 同级添加：

```bash
# ~/.clawdbot/scripts/heartbeat.sh
#!/bin/bash
cd /home/neardws/clawd

# 执行好奇心循环
python3 memory/curiosity/scripts/curiosity_loop.py

# 检查是否有重要发现需汇报
if [ $? -eq 1 ]; then
    echo "重要发现，建议主动汇报"
fi
```

## 🔍 手动操作

```bash
cd ~/clawd

# 查看当前状态
python3 memory/curiosity/scripts/curiosity_loop.py --dry-run

# 查看发现日志
head -50 memory/curiosity/discoveries.md

# 查看开放问题
cat memory/curiosity/open-questions.md

# 手动触发白日梦
python3 memory/curiosity/scripts/daydream.py run

# 验证预测
python3 memory/curiosity/scripts/surprise.py due
```

## 📝 待完善（可选）

1. **实际探索逻辑**: `curiosity_loop.py` 中的探索部分是占位符，需要实现实际的工具调用（搜索/读文件）

2. **自动化触发**: 可以配置 cron 或 systemd timer 定期执行心跳

3. **分享队列**: `share_queue.json` 目前为空，可以实现自动分享逻辑

## ✅ 整合验证

```bash
# 测试新路径
cd ~/clawd/memory/curiosity/scripts
python3 curiosity_loop.py --dry-run

# 应该输出：
# 📝 DRY RUN - Would explore: Neil 的 HARL 项目当前状态和进展如何？
# Tension: 0.50
# Emotion: interest=0.85, boredom=0.00
```

**状态**: ✅ 整合完成，好奇心内核现在是主记忆系统的核心组件
