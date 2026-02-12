# MEMORY.md - Long-term Memory
*Curated knowledge about Neil and the system. QMD indexes this file for semantic search.*

---

## 👤 Neil (许新操)
- **职业**: 电子科技大学深圳高等研究院副研究员
- **方向**: 边缘智能、智能体AI、强化学习
- **学历**: 2023重庆大学计算机博士
- **荣誉**: 2025亚太认知智能学会优秀博士论文奖
- **位置**: 深圳龙华

**联系方式**: GitHub: neardws | X: @neard_ws | 主邮箱: neard.ws@gmail.com | 微信: 15595714795

**偏好**: 中英混合回复 | Telegram 优先通知

**兴趣**: 王源音乐 | 《白日梦想家》等电影 | Apple Fitness+ | Switch/PS5/Steam Deck | 2024重庆半马PB 3:05:06

**设备**: Vision Pro, MacBook Pro M3 Pro, iPhone 15 Pro Max, Apple Watch Ultra 2, Sennheiser IE 600

---

## 🤖 Agent 配置速查
| Agent | 启动方式 | 用途 |
|-------|---------|------|
| **Droid** | `./skills/tmux-agents/scripts/spawn.sh <s> "<t>" droid` | 复杂编程 |
| **Claude Code** | `./scripts/spawn.sh <s> "<t>" claude` | 编程 (v2.1.9) |
| **Codex CLI** | `codex -m foxcode-gpt-5.3-codex` | Debug (v0.98.0) |

**子代理委托**: 编程→Droid | 搜索→Grok (`GrokCheck`) | 批量→MiniMax (`cheap`) | 长文档→Kimi K2.5

**API 限制**: 当前 Key 无法访问 `foxcode-*`，可用 `claude-opus-4-6` / `claude-opus-4-5-20251101` / `claude-sonnet-4-5-20251001`

> 详细配置: `docs/agent-setup.md`

---

## 🖥️ 基础设施速查

### Ubuntu Server
- **Workspace**: `~/clawd/`
- **源码**: `~/clawdbot/`
- **服务**: `~/User_Services/` | 日志: `~/User_Services/services-logs`

### Mac Mini M4 (192.168.31.114)
- **远程工具**: imsg, bird, notebooklm, apple-notes/reminders, bear-notes, things-mac, peekaboo
- **TTS**: http://192.168.31.114:5100 (wangyuan 音色)
- **ASR**: http://192.168.31.114:9001

### 核心服务端口
| 服务 | 端口 | 说明 |
|------|------|------|
| Clawdbot Gateway | 18789 | 主网关 |
| MetaMCP | 12010 | MCP 服务 |
| Embedding | 8001 | 向量服务 |
| TTS | 5100 | Mac Mini |
| ASR | 9001 | Mac Mini |

### 云隧道 (Cloudflare)
- clawdbot.neardws.com → 18789
- mcp.neardws.com → 12010

> 完整端口列表: `docs/infrastructure.md`

---

## 📐 项目规则
- **所有项目必须用 Git**（无论是否 GitHub）
- **操作边界**: ✅ Docker/服务操作 | ⚠️ 破坏性删除前询问
- **服务文档命名**: `XXX_SERVICE.md`

---

## 🔧 已知问题
- **Binding 变更需重启**: 修改 bindings 配置后需重启 Gateway
- **TTS 音色**: 可用 wangyuan, skywalker(Neil克隆)

---

*Axis (AI Assistant) - 邮箱: axis-ai@agentmail.to - 创建于 2026-02-04*
