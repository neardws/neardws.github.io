# Tmux 会话监控日志

## 🖥️ 当前运行中会话

| 会话 | 用途 | 模型 | 状态 | 最后活动 |
|------|------|------|------|---------|
| `jome-exp` | TMAO 实验开发 | Claude (droid) | 🟢 已完成核心开发 | 等待预实验运行 |
| `vec-gpu` | HARL GPU 化 | Claude Opus 4.6 | 🟢 正在实现核心方法 | 进行中 |
| `xiaohei` | Voice Assistant | Claude (droid) | ✅ 已完成 | 已完成 |
| `edge-vla` | Edge VLA 文献调研 | MiniMax M2.1 | 🟢 **已重启** | 运行中 |

## 📊 各会话详情

### 1. jome-exp (TMAO)
- **完成内容**:
  - ✅ Online DT 修复（删除重复 train() 方法）
  - ✅ D4PG 算法适配（PyTorch 实现）
  - ✅ 可视化脚本 plot_results.py（Fig.5/6/7 + LaTeX 表格）
  - ✅ 预实验脚本 run_preliminary.sh
- **下一步**: 运行预实验 `./run_preliminary.sh`
- **预计耗时**: 2-3 小时

### 2. vec-gpu (HARL GPU 化)
- **当前进展**: 实现 VECEnvGPU 核心方法
- **已完成**:
  - `_transform_actions()` - 动作解析
  - `_update_queues_vectorized()` - 队列更新
  - `_update_virtual_queues_vectorized()` - 虚拟队列
  - `_compute_reward_vectorized()` - 奖励计算
- **状态**: 正在开发中

### 3. xiaohei (Voice Assistant)
- **状态**: ✅ 已完成
- **交付内容**: 完整的 Voice Assistant 实现
- **待配置**: WebSocket URL (chat-manager.js)

### 4. edge-vla (Edge VLA 调研) ⚠️
- **状态**: 🔴 **启动错误**
- **问题**: opencode 命令将任务描述误认为目录路径
- **需要**: 修复启动方式

## 🔔 监控机制

- **检查频率**: 每 4 小时自动检查
- **汇报渠道**: #tasks 频道
- **异常处理**: 发现异常立即汇报

## 📋 待处理事项

- [ ] 修复 edge-vla 启动错误
- [ ] 跟进 jome-exp 预实验运行
- [ ] 跟进 vec-gpu 开发进度

