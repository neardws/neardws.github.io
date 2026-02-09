#!/bin/bash

# Axis Voice Assistant - 启动脚本
# 用于快速启动本地开发服务器

PORT=${1:-3000}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "⚡ Axis Voice Assistant"
echo "========================================"
echo ""
echo "启动本地服务器..."
echo "端口: $PORT"
echo "目录: $SCRIPT_DIR"
echo ""

# 检查依赖服务
echo "检查外部服务状态..."
echo ""

# 检查 ASR
ASR_URL="http://192.168.31.114:9001"
if curl -s -f -o /dev/null "$ASR_URL"; then
    echo "✅ ASR 服务运行正常: $ASR_URL"
else
    echo "⚠️  ASR 服务无法访问: $ASR_URL"
fi

# 检查 TTS
TTS_URL="http://192.168.31.114:5100"
if curl -s -f -o /dev/null "$TTS_URL"; then
    echo "✅ TTS 服务运行正常: $TTS_URL"
else
    echo "⚠️  TTS 服务无法访问: $TTS_URL"
fi

echo ""
echo "========================================"
echo ""

# 检查 Python
if command -v python3 &> /dev/null; then
    echo "使用 Python 启动服务器..."
    cd "$SCRIPT_DIR"
    python3 -m http.server "$PORT"
# 检查 Node.js
elif command -v npx &> /dev/null; then
    echo "使用 Node.js 启动服务器..."
    cd "$SCRIPT_DIR"
    npx serve -p "$PORT"
else
    echo "❌ 错误: 未找到 Python 或 Node.js"
    echo ""
    echo "请安装以下任一工具："
    echo "  - Python 3: https://www.python.org/"
    echo "  - Node.js: https://nodejs.org/"
    exit 1
fi
