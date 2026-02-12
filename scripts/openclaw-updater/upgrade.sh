#!/bin/bash
# OpenClaw 源码安全升级脚本
# 保留本地新增功能，合并上游更新

set -e

SOURCE_DIR="$HOME/clawdbot"
BACKUP_DIR="$HOME/clawd/backup/openclaw-$(date +%Y%m%d-%H%M%S)"

echo "🚀 OpenClaw 源码升级"
echo "===================="
echo ""

# 创建备份
echo "📦 创建备份..."
mkdir -p "$BACKUP_DIR"
cp -r "$SOURCE_DIR" "$BACKUP_DIR/"
echo "✓ 备份位置: $BACKUP_DIR"
echo ""

cd "$SOURCE_DIR"

# 检查当前状态
echo "📊 当前状态:"
echo "  分支: $(git branch --show-current)"
echo "  Commit: $(git rev-parse --short HEAD)"
echo ""

# 检查本地修改
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  检测到本地修改:"
    git status --short
    echo ""
    read -p "是否提交本地修改? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📝 提交本地修改..."
        git add -A
        git commit -m "local: save custom changes before upgrade ($(date +%Y-%m-%d))"
        echo "✓ 已提交"
    else
        echo "❌ 升级取消（存在未提交的本地修改）"
        exit 1
    fi
    echo ""
fi

# 获取远程更新
echo "📥 获取远程更新..."
git fetch origin main
echo ""

# 显示将要合并的内容
echo "🔍 即将合并的提交:"
git log HEAD..origin/main --oneline | head -20
TOTAL=$(git rev-list --count HEAD..origin/main)
echo "  共 $TOTAL 个提交"
echo ""

read -p "确认合并? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 升级取消"
    exit 1
fi

# 执行合并（保留本地修改）
echo ""
echo "🔀 合并更新..."
git merge origin/main --no-edit || {
    echo ""
    echo "⚠️  合并冲突!"
    echo "冲突文件:"
    git diff --name-only --diff-filter=U
    echo ""
    echo "解决策略:"
    echo "  - 对于 OpenClaw 核心代码: 接受远程版本"
    echo "  - 对于本地新增内容: 保留本地版本"
    echo ""
    read -p "是否自动解决冲突（保留本地 skills/ 和 agents/）? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 保留本地新增的技能和代理
        git checkout --ours skills/amap-places/ skills/arxiv-researcher/ skills/fact-check/ skills/notebooklm/ skills/paper-manager/ skills/remote-macos-*/ agents/ 2>/dev/null || true
        git add -A
        git commit -m "merge: upgrade from upstream with local additions preserved"
    else
        echo "请手动解决冲突后提交"
        exit 1
    fi
}

echo ""
echo "✅ 升级完成!"
echo ""
echo "新 commit: $(git rev-parse --short HEAD)"
echo ""
echo "📋 升级摘要:"
git log --oneline --graph HEAD~5..HEAD 2>/dev/null || git log --oneline -5
echo ""
echo "⚡ 需要重启 Gateway 生效: openclaw gateway restart"
