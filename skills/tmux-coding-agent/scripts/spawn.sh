#!/bin/bash
# Spawn a coding agent in a tmux session with PTY support
# Usage: ./spawn.sh <session-name> <task-description> [agent-type] [--auto-level <level>]

set -e

SESSION_NAME="$1"
TASK="$2"
AGENT="${3:-claude}"  # Default to claude
AUTO_LEVEL=""
INTERACTIVE="false"

# Parse optional arguments
shift 3
while [[ $# -gt 0 ]]; do
    case "$1" in
        --auto|--auto-level)
            AUTO_LEVEL="$2"
            shift 2
            ;;
        --interactive|-i)
            INTERACTIVE="true"
            shift
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$SESSION_NAME" ] || [ -z "$TASK" ]; then
    echo "Usage: $0 <session-name> <task-description> [agent-type] [options]"
    echo ""
    echo "Available agents: claude, codex, droid, opencode, gemini"
    echo ""
    echo "Options:"
    echo "  --auto-level <level>  Auto level for droid exec: low|medium|high"
    echo "  --interactive, -i     Run in interactive mode (TUI) instead of exec"
    echo ""
    echo "Examples:"
    echo "  $0 fix-bug 'Fix the login validation' claude"
    echo "  $0 refactor 'Refactor auth module' droid --auto-level medium"
    echo "  $0 chat 'Help me debug' droid --interactive"
    exit 1
fi

# Check if tmux is available
if ! command -v tmux &> /dev/null; then
    echo "Error: tmux is not installed"
    exit 1
fi

# Check if session already exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Error: Session '$SESSION_NAME' already exists"
    echo "Use: tmux attach -t $SESSION_NAME"
    exit 1
fi

# Get current directory
WORK_DIR="$(pwd)"

# Prepare agent command
case "$AGENT" in
    claude)
        # Claude Code - needs git repo, runs in interactive mode
        if [ ! -d "$WORK_DIR/.git" ]; then
            echo "Warning: $WORK_DIR is not a git repo. Claude may refuse to run."
        fi
        # Use --model to specify model (litellm model name)
        # Export env vars to ensure Claude Code uses correct API settings
        CMD="export ANTHROPIC_API_KEY='sk-litellm-neardws-1770801720' && export ANTHROPIC_BASE_URL='http://localhost:4000' && claude --model foxcode-claude-opus-4-6 \"$TASK\""
        ;;
    codex)
        # Codex CLI - one-shot mode
        CMD="codex exec \"$TASK\""
        ;;
    droid)
        # Droid - can be interactive or exec mode
        if [ "$INTERACTIVE" = "true" ]; then
            # Interactive mode (TUI)
            CMD="droid \"$TASK\""
        else
            # Exec mode with auto level
            if [ -n "$AUTO_LEVEL" ]; then
                CMD="droid exec --auto $AUTO_LEVEL \"$TASK\""
            else
                CMD="droid exec \"$TASK\""
            fi
        fi
        ;;
    opencode)
        # Opencode
        CMD="opencode run \"$TASK\""
        ;;
    gemini)
        # Gemini CLI (if available)
        if command -v gemini &> /dev/null; then
            CMD="gemini \"$TASK\""
        else
            echo "Error: gemini CLI not found. Using claude instead."
            CMD="claude \"$TASK\""
        fi
        ;;
    *)
        echo "Error: Unknown agent '$AGENT'"
        echo "Available: claude, codex, droid, opencode, gemini"
        exit 1
        ;;
esac

# Create tmux session with PTY support
echo "Spawning $AGENT agent in tmux session: $SESSION_NAME"
echo "Working directory: $WORK_DIR"
[ -n "$AUTO_LEVEL" ] && echo "Auto level: $AUTO_LEVEL"
echo "Task: $TASK"
echo ""

tmux new-session -d -s "$SESSION_NAME" -c "$WORK_DIR"

# Send the command to the session
tmux send-keys -t "$SESSION_NAME" "$CMD" Enter

echo "✅ Session '$SESSION_NAME' started"
echo ""
echo "Commands:"
echo "  Attach:     tmux attach -t $SESSION_NAME"
echo "  Check log:  ./skills/tmux-coding-agent/scripts/log.sh $SESSION_NAME"
echo "  Status:     ./skills/tmux-coding-agent/scripts/status.sh $SESSION_NAME"
echo "  Send input: ./skills/tmux-coding-agent/scripts/send.sh $SESSION_NAME 'your text'"
echo "  Kill:       ./skills/tmux-coding-agent/scripts/kill.sh $SESSION_NAME"
