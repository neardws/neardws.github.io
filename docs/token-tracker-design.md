# Token Tracker Design Document

## 1. Research Findings

### 1.1 OpenClaw Token Data Sources

**Session JSONL Files** (`~/.openclaw/agents/{agent}/sessions/*.jsonl`)
- Each message contains `usage` object with token counts:
```json
{
  "usage": {
    "input": 101,
    "output": 88,
    "cacheRead": 9344,
    "cacheWrite": 0,
    "totalTokens": 9533,
    "cost": {
      "input": 0.00017675,
      "output": 0.001232,
      "cacheRead": 0.0016352,
      "cacheWrite": 0,
      "total": 0.00304395
    }
  },
  "provider": "openai-codex",
  "model": "gpt-5.2"
}
```
- Models tracked: Opus (anthropic), Kimi K2.5 (kimi), MiniMax (minimax-portal)
- Files are JSONL format with `type: "message"` entries containing usage

**Hooks Available** (`openclaw.json` -> `hooks.internal`)
- `boot-md`, `command-logger`, `session-memory` hooks exist
- Can potentially add custom hook for token logging

**Plugin System**
- Plugins at `plugins.load.paths` can intercept requests
- `clawdbot-local-memory` plugin exists as reference

### 1.2 Coding Agents Log Formats

| Agent | Log Location | Format | Token Info |
|-------|-------------|--------|------------|
| **Droid (Factory)** | `~/.factory/logs/droid-log-single.log` | JSON lines | No direct token counts in log |
| **Codex CLI** | `~/.codex/sessions/YYYY/MM/DD/*.jsonl` | JSONL | Session metadata, no usage |
| **Gemini CLI** | `~/.gemini/tmp/{hash}/logs.json` | JSON | Empty arrays observed |
| **Claude Code** | `~/.claude/transcripts/ses_*.jsonl` | JSONL | Minimal (user messages only) |

**Note:** Coding agents don't expose token usage directly in logs. Need alternative approaches:
1. Parse API response headers if available
2. Use provider's usage APIs
3. Estimate based on message length

### 1.3 MiniMax Usage Script Analysis

`~/User_Services/services-logs/minimax-usage.sh`:
- Reads API key from `~/.clawdbot/agents/main/agent/auth-profiles.json`
- Two endpoints:
  - `coding_plan/remains` - prompts/plan usage
  - `anthropic/v1/messages` - token inference call
- Can be extended for token tracking

---

## 2. Architecture Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        Token Tracker                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Ingestors  │    │   SQLite DB  │    │    CLI/Web   │      │
│  │              │    │              │    │              │      │
│  │ • OpenClaw   │───▶│ • usage      │◀───│ • tt query   │      │
│  │   Sessions   │    │ • sessions   │    │ • tt report  │      │
│  │ • MiniMax    │    │ • providers  │    │ • Web UI     │      │
│  │   API        │    │ • models     │    │   (optional) │      │
│  │ • Agent Logs │    │              │    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    OpenClaw Plugin                        │  │
│  │  • Post-response hook captures usage in real-time        │  │
│  │  • Writes directly to SQLite                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Components

1. **Ingestors** - Data collectors for each source
2. **SQLite Database** - Central storage
3. **CLI Tool** (`tt`) - Query and reporting
4. **OpenClaw Plugin** - Real-time capture (recommended)
5. **Web UI** - Optional dashboard

---

## 3. Data Model

### 3.1 Database Schema

```sql
-- Providers (anthropic, kimi, minimax, openai-codex, etc.)
CREATE TABLE providers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Models
CREATE TABLE models (
    id INTEGER PRIMARY KEY,
    provider_id INTEGER NOT NULL REFERENCES providers(id),
    model_id TEXT NOT NULL,
    display_name TEXT,
    cost_input_per_1m REAL DEFAULT 0,
    cost_output_per_1m REAL DEFAULT 0,
    cost_cache_read_per_1m REAL DEFAULT 0,
    cost_cache_write_per_1m REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider_id, model_id)
);

-- Sources (openclaw, droid, codex, gemini, claude)
CREATE TABLE sources (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT
);

-- Sessions
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    session_id TEXT NOT NULL,
    agent_id TEXT,
    started_at TIMESTAMP,
    cwd TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, session_id)
);

-- Usage records (main tracking table)
CREATE TABLE usage (
    id INTEGER PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id),
    model_id INTEGER NOT NULL REFERENCES models(id),
    source_id INTEGER NOT NULL REFERENCES sources(id),
    
    -- Token counts
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cache_read_tokens INTEGER DEFAULT 0,
    cache_write_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    
    -- Cost (in USD)
    cost_input REAL DEFAULT 0,
    cost_output REAL DEFAULT 0,
    cost_cache_read REAL DEFAULT 0,
    cost_cache_write REAL DEFAULT 0,
    cost_total REAL DEFAULT 0,
    
    -- Metadata
    stop_reason TEXT,
    message_id TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- For deduplication
    UNIQUE(source_id, session_id, message_id)
);

-- Indexes for common queries
CREATE INDEX idx_usage_recorded_at ON usage(recorded_at);
CREATE INDEX idx_usage_model_id ON usage(model_id);
CREATE INDEX idx_usage_source_id ON usage(source_id);
CREATE INDEX idx_usage_session_id ON usage(session_id);

-- Daily aggregates (materialized view pattern)
CREATE TABLE daily_usage (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    model_id INTEGER NOT NULL REFERENCES models(id),
    source_id INTEGER NOT NULL REFERENCES sources(id),
    
    request_count INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cache_read_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_total REAL DEFAULT 0,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, model_id, source_id)
);
```

### 3.2 Sample Seed Data

```sql
-- Providers
INSERT INTO providers (name, display_name) VALUES
    ('anthropic', 'Anthropic (Opus中转站)'),
    ('kimi', 'Moonshot (Kimi K2.5)'),
    ('minimax-portal', 'MiniMax'),
    ('openai-codex', 'OpenAI Codex');

-- Sources
INSERT INTO sources (name, display_name) VALUES
    ('openclaw', 'OpenClaw Gateway'),
    ('droid', 'Factory Droid'),
    ('codex', 'Codex CLI'),
    ('gemini', 'Gemini CLI'),
    ('claude', 'Claude Code');

-- Models
INSERT INTO models (provider_id, model_id, display_name) VALUES
    (1, 'claude-opus-4-5-20251101', 'Claude Opus 4.5'),
    (2, 'kimi-k2-0711', 'Kimi K2.5'),
    (2, 'kimi-for-coding', 'Kimi K2.5 Turbo'),
    (3, 'MiniMax-M2.1', 'MiniMax M2.1'),
    (3, 'MiniMax-M2.1-lightning', 'MiniMax M2.1 Lightning'),
    (4, 'gpt-5.2', 'GPT-5.2');
```

---

## 4. Implementation Plan

### Phase 1: Core Infrastructure (Day 1-2)

1. **Create project structure**
```
~/clawd/services/token-tracker/
├── src/
│   ├── db/
│   │   ├── schema.sql
│   │   └── init.py
│   ├── ingestors/
│   │   ├── openclaw.py      # Main ingestor
│   │   ├── minimax_api.py   # Direct API query
│   │   └── base.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── commands.py
│   └── web/                  # Optional
│       └── app.py
├── tt                        # CLI entry point (symlink to /usr/local/bin)
├── pyproject.toml
└── README.md
```

2. **Initialize SQLite database**
   - Location: `~/.openclaw/token-tracker.db`
   - Run schema.sql on first launch

3. **Build OpenClaw session ingestor**
   - Parse `~/.openclaw/agents/*/sessions/*.jsonl`
   - Extract usage from `type: "message"` entries
   - Handle deduplication via message_id

### Phase 2: CLI Tool (Day 2-3)

**Commands:**
```bash
# Ingest data
tt ingest                     # Run all ingestors
tt ingest openclaw            # OpenClaw sessions only
tt ingest --since 2026-01-01  # From specific date

# Query usage
tt usage                      # Today's usage
tt usage --range 7d           # Last 7 days
tt usage --model opus         # Filter by model
tt usage --source openclaw    # Filter by source

# Reports
tt report daily               # Daily breakdown
tt report weekly              # Weekly summary
tt report monthly             # Monthly totals
tt report --csv               # Export as CSV

# Status
tt status                     # Show DB stats and last ingest
```

### Phase 3: Real-time Capture Plugin (Day 3-4)

**OpenClaw Plugin Structure:**
```
~/clawd/plugins/token-tracker-plugin/
├── package.json
├── dist/
│   └── index.js
└── src/
    └── index.ts
```

**Plugin hooks:**
- `onResponse` - Capture usage after each LLM response
- Writes directly to SQLite (no polling needed)

### Phase 4: Optional Web UI (Day 4-5)

Simple Flask/FastAPI dashboard:
- `/` - Dashboard with charts
- `/api/usage` - JSON API for usage data
- Charts: daily trends, model breakdown, cost analysis

Tech stack options:
- **Minimal:** Flask + Chart.js + vanilla HTML
- **Modern:** FastAPI + Vue/React SPA

---

## 5. File Structure

```
~/clawd/services/token-tracker/
├── src/
│   ├── __init__.py
│   ├── config.py             # Paths, DB location
│   ├── db/
│   │   ├── __init__.py
│   │   ├── schema.sql
│   │   ├── connection.py     # SQLite connection manager
│   │   └── queries.py        # Common queries
│   ├── ingestors/
│   │   ├── __init__.py
│   │   ├── base.py           # Base ingestor class
│   │   ├── openclaw.py       # OpenClaw session parser
│   │   └── minimax.py        # MiniMax API usage
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py           # Click CLI app
│   │   ├── ingest.py         # ingest commands
│   │   ├── usage.py          # usage queries
│   │   └── report.py         # report generation
│   └── web/                   # Optional
│       ├── __init__.py
│       ├── app.py            # Flask/FastAPI app
│       ├── templates/
│       │   └── dashboard.html
│       └── static/
│           └── charts.js
├── tests/
│   ├── test_ingestors.py
│   └── test_queries.py
├── tt                         # CLI entry script
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 6. Key Implementation Details

### 6.1 OpenClaw Session Parser

```python
# Pseudocode for openclaw.py
def parse_session_file(path: Path) -> List[UsageRecord]:
    records = []
    with open(path) as f:
        for line in f:
            entry = json.loads(line)
            if entry.get('type') == 'message' and 'usage' in entry.get('message', {}):
                msg = entry['message']
                usage = msg['usage']
                records.append(UsageRecord(
                    message_id=entry['id'],
                    provider=msg.get('provider'),
                    model=msg.get('model'),
                    input_tokens=usage.get('input', 0),
                    output_tokens=usage.get('output', 0),
                    cache_read=usage.get('cacheRead', 0),
                    cache_write=usage.get('cacheWrite', 0),
                    cost=usage.get('cost', {}).get('total', 0),
                    timestamp=entry.get('timestamp')
                ))
    return records
```

### 6.2 Incremental Ingestion

- Track last processed position per session file
- Store in `ingest_state` table:
```sql
CREATE TABLE ingest_state (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    file_path TEXT NOT NULL,
    last_position INTEGER DEFAULT 0,
    last_message_id TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, file_path)
);
```

### 6.3 MiniMax API Integration

Extend existing `minimax-usage.sh` logic:
```python
def fetch_minimax_usage(api_key: str) -> dict:
    # Plan/prompt usage
    plan_resp = requests.get(
        "https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    return plan_resp.json()
```

---

## 7. CLI Usage Examples

```bash
# Full ingest of OpenClaw sessions
$ tt ingest
Ingesting OpenClaw sessions...
  - agent:main: 523 new records
  - agent:telegram-fast: 87 new records
  - agent:voice-assistant: 42 new records
Total: 652 records ingested

# Today's usage summary
$ tt usage
Date: 2026-02-04

Model               │ Requests │ Input │ Output │ Cost
─────────────────────────────────────────────────────
Claude Opus 4.5     │      47  │ 125K  │  38K   │ $2.45
MiniMax M2.1        │      23  │  45K  │  12K   │ $0.18
Kimi K2.5           │      12  │  28K  │   8K   │ $0.08
─────────────────────────────────────────────────────
Total               │      82  │ 198K  │  58K   │ $2.71

# Weekly report
$ tt report weekly
Week 2026-W05 (Jan 27 - Feb 02)

Day        │ Opus  │ MiniMax │ Kimi  │ Total
────────────────────────────────────────────
Mon 27     │ $1.20 │  $0.15  │ $0.05 │ $1.40
Tue 28     │ $2.80 │  $0.22  │ $0.10 │ $3.12
...
────────────────────────────────────────────
Weekly Tot │ $18.5 │  $1.45  │ $0.62 │ $20.57
```

---

## 8. Future Enhancements

1. **Alerting** - Notify when daily spend exceeds threshold
2. **Budget caps** - Warn/block when approaching limits
3. **Agent comparison** - Usage breakdown by agent
4. **Grafana integration** - Export metrics for dashboards
5. **Coding agent tracking** - Parse Droid/Codex logs if format improves
6. **Cost estimation** - Predict monthly spend based on trends

---

## 9. Dependencies

```toml
[project]
dependencies = [
    "click>=8.0",        # CLI framework
    "rich>=13.0",        # Terminal formatting
    "python-dateutil",   # Date parsing
    "httpx",             # HTTP client (for API calls)
]

[project.optional-dependencies]
web = [
    "flask>=3.0",
    "plotly",            # Charts
]
```

---

## 10. Quick Start (After Implementation)

```bash
# Install
cd ~/clawd/services/token-tracker
pip install -e .

# Initialize database
tt init

# Run first ingest
tt ingest

# Check usage
tt usage --range 7d
```

---

## 11. Unified Architecture for All Sources

### 11.1 Data Source Availability (Updated)

| Source | Log Location | Token Data | Strategy |
|--------|-------------|------------|----------|
| **OpenClaw** | `~/.openclaw/agents/*/sessions/*.jsonl` | ✅ Full (input/output/cache/cost) | Direct parse |
| **Droid** | `~/.factory/logs/droid-log-single.log` | ✅ Partial (cacheRead/output) | Log parse |
| **Codex** | `~/.codex/sessions/*.jsonl` | ❌ None | API proxy |
| **Gemini** | `~/.gemini/` | ❌ None | API proxy |
| **Claude Code** | `~/.claude/transcripts/*.jsonl` | ❌ None | API proxy |

### 11.2 Unified Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Token Tracker Unified                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Data Collection Layer                         │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │                                                                   │   │
│  │  [Direct Parse]              [API Proxy]                         │   │
│  │  ┌──────────────┐           ┌──────────────┐                     │   │
│  │  │ OpenClaw     │           │ Local Proxy  │◀── Codex            │   │
│  │  │ Sessions     │           │ :18800       │◀── Gemini           │   │
│  │  └──────┬───────┘           │              │◀── Claude Code      │   │
│  │         │                   └──────┬───────┘                     │   │
│  │  ┌──────┴───────┐                  │                             │   │
│  │  │ Droid Logs   │                  │                             │   │
│  │  └──────┬───────┘                  │                             │   │
│  │         │                          │                             │   │
│  └─────────┼──────────────────────────┼─────────────────────────────┘   │
│            │                          │                                 │
│            ▼                          ▼                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      SQLite Database                             │   │
│  │                  ~/.openclaw/token-tracker.db                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│            │                                                           │
│            ▼                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      CLI / Web Interface                         │   │
│  │                    tt usage | tt report                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 11.3 API Proxy Solution

For agents without native token logging (Codex, Gemini, Claude Code), deploy a local proxy:

**Proxy Service** (`token-proxy`):
- Listens on `localhost:18800`
- Forwards requests to actual API endpoints
- Logs token usage from response headers/body
- Minimal latency overhead

**Configuration for Coding Agents:**
```bash
# Codex - set in ~/.codex/config.toml
[api]
base_url = "http://localhost:18800/openai"

# Gemini - set GEMINI_API_BASE
export GEMINI_API_BASE="http://localhost:18800/google"

# Claude Code - set ANTHROPIC_BASE_URL
export ANTHROPIC_BASE_URL="http://localhost:18800/anthropic"
```

### 11.4 Proxy Implementation

```python
# Pseudocode for token-proxy
from fastapi import FastAPI, Request
import httpx

app = FastAPI()
db = TokenTrackerDB()

BACKENDS = {
    "openai": "https://api.openai.com",
    "anthropic": "https://api.anthropic.com", 
    "google": "https://generativelanguage.googleapis.com",
}

@app.api_route("/{provider}/{path:path}", methods=["GET", "POST"])
async def proxy(provider: str, path: str, request: Request):
    backend = BACKENDS[provider]
    
    # Forward request
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=f"{backend}/{path}",
            headers=dict(request.headers),
            content=await request.body()
        )
    
    # Extract and log usage
    if "usage" in response.json():
        usage = response.json()["usage"]
        db.log_usage(
            source=f"proxy-{provider}",
            model=response.json().get("model"),
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0)
        )
    
    return Response(content=response.content, headers=dict(response.headers))
```

### 11.5 Updated Implementation Plan

| Phase | Task | Duration |
|-------|------|----------|
| 1 | Core: SQLite + OpenClaw ingestor | 1 day |
| 2 | Droid log parser | 0.5 day |
| 3 | CLI tool (`tt`) | 1 day |
| 4 | API Proxy service | 1-2 days |
| 5 | Agent config integration | 0.5 day |
| 6 | Web UI (optional) | 1 day |

**Total: 5-6 days**

### 11.6 Service Files

```
~/clawd/services/token-tracker/
├── src/
│   ├── ingestors/
│   │   ├── openclaw.py      # OpenClaw session parser
│   │   ├── droid.py         # Droid log parser (NEW)
│   │   └── base.py
│   ├── proxy/
│   │   ├── __init__.py
│   │   ├── server.py        # FastAPI proxy (NEW)
│   │   └── backends.py      # Provider configs
│   ├── cli/
│   │   └── commands.py
│   └── db/
│       └── schema.sql
├── systemd/
│   └── token-proxy.service  # Systemd unit (NEW)
├── tt                        # CLI entry
└── README.md
```
