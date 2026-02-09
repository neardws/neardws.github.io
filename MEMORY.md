# MEMORY.md - Long-term Memory

*Curated knowledge about Neil and the system. QMD indexes this file for semantic search.*

---

## 👤 About Neil

### Identity
- **全名**: 许新操 (Xincao Xu)
- **职业**: 电子科技大学深圳高等研究院副研究员
- **研究方向**: 边缘智能 (Edge Intelligence)、智能体AI、智能体强化学习
- **学历**: 2023年重庆大学计算机博士毕业
- **荣誉**: 2025年获亚太认知智能学会优秀博士论文奖，发表15+篇论文(IEEE T-ITS/ComMag/TMC等)，主持广东省基金和中国博士后基金项目

### Contact
- **GitHub**: neardws
- **X/Twitter**: @neard_ws
- **微信**: 15595714795
- **Gmail**: neard.ws@gmail.com (主邮箱)
- **学校邮箱**: xc.xu@uestc.edu.cn
- **QQ邮箱**: neardws@qq.com

### Location
- **工作地点**: 深圳龙华

---

## 🎯 Preferences

### Communication
- 回复语言偏好：中英混合
- 通知渠道偏好：Telegram 优先

### Interests
- **音乐**: 喜欢王源(Roy Wang)的音乐
- **电影**: 《白日梦想家》《请以你的名字呼唤我》《发条橙》等
- **运动**: Apple Fitness+用户，2024重庆半马PB 3:05:06，喜欢骑行和定向越野
- **游戏**: Nintendo Switch(塞尔达/马车/Splatoon)、PS5(最后生还者/FF7/底特律变人/奇异人生)、Steam Deck

### Tech Gear
- Apple Vision Pro
- MacBook Pro M3 Pro
- iPhone 15 Pro Max
- Apple Watch Ultra 2
- Sennheiser IE 600
- A&K SE300播放器

---

## 🤖 Agent Operating Rules

### Sub-agent Delegation
- **编程开发** → Droid 交互式 (Claude Code)
- **搜索/事实核查** → Grok (`GrokCheck` alias)
- **批量文本处理** → MiniMax (`cheap` alias)
- **复杂规划** → `droid exec` (Opus model)
- **主代理角色**: 项目经理，只看摘要、监督执行、汇报结果，不亲自写代码

### Planning Rule
For any planning/roadmap/complex multi-step request, generate the plan via local `droid exec` (read-only by default) using model `claude-opus-4-5-20251101`, then execute with main model.

### Automation Boundaries
- ✅ 可以直接操作 Docker/服务（run/rebuild/pause）和写配置文件
- ⚠️ 破坏性删除或公开暴露前需要先询问

### Service Management
- 服务日志统一放在 `~/User_Services/services-logs` 目录下
- 服务文档命名规范：使用 `XXX_SERVICE.md` 格式
- 端口操作前必须先查阅 Services Log 项目确认端口可用性

---

## 🖥️ Infrastructure

### Ubuntu Server (Main)
- **工作空间**: `~/clawd/` (Clawdbot workspace)
- **源码目录**: `~/clawdbot/` (Clawdbot source)
- **项目仓库**: `~/github/`
- **服务目录**: `~/User_Services/`
- **脚本目录**: `~/server-scripts/` (backup/deploy/monitor/utils)
- **AutoDL配置**: `~/AutoDL/`
- **NAS挂载点**: `~/nas_mount/`

### Mac Mini M4 (Remote Node)
- **地址**: neardws@192.168.31.114
- **Hostname**: neardwsdeMac-mini.local
- **配置**: M4 Pro 12核, 64GB RAM, macOS 26.2
- **Homebrew**: /opt/homebrew/bin/brew

#### Available Remote Tools
- `imsg` - iMessage CLI (/opt/homebrew/bin/imsg)
- `bird` - X/Twitter CLI (/opt/homebrew/bin/bird)
- `notebooklm` - NotebookLM automation
- `apple-notes` - Apple Notes
- `apple-reminders` - Apple Reminders
- `bear-notes` - Bear Notes
- `things-mac` - Things 3
- `model-usage` - CodexBar usage stats
- `peekaboo` - GUI automation

#### macOS Skill Pattern
For macOS-only skills, implement via "remote-macos proxy skill" approach (execute on LAN macOS host over SSH), rather than trying to run macOS-only binaries on Linux.

### Services & Ports

| Service | Port | Notes |
|---------|------|-------|
| Clash Proxy | 7890-7892 | |
| 1Panel | 8888 | |
| dongguatv | 8080 | |
| Clawdbot Gateway | 18789 | |
| MetaMCP | 12010 | |
| Embedding | 8001 | |
| TTS (Mac Mini) | 5100 | Qwen3-TTS-1.7B-VoiceDesign |
| ASR (Mac Mini) | 9001 | whisper-large-v3-mlx |
| Syncthing (Ubuntu) | 8384/22000 | Web GUI + sync protocol |
| Syncthing (Mac Mini) | 8384/22000 | Web GUI + sync protocol |

### Cloudflare Tunnels
- clawdbot.neardws.com → 18789
- mcp.neardws.com → 12010
- 1panel.neardws.com → 8888
- embedding.neardws.com → 8001

### Development Tools
- nvm (Node.js)
- cargo/rustup (Rust)
- rbenv (Ruby)
- bun
- oh-my-zsh
- fzf

---

## 📧 Email & Identity

### Axis (AI Assistant)
- **邮箱**: axis-ai@agentmail.to (AgentMail)
- **显示名**: Axis ⚡
- **创建日期**: 2026-02-04

### API Keys (Reference Only)
- ClawHub API Key: `clh_bI-wBTM8qQFI2UtPDUMkM2b_zpIjl52BdPw5MymMtAE`

---

## 🔧 Troubleshooting Notes

### OpenClaw Binding Changes
修改 bindings 配置后需要重启 Gateway 才能生效。已有 session 会缓存旧的 agent 路由，删除 session 文件无效（会重建）。**解决方案：重启 Gateway 进程。**

### TTS Voice Preference
Neil 想克隆王源的音色用于 TTS。当前可用音色：skywalker(Neil声音克隆), wangyuan, wangyuan_v2-v6

---

## 📁 Project Directories

### ~/User_Services/
- qwen3-tts
- vllm
- embedding
- telegram-notifier
- clawd-voice-web
- email-automation
- feishu
- notebooklm-mcp
- services-logs

### ~/github/
- HARL (强化学习)
- paper-monitor
- happy-cli/server
- ai-quant-trading
- vibe-kanban
- social-publisher
- zotero-library

---

*Last migrated from local-memory.json: 2026-02-07*
