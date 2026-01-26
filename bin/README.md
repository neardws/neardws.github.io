# bin/ helpers

Two local shortcuts for the "plan with Droid, implement with coding agents" workflow.

## plan

One-shot planning via `droid exec` (read-only by default).

```bash
bin/plan "Create a step-by-step plan to ..."
# or
bin/plan -f prompt.md
```

Defaults:
- model: `claude-opus-4-5-20251101`
- cwd: current directory

Override env vars:
- `DROID_PLAN_MODEL=...`
- `DROID_CWD=...`

## dev

Interactive agent entrypoint. **Must be run in a real terminal (TTY)**.

```bash
bin/dev                 # defaults to droid (interactive)
DEV_AGENT=codex bin/dev
DEV_AGENT=claude bin/dev
DEV_AGENT=opencode bin/dev
```
