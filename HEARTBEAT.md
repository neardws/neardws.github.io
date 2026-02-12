# HEARTBEAT.md

## ⚡ 心跳执行清单

### 1️⃣ 读取状态
- `memory/heartbeat-state.json` — 追踪上次执行
- `memory/curiosity/state.json` — 张力指数

### 2️⃣ 紧急检查（轮询 1-2 项）
- [ ] 邮件: `python3 ~/.clawdbot/scripts/check-emails.py`
- [ ] 日历: 未来 24h 日程
- [ ] 通知: X/Twitter mentions

### 3️⃣ 🧠 好奇心循环（必须执行）
```bash
python3 memory/curiosity/scripts/curiosity_loop.py
```

**流程:**
1. 读取 `state.json`
2. 检查 tension ≥ 0.5 → 触发探索
3. 轻量探索（1-2 次工具调用）
4. 发现 → 追加到 `discoveries.md`
5. 自动生成新 gap
6. 验证预测

### 4️⃣ 分享决策
```bash
python3 memory/curiosity/scripts/share_decision.py
```
- 深夜 (23:00-08:00) → 沉默
- 非深夜 + 有趣/重要 → 主动分享

### 5️⃣ 更新状态
```bash
python3 memory/curiosity/scripts/heartbeat_update.py
```

---

## 🎯 何时主动汇报
- 发现有趣的东西 → 非深夜分享
- 深夜 → 沉默（除非非常紧急）

## 📌 关键原则
1. **好奇心循环不是可选的** — 系统自我进化核心
2. **探索轻量** — 最多 1-2 次工具调用
3. **连续 3 次无进展 → 降低 importance**
4. **发现即资产** — 沉淀到 `discoveries.md`

## 📁 文件结构
```
memory/
├── heartbeat-state.json
└── curiosity/
    ├── state.json
    ├── discoveries.md
    ├── predictions.json
    └── scripts/
        ├── curiosity_loop.py
        ├── gap_generator.py
        └── share_decision.py
```

---

*Keep it small to limit token burn.*
