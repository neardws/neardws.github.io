# API Key Inventory

> Generated: 2026-02-10  
> Tool Reference: https://github.com/chekusu/shipkey

## Overview

This document catalogs all API keys and credentials used across the OpenClaw/Clawdbot infrastructure.

**Storage Status:**
- ✅ Stored in 1Password
- ⚠️ Stored in config file (encrypted at rest)
- 🔴 Needs migration
- ❌ Public/No key required

---

## Model Provider Keys

| Provider | Key Name | Purpose | Storage | Notes |
|----------|----------|---------|---------|-------|
| **xAI** | `XAI_API_KEY` | Grok models (Grok 2/3/4) | ⚠️ openclaw.json | Required for GrokCheck alias |
| **MiniMax** | `MINIMAX_API_KEY` | MiniMax M2.1 models | ⚠️ openclaw.json | Used for "cheap" alias |
| **Kimi** | `KIMI_API_KEY` | Kimi K2.5 models | ⚠️ openclaw.json | 256K context support |
| **AI CodeMirror** | `AICODEMIRROR_KEY` | Claude Opus 4.6 | ⚠️ openclaw.json | Mirror service |
| **NewCLI** | `NEWCLI_KEY` | Claude Opus 4.5 | ⚠️ openclaw.json | Planning agent |
| **Quotio** | `QUOTIO_KEY` | Local LLM proxy | ⚠️ openclaw.json | Mac Mini 192.168.31.114:18080 |
| **AI CodeMirror Codex** | `AICODEMIRROR_CODEX_KEY` | GPT-5.3 Codex | ⚠️ openclaw.json | OpenAI responses API |
| **ZenMux** | `ZENMUX_API_KEY` | Claude Opus 4.6 | ⚠️ openclaw.json | 1M context window |
| **Voyage AI** | `VOYAGE_API_KEY` | Embeddings | ⚠️ openclaw.json | voyage-4-lite model |
| **OpenRouter** | `OPENROUTER_API_KEY` | Pony Alpha, Free router | ⚠️ openclaw.json | Added 2026-02-09 |

---

## Service Keys

| Service | Key Name | Purpose | Storage | Notes |
|---------|----------|---------|---------|-------|
| **Brave Search** | `BRAVE_API_KEY` | Web search | ⚠️ openclaw.json | Used by web_search tool |
| **Nano Banana Pro** | `NANO_BANANA_KEY` | Image generation | ⚠️ openclaw.json | Gemini 3 Pro Image |

---

## Messaging Platform Keys

### Discord
| Key | Value | Storage |
|-----|-------|---------|
| Bot Token | `__OPENCLAW_REDACTED__` | ⚠️ openclaw.json |
| Gateway Token | `__OPENCLAW_REDACTED__` | ⚠️ openclaw.json |

### Telegram
| Key | Value | Storage |
|-----|-------|---------|
| Bot Token | `__OPENCLAW_REDACTED__` | ⚠️ openclaw.json |

### Feishu (Lark)
| Key | Value | Storage |
|-----|-------|---------|
| App ID | `cli_a9ff2a77faf8dbc4` | ⚠️ openclaw.json (unencrypted) |
| App Secret | `__OPENCLAW_REDACTED__` | ⚠️ openclaw.json |

---

## Gateway & Infrastructure

| Component | Key | Purpose | Storage |
|-----------|-----|---------|---------|
| OpenClaw Gateway | `GATEWAY_TOKEN` | API authentication | ⚠️ openclaw.json |
| Tailscale | (not configured) | VPN mesh | N/A |

---

## Security Issues Found

### 🔴 Hardcoded Key in Script

**Location:** `/home/neardws/clawd/skills/tmux-agents/scripts/spawn.sh`

```bash
ANTHROPIC_API_KEY='sk-cp-kqO98wO1Vu2yl9rDGj63JNLaAVZYN6Ru2xKWnsdU6OLdDX5sRNw2yzwqicx5Bz6QFBQjqMW3aPoILeDql0UsK3WUxi7kaLEUzt_nwv-ebdk7wtgJf5o1TZk'
```

**Risk:** Medium - This is a MiniMax API key embedded directly in the spawn script for the `opencode` agent.

**Recommendation:** 
- [ ] Extract to environment variable or 1Password
- [ ] Rotate this key immediately
- [ ] Use `op run` or similar to inject at runtime

---

## External Services (User_Services .env files)

| Service | Key | Location | Status |
|---------|-----|----------|--------|
| **Amap (高德地图)** | `AMAP_API_KEY` | `amap/.env` | ⚠️ Separate file |
| **AutoFigure Edit** | `OPENROUTER_API_KEY` | `autofigure-edit/.env` | ⚠️ Duplicate |
| **Email Automation** | `DEEPSEEK_API_KEY` | `email-automation/.env` | ⚠️ Separate file |
| **Email Automation** | `EMBEDDING_API_KEY` | `email-automation/.env` | ⚠️ Separate file |
| **Embedding Service** | `GOOGLE_API_KEY` | `embedding/.env` | ⚠️ Separate file |
| **Embedding Service** | `API_KEY` | `embedding/.env` | ⚠️ Generic name |
| **Feishu** | `FEISHU_APP_ID` | `feishu/.env` | ⚠️ Duplicate |
| **Feishu** | `FEISHU_APP_SECRET` | `feishu/.env` | ⚠️ Duplicate |
| **Mac Remote** | `MAC_USER` | `mac-remote/.env` | ❌ Not a secret |
| **Mac Remote** | `MAC_HOST` | `mac-remote/.env` | ❌ Not a secret |
| **MetaMCP** | `POSTGRES_PASSWORD` | `metamcp/.env` | ⚠️ DB credentials |
| **MetaMCP** | `DATABASE_URL` | `metamcp/.env` | 🔴 Contains password |
| **MetaMCP** | `BETTER_AUTH_SECRET` | `metamcp/.env` | ⚠️ Auth secret |
| **MetaMCP** | `ADMIN_API_KEY` | `metamcp/.env` | ⚠️ API key |
| **Nano Banana** | `GEMINI_API_KEY` | `nano-banana/.env` | ⚠️ Duplicate |
| **Trello** | `TRELLO_API_KEY` | `trello/.env` | ⚠️ Separate file |
| **Trello** | `TRELLO_TOKEN` | `trello/.env` | ⚠️ Separate file |
| **xAI** | `XAI_API_KEY` | `xai/.env` | ⚠️ Duplicate |

### ⚠️ Key Duplication Detected

The following keys appear in **both** `openclaw.json` and individual `.env` files:

- `OPENROUTER_API_KEY` - autofigure-edit/.env
- `FEISHU_APP_ID` / `FEISHU_APP_SECRET` - feishu/.env
- `GEMINI_API_KEY` / `NANO_BANANA_KEY` - nano-banana/.env (likely same)
- `XAI_API_KEY` - xai/.env

**Recommendation:** Consolidate all keys to 1Password to avoid drift.

---

## External Services (Other)

These services likely have credentials elsewhere:

| Service | Location | Status |
|---------|----------|--------|
| **GitHub** | `~/.config/gh/` | OAuth via gh CLI |
| **1Password** | `op` CLI | Manual auth |
| **Cloudflare** | Unknown | Tunnels configured |
| **Syncthing** | `~/.config/syncthing/` | Local API key |

---

## Key Rotation Schedule

| Provider | Last Rotated | Rotate Every | Next Rotation |
|----------|-------------|--------------|---------------|
| OpenRouter | 2026-02-09 | 90 days | 2026-05-10 |
| Discord | Unknown | 180 days | Unknown |
| Telegram | Unknown | 180 days | Unknown |
| Feishu | Unknown | 90 days | Unknown |

---

## Migration to 1Password

Using shipkey pattern:

```json
{
  "project": "clawdbot",
  "vault": "clawdbot-keys",
  "providers": {
    "xai": {
      "fields": ["XAI_API_KEY"]
    },
    "minimax": {
      "fields": ["MINIMAX_API_KEY"]
    },
    "kimi": {
      "fields": ["KIMI_API_KEY"]
    },
    "aicodemirror": {
      "fields": ["AICODEMIRROR_KEY", "AICODEMIRROR_CODEX_KEY"]
    },
    "newcli": {
      "fields": ["NEWCLI_KEY"]
    },
    "quotio": {
      "fields": ["QUOTIO_KEY"]
    },
    "zenmux": {
      "fields": ["ZENMUX_API_KEY"]
    },
    "voyage": {
      "fields": ["VOYAGE_API_KEY"]
    },
    "openrouter": {
      "fields": ["OPENROUTER_API_KEY"]
    },
    "brave": {
      "fields": ["BRAVE_API_KEY"]
    },
    "discord": {
      "fields": ["DISCORD_BOT_TOKEN"]
    },
    "telegram": {
      "fields": ["TELEGRAM_BOT_TOKEN"]
    },
    "feishu": {
      "fields": ["FEISHU_APP_ID", "FEISHU_APP_SECRET"]
    }
  }
}
```

### 1Password Storage Path

```
op://clawdbot-keys/xai/clawdbot/XAI_API_KEY
op://clawdbot-keys/minimax/clawdbot/MINIMAX_API_KEY
op://clawdbot-keys/kimi/clawdbot/KIMI_API_KEY
op://clawdbot-keys/aicodemirror/clawdbot/AICODEMIRROR_KEY
op://clawdbot-keys/newcli/clawdbot/NEWCLI_KEY
op://clawdbot-keys/quotio/clawdbot/QUOTIO_KEY
op://clawdbot-keys/zenmux/clawdbot/ZENMUX_API_KEY
op://clawdbot-keys/voyage/clawdbot/VOYAGE_API_KEY
op://clawdbot-keys/openrouter/clawdbot/OPENROUTER_API_KEY
op://clawdbot-keys/brave/clawdbot/BRAVE_API_KEY
op://clawdbot-keys/discord/clawdbot/DISCORD_BOT_TOKEN
op://clawdbot-keys/telegram/clawdbot/TELEGRAM_BOT_TOKEN
op://clawdbot-keys/feishu/clawdbot/FEISHU_APP_SECRET
```

---

## Summary Statistics

| Category | Count |
|----------|-------|
| **Model Providers** | 10 |
| **Service Keys** | 2 |
| **Messaging Platforms** | 3 |
| **User Services** | 18 |
| **Infrastructure** | 1 |
| **Hardcoded (🚨)** | 1 |
| **Total** | **35** |

### Storage Distribution

- 🔴 **Hardcoded in scripts:** 1 key (MiniMax in spawn.sh)
- ⚠️ **Scattered .env files:** 18 keys across 8 services
- ⚠️ **OpenClaw config:** ~15 keys
- ❌ **Not tracked:** Unknown

### Risk Assessment

| Risk Level | Count | Items |
|------------|-------|-------|
| 🔴 **High** | 1 | Hardcoded MiniMax key in spawn.sh |
| 🟡 **Medium** | 18 | Keys in scattered .env files |
| 🟢 **Low** | 15 | Keys in encrypted openclaw.json |

---

## Action Items (Prioritized)

### 🔴 Immediate (This Week)
- [ ] **Rotate hardcoded MiniMax key** in `spawn.sh`
- [ ] Extract MiniMax key to environment variable or 1Password
- [ ] Set up 1Password vault `clawdbot-keys`

### 🟡 Short-term (Next 2 Weeks)
- [ ] Install shipkey: `curl -fsSL https://shipkey.dev/install.sh | bash`
- [ ] Migrate all keys from `.env` files to 1Password
- [ ] Migrate all keys from `openclaw.json` to 1Password
- [ ] Create `.env.local` templates that use `op://` references
- [ ] Set up key rotation schedule

### 🟢 Long-term (Next Month)
- [ ] Audit key permissions/scopes for each provider
- [ ] Set up automated key rotation where possible
- [ ] Document key usage per service
- [ ] Set up monitoring for key usage/abuse

---

## Migration Plan (shipkey-style)

### Phase 1: Setup
```bash
# Install shipkey
curl -fsSL https://shipkey.dev/install.sh | bash

# Create 1Password vault
op vault create clawdbot-keys

# Authenticate
op signin
```

### Phase 2: Migrate Keys
```bash
# For each key in KEYS.md:
op item create --vault=clawdbot-keys \
  --category=login \
  --title="xAI API Key" \
  --field="api_key=$XAI_API_KEY"
```

### Phase 3: Update Configs
Replace all keys with 1Password references:

```bash
# openclaw.json
# Before: "apiKey": "sk-xxx..."
# After:  "apiKey": "op://clawdbot-keys/xai/clawdbot/XAI_API_KEY"

# .env files
# Before: XAI_API_KEY=sk-xxx...
# After:  XAI_API_KEY=op://clawdbot-keys/xai/clawdbot/XAI_API_KEY
```

### Phase 4: Pull on New Machines
```bash
# On a new machine
shipkey pull
# Generates .env files with resolved values
```

---

## Security Notes

1. **Config file encryption**: `openclaw.json` is encrypted at rest via OpenClaw's built-in encryption
2. **Key exposure**: Never commit this file (KEYS.md) to git
3. **Rotation**: Keys posted in Discord channels should be rotated immediately
4. **Local keys**: Quotio key is local-only (Mac Mini), low risk
5. **GitHub**: Ensure `.env` files are in `.gitignore`

---

## Related Tools

- **shipkey**: https://github.com/chekusu/shipkey - Scan, backup, sync API keys with 1Password
- **1Password CLI**: `op` command for scripting
- **truffleHog**: Scan git history for leaked secrets
- **git-secrets**: Prevent committing secrets to git

