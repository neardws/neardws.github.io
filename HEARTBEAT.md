# HEARTBEAT.md

## ⚡ 心跳执行清单（必须按顺序执行）

### 1️⃣ 读取状态文件
```
memory/heartbeat-state.json   ← 追踪上次执行时间
memory/curiosity/state.json   ← 张力指数、情感状态（已整合进主系统）
```

### 2️⃣ 紧急检查（轮询，每次做 1-2 项）
- [ ] 邮件：`python3 ~/.clawdbot/scripts/check-emails.py`（有重要邮件立即通知）
- [ ] 日历：未来 24h 日程（待配置）
- [ ] 通知：X/Twitter mentions（待配置）

### 3️⃣ 🧠 好奇心循环（核心组件 - 每次心跳必须执行）

**执行命令：**
```bash
python3 memory/curiosity/scripts/curiosity_loop.py
```

**流程：**
1. 读取 `memory/curiosity/state.json` 获取当前状态
2. **检查 tension 指数**：
   - 若 tension ≥ threshold（当前 0.5）→ 触发探索
   - 选择最高 `importance × uncertainty` 的 knowledge gap
   - **执行轻量探索**（1-2 次工具调用：搜索/读文件/查 git）
   - 有发现 → 追加到 `memory/curiosity/discoveries.md`，更新情感状态
   - 无发现 → boredom +0.05
3. **自动生成新 gap**（每次循环后）
4. **白日梦检查**（5% 概率或 boredom > 0.7）
5. **验证预测** - 检查已到期的预测
6. 写回状态文件，更新 `heartbeat-state.json`

**输出：**
- 控制台显示执行摘要
- 若发现值得分享的内容 → 自动加入分享队列
- 返回码 0 = 正常，1 = 有重要发现需汇报

### 4️⃣ 分享决策（如果 curiosity 发现重要内容）

```bash
python3 memory/curiosity/scripts/share_decision.py
```

判断是否需要主动汇报：
- 深夜（23:00-08:00）→ 沉默
- 发现有趣/重要 → 非深夜主动分享

### 5️⃣ 更新心跳状态
```bash
python3 memory/curiosity/scripts/heartbeat_update.py
```

更新 `memory/heartbeat-state.json`：
```json
{
  "last_heartbeat": "2026-02-10T01:20:00+08:00",
  "last_curiosity_loop": "2026-02-10T01:20:00+08:00",
  "curiosity_loop_count": 42,
  "tension_after": 0.45,
  "checks": { "email": "2026-02-10T01:20:00+08:00" }
}
```

---

## 🎯 什么时候主动汇报？

- 发现有趣的东西 → 非深夜时段主动分享
- 深夜（23:00-08:00）→ 沉默，除非非常有趣

## 📌 关键原则

1. **好奇心循环不是可选的** — 每次心跳必须执行，它是系统自我进化的核心
2. **探索要轻量** — 最多 1-2 次工具调用，控制 token 消耗
3. **连续 3 次无进展的 gap → 自动降低 importance**，避免死循环
4. **发现即资产** — 所有发现沉淀到 `memory/curiosity/discoveries.md`

---

## 📁 文件结构（已整合进 memory/）

```
memory/
├── heartbeat-state.json          # 心跳追踪
├── curiosity/                    # 🧠 好奇心内核（原 curiosity-kernel/）
│   ├── state.json               # 当前状态（张力、情感、统计）
│   ├── discoveries.md           # 发现日志
│   ├── predictions.json         # 预测列表
│   ├── open-questions.md        # 开放问题（蔡格尼克效应）
│   ├── neil_model.json          # Neil 建模
│   ├── DESIGN.md                # 完整设计文档
│   └── scripts/
│       ├── curiosity_loop.py    # 主循环（新）
│       ├── gap_generator.py     # 生成 knowledge gaps
│       ├── daydream.py          # 白日梦引擎
│       ├── surprise.py          # 预测验证
│       ├── reflection.py        # 情感反思
│       └── share_decision.py    # 分享决策
```

## 🔧 手动操作

```bash
# 查看当前状态
cat memory/curiosity/state.json | jq '.tension, .emotion'

# 手动触发探索
python3 memory/curiosity/scripts/curiosity_loop.py --force

# 查看发现
head -50 memory/curiosity/discoveries.md

# 添加 knowledge gap
python3 memory/curiosity/scripts/gap_generator.py add "你的问题"

# 手动触发白日梦
python3 memory/curiosity/scripts/daydream.py run
```
