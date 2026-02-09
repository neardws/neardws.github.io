---
name: qwen3-tts
description: Generate speech using Qwen3-TTS on Mac Mini M4. Use for text-to-speech, voice synthesis, audio output.
homepage: https://github.com/QwenLM/Qwen3-TTS
metadata: {"clawdbot":{"emoji":"🎤"}}
---

# 🎤 Qwen3-TTS Voice Synthesis

TTS service running on Mac Mini M4 (MLX optimized).

## Service

- **URL**: http://192.168.31.114:5100
- **Host**: Mac Mini M4 Pro
- **Model**: Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/voices` | GET | List available voices |
| `/tts` | POST | Generate speech (form-data) |

## Quick Usage

### Generate Speech

```bash
curl -X POST -F "text=你好，很高兴认识你" -F "voice_id=wangyuan" \
  http://192.168.31.114:5100/tts -o output.wav
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| text | string | required | Text to synthesize |
| voice_id | string | "wangyuan" | Voice preset name |
| language | string | "zh-cn" | Language code |

## Available Voices

| Voice | Description |
|-------|-------------|
| wangyuan | 年轻中国男声，温暖柔和 |
| male_cn | 成熟中国男声，沉稳专业 |
| female_cn | 年轻中国女声，甜美活力 |
| default | 自然中文声音 |

## Clawdbot Integration

```python
import requests

def tts(text, voice="wangyuan", output_path="/tmp/tts_output.wav"):
    resp = requests.post(
        "http://192.168.31.114:5100/tts",
        data={"text": text, "voice_id": voice},
        timeout=120
    )
    if resp.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return output_path
    return None
```

## Service Management (Mac Mini SSH)

```bash
# Check status
ssh neardws@192.168.31.114 "launchctl list | grep mlx"

# View logs
ssh neardws@192.168.31.114 "tail -f ~/Services/mlx-audio/logs/tts.log"

# Restart
ssh neardws@192.168.31.114 "launchctl unload ~/Library/LaunchAgents/com.mlx.tts.plist && launchctl load ~/Library/LaunchAgents/com.mlx.tts.plist"
```
