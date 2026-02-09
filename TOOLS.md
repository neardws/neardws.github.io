# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod

### Defaults
- Default weather location: 深圳龙华
- Logs folder: ~/User_Services/services-logs

### Remote macOS
- mac-lan → neardws@192.168.31.114 (SSH)
  - **Hostname**: neardwsdeMac-mini.local
  - **Hardware**: Mac mini (Mac16,11) - Apple M4 Pro
  - **CPU**: 12 cores (8P + 4E)
  - **Memory**: 64 GB
  - **Storage**: 460 GB (401 GB free)
  - **macOS**: 26.2 (Build 25C56)
  - **Homebrew**: /opt/homebrew/bin/brew
  - **Python**: /usr/bin/python3 (3.9.6)
  - **Proxy**: 通过服务器 192.168.31.211:7890
  - **Supports**: imsg, bird, notebooklm, apple-notes, apple-reminders, bear-notes, things-mac, model-usage, peekaboo
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### Qwen3-TTS (Mac Mini MLX)
- **Service**: http://192.168.31.114:5100
- **Host**: Mac Mini M4 Pro (launchd: com.mlx.tts)
- **Model**: Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16
- **Available voices**: wangyuan, male_cn, female_cn, default
- **Usage**: 
  ```bash
  curl -X POST -F "text=要说的话" -F "voice_id=wangyuan" \
    http://192.168.31.114:5100/tts -o output.wav
  ```

---

Add whatever helps you do your job. This is your cheat sheet.

---

### 复杂任务处理规范
- **前后端开发等复杂任务**：先做整体规划，然后调用 coding agent (droid/Joyce) 分别处理
- **并行开发**：前端、后端可以分开让 coding agent 并行处理
- **工作流**：规划 → 拆分任务 → 调用 coding agent → 整合结果

### Syncthing (双向文件同步)
- **Ubuntu**: systemd user service (`systemctl --user status syncthing`)
  - API: http://127.0.0.1:8384, Key: `mzkbZi6SVvduf52JeUo3ZfUtm7a4uzbJ`
  - Device ID: `SYDLVOG-SN6EHAM-I6GCFVM-KTI5H3Y-2UNLLTF-LAOEPHI-7WXJ7TQ-6MNJLQD`
- **Mac Mini**: brew services (`brew services info syncthing`)
  - API: http://127.0.0.1:8384, Key: `bThE5WJTEVrgYnjFuogChEGy3DnUWH2m`
  - Device ID: `5ZNDMYY-WNTQ3VL-ZDV3XXE-SSC6HYM-KLBFKCD-IUZUHGF-BGRXGOV-SVPQVQZ`
- **共享文件夹** `clawd-workspace`:
  - Ubuntu `/home/neardws/clawd` ↔ Mac Mini `/Users/neardws/ObsidianVault/clawd`
  - 双向同步, fsWatcher 启用

### Obsidian
- Mac Mini: `/Applications/Obsidian.app` (v1.11.7, brew cask)
- Vault 路径: `~/ObsidianVault/` (含 Syncthing 同步的 clawd workspace)

### 服务部署原则
- **优先本地服务**：部署任何服务/模型前，先查看本地已有服务（如 systemctl、docker ps）
- **不要重复造轮子**：已有的服务直接用，不要自己去找外部替代
- **TTS 用 Mac Mini**：语音合成用 `192.168.31.114:5100`，wangyuan 音色
