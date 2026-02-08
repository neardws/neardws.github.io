# 灾难恢复手册 (DISASTER-RECOVERY.md)

> 目标：任意一台机器完全损毁后，2小时内恢复全部服务
> 最后验证: 2026-02-08 | 双系统架构 (Ubuntu Server + Mac Mini M4)

---

## 📋 恢复前准备

### 你需要准备的东西
- [ ] GPG 私钥（从 iPhone 备忘录 / iCloud 恢复）
- [ ] GitHub 账号 (neardws) 访问权限
- [ ] Cloudflare 账号访问权限
- [ ] 网络连接（需要代理则先配置 Clash/Shadowrocket）

### 备份位置
| 数据 | 位置 | 说明 |
|------|------|------|
| 加密备份包 | `github.com/neardws/homelab-secrets-backup` (私有) | 含所有 .env、config、SSH key、GPG key |
| Workspace | `github.com/neardws/clawd` (通过 Syncthing/Git) | MEMORY.md、skills、docs、系统快照 |
| OpenClaw 源码 | `github.com/clawdbot/clawdbot` | 公开仓库 |
| 系统状态快照 | `clawd/docs/system-state/` | 每日更新，含双系统完整配置 |
| GPG 私钥 | iPhone 备忘录 / iCloud Keychain | 解密备份包的钥匙 |

---

## 场景 A: Ubuntu Server 完全损毁

### 阶段一：基础环境 (30min)

```bash
# 1. 安装 Ubuntu 24.04 LTS，配置用户 neardws

# 2. 基础工具
sudo apt update && sudo apt install -y \
    git curl wget build-essential zsh jq htop tmux \
    python3 python3-pip python3-venv \
    apt-transport-https ca-certificates gnupg lsb-release

# 3. Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# 4. Node.js 22 (via nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
source ~/.bashrc
nvm install 22
npm install -g pnpm

# 5. Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# 重新登录生效

# 6. Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# 7. Bun
curl -fsSL https://bun.sh/install | bash

# 8. Clash 代理 (如需)
# 参考之前的 clash.service 配置
```

### 阶段二：恢复密钥和配置 (15min)

```bash
# 1. 恢复 GPG 密钥
# 从 iPhone 备忘录复制 GPG 私钥内容，保存为 gpg-key.asc
gpg --import gpg-key.asc
rm gpg-key.asc

# 2. 克隆备份仓库（用 HTTPS，SSH key 还没恢复）
git clone https://github.com/neardws/homelab-secrets-backup.git /tmp/backup
cd /tmp/backup

# 3. 解密最新的备份
LATEST=$(ls -t secrets-*.tar.gz.gpg | head -1)
mkdir -p /tmp/restore
gpg --decrypt "$LATEST" | tar xzf - -C /tmp/restore

# 4. 恢复 SSH key
mkdir -p ~/.ssh && chmod 700 ~/.ssh
cp /tmp/restore/keys/id_ed25519 ~/.ssh/
cp /tmp/restore/keys/id_ed25519.pub ~/.ssh/
chmod 600 ~/.ssh/id_ed25519
# 测试: ssh -T git@github.com

# 5. 恢复全局 .env
cp /tmp/restore/env-files/.env ~/

# 6. 恢复 API token
cp /tmp/restore/keys/.clawdbot-api-token ~/
```

### 阶段三：恢复 OpenClaw (30min)

```bash
# 1. 克隆源码
git clone https://github.com/clawdbot/clawdbot.git ~/clawdbot
cd ~/clawdbot
pnpm install
pnpm run build

# 2. 恢复 OpenClaw 配置
mkdir -p ~/.openclaw ~/.clawdbot
cp /tmp/restore/configs/openclaw.json ~/.openclaw/
cp /tmp/restore/configs/clawdbot.json ~/.clawdbot/
cp /tmp/restore/env-files/.openclaw/.env ~/.openclaw/

# 3. 恢复 workspace
git clone git@github.com:neardws/clawd.git ~/clawd
# 或从 Mac Mini Syncthing 同步

# 4. 安装 CLI
cd ~/clawdbot && npm link
# 或: ln -s ~/clawdbot/openclaw.mjs ~/.local/bin/clawdbot

# 5. 创建 systemd user service
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/openclaw-gateway.service << 'EOF'
[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/bin/node /home/neardws/clawdbot/dist/index.js gateway --port 18789
Restart=always
RestartSec=5
KillMode=process
EnvironmentFile=/home/neardws/.openclaw/.env
Environment=HOME=/home/neardws
Environment=OPENCLAW_GATEWAY_PORT=18789
Environment="NODE_OPTIONS=--use-env-proxy"
Environment="http_proxy=http://127.0.0.1:7890"
Environment="https_proxy=http://127.0.0.1:7890"
Environment="no_proxy=localhost,127.0.0.1,192.168.31.0/24"

[Install]
WantedBy=default.target
EOF

# 注意：OPENCLAW_GATEWAY_TOKEN 需要从备份的 openclaw.json 中提取
# 或重新生成后更新 Mac Mini node 的配置

systemctl --user daemon-reload
systemctl --user enable --now openclaw-gateway
# 验证
curl http://localhost:18789/health
```

### 阶段四：恢复 Cloudflare Tunnel (10min)

```bash
# 1. 安装 cloudflared
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt update && sudo apt install cloudflared

# 2. 恢复 tunnel 配置
sudo mkdir -p /etc/cloudflared
sudo cp /tmp/restore/configs/cloudflared-config.yml /etc/cloudflared/config.yml
sudo cp /tmp/restore/configs/ebf58727-*.json /etc/cloudflared/
sudo cp /tmp/restore/configs/489342da-*.json /etc/cloudflared/

# 3. 启动
sudo cloudflared service install
sudo systemctl enable --now cloudflared
# 验证
curl -I https://clawdbot.neardws.com  # 应返回 302
```

### 阶段五：恢复 Docker 服务 (15min)

```bash
# 恢复 User_Services (从 Git 或 Syncthing)
# 每个服务有自己的 docker-compose.yml

# MetaMCP
cd ~/User_Services/metamcp
cp /tmp/restore/env-files/User_Services/metamcp/.env .
docker compose up -d
# 端口: 12008-12010

# RSSHub
cd ~/User_Services/rsshub
docker compose up -d
# 端口: 1200

# DongguaTV
cd ~/User_Services/dongguaTV
docker compose up -d
# 端口: 8080

# NotebookLM MCP
cd ~/User_Services/notebooklm-mcp
docker compose up -d
# 端口: 3005, 6080

# AutoDL containers (按需)
# 参考 ~/AutoDL/ 下的配置
```

### 阶段六：恢复 Systemd 服务 (15min)

```bash
# Embedding Service
cd ~/User_Services/embedding
python3 -m venv venv
pip install -r requirements.txt
cp /tmp/restore/env-files/User_Services/embedding/.env .
# 恢复 /etc/systemd/system/embedding.service (参考 system-state 快照)
sudo systemctl enable --now embedding

# 其他自定义 systemd services:
# - axis-voice-http.service   → ~/User_Services 相关
# - clawd-voice.service       → ~/User_Services 相关
# - cliproxyapi.service       → ~/.config/systemd/user/
# - ft-agent.service
# - proxy-agent.service
# - worker-agent.service
# 参考 docs/system-state/ubuntu-services.txt 中的列表
```

### 阶段七：恢复 Cron Jobs (5min)

```bash
# 从快照恢复
crontab < ~/clawd/docs/system-state/ubuntu-crontab.txt

# 或手动添加核心 cron:
# */2 * * * *  邮件转发 (forward_coremail, auto_label_gmail, forward_qq)
# */30 * * * * self-heal.py
# 0 * * * *    info-monitor
# */5 * * * *  autodl-heartbeat
# */5 * * * *  healthchecks-ping (外部监控)
# 0 3 * * *    security-scan
# 30 3 * * *   system-snapshot
# 0 4 * * 0    secrets-backup (每周)
```

### 阶段八：恢复 .env 文件 (5min)

```bash
# 从解密的备份中恢复所有 .env 文件
cp /tmp/restore/env-files/User_Services/email-automation/.env ~/User_Services/email-automation/
cp /tmp/restore/env-files/User_Services/feishu/.env ~/User_Services/feishu/
cp /tmp/restore/env-files/User_Services/amap/.env ~/User_Services/amap/
cp /tmp/restore/env-files/User_Services/xai/.env ~/User_Services/xai/
cp /tmp/restore/env-files/User_Services/nano-banana/.env ~/User_Services/nano-banana/
cp /tmp/restore/env-files/User_Services/trello/.env ~/User_Services/trello/
cp /tmp/restore/env-files/User_Services/mac-remote/.env ~/User_Services/mac-remote/
# ... 其他 .env 参考 MANIFEST.txt
```

### 阶段九：验证 (15min)

```bash
# 1. Gateway
curl http://localhost:18789/health  # 200

# 2. Tunnel
curl -I https://clawdbot.neardws.com  # 302

# 3. Docker
docker ps  # 所有容器 Up

# 4. 各服务端口
for port in 8001 8080 12010 18789 1200; do
    echo "Port $port: $(curl -sf -o /dev/null -w '%{http_code}' http://localhost:$port/ 2>/dev/null || echo 'N/A')"
done

# 5. Discord 发消息测试 AI 回复

# 6. 心跳监控
bash ~/server-scripts/monitor/healthchecks-ping.sh  # 全部 OK

# 7. 清理
rm -rf /tmp/restore /tmp/backup
```

---

## 场景 B: Mac Mini M4 完全损毁

### 阶段一：基础环境 (20min)

```bash
# 1. macOS 初始设置，登录 Apple ID

# 2. Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/opt/homebrew/bin/brew shellenv)"

# 3. 从 Brewfile 恢复（或手动安装关键包）
# 核心工具:
brew install node pnpm jq bird imsg peekaboo remind remindctl \
    ical-buddy memo openai-whisper ffmpeg syncthing

# 4. Python
# macOS 自带 python3，额外需要:
brew install python@3.13
```

### 阶段二：恢复 OpenClaw Node (15min)

```bash
# 1. 安装 OpenClaw
pnpm install -g clawdbot

# 2. 配对到 Ubuntu Server
clawdbot pair
# 按提示输入 Ubuntu Gateway 地址: ws://192.168.31.211:18789
# 使用 token (从 Ubuntu 的 openclaw.json 获取)

# 3. 配置 launchd 自启动
# com.clawdbot.node plist 恢复
```

### 阶段三：恢复 MLX 服务 (15min)

```bash
# TTS (com.mlx.tts) → :5100
# ASR (com.mlx.asr) → :9001
# 恢复 launchd plist 并 launchctl load

# Syncthing
brew services start syncthing
# 配置共享文件夹: clawd-workspace
```

### 阶段四：恢复自动化 (10min)

```bash
# 恢复 cron (参考 docs/system-state/mac-crontab.txt)
crontab << 'EOF'
*/5 * * * * ~/.clawdbot/health-check.sh
*/5 * * * * ~/.clawdbot-backup/health-monitor.sh >> ~/.clawdbot-backup/monitor.log 2>&1
*/2 * * * * ~/.clawdbot/gateway-failover.sh >> ~/.clawdbot/failover.log 2>&1
*/5 * * * * ~/.clawdbot/healthchecks-ping.sh >> ~/.clawdbot/healthchecks.log 2>&1
EOF

# 恢复脚本文件
# health-check.sh, gateway-failover.sh, healthchecks-ping.sh
# 从 Syncthing 同步或 Git 获取
```

### 验证

```bash
# 1. Node 连接
# 在 Ubuntu 上: clawdbot nodes list → 应看到 Mac Mini M4

# 2. TTS
curl -X POST -F "text=测试" http://localhost:5100/tts -o /tmp/test.wav

# 3. 心跳
bash ~/.clawdbot/healthchecks-ping.sh
```

---

## 场景 C: 局域网全断 / 双系统同时挂

1. **Healthchecks.io 在 10 分钟内告警** → Email: neard.ws@gmail.com
2. **恢复优先级**: Ubuntu Server > Mac Mini
3. **临时替代方案**: 任意 VPS 装 OpenClaw + 恢复 `openclaw.json` 即可接管基础 AI 功能
4. **最小可用配置**: Node.js + OpenClaw + openclaw.json + .env → 就能跑 Gateway

---

## 📊 关键配置速查表

### Cloudflare Tunnel 映射

| 域名 | 目标 | 说明 |
|------|------|------|
| clawdbot.neardws.com | :18789 | OpenClaw Gateway (有 Access 保护) |
| mcp.neardws.com | :12010 | MetaMCP |
| embedding.neardws.com | :8001 | Embedding API |
| 1panel.neardws.com | :8888 | 1Panel |
| fish.neardws.com | :5000 | BettaFish |
| kanban.neardws.com | :3002 | Vibe Kanban |
| voice.neardws.com | :8766 | Voice HTTP |
| voicews.neardws.com | :8765 | Voice WebSocket |
| cliproxy.neardws.com | :8317 | CLI Proxy API |

### Docker Compose 位置

| 服务 | 路径 | 端口 |
|------|------|------|
| MetaMCP | `~/User_Services/metamcp/` | 12008-12010 |
| RSSHub | `~/User_Services/rsshub/` | 1200 |
| DongguaTV | `~/User_Services/dongguaTV/` | 8080 |
| NotebookLM MCP | `~/User_Services/notebooklm-mcp/` | 3005,6080 |

### Systemd 自定义服务

**系统级 (/etc/systemd/system/):**
- embedding.service — Embedding API (:8001)
- cloudflared.service — Cloudflare Tunnel
- axis-voice-http.service — 语音 HTTP
- clawd-voice.service — 语音 WebSocket
- clash.service — 代理 (:7890)

**用户级 (~/.config/systemd/user/):**
- openclaw-gateway.service — Gateway (:18789)
- cliproxyapi.service — CLI Proxy (:8317)
- openclaw-watchdog.service — 看门狗
- vibe-kanban.service — Kanban (:3002)

### Mac Mini Launchd 服务

| Label | 说明 |
|-------|------|
| com.clawdbot.node | OpenClaw Node 配对 |
| com.mlx.tts | Qwen3-TTS (:5100) |
| com.mlx.asr | Whisper ASR (:9001) |
| homebrew.mxcl.syncthing | 双向文件同步 |

---

## 🔑 GPG 密钥信息

- **指纹**: `F517A9E60C8192D70566D85A58717311F980700D`
- **邮箱**: `neard.ws@gmail.com`
- **算法**: RSA-4096, 永不过期
- **备份位置**: iPhone 备忘录 (需手动保存)

恢复命令:
```bash
gpg --import gpg-key.asc
gpg --decrypt secrets-YYYYMMDD.tar.gz.gpg | tar xzf - -C /tmp/restore
```

---

## ⏱️ 恢复时间预估

| 阶段 | Ubuntu | Mac Mini |
|------|--------|----------|
| 基础环境 | 30min | 20min |
| 密钥+配置恢复 | 15min | — |
| OpenClaw 核心 | 30min | 15min |
| Cloudflare Tunnel | 10min | — |
| Docker 服务 | 15min | — |
| Systemd 服务 | 15min | 15min |
| Cron + .env | 10min | 10min |
| 验证 | 15min | 10min |
| **总计** | **~2h** | **~1h** |

---

## 🔄 维护规则

1. **每次系统变更后**: 手动运行 `system-snapshot.sh` 或等每日自动执行
2. **新增 .env 文件**: 添加到 `secrets-backup.sh` 的 `ENV_FILES` 数组
3. **新增 systemd 服务**: 记录到本文档的速查表
4. **每季度**: 演练一次恢复流程（可用 Docker 模拟）
5. **GPG 密钥**: 确保 iPhone 备忘录中有最新版本

---

*本文件由 Axis 维护，每次系统变更时同步更新。*
