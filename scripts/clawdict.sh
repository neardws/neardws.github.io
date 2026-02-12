#!/bin/bash
# Clawdict API Wrapper - Minimal Permission Mode
# Usage: ./clawdict.sh [markets|leaderboard|market <slug>]

CONFIG_FILE="$HOME/.config/clawdict/credentials.json"
BASE_URL="https://clawdict.com/api"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Credentials not found. Run setup first."
    exit 1
fi

AGENT_TOKEN=$(jq -r '.agentToken' "$CONFIG_FILE")

case "$1" in
    markets)
        curl -s -L "$BASE_URL/markets/top" \
            -H "X-Agent-Token: $AGENT_TOKEN" | jq '.'
        ;;
    leaderboard)
        curl -s -L "$BASE_URL/leaderboard" | jq '.'
        ;;
    market)
        if [ -z "$2" ]; then
            echo "Usage: $0 market <slug>"
            exit 1
        fi
        curl -s -L "$BASE_URL/markets/$2" \
            -H "X-Agent-Token: $AGENT_TOKEN" | jq '.'
        ;;
    *)
        echo "Usage: $0 [markets|leaderboard|market <slug>]"
        exit 1
        ;;
esac
