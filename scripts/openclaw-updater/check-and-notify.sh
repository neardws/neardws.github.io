#!/bin/bash
# OpenClaw 更新检查并通知包装脚本

MONITOR_DIR="$HOME/clawd/scripts/openclaw-updater"
LOG_FILE="$MONITOR_DIR/monitor.log"

# 运行检查并捕获输出
OUTPUT=$("$MONITOR_DIR/monitor.py" 2>&)
EXIT_CODE=$?

# 总是记录日志
echo "$OUTPUT" >> "$LOG_FILE"

# 如果发现有更新
if [ $EXIT_CODE -eq 1 ]; then
    # 提取通知内容
    NOTIFICATION=$(echo "$OUTPUT" | sed -n '/UPDATE_FOUND/,/^==/p' | sed '1d;$d')
    
    # 发送到 Discord 或 Telegram
    # 使用 clawdbot 的 notify 功能
    echo "$NOTIFICATION"
    echo ""
    echo "To upgrade, run: ./clawd/scripts/openclaw-updater/upgrade.sh"
    exit 0
fi

exit 0
