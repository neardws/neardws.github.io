# Shipkey Key Management Setup

## ✅ Completed

### 1. Extracted 31 API Keys

All keys from the following sources have been extracted and stored:

**From openclaw.json (17 keys):**
- xAI, MiniMax, Kimi, AI CodeMirror (2), NewCLI, Quotio, ZenMux, Voyage, OpenRouter
- Brave Search, Gemini (Nano Banana)
- Discord, Telegram, Feishu, OpenClaw Gateway

**From User_Services .env files (14 keys):**
- Trello, Email Automation (DeepSeek, Embedding), AutoFigure Edit
- Amap (高德地图), Embedding (Google), Nano Banana (Gemini)
- xAI (duplicate), Feishu (duplicate)
- MetaMCP (Postgres, Auth secrets)

### 2. Storage Location

```
~/.config/shipkey-local/keys.json
```

This file is:
- ✅ Excluded from git (added to .gitignore)
- ✅ Located outside project directory
- ⚠️ **Not encrypted yet** - see security notes below

### 3. Generated Files

| File | Purpose |
|------|---------|
| `shipkey.json` | Shipkey configuration |
| `.env.local.op` | 1Password reference template |
| `migrate-to-1password.sh` | Migration script (run after installing `op` CLI) |
| `KEYS.md` | Complete key inventory and documentation |

---

## 🔐 Security Recommendations

### Option 1: 1Password (Recommended)

**Install 1Password CLI:**
```bash
brew install 1password-cli  # macOS
# OR
curl -sS https://downloads.1password.com/linux/keys/1password.asc | sudo gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/$(dpkg --print-architecture) stable main" | sudo tee /etc/apt/sources.list.d/1password.list
sudo apt update && sudo apt install 1password-cli
```

**Run migration:**
```bash
cd ~/clawd
./migrate-to-1password.sh
```

**Use with OpenClaw:**
```bash
# Option A: Use op run to inject keys
op run --env-file=.env.local -- openclaw

# Option B: Use direnv with 1Password
# Add to .envrc:
eval "$(op signin)"
export XAI_API_KEY="op://clawdbot-keys/xai/clawdbot/XAI_API_KEY"
# ... other keys
```

### Option 2: git-crypt (Alternative)

If you prefer not to use 1Password, encrypt the keys file with git-crypt:

```bash
# Install git-crypt
sudo apt install git-crypt  # Ubuntu
brew install git-crypt       # macOS

# Initialize in clawd repo
cd ~/clawd
git-crypt init

# Create .gitattributes
echo "*.json filter=git-crypt diff=git-crypt" > .gitattributes
echo "keys.json filter=git-crypt diff=git-crypt" >> .gitattributes

# Copy keys file and encrypt
cp ~/.config/shipkey-local/keys.json ./keys.json
git-crypt status
```

### Option 3: SOPS + Age (Cloud-native)

For AWS/GCP/Azure environments:

```bash
# Install sops and age
brew install sops age

# Generate age key
age-keygen -o key.txt

# Encrypt keys file
export SOPS_AGE_KEY_FILE=key.txt
sops encrypt --in-place ~/.config/shipkey-local/keys.json

# Decrypt when needed
sops decrypt ~/.config/shipkey-local/keys.json | jq
```

---

## 🚨 Immediate Actions Required

### 1. Rotate Hardcoded Key

**Location:** `skills/tmux-agents/scripts/spawn.sh` (line 87)

```bash
# Current (INSECURE):
ANTHROPIC_API_KEY='sk-cp-kqO98wO1Vu2yl9rDGj63JNLaAVZYN6Ru2xKWnsdU6OLdDX5sRNw2yzwqicx5Bz6QFBQjqMW3aPoILeDql0UsK3WUxi7kaLEUzt_nwv-ebdk7wtgJf5o1TZk'

# Should be:
ANTHROPIC_API_KEY="${MINIMAX_API_KEY}"
```

**Action:**
- Rotate this key at https://api.minimaxi.com/
- Update to use environment variable

### 2. Consolidate Duplicate Keys

These keys appear in multiple places:

| Key | Locations | Action |
|-----|-----------|--------|
| `OPENROUTER_API_KEY` | openclaw.json, autofigure-edit/.env | Choose one source |
| `XAI_API_KEY` | openclaw.json, xai/.env | Choose one source |
| `FEISHU_APP_*` | openclaw.json, feishu/.env | Choose one source |
| `GEMINI_API_KEY` | openclaw.json, nano-banana/.env | Likely same key |

---

## 📝 Usage Guide

### View Stored Keys
```bash
shipkey-local list
```

### Generate .env.local (resolved values)
```bash
shipkey-local pull
```

### Update a Key
```bash
# Edit the JSON directly
nano ~/.config/shipkey-local/keys.json

# Or use jq
jq '.XAI_API_KEY.value = "new-key-here"' ~/.config/shipkey-local/keys.json > tmp.json && mv tmp.json ~/.config/shipkey-local/keys.json
```

### Rescan for New Keys
```bash
shipkey-local scan
```

---

## 🔄 Integration with OpenClaw

### Option A: Use shipkey-local in spawn.sh

Update `skills/tmux-agents/scripts/spawn.sh`:

```bash
# Before:
tmux send-keys -t "$SESSION_NAME" "ANTHROPIC_API_KEY='sk-cp-kq...' ..."

# After:
MINIMAX_API_KEY=$(jq -r '.MINIMAX_API_KEY.value' ~/.config/shipkey-local/keys.json)
tmux send-keys -t "$SESSION_NAME" "ANTHROPIC_API_KEY='$MINIMAX_API_KEY' ..."
```

### Option B: Source .env.local in sessions

```bash
# In .zshrc or before running agents
source ~/clawd/.env.local
```

### Option C: Use 1Password with op run

```bash
# Run OpenClaw with injected keys
op run --env-file=~/clawd/.env.local -- clawdbot
```

---

## 📊 Key Statistics

| Category | Count |
|----------|-------|
| **Model Providers** | 10 |
| **Search/Services** | 3 |
| **Messaging Platforms** | 3 |
| **External Services** | 8 |
| **Infrastructure** | 4 |
| **Duplicates** | 3 |
| **Total Unique** | **28** |

---

## 🎯 Next Steps (Priority Order)

1. **🔴 This Week:**
   - [ ] Rotate hardcoded MiniMax key
   - [ ] Choose encryption method (1Password/git-crypt/SOPS)
   - [ ] Implement chosen solution

2. **🟡 Next 2 Weeks:**
   - [ ] Consolidate duplicate keys
   - [ ] Update all User_Services to use central key store
   - [ ] Remove keys from openclaw.json (use env vars)

3. **🟢 Next Month:**
   - [ ] Set up key rotation schedule
   - [ ] Document key permissions per provider
   - [ ] Set up monitoring/alerting for key usage

---

## 🔧 Tools Reference

| Tool | Purpose | Install |
|------|---------|---------|
| `shipkey-local` | Custom key manager | Already installed at `~/.local/bin/` |
| `shipkey` | Official shipkey CLI | `curl -fsSL https://shipkey.dev/install.sh \| bash` |
| `op` | 1Password CLI | `brew install 1password-cli` |
| `git-crypt` | Git encryption | `apt install git-crypt` |
| `sops` | Mozilla secrets manager | `brew install sops` |

---

## 📚 Related Documentation

- `KEYS.md` - Complete key inventory
- `shipkey.json` - Shipkey configuration
- https://github.com/chekusu/shipkey - Official shipkey docs
- https://developer.1password.com/docs/cli/ - 1Password CLI docs
