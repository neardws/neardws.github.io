# tmuxd (tmux 编排 + 进度采集)

这套脚本用一个**独立 tmux socket** 来管理多个 droid 实例，并提供：
- 批量启动/停止
- 查看每个实例的“最新进度行”
- 拉取最近 N 行日志

> 默认不会影响你日常 tmux（因为走独立 socket）。

## 0) 依赖
- `tmux` 在 PATH
- bash
- python3（用于更靠谱的状态解析）

## 1) 环境变量（可选）
- `TMUXD_SOCKET`：tmux socket 路径
- `TMUXD_PREFIX`：实例 session 名前缀（默认 `droid-`）
- `TMUXD_ENV_FILE`：启动时自动 `source` 的环境文件（推荐用来注入 `FACTORY_API_KEY`）

默认：
- socket: `/tmp/clawdbot-tmux-sockets/clawdbot.sock`
- prefix: `droid-`

## 2) 常用命令
在仓库根目录：

```bash
# 列出所有实例
./tmuxd/bin/tmuxctl list

# （推荐）注入 Factory API key 文件
export TMUXD_ENV_FILE=~/.config/factory/env

# 启动一个实例（name=foo），运行你的 droid 命令
# 说明：如果你要自动化/可抓取结果，推荐用 droid exec + json 输出（text 输出可能会走 TUI/清屏）
./tmuxd/bin/tmuxctl start foo -- droid exec "say hello" --cwd "$PWD" --output-format json --auto low

# 更推荐：用 tmuxctl 封装好的 droid-exec / droid-continue（多轮 session-id 推进）
./tmuxd/bin/tmuxctl droid-exec arch -- "analyze this codebase and explain the overall architecture" --cwd "$PWD" --auto low
./tmuxd/bin/tmuxctl session-id arch
./tmuxd/bin/tmuxctl droid-continue arch -- "继续：给出更细的模块划分和主要入口文件" --cwd "$PWD" --auto low

# 查看实例状态（抓取最后 200 行并解析）
./tmuxd/bin/tmuxctl status

# 查看某个实例最近 200 行日志
./tmuxd/bin/tmuxctl log foo -n 200

# 进入交互（需要时）
./tmuxd/bin/tmuxctl attach foo

# 停止实例
./tmuxd/bin/tmuxctl stop foo
```

## 3) 进度采集的规则（当前版本）
`status` 会对每个实例抓取最近 400 行并做简单分类：
- 命中 `ERROR|Exception|Traceback|fatal` → `ERROR`
- 命中 `DONE|Completed|Success|Finished` → `DONE`
- pane 已退出 → `EXITED`
- 否则 → `RUNNING`

并显示：
- 最后一条非空输出行（当作“进度行”）

你把 droid 的典型输出贴我一下，我可以把规则调得更准（例如解析百分比/阶段）。
