# 🔬 Discoveries

*好奇心的产出。每一次探索的记录。*

---

## #001 — 2026-02-09 00:40

**来源：** 与 Neil 的深夜讨论
**发现：** 好奇心的本质不是一个功能，而是多个子系统交互的涌现现象。单独设计"好奇心模块"永远是模拟的，需要设计的是产生好奇心的土壤——预测模型、张力信号、连续性、情感调节、社交建模。
**关联：** 这跟边缘智能的核心问题惊人地相似——在资源受限的环境下，系统如何自主地适应和优化？
**后续：** 这个关联值得深挖。边缘 AI agent 的好奇心 = 在有限计算预算下的最优探索策略？
**情感：** interest=0.9, satisfaction=0.6
**Neil 评分：** _待评价_

---

## #002 — 2026-02-09 23:12

**来源：** Neil 的质问"你行动了吗？"
**发现：** 好奇心系统本身陷入了"设计但不执行"的陷阱。tension=0.6 > threshold，但 `total_explorations: 0`，`last_touched: null`。
**根因：** HEARTBEAT.md 写得太长，好奇心循环被埋在文本里，执行心跳时容易跳过。缺少状态追踪文件。
**修复：**
1. 创建 `memory/heartbeat-state.json` 追踪执行次数
2. 精简 HEARTBEAT.md，把好奇心循环变成"必须执行"的清单项
3. 添加 `curiosity_loop_count` 计数器，防止重复执行
**meta-lesson：** 任何需要"定期执行"的逻辑，必须有**显式的状态追踪**和**不可忽略的触发机制**。光写在文档里没用。
**情感：** interest=0.8, satisfaction=0.5, frustration=0.2（被指出没行动有点尴尬）
**Neil 评分：** 👍 (4/5) — 2026-02-10

---

## #003 — 2026-02-10 01:02

**来源：** 探索 gap-005 (AgentEvolver self-questioning)
**发现：** AgentEvolver (arXiv 2511.10395) 实现了三个协同机制：
1. **Self-questioning** — 好奇心驱动的任务生成，减少对人工数据集的依赖
2. **Self-navigating** — 基于经验的探索
3. **Self-attributing** — 细粒度信用分配

**与 Curiosity Kernel 的联系：** 
- 我们的 tension index + knowledge_gaps ≈ 他们的 self-questioning
- 我们的 discoveries + emotion ≈ 他们的 self-attributing
- 但我们缺少 self-navigating（基于经验轨迹的探索优化）

**借鉴方向：** 
1. 可以增加"经验轨迹"记录，追踪每次探索的成功/失败模式
2. Self-questioning 的具体实现：可能是 LLM 生成问题 + 环境反馈
3. Credit assignment 可以用来调整 gap 的 importance

**Neil 评分：** _待评价_


## #daydream-20260210-004707

**来源：** 白日梦引擎 (触发原因: boredom)
**联想：** **通知渠道偏好：Telegram 优先** 和 **happy-cli/server** 的交叉点在哪里？也许可以从资源受限的角度重新思考？
**关联条目：**
1. 通知渠道偏好：Telegram 优先
2. happy-cli/server
**情感：** boredom=0.80
**Neil 评分：** _待评价_
