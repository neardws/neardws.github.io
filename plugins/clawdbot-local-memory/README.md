# Local Memory Plugin for Clawdbot

Supermemory-style local memory system. Auto-captures and recalls relevant context without cloud dependencies.

## Features

- **Auto-Recall**: Injects relevant memories before each AI turn
- **Auto-Capture**: Extracts facts from conversations automatically
- **User Profile**: Builds persistent + dynamic user context
- **Local Storage**: All data stays on your machine

## Install

```bash
# From workspace
cd /path/to/workspace/plugins/clawdbot-local-memory
npm install && npm run build

# Enable in clawdbot.json
```

## Configuration

```json
{
  "plugins": {
    "entries": {
      "clawdbot-local-memory": {
        "enabled": true,
        "config": {
          "autoRecall": true,
          "autoCapture": true,
          "maxRecallResults": 10,
          "profileFrequency": 50,
          "debug": false
        }
      }
    }
  }
}
```

## Commands

| Command | Description |
|---------|-------------|
| `/remember <text>` | Save to memory |
| `/recall <query>` | Search memories |

## CLI

```bash
clawdbot local-memory search <query>
clawdbot local-memory profile
clawdbot local-memory stats
clawdbot local-memory wipe --yes
```

## AI Tools

- `local_memory_store` - Save to memory
- `local_memory_search` - Search memories
- `local_memory_forget` - Delete memory
- `local_memory_profile` - View profile
