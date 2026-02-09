#!/bin/bash
# Complete migration script for OpenClaw keys to 1Password
# Run this after installing 1Password CLI

set -e

KEYS_FILE="${HOME}/.config/shipkey-local/keys.json"
VAULT_NAME="clawdbot-keys"

echo "═══════════════════════════════════════════════════════════"
echo "  OpenClaw API Keys → 1Password Migration"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check 1Password CLI
if ! command -v op &> /dev/null; then
    echo "❌ 1Password CLI (op) not found"
    echo "   Install: https://developer.1password.com/docs/cli/get-started/"
    echo "   Or use: brew install 1password-cli"
    exit 1
fi

# Check if logged in
if ! op account list &> /dev/null; then
    echo "🔐 Please sign in to 1Password first:"
    echo "   eval \$(op signin)"
    exit 1
fi

# Create vault if not exists
echo "📦 Checking vault: $VAULT_NAME"
if ! op vault list | grep -q "$VAULT_NAME"; then
    echo "   Creating vault..."
    op vault create "$VAULT_NAME"
    echo "   ✓ Vault created"
else
    echo "   ✓ Vault exists"
fi

echo ""
echo "🔑 Migrating keys to 1Password..."

# Function to migrate a key
migrate_key() {
    local key_name="$1"
    local provider="$2"
    local value=$(jq -r ".[\"$key_name\"].value // empty" "$KEYS_FILE")
    
    if [ -z "$value" ] || [ "$value" = "null" ]; then
        echo "   ⚠️  Skipping $key_name (empty value)"
        return
    fi
    
    # Check if already exists
    if op item get "$key_name" --vault="$VAULT_NAME" &> /dev/null; then
        echo "   ↻ Updating: $key_name"
        op item edit "$key_name" --vault="$VAULT_NAME" "api_key=$value" &> /dev/null
    else
        echo "   ✓ Creating: $key_name"
        op item create \
            --vault="$VAULT_NAME" \
            --category="api_credential" \
            --title="$key_name" \
            --tags="$provider,clawdbot" \
            "api_key=$value" \
            "provider=$provider" \
            "project=clawdbot" \
            &> /dev/null
    fi
}

# Migrate all keys
jq -r 'to_entries[] | "\(.key)|\(.value.provider)"' "$KEYS_FILE" | while IFS='|' read -r key_name provider; do
    migrate_key "$key_name" "$provider"
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✓ Migration complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo ""
echo "1. Review keys in 1Password:"
echo "   op item list --vault=$VAULT_NAME"
echo ""
echo "2. Generate .env.local with 1Password references:"
echo "   cp .env.local.op .env.local"
echo ""
echo "3. Install 1Password shell integration:"
echo "   echo 'eval \"\$(op signin)\"' >> ~/.zshrc"
echo ""
echo "4. Use with direnv (optional):"
echo "   echo 'eval \"\$(op signin)\"' >> .envrc"
echo "   echo 'export XAI_API_KEY=\"op://$VAULT_NAME/xai/clawdbot/XAI_API_KEY\"' >> .envrc"
echo ""
echo "5. Pull resolved values (for non-1Password systems):"
echo "   op run --env-file=.env.local -- printenv | grep API_KEY"
