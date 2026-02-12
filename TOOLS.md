# TOOLS.md - Local Notes

*Environment-specific configurations.*

---

## Qwen3-TTS (Mac Mini)
- **Service**: http://192.168.31.114:5100
- **Voices**: wangyuan, male_cn, female_cn, default
- **Usage**: `curl -X POST -F "text=..." -F "voice_id=wangyuan" http://192.168.31.114:5100/tts -o out.wav`

---

## Remote macOS (Mac Mini M4)
- **SSH**: neardws@192.168.31.114
- **Homebrew**: /opt/homebrew/bin/brew
- **Tools**: imsg, bird, notebooklm, apple-notes/reminders, bear-notes, things-mac, peekaboo

---

## Syncthing
| Host | API | Device ID |
|------|-----|-----------|
| Ubuntu | http://127.0.0.1:8384, Key: `mzkb...` | SYDLVOG-... |
| Mac Mini | http://127.0.0.1:8384, Key: `bThE...` | 5ZNDMYY-... |

**Shared**: `clawd-workspace` (Ubuntu `/home/neardws/clawd` ↔ Mac Mini `~/ObsidianVault/clawd`)

---

## Defaults
- **Weather location**: 深圳龙华
- **Logs folder**: `~/User_Services/services-logs`
- **Service docs**: `XXX_SERVICE.md`

---

## Principles
- **优先本地服务**: 部署前检查 `systemctl` / `docker ps`
- **不要重复造轮子**: 有现成直接用
- **TTS 用 Mac Mini**: `192.168.31.114:5100`

---

*Add whatever helps you do your job. This is your cheat sheet.*
