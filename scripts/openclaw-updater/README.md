# OpenClaw 源码更新监控系统

自动监控 OpenClaw 上游仓库更新，支持**零宕机升级**并保留本地自定义功能。

## 核心特性

- **零宕机升级**: 热重载优先，滚动重启备用
- **自动回滚**: 升级失败自动恢复
- **系统级自愈**: Watchdog 独立于 Gateway 运行
- **本地内容保护**: 自动保留自定义技能和代理

---

## 系统结构

```
~/clawd/scripts/openclaw-updater/
├── monitor.py          # 监控脚本，检查远程更新
├── upgrade-safe.sh     # 零宕机升级脚本（推荐）
├── upgrade.sh          # 基础升级脚本
├── watchdog.sh         # 系统级自愈 watchdog
├── state.json          # 状态文件
├── guard-state.json    # 升级保护状态
└── monitor.log         # 日志文件
```

---

## 零宕机升级策略

### 1. 热重载（首选）
```
SIGUSR1 → Gateway 不重启进程，仅重载配置/代码
├── 适用于: 技能更新、配置变更、非核心代码
├── 中断时间: 0秒
└── 回退: 如失败自动切换滚动重启
```

### 2. 滚动重启（备用）
```
启动新进程 → 健康检查通过 → 终止旧进程
├── 适用于: 核心依赖变更、gateway 代码更新
├── 中断时间: 2-5秒
└── 回退: 如失败自动回滚
```

### 3. 自动回滚（兜底）
```
检测到失败 → 恢复代码 → 重启 Gateway
├── 触发条件: 3次重启失败 或 6次健康检查失败
├── 回滚时间: 10-30秒
└── 保证: Gateway 最终会恢复运行
```

---

## 快速使用

### 立即升级（零宕机）
```bash
~/clawd/scripts/openclaw-updater/upgrade-safe.sh
```

### 安装 Watchdog（推荐）
```bash
# 安装为 systemd timer（每分钟检查一次）
~/clawd/scripts/openclaw-updater/watchdog.sh install

# 查看状态
~/clawd/scripts/openclaw-updater/watchdog.sh status
```

### 检查更新（不执行）
```bash
~/clawd/scripts/openclaw-updater/monitor.py
```

---

## 本地新增内容（自动保留）

以下目录和文件在升级时会被保留：

- `skills/amap-places/` - 高德地图技能
- `skills/arxiv-researcher/` - arXiv 论文管理
- `skills/fact-check/` - 事实核查
- `skills/notebooklm/` - NotebookLM 集成
- `skills/paper-manager/` - 论文管理
- `skills/remote-macos-*/` - 远程 macOS 工具集
- `agents/luoxiaohei/` - 罗小黑语音助手

---

## 自动监控

- **频率**: 每小时检查一次
- **通知**: 发现更新时自动发送到 Discord #ops 频道
- **Cron ID**: `79b6db48-07a8-4862-9ba5-85a370438de7`

---

## 升级前状态

当前状态：
- **本地 commit**: `bc475f01`
- **远程 commit**: `661279cb`
- **落后**: 106 个提交
- **风险等级**: 中（106个提交建议分批升级）

建议：
```bash
# 1. 先安装 watchdog
~/clawd/scripts/openclaw-updater/watchdog.sh install

# 2. 执行零宕机升级
~/clawd/scripts/openclaw-updater/upgrade-safe.sh
```

---

## 故障处理

### 升级中断
```bash
# 手动回滚
cd ~/clawdbot
git reset --hard bc475f01  # 恢复到升级前
openclaw gateway restart
```

### Gateway 无响应
```bash
# Watchdog 会自动处理，或手动重启
openclaw gateway restart
```

### 完全恢复备份
```bash
# 从备份恢复
rm -rf ~/clawdbot
cp -r ~/clawd/backup/openclaw-*/clawdbot ~/
openclaw gateway restart
```
