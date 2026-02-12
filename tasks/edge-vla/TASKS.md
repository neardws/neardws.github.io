# Edge VLA 研究方向调研任务追踪

## 🎯 目标
调研并确认 Edge VLA (Vision-Language-Action on Edge) 具体研究方向

## ⚠️ 关键信息
- **优先级**: P0 (最高)
- **前置依赖**: 国自然青基申请书需要基于此确定研究方向
- **产出要求**: 需要在青基撰写前完成方向决策
- **协作频道**: `#papers` (Discord) - 文献调研与论文讨论主战场

## 📋 当前状态

### ✅ 已确定的核心方向

**科学问题**:
> 边缘算力约束下VLA高效压缩与任务适应的协同优化机理

**研究内容** (三个方向):
1. **边缘算力约束下VLA高效压缩与任务适应的协同优化机理**
2. **资源受限条件下VLA压缩-后训练-适应的协同作用机制**
3. **边缘端VLA模型压缩与快速任务适应的耦合优化机理**

### 📚 已有调研基础

**VLA 基座模型调研**:
- π0 系列 (Physical Intelligence): π0 → π0-FAST → π0.5 → π*₀.₆
- OpenPI 开源框架: JAX + PyTorch, LoRA 微调管线
- 其他开源 VLA: OpenVLA (7B), Octo (93M), SmolVLA (450M)

**关键发现**:
- π0 系列 ~3.3B 参数，全部云端部署，**边缘化空白 = 研究切入点**
- FAST Tokenizer (DCT 频域压缩 13.2x) - 动作表示压缩
- 尚无边缘部署方案，正是"高效后训练"研究空间

### 🎨 已产出材料
- π0 系列演进图 (PPT半栏) - SVG + PNG 版本
- 科学问题凝练 (短句版本)

## 🚀 执行方式

### 常驻代理（已启动 ✅）
- **会话名**: `edge-vla`
- **类型**: tmux 常驻后台代理
- **模型**: **MiniMax M2.1** (opencode)
- **状态**: 🟢 运行中
- **工作目录**: `~/clawd/arxiv-lab/edge-vla/`

### 论文管理
- **PDF 存储**: `~/clawd/arxiv-lab/edge-vla/papers/`
- **阅读笔记**: `~/clawd/arxiv-lab/edge-vla/notes/`
- **Gap 分析**: `~/clawd/arxiv-lab/edge-vla/gap-analysis.md`
- **目录索引**: `~/clawd/arxiv-lab/edge-vla/README.md`

### 子代理任务
1. **文献搜索**: Edge AI × VLA 交叉领域论文
2. **论文下载**: 自动下载到 arxiv-lab
3. **笔记生成**: 每篇论文生成结构化阅读笔记
4. **Gap识别**: 对比分析，更新 gap-analysis.md
5. **主动讨论**: 在 `#papers` 频道汇报并提问
6. **定期汇总**: 每日进展摘要

### 管理命令
```bash
# 查看状态
./skills/tmux-agents/scripts/check.sh edge-vla

# 实时查看
tmux attach -t edge-vla

# 发送指令
tmux send-keys -t edge-vla '搜索 Edge VLA 相关论文' Enter

# 停止代理
tmux kill-session -t edge-vla
```

---

| 任务 | 预计时间 | 状态 | 产出 | 协作位置 |
|------|---------|------|------|---------|
| VLA基座模型调研 | 已完成 | ✅ | π0系列分析 | `#papers` |
| 科学问题凝练 | 已完成 | ✅ | 三方向机理 | `#papers` |
| 文献收集 (Edge AI交叉) | 2天 | 🔄 | 文献列表 | `#papers` |
| 技术趋势分析 | 2天 | ⏳ | 趋势报告 | `#papers` |
| 研究gap识别 | 1天 | ⏳ | gap清单 | `#papers` |
| **方向决策文档** | 1天 | ⏳ | **决策文档** | **2/20** |

---

## 📝 进展日志

| 日期 | 进展 | 备注 |
|------|------|------|
| 2/8 | π0系列调研完成 | 生成演进图，确认边缘化空白切入点 |
| 2/8 | 科学问题凝练完成 | 三个机理方向确定 |

