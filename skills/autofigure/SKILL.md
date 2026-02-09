# AutoFigure Skill

从论文方法文本生成可编辑的 SVG 插图。

## 功能

- **Text-to-Figure**: 从方法描述生成学术风格插图
- **SAM3 分割**: 自动检测图标区域 (本地运行)
- **RMBG 抠图**: AI 背景移除 (本地运行)
- **SVG 输出**: 完全可编辑的矢量图

## 依赖

- AutoFigure-Edit 已部署在 `/home/neardws/User_Services/autofigure-edit/`
- Gemini API Key (在 `~/.env` 中配置 `GEMINI_API_KEY`)

## 安装

```bash
# 1. 配置 API Key (二选一)
# 方案 A: OpenRouter (推荐，支持中国访问)
# 编辑 ~/.env 添加: OPENROUTER_API_KEY=sk-or-v1-...
# 获取: https://openrouter.ai/keys

# 方案 B: Gemini (需要代理)
# 编辑 ~/.env 添加: GEMINI_API_KEY=your_key
# 获取: https://aistudio.google.com/app/apikey

# 2. 验证安装
/autofigure/generate --help
```

## 使用方式

### 命令行

```bash
# 基本用法 - 生成插图
/autofigure/generate "论文方法文本描述"

# 指定输出名称
/autofigure/generate "方法文本" my_figure_name

# 带参考图进行风格迁移
/autofigure/generate "方法文本" output_name --reference /path/to/ref.png

# 完整示例
/autofigure/generate "我们提出了一个三阶段的训练流程：第一阶段使用预训练模型进行特征提取，第二阶段采用对比学习优化表示，第三阶段通过强化学习微调策略..." my_method --reference ./reference.png
```

### OpenClaw 调用

当用户需要生成论文插图时，直接调用：

```
/autofigure/generate "{论文方法文本}"
```

**示例对话**:
> User: "帮我生成一个流程图，描述：首先输入数据经过编码器提取特征，然后通过注意力机制计算权重，最后输出预测结果"
> 
> Assistant: 调用 `/autofigure/generate "首先输入数据经过编码器提取特征..."`

## 输出

生成文件保存在 `~/User_Services/autofigure-edit/outputs/{name}/`:

| 文件 | 说明 |
|------|------|
| `final.svg` | 最终可编辑 SVG ⭐ |
| `figure.png` | 原始生成图像 |
| `samed.png` | SAM3 分割标记图 |
| `template.svg` | SVG 模板 |
| `icons/` | 透明背景图标集合 |

## 技术栈

| 组件 | 类型 | 来源 |
|------|------|------|
| Gemini-3-Pro-Image | API | Google AI Studio |
| SAM3 | 本地 | Meta Research |
| RMBG-2.0 | 本地 | BRIA AI |
| FastAPI | 后端 | - |

## 项目链接

- **项目**: https://github.com/ResearAI/AutoFigure-Edit
- **论文**: AutoFigure: Generating and Refining Publication-Ready Scientific Illustrations (ICLR 2026)
- **数据集**: https://huggingface.co/datasets/WestlakeNLP/FigureBench

## 故障排除

### API Key 未配置
```
错误: 未配置 GEMINI_API_KEY
解决: 编辑 ~/.env 添加 GEMINI_API_KEY=your_key
```

### 模型下载
首次运行会自动下载 SAM3 和 RMBG-2.0 模型，需要 HuggingFace 登录:
```bash
huggingface-cli login
```

### GPU 内存不足
如果 CUDA OOM，尝试关闭其他 GPU 进程或减少并发。

## 文件结构

```
~/clawd/skills/autofigure/
├── SKILL.md              # 本文件
├── scripts/
│   ├── generate          # 命令入口
│   └── generate.py       # Python 实现
└── bin/
    └── autofigure-generate  # 命令链接
```
