# Infrastructure Reference

Complete infrastructure and service documentation.

---

## Ubuntu Server (Main)

| Directory | Purpose |
|-----------|---------|
| `~/clawd/` | Clawdbot workspace |
| `~/clawdbot/` | Clawdbot source |
| `~/github/` | Project repos |
| `~/User_Services/` | Services |
| `~/server-scripts/` | Backup/deploy/monitor |
| `~/AutoDL/` | AutoDL config |
| `~/nas_mount/` | NAS mount |

---

## Mac Mini M4 (Remote Node)

- **SSH**: neardws@192.168.31.114
- **Hostname**: neardwsdeMac-mini.local
- **Spec**: M4 Pro 12-core, 64GB RAM, macOS 26.2
- **Homebrew**: /opt/homebrew/bin/brew

### Available Remote Tools
- `imsg` — iMessage CLI
- `bird` — X/Twitter CLI
- `notebooklm` — NotebookLM automation
- `apple-notes` — Apple Notes
- `apple-reminders` — Apple Reminders
- `bear-notes` — Bear Notes
- `things-mac` — Things 3
- `model-usage` — CodexBar usage
- `peekaboo` — GUI automation

---

## Services & Ports

| Service | Port | Notes |
|---------|------|-------|
| Clash Proxy | 7890-7892 | |
| 1Panel | 8888 | |
| dongguatv | 8080 | |
| Clawdbot Gateway | 18789 | Main gateway |
| MetaMCP | 12010 | |
| Embedding | 8001 | |
| TTS (Mac Mini) | 5100 | Qwen3-TTS |
| ASR (Mac Mini) | 9001 | whisper-large-v3 |
| Syncthing Ubuntu | 8384/22000 | |
| Syncthing Mac | 8384/22000 | |
| BotDrop (Pixel 9) | 8022 | SSH + Gateway |

---

## Cloudflare Tunnels

| Domain | Target |
|--------|--------|
| clawdbot.neardws.com | 18789 |
| mcp.neardws.com | 12010 |
| 1panel.neardws.com | 8888 |
| embedding.neardws.com | 8001 |

---

## BotDrop / ClawPhone (Pixel 9 Pro XL)

- **IP**: 192.168.31.87:8022
- **Host**: Mac Mini M4 (USB-C)
- **Root**: Magisk authorized
- **AutoJs6**: Installed + accessibility

**Automations:**
- ✅ X/Twitter — Full
- ✅ SMS — Full
- ⚠️ WeChat — Requires AutoJs6 accessibility

---

## Syncthing

### Ubuntu
```bash
systemctl --user status syncthing
API: http://127.0.0.1:8384
Key: mzkbZi6SVvduf52JeUo3ZfUtm7a4uzbJ
Device: SYDLVOG-SN6EHAM-I6GCFVM-KTI5H3Y-2UNLLTF-LAOEPHI-7WXJ7TQ-6MNJLQD
```

### Mac Mini
```bash
brew services info syncthing
API: http://127.0.0.1:8384
Key: bThE5WJTEVrgYnjFuogChEGy3DnUWH2m
Device: 5ZNDMYY-WNTQ3VL-ZDV3XXE-SSC6HYM-KLBFKCD-IUZUHGF-BGRXGOV-SVPQVQZ
```

**Shared folder** `clawd-workspace`:
- Ubuntu: `/home/neardws/clawd`
- Mac: `/Users/neardws/ObsidianVault/clawd`

---

## Obsidian

- **Mac Mini**: `/Applications/Obsidian.app` (v1.11.7)
- **Vault**: `~/ObsidianVault/`
- **Synced**: Includes `clawd` workspace via Syncthing

---

## Development Tools

- nvm (Node.js)
- cargo/rustup (Rust)
- rbenv (Ruby)
- bun
- oh-my-zsh
- fzf

---

## User Services

```
~/User_Services/
├── qwen3-tts
├── vllm
├── embedding
├── telegram-notifier
├── clawd-voice-web
├── email-automation
├── feishu
├── notebooklm-mcp
└── services-logs
```

---

## GitHub Projects

```
~/github/
├── HARL (RL)
├── paper-monitor
├── happy-cli/server
├── ai-quant-trading
├── vibe-kanban
├── social-publisher
└── zotero-library
```

---

## Troubleshooting

### OpenClaw Binding Changes
Modifying bindings requires Gateway restart. Session files cache old routes.

### TTS Voices
- skywalker (Neil voice clone)
- wangyuan, wangyuan_v2-v6

---

*Last updated: 2026-02-12*
