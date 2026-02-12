#!/bin/bash
# Edge VLA 常驻调研代理启动脚本

SESSION_NAME="edge-vla-researcher"

# 检查是否已存在
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Session '$SESSION_NAME' already exists. Attaching..."
    tmux attach -t "$SESSION_NAME"
    exit 0
fi

# 创建新会话
tmux new-session -d -s "$SESSION_NAME" -c "$HOME/clawd"

# 设置环境变量和任务
tmux send-keys -t "$SESSION_NAME" 'cd ~/clawd && export TASK="edge-vla-literature-review"' Enter

# 运行调研循环
tmux send-keys -t "$SESSION_NAME" '
cat > /tmp/edge_vla_loop.sh << "EOF"
#!/bin/bash
# Edge VLA 文献调研循环

PAPERS_DIR="$HOME/clawd/arxiv-lab/edge-vla"
LOG_FILE="$PAPERS_DIR/researcher.log"
DISCORD_CHANNEL="1468520658567954609"

echo "[$(date)] Edge VLA Researcher Started" >> "$LOG_FILE"

while true; do
    echo "[$(date)] Starting research iteration..." >> "$LOG_FILE"
    
    # 这里会被 Clawdbot 定期接管执行任务
    # 实际任务通过外部 cron 或手动触发
    
    # 等待 1 小时后检查
    sleep 3600
done
EOF
chmod +x /tmp/edge_vla_loop.sh
/tmp/edge_vla_loop.sh
' Enter

echo "Edge VLA Researcher session created: $SESSION_NAME"
echo "Use 'tmux attach -t $SESSION_NAME' to view"
