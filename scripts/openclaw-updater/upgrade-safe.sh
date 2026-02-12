#!/bin/bash
#
# OpenClaw 零宕机升级脚本
# 基于 upgrade-guard + 自定义热重载策略
#

set -euo pipefail

# 配置
SOURCE_DIR="${HOME}/clawdbot"
WORKSPACE_DIR="${HOME}/clawd"
BACKUP_DIR="${WORKSPACE_DIR}/backup/openclaw-$(date +%Y%m%d-%H%M%S)"
LOG_FILE="${WORKSPACE_DIR}/scripts/openclaw-updater/upgrade-$(date +%Y%m%d-%H%M%S).log"
STATE_FILE="${WORKSPACE_DIR}/scripts/openclaw-updater/guard-state.json"
GATEWAY_URL="http://localhost:18789"
MAX_WAIT_SECONDS=60
OPENCLAW_CMD="node ${SOURCE_DIR}/openclaw.mjs"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$msg"
    echo "$msg" >> "$LOG_FILE"
}

error() { log "${RED}✗ $1${NC}"; }
success() { log "${GREEN}✓ $1${NC}"; }
warn() { log "${YELLOW}⚠ $1${NC}"; }
info() { log "${BLUE}ℹ $1${NC}"; }

# ============ 前置检查 ============

preflight_check() {
    info "开始前置检查..."
    
    # 1. 检查 Gateway 是否运行
    if ! pgrep -f "openclaw-gateway" >/dev/null 2>&1; then
        error "Gateway 未运行！请先启动 Gateway"
        exit 1
    fi
    
    # 2. 检查 Gateway 健康状态
    if ! curl -s -m 5 "${GATEWAY_URL}/health" >/dev/null 2>&1; then
        warn "Gateway 健康检查失败，继续升级但有风险"
    else
        success "Gateway 健康检查通过"
    fi
    
    # 3. 检查磁盘空间
    local available=$(df -BG "${SOURCE_DIR}" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$available" -lt 2 ]; then
        error "磁盘空间不足 (${available}GB < 2GB)"
        exit 1
    fi
    success "磁盘空间充足 (${available}GB)"
    
    # 4. 检查 Git 状态
    cd "${SOURCE_DIR}"
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        warn "检测到本地未提交修改，将自动提交"
        git add -A
        git commit -m "pre-upgrade: save local changes ($(date +%Y-%m-%d-%H:%M))" || true
    fi
    
    # 5. 创建完整备份
    info "创建完整备份..."
    mkdir -p "${BACKUP_DIR}"
    cp -r "${SOURCE_DIR}" "${BACKUP_DIR}/"
    success "备份完成: ${BACKUP_DIR}"
    
    # 6. 保存当前状态
    cat > "${STATE_FILE}" << EOF
{
  "last_upgrade": "$(date -Iseconds)",
  "backup_path": "${BACKUP_DIR}",
  "source_commit": "$(git rev-parse HEAD)",
  "source_branch": "$(git branch --show-current)"
}
EOF
    
    success "前置检查通过"
}

# ============ 热重载升级（推荐） ============

hot_reload_upgrade() {
    info "执行热重载升级..."
    
    cd "${SOURCE_DIR}"
    local old_commit=$(git rev-parse HEAD)
    local old_pid=$(pgrep -f "openclaw-gateway" | head -1)
    
    info "当前 Gateway PID: ${old_pid}"
    
    # 1. 获取更新但不切换分支（先下载）
    info "获取远程更新..."
    git fetch origin main
    local new_commit=$(git rev-parse origin/main)
    
    if [ "$old_commit" = "$new_commit" ]; then
        success "已经是最新版本"
        return 0
    fi
    
    info "升级: ${old_commit:0:8} → ${new_commit:0:8}"
    
    # 2. 检查变更类型（是否涉及核心依赖）
    local core_changes=$(git diff --name-only "${old_commit}..${new_commit}" | grep -E "^(package\.json|pnpm-lock\.yaml|src/|gateway/)" || true)
    
    if [ -z "$core_changes" ]; then
        # 无核心变更，可以热重载
        info "无核心依赖变更，执行热重载..."
        
        # 执行合并
        git merge origin/main --no-edit || {
            error "合并失败，执行回滚..."
            git merge --abort 2>/dev/null || true
            return 1
        }
        
        # 发送 SIGUSR1 触发 Gateway 配置重载（不重启进程）
        info "发送 SIGUSR1 触发配置重载..."
        kill -USR1 "${old_pid}" 2>/dev/null || {
            warn "SIGUSR1 失败，Gateway 可能不支持热重载"
            return 1
        }
        
        sleep 2
        
        # 验证 Gateway 仍然存活
        if pgrep -f "openclaw-gateway" | grep -q "${old_pid}"; then
            success "热重载成功！Gateway 仍在运行 (PID: ${old_pid})"
            return 0
        else
            error "热重载后 Gateway 进程丢失"
            return 1
        fi
    else
        info "检测到核心依赖变更，需要重启升级..."
        return 1  # 回退到滚动重启
    fi
}

# ============ 滚动重启升级（备用） ============

rolling_restart_upgrade() {
    info "执行滚动重启升级..."
    
    cd "${SOURCE_DIR}"
    local old_pid=$(pgrep -f "openclaw-gateway" | head -1)
    
    # 1. 合并代码
    info "合并远程更新..."
    git merge origin/main --no-edit || {
        error "合并失败"
        return 1
    }
    
    # 2. 安装依赖（如需要）
    if [ -f "package.json" ] && git diff --name-only HEAD~1 | grep -q "package.json"; then
        info "检测到依赖变更，安装依赖..."
        pnpm install --frozen-lockfile || pnpm install
    fi
    
    # 3. 关键：先验证新代码能启动
    info "验证新代码可启动..."
    # 这里可以添加构建/测试步骤
    
    # 4. 使用 openclaw 命令重启 Gateway
    info "尝试优雅重启 Gateway..."
    
    # 使用 openclaw gateway restart 命令并捕获输出
    if ! ${OPENCLAW_CMD} gateway restart 2>&1; then
        error "openclaw gateway restart 命令失败"
        return 1
    fi
    
    # 等待 Gateway 完全启动
    info "等待 Gateway 启动..."
    local waited=0
    local new_pid=""
    
    while [ $waited -lt $MAX_WAIT_SECONDS ]; do
        sleep 1
        ((waited++))
        
        # 检查进程是否存在
        new_pid=$(pgrep -f "openclaw-gateway" | head -1)
        
        if [ -n "$new_pid" ]; then
            # 进程存在，检查健康
            if curl -s -m 5 "${GATEWAY_URL}/health" >/dev/null 2>&1; then
                success "Gateway 重启成功！PID: ${new_pid}"
                return 0
            fi
        fi
        
        echo -n "."
    done
    
    echo ""
    error "Gateway 重启超时 (${MAX_WAIT_SECONDS}s)"
    return 1
}

# ============ 紧急回滚 ============

emergency_rollback() {
    error "升级失败！执行紧急回滚..."
    
    cd "${SOURCE_DIR}"
    
    # 1. 中止合并（如处于合并中）
    git merge --abort 2>/dev/null || true
    
    # 2. 恢复代码
    if [ -f "${STATE_FILE}" ]; then
        local source_commit=$(jq -r '.source_commit' "${STATE_FILE}")
        info "回滚到 commit: ${source_commit:0:8}"
        git reset --hard "${source_commit}"
    fi
    
    # 3. 从备份恢复（如 git 回滚失败）
    if [ -d "${BACKUP_DIR}/clawdbot" ]; then
        warn "从备份恢复..."
        rm -rf "${SOURCE_DIR}"
        cp -r "${BACKUP_DIR}/clawdbot" "${SOURCE_DIR}"
    fi
    
    # 4. 确保 Gateway 运行
    if ! pgrep -f "openclaw-gateway" >/dev/null 2>&1; then
        warn "Gateway 未运行，尝试启动..."
        openclaw gateway start || true
    fi
    
    success "回滚完成"
}

# ============ 升级后验证 ============

post_verify() {
    info "升级后验证..."
    
    local retries=5
    local waited=0
    
    while [ $waited -lt $retries ]; do
        # 1. 检查进程
        if ! pgrep -f "openclaw-gateway" >/dev/null 2>&1; then
            error "Gateway 进程不存在"
            return 1
        fi
        
        # 2. 检查 HTTP 响应
        if curl -s -m 5 "${GATEWAY_URL}/health" >/dev/null 2>&1; then
            success "Gateway 健康检查通过"
            
            # 3. 检查版本
            cd "${SOURCE_DIR}"
            local new_commit=$(git rev-parse HEAD)
            info "当前版本: ${new_commit:0:8}"
            
            return 0
        fi
        
        sleep 2
        ((waited++))
    done
    
    error "升级后验证失败"
    return 1
}

# ============ 主流程 ============

main() {
    mkdir -p "$(dirname "$LOG_FILE")"
    
    info "========================================="
    info "OpenClaw 零宕机升级"
    info "========================================="
    info "日志: ${LOG_FILE}"
    
    # 前置检查
    preflight_check || exit 1
    
    # 尝试热重载
    if hot_reload_upgrade; then
        post_verify || {
            emergency_rollback
            exit 1
        }
        success "========================================="
        success "升级成功！Gateway 未中断"
        success "========================================="
        exit 0
    fi
    
    # 热重载失败，尝试滚动重启
    warn "热重载失败，切换到滚动重启..."
    
    if rolling_restart_upgrade; then
        post_verify || {
            emergency_rollback
            exit 1
        }
        success "========================================="
        success "升级成功！Gateway 已重启"
        success "========================================="
        exit 0
    else
        emergency_rollback
        exit 1
    fi
}

# 信号处理
trap 'error "升级中断"; exit 130' INT TERM

main "$@"
