#!/bin/bash

#===============================================================================
# Vibe Coding 环境一键配置脚本
# 
# 功能：自动安装和配置 Vibe Coding 所需的全部工具
# 支持：macOS, Ubuntu/Debian, Arch Linux
# 
# 使用方法：
#   curl -fsSL https://neardws.com/scripts/vibe-setup.sh | bash
#
# 或下载后执行：
#   chmod +x vibe-setup.sh
#   ./vibe-setup.sh
#===============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo -e "\n${PURPLE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}════════════════════════════════════════════════════════════${NC}\n"
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    elif [[ -f /etc/debian_version ]]; then
        OS="debian"
        PACKAGE_MANAGER="apt"
    elif [[ -f /etc/arch-release ]]; then
        OS="arch"
        PACKAGE_MANAGER="pacman"
    else
        OS="unknown"
        PACKAGE_MANAGER="unknown"
    fi
    print_info "检测到操作系统: $OS (包管理器: $PACKAGE_MANAGER)"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" &> /dev/null
}

# 询问用户是否继续
ask_continue() {
    local prompt="$1"
    local default="${2:-y}"
    
    if [[ "$default" == "y" ]]; then
        prompt="$prompt [Y/n] "
    else
        prompt="$prompt [y/N] "
    fi
    
    read -p "$prompt" response
    response=${response:-$default}
    
    [[ "$response" =~ ^[Yy]$ ]]
}

#===============================================================================
# 安装函数
#===============================================================================

# 安装 Homebrew (macOS)
install_homebrew() {
    if [[ "$OS" != "macos" ]]; then
        return
    fi
    
    if command_exists brew; then
        print_success "Homebrew 已安装"
        return
    fi
    
    print_step "安装 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # 添加到 PATH
    if [[ -f /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    
    print_success "Homebrew 安装完成"
}

# 安装 Kitty 终端
install_kitty() {
    print_step "安装 Kitty 终端..."
    
    if command_exists kitty; then
        print_success "Kitty 已安装: $(kitty --version)"
        return
    fi
    
    case $OS in
        macos)
            brew install --cask kitty
            ;;
        debian)
            curl -L https://sw.kovidgoyal.net/kitty/installer.sh | sh /dev/stdin launch=n
            # 创建符号链接
            mkdir -p ~/.local/bin
            ln -sf ~/.local/kitty.app/bin/kitty ~/.local/bin/
            ;;
        arch)
            sudo pacman -S --noconfirm kitty
            ;;
    esac
    
    print_success "Kitty 安装完成"
}

# 配置 Kitty
configure_kitty() {
    print_step "配置 Kitty..."
    
    mkdir -p ~/.config/kitty
    
    cat > ~/.config/kitty/kitty.conf << 'EOF'
# Vibe Coding Kitty 配置

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

# Dracula 主题
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
    
    print_success "Kitty 配置完成"
}

# 安装 Zsh
install_zsh() {
    print_step "安装 Zsh..."
    
    if command_exists zsh; then
        print_success "Zsh 已安装: $(zsh --version)"
    else
        case $OS in
            macos)
                # macOS 自带 zsh
                ;;
            debian)
                sudo apt update && sudo apt install -y zsh
                ;;
            arch)
                sudo pacman -S --noconfirm zsh
                ;;
        esac
        print_success "Zsh 安装完成"
    fi
    
    # 设置为默认 Shell
    if [[ "$SHELL" != *"zsh"* ]]; then
        print_step "设置 Zsh 为默认 Shell..."
        chsh -s $(which zsh)
        print_success "默认 Shell 已设置为 Zsh"
    fi
}

# 安装 Oh-My-Zsh
install_ohmyzsh() {
    print_step "安装 Oh-My-Zsh..."
    
    if [[ -d "$HOME/.oh-my-zsh" ]]; then
        print_success "Oh-My-Zsh 已安装"
        return
    fi
    
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    
    print_success "Oh-My-Zsh 安装完成"
}

# 安装 Powerlevel10k
install_powerlevel10k() {
    print_step "安装 Powerlevel10k 主题..."
    
    local P10K_DIR="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k"
    
    if [[ -d "$P10K_DIR" ]]; then
        print_success "Powerlevel10k 已安装"
        return
    fi
    
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$P10K_DIR"
    
    print_success "Powerlevel10k 安装完成"
}

# 安装 Zsh 插件
install_zsh_plugins() {
    print_step "安装 Zsh 插件..."
    
    local ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
    
    # zsh-autosuggestions
    if [[ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]]; then
        git clone https://github.com/zsh-users/zsh-autosuggestions "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
        print_success "zsh-autosuggestions 安装完成"
    else
        print_success "zsh-autosuggestions 已安装"
    fi
    
    # zsh-syntax-highlighting
    if [[ ! -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]]; then
        git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
        print_success "zsh-syntax-highlighting 安装完成"
    else
        print_success "zsh-syntax-highlighting 已安装"
    fi
}

# 安装 Nerd Font
install_nerd_font() {
    print_step "安装 Nerd Font (MesloLGS NF)..."
    
    case $OS in
        macos)
            brew tap homebrew/cask-fonts 2>/dev/null || true
            brew install --cask font-meslo-lg-nerd-font 2>/dev/null || print_warning "字体可能已安装"
            ;;
        *)
            mkdir -p ~/.local/share/fonts
            cd ~/.local/share/fonts
            
            local FONTS=(
                "MesloLGS%20NF%20Regular.ttf"
                "MesloLGS%20NF%20Bold.ttf"
                "MesloLGS%20NF%20Italic.ttf"
                "MesloLGS%20NF%20Bold%20Italic.ttf"
            )
            
            for font in "${FONTS[@]}"; do
                local filename=$(echo "$font" | sed 's/%20/ /g')
                if [[ ! -f "$filename" ]]; then
                    curl -fLo "$filename" "https://github.com/romkatv/powerlevel10k-media/raw/master/$font"
                fi
            done
            
            fc-cache -fv
            cd - > /dev/null
            ;;
    esac
    
    print_success "Nerd Font 安装完成"
}

# 配置 .zshrc
configure_zshrc() {
    print_step "配置 .zshrc..."
    
    # 备份现有配置
    if [[ -f ~/.zshrc ]]; then
        cp ~/.zshrc ~/.zshrc.backup.$(date +%Y%m%d%H%M%S)
        print_info "已备份现有 .zshrc"
    fi
    
    cat > ~/.zshrc << 'EOF'
# Vibe Coding Zsh 配置

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
    docker
    npm
)

source $ZSH/oh-my-zsh.sh

# User configuration

# Aliases
alias ll="ls -la"
alias cls="clear"
alias ..="cd .."
alias ...="cd ../.."
alias g="git"
alias d="droid"

# Node.js (nvm)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# PATH
export PATH="$HOME/.local/bin:$PATH"

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
EOF
    
    print_success ".zshrc 配置完成"
}

# 安装 Node.js
install_nodejs() {
    print_step "安装 Node.js..."
    
    if command_exists node; then
        print_success "Node.js 已安装: $(node --version)"
        return
    fi
    
    # 使用 nvm 安装
    if [[ ! -d "$HOME/.nvm" ]]; then
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    fi
    
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    
    nvm install --lts
    nvm use --lts
    
    print_success "Node.js 安装完成: $(node --version)"
}

# 安装 Factory Droid
install_factory_droid() {
    print_step "安装 Factory Droid..."
    
    if command_exists droid; then
        print_success "Factory Droid 已安装: $(droid --version 2>/dev/null || echo 'version unknown')"
        return
    fi
    
    # 确保 npm 可用
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    
    npm install -g @anthropic-ai/droid
    
    print_success "Factory Droid 安装完成"
    print_info "请运行 'droid login' 完成登录"
}

# 创建 Factory 目录结构
setup_factory_dirs() {
    print_step "创建 Factory 目录结构..."
    
    mkdir -p ~/.factory/skills
    mkdir -p ~/.factory/droids
    
    print_success "Factory 目录结构创建完成"
}

# 创建 MCP 配置模板
setup_mcp_config() {
    print_step "创建 MCP 配置模板..."
    
    if [[ -f ~/.factory/mcp.json ]]; then
        print_warning "MCP 配置已存在，跳过"
        return
    fi
    
    cat > ~/.factory/mcp.json << 'EOF'
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-filesystem", "~/Documents", "~/Projects"]
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-fetch"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-memory"]
    }
  }
}
EOF
    
    print_success "MCP 配置模板创建完成"
    print_info "请根据需要编辑 ~/.factory/mcp.json"
}

# 安装推荐 Skills
install_skills() {
    print_step "安装推荐 Skills..."
    
    local SKILLS_DIR="$HOME/.factory/skills"
    
    # superpowers
    if [[ ! -d "$SKILLS_DIR/superpowers" ]]; then
        git clone --depth=1 https://github.com/obra/superpowers "$SKILLS_DIR/superpowers" 2>/dev/null || print_warning "superpowers 安装失败"
    fi
    
    # planning-with-files
    if [[ ! -d "$SKILLS_DIR/planning-with-files" ]]; then
        git clone --depth=1 https://github.com/OthmanAdi/planning-with-files "$SKILLS_DIR/planning-with-files" 2>/dev/null || print_warning "planning-with-files 安装失败"
    fi
    
    print_success "推荐 Skills 安装完成"
}

# 创建示例 Custom Droid
create_sample_droid() {
    print_step "创建示例 Custom Droid..."
    
    local DROID_DIR="$HOME/.factory/droids/code-reviewer"
    
    if [[ -d "$DROID_DIR" ]]; then
        print_warning "示例 Droid 已存在，跳过"
        return
    fi
    
    mkdir -p "$DROID_DIR"
    
    cat > "$DROID_DIR/DROID.md" << 'EOF'
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
    
    print_success "示例 Custom Droid 创建完成"
}

#===============================================================================
# 主程序
#===============================================================================

main() {
    print_header "🚀 Vibe Coding 环境一键配置"
    
    echo -e "本脚本将安装和配置以下组件:\n"
    echo "  1. Kitty 终端"
    echo "  2. Zsh + Oh-My-Zsh + Powerlevel10k"
    echo "  3. Zsh 插件 (autosuggestions, syntax-highlighting)"
    echo "  4. Nerd Font"
    echo "  5. Node.js"
    echo "  6. Factory Droid"
    echo "  7. Skills 和 MCP 配置"
    echo ""
    
    if ! ask_continue "是否继续安装?"; then
        echo "安装已取消"
        exit 0
    fi
    
    # 检测操作系统
    detect_os
    
    if [[ "$OS" == "unknown" ]]; then
        print_error "不支持的操作系统"
        exit 1
    fi
    
    # 安装 Homebrew (macOS)
    install_homebrew
    
    # 安装组件
    print_header "📦 安装终端和 Shell"
    install_kitty
    configure_kitty
    install_zsh
    install_ohmyzsh
    install_powerlevel10k
    install_zsh_plugins
    install_nerd_font
    configure_zshrc
    
    print_header "📦 安装开发工具"
    install_nodejs
    install_factory_droid
    
    print_header "⚙️ 配置 Factory Droid"
    setup_factory_dirs
    setup_mcp_config
    install_skills
    create_sample_droid
    
    print_header "✅ 安装完成!"
    
    echo -e "\n${GREEN}Vibe Coding 环境配置完成!${NC}\n"
    echo "后续步骤:"
    echo "  1. 重启终端或运行: source ~/.zshrc"
    echo "  2. 首次启动会运行 Powerlevel10k 配置向导"
    echo "  3. 运行 'droid login' 登录 Factory"
    echo "  4. 编辑 ~/.factory/settings.json 配置 API Key"
    echo "  5. 在项目目录运行 'droid' 开始使用"
    echo ""
    echo -e "${CYAN}享受 Vibe Coding! 🎉${NC}"
}

# 运行主程序
main "$@"
