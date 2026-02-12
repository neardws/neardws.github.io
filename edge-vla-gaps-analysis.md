# Edge VLA 深度调研 — VLA-Adapter & Lite VLA

## 1. VLA-Adapter (OpenHelix Team)

**Paper**: arXiv:2509.09372  
**团队**: OpenHelix Team (机构未明确，GitHub 组织名)  
**Code**: https://github.com/OpenHelix-Team/VLA-Adapter

### 核心创新

**问题**: 传统 VLA 依赖大规模 VLM 预训练，计算成本高昂

**解决方案**: 
- **Bridge Attention 机制**: 轻量级 Policy 模块，自主选择最优 VL 条件注入动作空间
- **0.5B 参数骨干**: 无需机器人数据预训练，从零开始训练
- **8 小时单卡训练**: 消费级 GPU 即可训练出 SOTA 级 VLA

### 关键发现 — 与 Gap 2 (自适应模型切换) 高度相关

论文系统分析了**哪些 VL 条件对动作空间真正有用**：
- 不是所有视觉-语言特征都需要
- Bridge Attention 可以**动态选择**最相关的条件
- 这为实现**运行时自适应**提供了架构基础

### 技术细节

| 组件 | 设计 |
|------|------|
| Vision Encoder | 轻量级 (如 SigLIP-small) |
| Language Model | 0.5B 参数 SLM |
| Bridge Attention | Cross-attention 机制，选择性注入 VL 特征 |
| Action Head | 简单 MLP 或 Diffusion |

### 实验结果

- **性能**: 达到 SOTA 级 (与 7B OpenVLA 相当)
- **速度**: 当前报道的最快推理速度
- **训练成本**: 相比 OpenVLA 降低 **10x+**

### 与 Gap 2 的关联

VLA-Adapter 的 Bridge Attention 机制可以直接扩展为**自适应模型切换**的基础：
- 简单任务 → 只用轻量级 VL 特征
- 复杂任务 → 激活更多 VL 条件
- 进一步 → 根据任务难度切换不同大小的 backbone

---

## 2. Lite VLA: CPU-Bound Edge Robots

**Paper**: arXiv:2511.05642  
**作者**: Kishor Datta Gupta 等  
**机构**: 未明确 (推测为美国国防/航天背景)

### 核心创新

**问题**: 现有 VLA/VLM 要么云端推理，要么感知与移动分离

**解决方案**:
- **纯 CPU 部署**: 小型 VLM 在移动机器人上实时运行
- **同时移动+推理**: 突破性地实现 concurrent reasoning and mobility
- **无需云连接**: 完全自主，适用于 GPS-denied 环境

### 技术实现

| 组件 | 设计 |
|------|------|
| VLM | 小型模型 (具体型号未披露，推测 <1B) |
| 量化 | 4-bit NF4 量化 |
| 混合精度 | NF4 骨干 + FP32 投影头 |
| 硬件 | 嵌入式 CPU (无 GPU) |

### 关键数据

- **速度提升**: 比 FP32 基线快 **9x**
- **稳定性**: 输出质量保持稳定
- **场景**: disaster response, defense, service robotics

### 与 Gap 1 (Edge-Cloud 协同) 的关联

Lite VLA 证明了**纯 Edge 推理的可行性**，但仍有局限：
- 仅适用于简单场景理解任务
- 复杂长程规划仍需更强算力

**这正是 Gap 1 的机会所在**：
- 简单任务 → Lite VLA (CPU)
- 中等任务 → VLA-Adapter (Edge GPU)
- 复杂任务 → Cloud VLA (A100)

**需要智能调度机制**来决定何时切换

---

## 3. Research Gaps 深度分析

### Gap 1: Edge-Cloud 协同 VLA 推理

**现状**:
| 模式 | 代表工作 | 优点 | 缺点 |
|------|----------|------|------|
| 纯 Cloud | OpenVLA-7B, π₀ | 性能强 | 延迟高，需联网 |
| 纯 Edge | Lite VLA, VLA-Adapter | 实时，自主 | 能力有限 |

**缺失**: Split Computing / Edge-Cloud Collaborative VLA

**研究机会**:
1. **任务分解**: 哪些子任务必须在 edge？哪些可以 offload？
2. **动态调度**: 根据网络状况、任务紧急度、电量等实时决策
3. **状态同步**: Edge 和 Cloud VLA 如何共享上下文？

**Neil 的研究基础可迁移**:
- 之前 LLM edge-cloud 协同的方法论
- Split learning / Federated learning 经验
- 通信-计算联合优化建模

### Gap 2: 自适应模型切换

**现状**:
- 当前 VLA 部署都是**固定模型**
- 无论任务简单还是复杂，都用同一个大模型

**VLA-Adapter 的启示**:
- Bridge Attention 已经在做**特征级别的选择**
- 可以扩展到**模型级别的选择**

**研究机会**:
1. **多尺度 VLA 族**: 训练 0.1B / 0.5B / 1B / 3B 多个版本
2. **任务复杂度估计**: 快速判断当前任务难度
3. **切换策略**: 
   - Hard switch: 完全换一个模型
   - Soft switch: MoE 风格，动态激活子网络
   - Early exit: 简单任务提前退出深层网络

**技术路线**:
- 用 RL 学习最优切换策略
- 状态: 任务特征、延迟要求、电量、网络状况
- 动作: 选择哪个模型 / 是否 offload
- 奖励: 准确率 - λ×延迟 - μ×能耗

---

## 4. 下一步建议

### 短期 (1-2 周)
1. **复现 VLA-Adapter**: 跑通代码，理解 Bridge Attention 机制
2. **深入阅读 Lite VLA**: 如果论文有开源，研究其量化策略

### 中期 (1-2 月)
3. **Gap 1 原型**: 实现一个简单的 Edge-Cloud VLA 切换 demo
   - Edge: VLA-Adapter (0.5B)
   - Cloud: OpenVLA (7B)
   - 调度器: 基于任务复杂度选择

4. **Gap 2 原型**: 在 VLA-Adapter 基础上实现 early-exit
   - 简单任务只跑前几层
   - 测量准确率-延迟 trade-off

### 长期 (3-6 月)
5. **系统整合**: Edge-Cloud 协同 + 自适应模型切换 统一框架
6. **理论分析**: 通信-计算优化模型，给出最优调度策略的理论保证

---

## 5. 排除的安全相关方向

根据 Neil 的要求，以下方向**不考虑**:
- ❌ 对抗攻击防御
- ❌ 分布外输入检测
- ❌ 硬件故障容错
- ❌ 安全关键系统的形式化验证

聚焦于**效率、自适应、协同优化**等性能方向。

---

*文档生成时间: 2026-02-10*  
*关联论文: arXiv:2509.09372, arXiv:2511.05642*
