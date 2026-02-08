# 灾难恢复与监控规划 🛡️

> 基于双系统（Ubuntu Server + Mac Mini M4）的实际架构制定
> 最后更新: 2026-02-08

---

## 系统现状总览

### Ubuntu Server (主机, 192.168.31.211)
| 组件 | 说明 |
|------|------|
| OpenClaw Gateway | :18789, 核心 AI 助手 |
| Cloudflared | 4 条隧道 (clawdbot/mcp/embedding/1panel...) |
| Docker 容器 | rsshub, metamcp, dongguatv, notebooklm-mcp, autodl×4 |
| Systemd 服务 | embedding, clawd-voice, axis-voice-http, cliproxyapi, ft-agent |
| Cron Jobs | 邮件转发×3, self-heal, info-monitor, autodl-heartbeat, security-scan |
| 数据 | ~/.clawdbot/, ~/.openclaw/, ~/clawd/, ~/User_Services/, ~/github/ |

### Mac Mini M4 (备机, 192.168.31.114)
| 组件 | 说明 |
|------|------|
| OpenClaw Node | com.clawdbot.node (设备配对) |
| MLX TTS | :5100 Qwen3-TTS |
| MLX ASR | :9001 whisper-large-v3 |
| 健康检查 | 每5min检查Ubuntu Gateway |
| 故障切换 | gateway-failover.sh (可接管) |
| 工具 | bird, imsg, peekaboo, remind, memo, ical-buddy |

### 已有安全机制 ✅
- [x] Mac Mini → Ubuntu 健康检查 (每5min)
- [x] Mac Mini gateway-failover.sh (自动接管)
- [x] self-heal.py (每30min, Ubuntu自检)
- [x] clawd workspace Git 备份
- [x] Cloudflare Tunnel (无需公网IP)

### 缺失的关键环节 ❌
- [ ] **P0: 外部心跳监控** — 两台机器互相监控，但如果整个局域网断了？没人知道
- [ ] **P1: 敏感数据加密备份** — 30+ 个 .env 文件只存本地，硬盘挂了全丢
- [ ] **P1: 系统状态快照** — cron/systemd/docker 配置没有版本化
- [ ] **P2: 从零恢复手册** — 没有可执行的 DR 文档

---

## P0: 外部心跳监控 (30分钟)

### 方案: Healthchecks.io + 双系统上报

选 Healthchecks.io 的理由：免费20个check、支持 /fail 端点、支持邮件/Telegram/Discord 通知。

#### 需要的检查点 (5个)

| Check 名称 | 来源 | Period | Grace | 说明 |
|------------|------|--------|-------|------|
| `ubuntu-alive` | Ubuntu cron | 5min | 10min | Ubuntu 系统是否在线 |
| `openclaw-gateway` | Ubuntu cron | 5min | 10min | Gateway 进程+HTTP 健康 |
| `mac-mini-alive` | Mac cron | 5min | 10min | Mac Mini 是否在线 |
| `cloudflare-tunnel` | Ubuntu cron | 15min | 30min | Tunnel 外部可达性 |
| `email-forward` | Ubuntu cron | 10min | 20min | 邮件转发正常工作 |

#### 实施步骤

**Step 1: 注册 Healthchecks.io**
- 用 neard.ws@gmail.com 注册
- 创建项目 "Neil Homelab"
- 添加通知渠道: Email + Discord Webhook (ops 频道)

**Step 2: Ubuntu 心跳脚本**

```bash
# /home/neardws/server-scripts/monitor/healthchecks-ping.sh
#!/bin/bash
# 每5分钟由 cron 调用

HC_UUID_ALIVE="<填入>"
HC_UUID_GATEWAY="<填入>"
HC_UUID_TUNNEL="<填入>"

# 1. 系统存活 (能跑这个脚本就是活的)
curl -fsS --retry 3 "https://hc-ping.com/$HC_UUID_ALIVE" > /dev/null

# 2. Gateway 进程检查
if pgrep -f "openclaw-gateway" > /dev/null && \
   curl -sf --connect-timeout 5 "http://127.0.0.1:18789/health" > /dev/null; then
    curl -fsS --retry 3 "https://hc-ping.com/$HC_UUID_GATEWAY" > /dev/null
else
    curl -fsS --retry 3 "https://hc-ping.com/$HC_UUID_GATEWAY/fail" > /dev/null
fi

# 3. Cloudflare Tunnel (每15分钟才需要，但跟着跑也行)
if curl -sf --connect-timeout 10 "https://clawdbot.neardws.com/health" > /dev/null; then
    curl -fsS --retry 3 "https://hc-ping.com/$HC_UUID_TUNNEL" > /dev/null
else
    curl -fsS --retry 3 "https://hc-ping.com/$HC_UUID_TUNNEL/fail" > /dev/null
fi
```

**Cron 条目:**
```cron
*/5 * * * * /home/neardws/server-scripts/monitor/healthchecks-ping.sh >> /home/neardws/User_Services/services-logs/healthchecks.log 2>&1
```

**Step 3: Mac Mini 心跳脚本**

```bash
# ~/.clawdbot/healthchecks-ping.sh
#!/bin/bash
HC_UUID_MAC="<填入>"
curl -fsS --retry 3 "https://hc-ping.com/$HC_UUID_MAC" > /dev/null
```

**Cron 条目:**
```cron
*/5 * * * * ~/.clawdbot/healthchecks-ping.sh
```

---

## P1: 敏感数据加密备份 (1小时)

### 方案: GPG 加密 → Git 私有仓库

为什么不用 iCloud/S3: 多一层依赖。GitHub 私有仓库 + GPG 加密够用，且已有 SSH key。

#### 需要备份的敏感文件清单

**配置文件 (关键)**
```
~/.clawdbot/clawdbot.json
~/.openclaw/openclaw.json
~/.openclaw/.env
/etc/cloudflared/config.yml
/etc/cloudflared/*.json (tunnel credentials)
```

**API Keys / .env (30+个)**
```
~/User_Services/email-automation/.env
~/User_Services/embedding/.env
~/User_Services/feishu/.env
~/User_Services/amap/.env
~/User_Services/xai/.env
~/User_Services/nano-banana/.env
~/User_Services/trello/.env
~/User_Services/mac-remote/.env
~/.env (全局)
~/github/BettaFish/.env
~/github/vibe-kanban/.env.remote
~/github/veapi-python/.env
~/Documents/latex-paper-polishing/.env
```

**SSH & 认证**
```
~/.ssh/id_ed25519 + id_ed25519.pub
~/.cloudflared/ (tunnel creds)
```

#### 实施方案

**Step 1: 生成 GPG 密钥**
```bash
gpg --full-generate-key
# 选择 RSA 4096, 永不过期
# 用 neard.ws@gmail.com
# 导出并安全存储密钥(打印纸质备份 or 存手机备忘录)
gpg --export-secret-keys --armor > ~/gpg-key-backup.asc
```

**Step 2: 备份脚本**
```bash
# /home/neardws/server-scripts/backup/secrets-backup.sh
#!/bin/bash
set -euo pipefail

BACKUP_DIR="/tmp/secrets-backup-$(date +%Y%m%d)"
ARCHIVE="/tmp/secrets-$(date +%Y%m%d).tar.gz.gpg"
REPO="$HOME/server-scripts/backup/secrets-encrypted"
GPG_RECIPIENT="neard.ws@gmail.com"

mkdir -p "$BACKUP_DIR"

# 收集所有敏感文件
echo "Collecting secrets..."
find /home/neardws -maxdepth 4 -name ".env*" \
  -not -path "*/node_modules/*" -not -path "*/.git/*" \
  -not -name ".env.example" \
  -exec cp --parents {} "$BACKUP_DIR/" \;

# 配置文件
cp --parents ~/.clawdbot/clawdbot.json "$BACKUP_DIR/" 2>/dev/null || true
cp --parents ~/.openclaw/openclaw.json "$BACKUP_DIR/" 2>/dev/null || true
cp --parents ~/.openclaw/.env "$BACKUP_DIR/" 2>/dev/null || true
cp --parents ~/.ssh/id_ed25519 "$BACKUP_DIR/" 2>/dev/null || true
sudo cp --parents /etc/cloudflared/config.yml "$BACKUP_DIR/" 2>/dev/null || true
sudo cp --parents /etc/cloudflared/*.json "$BACKUP_DIR/" 2>/dev/null || true

# 导出 crontab 和 systemd 服务
crontab -l > "$BACKUP_DIR/crontab.txt" 2>/dev/null
systemctl list-units --type=service --state=running --no-pager > "$BACKUP_DIR/systemd-services.txt"
docker ps --format "{{.Names}}: {{.Image}} {{.Ports}}" > "$BACKUP_DIR/docker-containers.txt"

# 加密打包
tar czf - -C "$BACKUP_DIR" . | gpg --encrypt --recipient "$GPG_RECIPIENT" -o "$ARCHIVE"

# 提交到 Git
cd "$REPO"
cp "$ARCHIVE" ./
git add .
git commit -m "backup: $(date +%Y-%m-%d)"
git push origin main

# 清理
rm -rf "$BACKUP_DIR" "$ARCHIVE"
echo "Backup complete: $(date)"
```

**Step 3: 设置 Cron (每周日凌晨4点)**
```cron
0 4 * * 0 /home/neardws/server-scripts/backup/secrets-backup.sh >> /home/neardws/User_Services/services-logs/secrets-backup.log 2>&1
```

### Mac Mini 备份
Mac Mini 关键数据较少（主要是 Homebrew 和 launchd 配置），通过 Time Machine 或 iCloud 已覆盖。额外需要：
```bash
# 导出 Mac Mini 状态
brew bundle dump --file=~/.clawdbot/Brewfile
launchctl list | grep -v com.apple > ~/.clawdbot/launchd-services.txt
crontab -l > ~/.clawdbot/crontab-backup.txt
```

---

## P1.5: 系统状态快照版本化 (30分钟)

### 方案: 状态快照脚本 → Git 追踪

```bash
# /home/neardws/server-scripts/backup/system-snapshot.sh
#!/bin/bash
SNAP_DIR="$HOME/clawd/docs/system-state"
mkdir -p "$SNAP_DIR"

echo "Generating system snapshot..."

# Cron jobs
crontab -l > "$SNAP_DIR/ubuntu-crontab.txt" 2>/dev/null

# Systemd services
systemctl list-units --type=service --state=running --plain --no-pager \
  | grep -vE '(systemd|dbus|ssh|udev|cron|snap)' > "$SNAP_DIR/ubuntu-services.txt"

# Docker containers
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" \
  > "$SNAP_DIR/docker-containers.txt" 2>/dev/null

# Listening ports
ss -tlnp 2>/dev/null | grep LISTEN > "$SNAP_DIR/listening-ports.txt"

# Cloudflared config (sanitized)
sudo cat /etc/cloudflared/config.yml 2>/dev/null | \
  sed 's/credentials-file:.*/credentials-file: [REDACTED]/' > "$SNAP_DIR/cloudflared.txt"

# npm global packages
ls $(npm root -g) 2>/dev/null > "$SNAP_DIR/npm-global.txt" || true

# Node.js version
node -v > "$SNAP_DIR/versions.txt"
pnpm -v >> "$SNAP_DIR/versions.txt" 2>/dev/null
git --version >> "$SNAP_DIR/versions.txt"

# OpenClaw version
cd ~/clawdbot && git describe --tags --always >> "$SNAP_DIR/versions.txt" 2>/dev/null

echo "Snapshot saved to $SNAP_DIR"
```

**Cron (每天凌晨3:30):**
```cron
30 3 * * * /home/neardws/server-scripts/backup/system-snapshot.sh && cd ~/clawd && git add docs/system-state/ && git commit -m "snapshot: $(date +%Y-%m-%d)" && git push 2>/dev/null
```

---

## P2: 从零恢复手册

### 场景 A: Ubuntu Server 完全损毁

**阶段一：基础环境 (30min)**
```bash
# 1. 安装系统 (Ubuntu 24.04 LTS)
# 2. 基础工具
sudo apt update && sudo apt install -y git curl build-essential zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# 3. SSH key
# 从 GPG 加密备份中恢复，或重新生成并添加到 GitHub

# 4. Node.js (via nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
nvm install 22
npm install -g pnpm

# 5. Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 6. Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

**阶段二：恢复 OpenClaw (30min)**
```bash
# 1. 克隆源码
git clone https://github.com/clawdbot/clawdbot.git ~/clawdbot
cd ~/clawdbot && pnpm install && pnpm run build

# 2. 恢复 workspace
git clone <workspace-repo> ~/clawd

# 3. 恢复配置
# 解密 GPG 备份
gpg --decrypt secrets-YYYYMMDD.tar.gz.gpg | tar xzf -
# 还原 ~/.openclaw/openclaw.json, ~/.clawdbot/clawdbot.json, .env 文件

# 4. 安装 OpenClaw CLI
cd ~/clawdbot && npm link  # 或 pnpm link --global

# 5. 启动 Gateway
clawdbot gateway start
```

**阶段三：恢复服务 (30min)**
```bash
# 1. Cloudflare Tunnel
sudo cloudflared service install
sudo cp /path/to/backup/cloudflared/* /etc/cloudflared/
sudo systemctl restart cloudflared

# 2. Docker 容器
cd ~/User_Services/metamcp && docker compose up -d
cd ~/User_Services/rsshub && docker compose up -d
# ... 其他容器

# 3. Systemd 服务
# 参考 docs/system-state/ubuntu-services.txt 逐一恢复

# 4. Cron Jobs
crontab < ~/clawd/docs/system-state/ubuntu-crontab.txt

# 5. Embedding 服务
cd ~/User_Services/embedding && pip install -r requirements.txt
sudo systemctl start embedding
```

**阶段四：验证 (30min)**
```bash
# 1. Gateway
curl http://localhost:18789/health

# 2. Tunnel
curl https://clawdbot.neardws.com/health

# 3. 各服务端口
for port in 8001 8080 12010 18789; do
    echo "Port $port: $(curl -sf -o /dev/null -w '%{http_code}' http://localhost:$port/health 2>/dev/null || echo 'N/A')"
done

# 4. 发一条测试消息
# 通过 Discord 确认 AI 回复正常

# 5. 恢复心跳监控
crontab -e  # 添加 healthchecks-ping.sh
```

### 场景 B: Mac Mini M4 完全损毁

**阶段一：基础环境 (20min)**
```bash
# 1. macOS 已预装 Git
# 2. Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 3. 从 Brewfile 恢复
brew bundle install --file=Brewfile

# 4. Node + pnpm
brew install node pnpm
```

**阶段二：恢复 OpenClaw Node (20min)**
```bash
# 1. 安装 OpenClaw
pnpm install -g clawdbot  # 或从源码

# 2. 恢复配置
# 从备份解密 .clawdbot/clawdbot.json

# 3. 配对到 Ubuntu Server
clawdbot pair  # 按提示操作

# 4. MLX TTS/ASR
# 恢复 launchd plist 并 load
```

**阶段三：恢复自动化 (20min)**
```bash
# 恢复 cron
crontab < ~/.clawdbot/crontab-backup.txt

# 恢复健康检查脚本
# 从 Git workspace 中复制
```

### 场景 C: 局域网全断 / 两台机器同时挂

- Healthchecks.io 10分钟内告警到邮箱 + Discord
- 恢复优先级: Ubuntu Server > Mac Mini
- 如果需要临时替代：任意 VPS 装 OpenClaw + 恢复 openclaw.json 即可接管基础 AI 功能

---

## 执行计划 (推荐时间线)

| 优先级 | 任务 | 预计耗时 | 建议时间 |
|--------|------|----------|----------|
| **P0** | 注册 Healthchecks.io + 配置5个检查点 | 30min | **今天** |
| **P0** | Ubuntu/Mac 心跳 cron 部署 | 15min | **今天** |
| **P1** | 生成 GPG 密钥 | 10min | 本周末 |
| **P1** | 编写并测试 secrets-backup.sh | 30min | 本周末 |
| **P1** | 首次手动执行备份，验证可恢复 | 20min | 本周末 |
| **P1.5** | 系统状态快照脚本 + Git 追踪 | 15min | 本周末 |
| **P2** | 完善本文档中的恢复步骤 | 30min | 下周 |
| **P2** | 演练一次恢复流程 (用 Docker 模拟) | 2h | 下下周末 |

---

## 下一步

Neil 确认后我立刻执行 P0:
1. 你去 [healthchecks.io](https://healthchecks.io) 注册账号，创建项目
2. 我在两台机器上部署心跳脚本
3. 配置 Discord Webhook 通知到 #ops 频道

需要我先执行哪个？
