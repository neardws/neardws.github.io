#!/bin/bash
# OpenClaw Release 监控 - 自动通知包装脚本

SCRIPT_DIR="$HOME/clawd/scripts/openclaw-updater"
LOG_FILE="$SCRIPT_DIR/notify-wrapper.log"
DISCORD_CHANNEL="1468244824405839894"

# 运行监控脚本并捕获输出
OUTPUT=$(python3 "$SCRIPT_DIR/monitor-release.py" 2>&1)
EXIT_CODE=$?

# 记录日志
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Exit code: $EXIT_CODE" >> "$LOG_FILE"

# 如果发现新版本 (exit code 1)
if [ $EXIT_CODE -eq 1 ]; then
    # 提取通知内容（NEW_RELEASE_FOUND 后面的内容）
    NOTIFICATION=$(echo "$OUTPUT" | sed -n '/NEW_RELEASE_FOUND/,/^=*$/p' | tail -n +2 | head -n -1)
    
    # 如果没有提取到，使用完整输出
    if [ -z "$NOTIFICATION" ]; then
        NOTIFICATION="$OUTPUT"
    fi
    
    # 发送 Discord 通知
    # 使用 openclaw 的 message 工具或 webhook
    curl -X POST "https://discord.com/api/channels/$DISCORD_CHANNEL/messages" \
        -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"content\":$(echo "$NOTIFICATION" | jq -Rs .)}" 2>/dev/null || \
    echo "Discord notification failed" >> "$LOG_FILE"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] New release notification sent" >> "$LOG_FILE"
fi

exit 0
