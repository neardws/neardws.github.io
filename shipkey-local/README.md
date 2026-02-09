# Local Key Storage with git-crypt

## ✅ Setup Complete

Your API keys are now stored locally with **git-crypt encryption**.

### Storage Location

```
~/clawd/shipkey-local/
├── keys.json          # Encrypted key database (31 keys)
└── git-crypt.key      # git-crypt symmetric key (backup)
```

### Encryption Status

- ✅ **keys.json** - Automatically encrypted by git-crypt
- ✅ **.env files** - Configured for encryption in .gitattributes
- 🔑 **Backup key** - Stored at `shipkey-local/git-crypt.key`

---

## 🔐 Security

### How git-crypt Works

1. **Transparent encryption**: Files are encrypted when committed to git, decrypted when checked out
2. **Symmetric key**: Uses AES-256-GCM encryption
3. **Selective**: Only files matching `.gitattributes` patterns are encrypted

### Backup Your Key

**IMPORTANT**: Back up `shipkey-local/git-crypt.key` to a secure location:

```bash
# Copy to secure storage (1Password, USB drive, etc.)
cp ~/clawd/shipkey-local/git-crypt.key /path/to/secure/backup/

# Or export to GPG-encrypted file
gpg --symmetric --cipher-algo AES256 --output git-crypt.key.gpg ~/clawd/shipkey-local/git-crypt.key
```

### Unlock Repository

On a new machine or after cloning:

```bash
cd ~/clawd

# If you have the key file
git-crypt unlock /path/to/git-crypt.key

# If the key is in 1Password
op document get "git-crypt-key" --output git-crypt.key
git-crypt unlock git-crypt.key
rm git-crypt.key
```

---

## 🛠️ Usage

### View Keys

```bash
cd ~/clawd

# List all keys (decrypted automatically)
shipkey-local list

# Get specific key value
jq -r '.XAI_API_KEY.value' shipkey-local/keys.json
```

### Generate .env.local

```bash
cd ~/clawd
shipkey-local pull

# This creates .env.local with all resolved values
```

### Add/Update a Key

```bash
cd ~/clawd

# Edit the JSON file
nano shipkey-local/keys.json

# Or use jq
jq '.NEW_KEY = {"value": "secret", "provider": "custom", "created_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' shipkey-local/keys.json > tmp.json && mv tmp.json shipkey-local/keys.json
```

### Rescan for New Keys

```bash
cd ~/clawd
shipkey-local scan
```

---

## 🔧 Integration

### With OpenClaw

OpenClaw currently reads keys from `~/.openclaw/openclaw.json`. To use shipkey-local:

**Option 1: Environment Variables (Recommended)**

Update OpenClaw config to use environment variable references:

```json
{
  "models": {
    "providers": {
      "xai": {
        "apiKey": "${XAI_API_KEY}"
      }
    }
  }
}
```

Then source .env.local before running OpenClaw:

```bash
source ~/clawd/.env.local
openclaw
```

**Option 2: Direct JSON Reference**

Modify OpenClaw to support reading from shipkey-local/keys.json directly.

### With User Services

Each service in `~/User_Services/` currently has its own `.env` file. To centralize:

```bash
# For each service
cd ~/User_Services/some-service

# Replace .env with symlink to generated file
mv .env .env.backup
ln -s ~/clawd/.env.local .env

# Or source it at the top of .env
echo 'source ~/clawd/.env.local' > .env
```

### With tmux-agents

The hardcoded MiniMax key has been fixed. The spawn script now reads from shipkey-local:

```bash
# In spawn.sh
MINIMAX_API_KEY=$(jq -r '.MINIMAX_API_KEY.value' ~/clawd/shipkey-local/keys.json)
```

---

## 📊 Current Status

| Metric | Value |
|--------|-------|
| **Total Keys** | 31 |
| **Encrypted** | ✅ Yes (git-crypt) |
| **Storage** | ~/clawd/shipkey-local/keys.json |
| **Backup Key** | ~/clawd/shipkey-local/git-crypt.key |
| **Hardcoded Keys** | 0 (fixed) |

---

## 🚨 Important Notes

1. **Never commit git-crypt.key**: It's in .gitignore, but double-check
2. **Backup the key**: Without it, you cannot decrypt on new machines
3. **Team access**: Share git-crypt.key securely if others need access
4. **Rotation**: When rotating keys, update shipkey-local/keys.json

---

## 🔍 Verification

Check encryption is working:

```bash
cd ~/clawd

# Check file is encrypted in git
git show HEAD:shipkey-local/keys.json | file -
# Should show: "data" (encrypted)

# Check file is decrypted in working directory
cat shipkey-local/keys.json | head -5
# Should show readable JSON
```

---

## 🔄 Migration from Other Systems

### From 1Password (if you later change your mind)

```bash
# Export from 1Password
op item list --vault=clawdbot-keys --format=json | jq -r '.[].title' | while read title; do
  value=$(op item get "$title" --field=api_key)
  jq ".[\"$title\"] = {\"value\": \"$value\", \"provider\": \"1password\"}" shipkey-local/keys.json > tmp.json && mv tmp.json shipkey-local/keys.json
done
```

### To 1Password (future migration)

Use the existing `migrate-to-1password.sh` script.

