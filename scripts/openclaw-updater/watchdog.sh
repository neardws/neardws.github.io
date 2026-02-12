#!/bin/bash
#
# OpenClaw Gateway Watchdog
# 系统级自愈，独立于 Gateway 进程
#

set -euo pipefail

WATCHDOG_DIR="${HOME}/clawd/scripts/openclaw-updater"
LOG_FILE="${WATCHDOG_DIR}/watchdog.log"
STATE_FILE="${WATCHDOG_DIR}/watchdog-state.json"
GATEWAY_URL="http://localhost:18789"
MAX_FAILS_BEFORE_RESTART=3
MAX_FAILS_BEFORE_ROLLBACK=6
COOLDOWN_SECONDS=300  # 5分钟内不重复操作

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查 Gateway 健康
check_gateway() {
    # 1. 检查进程
    if ! pgrep -f "openclaw-gateway" >/dev/null 2>&1; then
        echo "DOWN:process"
        return 1
    fi
    
    # 2. 检查 HTTP 端口
    if ! curl -s -m 5 "${GATEWAY_URL}/health" >/dev/null 2>&1; then
        echo "DOWN:http"
        return 1
    fi
    
    echo "UP"
    return 0
}

# 加载状态
load_state() {
    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE"
    else
        echo '{"consecutive_fails":0,"last_action":"","last_action_time":0}'
    fi
}

# 保存状态
save_state() {
    echo "$1" > "$STATE_FILE"
}

# 检查是否在冷却期
in_cooldown() {
    local last_time=$1
    local now=$(date +%s)
    local diff=$((now - last_time))
    [ $diff -lt $COOLDOWN_SECONDS ]
}

# 执行操作
perform_action() {
    local action=$1
    local state=$2
    
    log "执行操作: $action"
    
    case $action in
        restart)
            log "尝试重启 Gateway..."
            openclaw gateway restart 2>&1 || {
                # 如果 restart 失败，尝试 stop + start
                openclaw gateway stop 2>&1 || true
                sleep 2
                openclaw gateway start 2>&1
            }
            ;;
        
        rollback)
            log "执行紧急回滚..."
            if [ -x "${WATCHDOG_DIR}/upgrade-safe.sh" ]; then
                # 使用升级脚本的回滚功能
                cd "${HOME}/clawdbot"
                
                # 恢复到上一个已知好的版本
                if [ -f "${WATCHDOG_DIR}/guard-state.json" ]; then
                    local commit=$(jq -r '.source_commit' "${WATCHDOG_DIR}/guard-state.json" 2>/dev/null)
                    if [ -n "$commit" ] && [ "$commit" != "null" ]; then
                        log "回滚到 commit: ${commit:0:8}"
                        git reset --hard "$commit"
                        openclaw gateway restart
                    fi
                fi
            fi
            ;;
    esac
    
    # 更新状态
    local now=$(date +%s)
    echo "$state" | jq --arg action "$action" --argjson time "$now" \
        '.last_action=$action | .last_action_time=$time | .consecutive_fails=0'
}

# 主检查逻辑
main() {
    mkdir -p "$WATCHDOG_DIR"
    
    local result
    local status
    
    # 执行健康检查
    result=$(check_gateway)
    status=$?
    
    # 加载当前状态
    local state=$(load_state)
    local fails=$(echo "$state" | jq -r '.consecutive_fails')
    local last_action=$(echo "$state" | jq -r '.last_action')
    local last_time=$(echo "$state" | jq -r '.last_action_time')
    
    if [ $status -eq 0 ]; then
        # Gateway 正常
        if [ "$fails" -gt 0 ]; then
            log "Gateway 恢复正常 (连续失败: $fails)"
            echo "$state" | jq '.consecutive_fails=0' > "$STATE_FILE"
        fi
        exit 0
    fi
    
    # Gateway 异常
    ((fails++))
    log "Gateway 异常: $result (连续失败: $fails)"
    
    # 检查是否需要执行操作
    local action=""
    
    if [ $fails -ge $MAX_FAILS_BEFORE_ROLLBACK ]; then
        action="rollback"
    elif [ $fails -ge $MAX_FAILS_BEFORE_RESTART ]; then
        action="restart"
    fi
    
    if [ -n "$action" ]; then
        # 检查冷却期
        if in_cooldown "$last_time"; then
            log "冷却期中，跳过 $action (上次: $last_action)"
            echo "$state" | jq --argjson f "$fails" '.consecutive_fails=$f' > "$STATE_FILE"
            exit 0
        fi
        
        # 执行操作
        local new_state=$(perform_action "$action" "$state")
        save_state "$new_state"
        
        # 再次检查
        sleep 5
        if check_gateway >/dev/null 2>&1; then
            log "$action 成功，Gateway 恢复正常"
        else
            log "$action 后 Gateway 仍异常"
        fi
    else
        # 只更新失败计数
        echo "$state" | jq --argjson f "$fails" '.consecutive_fails=$f' > "$STATE_FILE"
    fi
}

# 安装为 systemd 服务（可选）
install_systemd() {
    local service_file="${HOME}/.config/systemd/user/openclaw-watchdog.service"
    local timer_file="${HOME}/.config/systemd/user/openclaw-watchdog.timer"
    
    mkdir -p "$(dirname "$service_file")"
    
    cat > "$service_file" << 'EOF'
[Unit]
Description=OpenClaw Gateway Watchdog
After=network.target

[Service]
Type=oneshot
ExecStart=%h/clawd/scripts/openclaw-updater/watchdog.sh
StandardOutput=append:%h/clawd/scripts/openclaw-updater/watchdog.log
StandardError=append:%h/clawd/scripts/openclaw-updater/watchdog.log

[Install]
WantedBy=default.target
EOF

    cat > "$timer_file" << 'EOF'
[Unit]
Description=Run OpenClaw Watchdog every minute

[Timer]
OnBootSec=1min
OnUnitActiveSec=1min
Persistent=true

[Install]
WantedBy=timers.target
EOF

    # 替换 %h 为实际路径
    sed -i "s|%h|${HOME}|g" "$service_file"
    
    systemctl --user daemon-reload
    systemctl --user enable openclaw-watchdog.timer
    systemctl --user start openclaw-watchdog.timer
    
    log "Systemd timer 已安装"
    systemctl --user status openclaw-watchdog.timer --no-pager
}

# 主入口
case "${1:-check}" in
    check)
        main
        ;;
    install)
        install_systemd
        ;;
    status)
        cat "$STATE_FILE" 2>/dev/null || echo '{}'
        ;;
    *)
        echo "用法: $0 [check|install|status]"
        exit 1
        ;;
esac
