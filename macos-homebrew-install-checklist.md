# Homebrew Installation Checklist for macOS (arm64)

## Prerequisites
```bash
# Check if Homebrew is installed
brew --version

# If not installed, install Homebrew (official script)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## PATH Configuration (Non-Interactive Shells)
```bash
# Add to ~/.zshrc or ~/.bash_profile
export PATH="/opt/homebrew/bin:$PATH"

# Verify PATH is set correctly
echo $PATH | grep -q "/opt/homebrew/bin" && echo "PATH configured" || echo "PATH missing"
```

## Core Packages Installation
```bash
# Essential packages for Clawdbot
brew install git
brew install curl
brew install wget
brew install jq
brew install yq
brew install tmux
brew install vim
brew install nano
brew install tree
brew install unzip
brew install zip
brew install openssl
brew install readline
brew install sqlite3
brew install postgresql
brew install redis
brew install node
brew install python@3.11
brew install ffmpeg
brew install imagemagick
brew install fswatch
brew install coreutils
```

## Verification Commands
```bash
# Verify all installed packages
for pkg in git curl wget jq yq tmux vim nano tree unzip zip openssl readline sqlite3 postgresql redis node python@3.11 ffmpeg imagemagick fswatch coreutils; do
  brew list --versions $pkg 2>/dev/null || echo "MISSING: $pkg"
done

# Check specific versions
git --version
curl --version
wget --version || echo "wget not available (use curl)"
jq --version
node --version
python3 --version

# Verify services (if needed)
brew services list | grep -E "(postgresql|redis|mysql)" || echo "No services configured"
```

## Important Notes
```bash
# DO NOT install: rewind cask (deprecated)
# Skip: brew install --cask rewind  # REMOVED - Do not use

# Clean up old kegs
brew cleanup -s

# Update Homebrew
brew update

# Check for issues
brew doctor
```

## Troubleshooting
```bash
# If brew command not found in new shell
source ~/.zshrc  # or source ~/.bash_profile

# Fix permissions if needed
sudo chown -R $(whoami) /opt/homebrew

# Reinstall missing formula
brew install <formula-name>
```
