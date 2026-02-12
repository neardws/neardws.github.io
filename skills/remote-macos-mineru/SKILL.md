---
name: remote-macos-mineru
description: 通过 SSH 调用 Mac Mini 上部署的 MinerU PDF 解析服务，将 PDF 转换为 Markdown。支持公式识别、表格识别、多语言解析。当用户需要将 PDF 文档转换为结构化 Markdown、提取 PDF 文本内容、处理学术论文或扫描文档时触发使用。
---

# Remote MacOS MinerU

MinerU 是一个开源的 PDF 解析工具，支持将 PDF 转换为 Markdown，特别适合处理包含公式、表格的学术论文和扫描文档。

## 服务信息

- **主机**: Mac Mini M4 (192.168.31.114)
- **服务类型**: Gradio WebUI (HTTP API)
- **监听地址**: 127.0.0.1:7860（仅本地访问）
- **访问方式**: 通过 SSH 在 Mac Mini 上执行 API 调用
- **环境**: micromamba `mineru`

## 架构

```
┌─────────────────┐     SSH+SCP       ┌─────────────────────────────┐
│   OpenClaw      │ ◀──────────────▶  │   Mac Mini M4               │
│   (调用脚本)     │                   │   ┌───────────────────────┐ │
│                 │   1. scp 上传 PDF  │   │   Gradio WebUI        │ │
│                 │   2. ssh 执行 API  │   │   - /gradio_api/*      │ │
│                 │   3. 返回结果      │   │   (127.0.0.1:7860)    │ │
└─────────────────┘                   │   └───────────────────────┘ │
                                      │            │                │
                                      │            ▼                │
                                      │   ┌───────────────────────┐ │
                                      │   │   MinerU CLI          │ │
                                      │   │   (micromamba env)    │ │
                                      │   └───────────────────────┘ │
                                      └─────────────────────────────┘
```

## 支持的解析后端

| 后端 | 说明 |
|------|------|
| `hybrid-auto-engine` | 自动选择最佳引擎 (默认) |
| `pipeline` | 传统 pipeline 模式 |
| `vlm-auto-engine` | VLM 视觉语言模型模式 |

## 支持的语言

- `ch` - 中文 (默认)
- `en` - 英文
- `ch_server` - 中文服务器模式
- `ch_lite` - 中文轻量模式
- `korean` - 韩语
- `japan` - 日语

## 前置条件

1. **SSH 免密登录**: 确保可以从 OpenClaw 主机免密 SSH 到 Mac Mini
   ```bash
   ssh neardws@192.168.31.114
   ```

2. **Gradio 服务运行**: 确保 Mac Mini 上的 MinerU 服务已启动
   ```bash
   ssh neardws@192.168.31.114 "curl -s http://localhost:7860/ | head -1"
   ```

## 使用方法

### 命令行调用

```bash
# 基本用法
python3 ~/.clawdbot/skills/remote-macos-mineru/scripts/mineru_client.py /path/to/document.pdf

# 保存结果到文件
python3 ~/.clawdbot/skills/remote-macos-mineru/scripts/mineru_client.py document.pdf -o output.md

# 指定解析后端和语言
python3 ~/.clawdbot/skills/remote-macos-mineru/scripts/mineru_client.py paper.pdf \
    --backend vlm-auto-engine --lang en

# 禁用公式识别（加快速度）
python3 ~/.clawdbot/skills/remote-macos-mineru/scripts/mineru_client.py document.pdf --no-formula

# 禁用表格识别
python3 ~/.clawdbot/skills/remote-macos-mineru/scripts/mineru_client.py document.pdf --no-table
```

### 在 Python 中调用

```python
import sys
sys.path.insert(0, '~/.clawdbot/skills/remote-macos-mineru/scripts')
from mineru_client import MinerUClient

# 创建客户端
client = MinerUClient(host="192.168.31.114", port=7860, user="neardws")

# 解析 PDF
result = client.parse_pdf(
    pdf_path="/path/to/paper.pdf",
    backend="vlm-auto-engine",  # 最佳质量
    lang="ch",
    formula=True,
    table=True
)

if result["success"]:
    print(result["markdown"])
else:
    print(f"Error: {result['error']}")
```

### 在 OpenClaw 中使用

```python
import subprocess
import json

result = subprocess.run([
    "python3", "~/.clawdbot/skills/remote-macos-mineru/scripts/mineru_client.py",
    "document.pdf",
    "--backend", "hybrid-auto-engine",
    "--lang", "ch"
], capture_output=True, text=True)

data = json.loads(result.stdout)
if data["success"]:
    markdown = data["markdown"]
    # 处理 markdown...
```

## 输出格式

```json
{
  "success": true,
  "status": "解析成功！",
  "markdown": "# 文档标题\n\n正文内容..."
}
```

错误时：

```json
{
  "success": false,
  "error": "错误信息"
}
```

## 适用场景

- **学术论文**: 解析包含数学公式的研究论文
- **技术文档**: 提取 API 文档、用户手册
- **扫描文档**: OCR 识别并结构化扫描 PDF
- **表格数据**: 保留表格结构转换为 Markdown 表格

## 故障排除

**SSH 连接失败**:
```bash
# 检查 SSH 配置
ssh -v neardws@192.168.31.114
```

**Gradio 服务未运行**:
```bash
# 在 Mac Mini 上启动服务
ssh neardws@192.168.31.114
cd ~/mineru-webui
export MAMBA_ROOT_PREFIX=/Users/neardws/micromamba
/tmp/mineru-install/micromamba run -n mineru python3 app.py
```

**解析超时**: 大文件可能需要更长时间，脚本默认 300 秒超时

**公式识别失败**: 尝试切换到 `vlm-auto-engine` 后端

## 依赖

- Python 3.8+
- SSH 客户端
- scp

无需安装 Python 依赖包（所有调用在 Mac Mini 上执行）
