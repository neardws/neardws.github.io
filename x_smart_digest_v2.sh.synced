#!/bin/bash
# X Smart Digest - 提取内容并总结，不再直接发图片

PHONE_IP="192.168.31.87"
PHONE_PORT="8022"
PHONE_PASS="jVzus5h5toln"
LOG_DIR="/Users/neardws/clawphone/logs"
WEBHOOK="https://discord.com/api/webhooks/1470696274775769205/Tp6q93PwB2MVowcv3YCbAkdBIL_FvnaXZSIzJGwnhTdfeDGzEV1ZdbHIORb3oZXgL2HD"
SCRIPT_DIR="/Users/neardws/clawphone"

mkdir -p "$LOG_DIR"

# 随机等待防检测
RANDOM_MINUTE=$((RANDOM % 60))
echo "Waiting until minute $RANDOM_MINUTE..."
while [ "$(date +%M)" -ne "$RANDOM_MINUTE" ]; do sleep 10; done

echo "Starting X check at $(date)"

# 启动 X App
sshpass -p "$PHONE_PASS" ssh -p "$PHONE_PORT" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$PHONE_IP" "su -c am start -n com.twitter.android/.StartActivity"
sleep 5

# 截图3张
for i in 1 2 3; do
    sleep 2
    sshpass -p "$PHONE_PASS" ssh -p "$PHONE_PORT" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$PHONE_IP" "su -c input swipe 500 1500 500 600 800"
    sleep 1
    DATE=$(date +%Y%m%d_%H%M%S)
    sshpass -p "$PHONE_PASS" ssh -p "$PHONE_PORT" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$PHONE_IP" "su -c screencap -p /sdcard/x_check_$i.png"
    sshpass -p "$PHONE_PASS" ssh -p "$PHONE_PORT" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$PHONE_IP" "su -c cat /sdcard/x_check_$i.png" > "$LOG_DIR/x_${DATE}_$i.png" 2>/dev/null
    echo "Captured screen $i"
done

echo "Check complete at $(date)"

# 8AM/12PM/6PM 时提取内容并发送总结
HOUR=$(date +%H)
if [ "$HOUR" = "08" ] || [ "$HOUR" = "12" ] || [ "$HOUR" = "18" ]; then
    echo "Processing screenshots with AI..."
    
    # 运行 Python 脚本提取和总结内容
    cd "$SCRIPT_DIR"
    /opt/homebrew/bin/python3 x_content_extractor.py > "$LOG_DIR/extractor_$(date +%Y%m%d_%H%M%S).log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "Content extracted and sent successfully"
    else
        echo "Failed to extract content, sending fallback notification"
        curl -s -X POST -H "Content-Type: application/json" \
            -d "{\"content\":\"⚠️ X Smart Digest - $(date) | 内容提取失败，请检查日志\"}" \
            "$WEBHOOK"
    fi
else
    echo "Not push time (8AM/12PM/6PM), screenshots saved locally only"
fi
