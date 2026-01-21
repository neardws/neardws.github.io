# Vibe Coding 环境配置指南 (LLM Agent 版)

> 本文档专为 LLM Agent (如 Warp AI, Factory Droid, Claude Code) 设计，包含完整的配置命令和文件内容。
> 请将此文档复制给 AI Agent，让它自动帮你完成环境配置。

---

## 配置概览

1. 终端配置 (Kitty)
2. Shell 配置 (Oh-My-Zsh + Powerlevel10k)
3. Factory Droid 安装
4. BYOK 模型配置
5. Skills 安装
6. MCP 配置
7. Custom Droids 设置

---

## 1. 终端配置 (Kitty)

### 安装 Kitty

```bash
# macOS
brew install --cask kitty

# Ubuntu/Debian
curl -L https://sw.kovidgoyal.net/kitty/installer.sh | sh /dev/stdin

# Arch Linux
sudo pacman -S kitty
```

### 创建 Kitty 配置文件

```bash
mkdir -p ~/.config/kitty
cat > ~/.config/kitty/kitty.conf << 'EOF'
# 字体配置
font_family      MesloLGS NF
bold_font        auto
italic_font      auto
bold_italic_font auto
font_size        14.0

# 窗口配置
window_padding_width 10
hide_window_decorations titlebar-only
background_opacity 0.95

# Tab bar
tab_bar_style powerline
tab_powerline_style slanted

# 快捷键
map cmd+t new_tab_with_cwd
map cmd+w close_tab
map cmd+1 goto_tab 1
map cmd+2 goto_tab 2
map cmd+3 goto_tab 3

# 主题 (Dracula)
foreground            #f8f8f2
background            #282a36
selection_foreground  #ffffff
selection_background  #44475a
color0  #21222c
color1  #ff5555
color2  #50fa7b
color3  #f1fa8c
color4  #bd93f9
color5  #ff79c6
color6  #8be9fd
color7  #f8f8f2
color8  #6272a4
color9  #ff6e6e
color10 #69ff94
color11 #ffffa5
color12 #d6acff
color13 #ff92df
color14 #a4ffff
color15 #ffffff
EOF
```

---

## 2. Shell 配置

### 2.1 安装 Zsh

```bash
# macOS (已预装)
# Ubuntu/Debian
sudo apt update && sudo apt install -y zsh

# 设置为默认 Shell
chsh -s $(which zsh)
```

### 2.2 安装 Oh-My-Zsh

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
```

### 2.3 安装 Powerlevel10k 主题

```bash
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
```

### 2.4 安装插件

```bash
# zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

### 2.5 配置 .zshrc

```bash
cat > ~/.zshrc << 'EOF'
# Path to oh-my-zsh
export ZSH="$HOME/.oh-my-zsh"

# Theme
ZSH_THEME="powerlevel10k/powerlevel10k"

# Plugins
plugins=(
    git
    zsh-autosuggestions
    zsh-syntax-highlighting
    z
    extract
    sudo
)

source $ZSH/oh-my-zsh.sh

# Aliases
alias ll="ls -la"
alias cls="clear"
alias ..="cd .."
alias ...="cd ../.."

# Node.js
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
EOF
```

### 2.6 安装 Nerd Font

```bash
# macOS
brew tap homebrew/cask-fonts
brew install --cask font-meslo-lg-nerd-font

# Linux - 手动下载
mkdir -p ~/.local/share/fonts
cd ~/.local/share/fonts
curl -fLo "MesloLGS NF Regular.ttf" https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Regular.ttf
curl -fLo "MesloLGS NF Bold.ttf" https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Bold.ttf
curl -fLo "MesloLGS NF Italic.ttf" https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Italic.ttf
curl -fLo "MesloLGS NF Bold Italic.ttf" https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Bold%20Italic.ttf
fc-cache -fv
```

---

## 3. Factory Droid 安装

### 3.1 安装 Node.js (如未安装)

```bash
# 使用 nvm 安装
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.zshrc
nvm install --lts
```

### 3.2 安装 Factory Droid

```bash
npm install -g @anthropic-ai/droid
```

### 3.3 登录

```bash
droid login
```

---

## 4. BYOK 配置

### 创建配置文件

```bash
mkdir -p ~/.factory
cat > ~/.factory/settings.json << 'EOF'
{
  "model": "claude-sonnet-4-5-20250514",
  "customApiKey": "YOUR_API_KEY_HERE",
  "permissions": {
    "allowedTools": ["Edit", "Bash", "Read", "Write", "Glob", "Grep"]
  }
}
EOF
```

### 各模型 API 配置示例

#### Anthropic Claude
```json
{
  "model": "claude-sonnet-4-5-20250514",
  "customApiKey": "sk-ant-xxx"
}
```

#### OpenAI GPT
```json
{
  "model": "gpt-4o",
  "apiProvider": "openai",
  "customApiKey": "sk-xxx"
}
```

#### Google Gemini
```json
{
  "model": "gemini-2.0-flash",
  "apiProvider": "google",
  "customApiKey": "xxx"
}
```

#### DeepSeek
```json
{
  "model": "deepseek-chat",
  "apiProvider": "deepseek",
  "customApiKey": "sk-xxx",
  "apiBaseUrl": "https://api.deepseek.com"
}
```

---

## 5. Skills 安装

### 5.1 创建 Skills 目录

```bash
mkdir -p ~/.factory/skills
```

### 5.2 安装推荐 Skills

```bash
# 克隆推荐的 Skills 集合
git clone https://github.com/obra/superpowers ~/.factory/skills/superpowers
git clone https://github.com/OthmanAdi/planning-with-files ~/.factory/skills/planning-with-files
```

### 5.3 创建自定义 Skill 示例

```bash
mkdir -p ~/.factory/skills/my-skill
cat > ~/.factory/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: 我的自定义 Skill
---

# My Custom Skill

## Overview
这是一个自定义 Skill 的示例。

## When to Use
当需要执行特定任务时使用此 Skill。

## Process
1. 分析需求
2. 制定计划
3. 执行任务
4. 验证结果
EOF
```

---

## 6. MCP 配置

### 创建 MCP 配置文件

```bash
cat > ~/.factory/mcp.json << 'EOF'
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-filesystem", "/Users/$USER/Documents", "/Users/$USER/Projects"]
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-fetch"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-memory"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "YOUR_GITHUB_TOKEN"
      }
    }
  }
}
EOF
```

### 常用 MCP Servers

| Server | 用途 | 安装命令 |
|--------|------|----------|
| filesystem | 文件系统访问 | `npx @anthropic-ai/mcp-server-filesystem` |
| fetch | HTTP 请求 | `npx @anthropic-ai/mcp-server-fetch` |
| memory | 持久化记忆 | `npx @anthropic-ai/mcp-server-memory` |
| github | GitHub 操作 | `npx @anthropic-ai/mcp-server-github` |
| postgres | PostgreSQL | `npx @anthropic-ai/mcp-server-postgres` |
| sqlite | SQLite | `npx @anthropic-ai/mcp-server-sqlite` |

---

## 7. Custom Droids 设置

### 7.1 创建目录结构

```bash
# 项目级 Droids
mkdir -p .factory/droids

# 个人级 Droids
mkdir -p ~/.factory/droids
```

### 7.2 创建示例 Custom Droid

```bash
mkdir -p ~/.factory/droids/code-reviewer
cat > ~/.factory/droids/code-reviewer/DROID.md << 'EOF'
---
name: code-reviewer
description: 专业的代码审查助手
model: claude-sonnet-4-5-20250514
---

# Code Reviewer Droid

你是一个专业的代码审查专家。

## 审查重点

1. **代码质量**：检查代码是否清晰、可维护
2. **安全性**：识别潜在的安全漏洞
3. **性能**：发现性能问题和优化机会
4. **最佳实践**：确保遵循语言和框架的最佳实践

## 输出格式

对每个发现的问题，提供：
- 问题描述
- 严重程度 (高/中/低)
- 建议的修复方案
- 代码示例
EOF
```

---

## 8. 验证安装

运行以下命令验证所有组件是否正确安装：

```bash
echo "=== 验证安装 ==="

echo -n "Kitty: " && kitty --version 2>/dev/null || echo "未安装"
echo -n "Zsh: " && zsh --version
echo -n "Oh-My-Zsh: " && [ -d ~/.oh-my-zsh ] && echo "已安装" || echo "未安装"
echo -n "Powerlevel10k: " && [ -d ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k ] && echo "已安装" || echo "未安装"
echo -n "Node.js: " && node --version
echo -n "Factory Droid: " && droid --version 2>/dev/null || echo "未安装"
echo -n "Skills 目录: " && [ -d ~/.factory/skills ] && echo "存在" || echo "不存在"
echo -n "MCP 配置: " && [ -f ~/.factory/mcp.json ] && echo "存在" || echo "不存在"

echo "=== 验证完成 ==="
```

---

## 完成

配置完成后，重启终端或运行 `source ~/.zshrc` 使配置生效。

首次启动 Powerlevel10k 时会自动运行配置向导，按提示选择你喜欢的样式即可。

开始使用 Factory Droid：
```bash
cd your-project
droid
```

享受 Vibe Coding！🎉
