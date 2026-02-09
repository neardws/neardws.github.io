"""OpenClaw session ingestor."""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config import DB_PATH, OPENCLAW_BASE
from src.db.connection import get_connection
from src.ingestors.base import BaseIngestor, UsageRecord


class OpenClawIngestor(BaseIngestor):
    """Ingest token usage from OpenClaw session files."""
    
    source_name = "openclaw"
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.sessions_base = OPENCLAW_BASE / "agents"
    
    def _get_or_create_source_id(self, conn: sqlite3.Connection) -> int:
        """Get or create source ID."""
        cursor = conn.execute(
            "SELECT id FROM sources WHERE name = ?", (self.source_name,)
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor = conn.execute(
            "INSERT INTO sources (name, display_name) VALUES (?, ?)",
            (self.source_name, "OpenClaw Gateway")
        )
        return cursor.lastrowid
    
    def _get_or_create_model_id(
        self, conn: sqlite3.Connection, provider: str, model: str
    ) -> int:
        """Get or create model ID, creating provider if needed."""
        # Get or create provider
        cursor = conn.execute(
            "SELECT id FROM providers WHERE name = ?", (provider,)
        )
        row = cursor.fetchone()
        if row:
            provider_id = row[0]
        else:
            cursor = conn.execute(
                "INSERT INTO providers (name, display_name) VALUES (?, ?)",
                (provider, provider)
            )
            provider_id = cursor.lastrowid
        
        # Get or create model
        cursor = conn.execute(
            "SELECT id FROM models WHERE provider_id = ? AND model_id = ?",
            (provider_id, model)
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor = conn.execute(
            "INSERT INTO models (provider_id, model_id, display_name) VALUES (?, ?, ?)",
            (provider_id, model, model)
        )
        return cursor.lastrowid
    
    def _get_or_create_session_id(
        self, conn: sqlite3.Connection, source_id: int, session_id: str,
        agent_id: Optional[str] = None, started_at: Optional[datetime] = None,
        cwd: Optional[str] = None
    ) -> int:
        """Get or create session ID."""
        cursor = conn.execute(
            "SELECT id FROM sessions WHERE source_id = ? AND session_id = ?",
            (source_id, session_id)
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor = conn.execute(
            "INSERT INTO sessions (source_id, session_id, agent_id, started_at, cwd) VALUES (?, ?, ?, ?, ?)",
            (source_id, session_id, agent_id, started_at, cwd)
        )
        return cursor.lastrowid
    
    def _get_ingest_state(
        self, conn: sqlite3.Connection, file_path: str
    ) -> tuple[int, Optional[str]]:
        """Get last processed position and message ID for a file."""
        cursor = conn.execute(
            "SELECT last_position, last_message_id FROM ingest_state WHERE source = ? AND file_path = ?",
            (self.source_name, file_path)
        )
        row = cursor.fetchone()
        if row:
            return row[0], row[1]
        return 0, None
    
    def _update_ingest_state(
        self, conn: sqlite3.Connection, file_path: str,
        position: int, message_id: str
    ) -> None:
        """Update ingest state for a file."""
        conn.execute(
            """INSERT INTO ingest_state (source, file_path, last_position, last_message_id, updated_at)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(source, file_path) DO UPDATE SET
               last_position = excluded.last_position,
               last_message_id = excluded.last_message_id,
               updated_at = CURRENT_TIMESTAMP""",
            (self.source_name, file_path, position, message_id)
        )
    
    def _parse_session_file(
        self, file_path: Path, start_position: int = 0
    ) -> tuple[list[UsageRecord], int, Optional[str], Optional[str], Optional[str], Optional[datetime]]:
        """Parse a session JSONL file starting from position.
        
        Returns: (records, final_position, last_message_id, session_id, cwd, started_at)
        """
        records = []
        session_id = None
        cwd = None
        started_at = None
        last_message_id = None
        
        with open(file_path, "r") as f:
            if start_position > 0:
                f.seek(start_position)
            
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                # Extract session metadata
                if entry.get("type") == "session":
                    session_id = entry.get("id")
                    cwd = entry.get("cwd")
                    if entry.get("timestamp"):
                        started_at = datetime.fromisoformat(
                            entry["timestamp"].replace("Z", "+00:00")
                        )
                
                # Extract usage from assistant messages
                if entry.get("type") == "message":
                    message = entry.get("message", {})
                    if message.get("role") == "assistant" and "usage" in message:
                        usage = message["usage"]
                        cost = usage.get("cost", {})
                        
                        timestamp_str = entry.get("timestamp") or message.get("timestamp")
                        if timestamp_str:
                            if isinstance(timestamp_str, (int, float)):
                                timestamp = datetime.fromtimestamp(timestamp_str / 1000)
                            else:
                                timestamp = datetime.fromisoformat(
                                    timestamp_str.replace("Z", "+00:00")
                                )
                        else:
                            timestamp = datetime.now()
                        
                        record = UsageRecord(
                            message_id=entry.get("id", ""),
                            provider=message.get("provider", "unknown"),
                            model=message.get("model", "unknown"),
                            input_tokens=usage.get("input", 0),
                            output_tokens=usage.get("output", 0),
                            cache_read_tokens=usage.get("cacheRead", 0),
                            cache_write_tokens=usage.get("cacheWrite", 0),
                            total_tokens=usage.get("totalTokens", 0),
                            cost_input=cost.get("input", 0),
                            cost_output=cost.get("output", 0),
                            cost_cache_read=cost.get("cacheRead", 0),
                            cost_cache_write=cost.get("cacheWrite", 0),
                            cost_total=cost.get("total", 0),
                            stop_reason=message.get("stopReason"),
                            timestamp=timestamp,
                        )
                        records.append(record)
                        last_message_id = record.message_id
            
            final_position = f.tell()
        
        return records, final_position, last_message_id, session_id, cwd, started_at
    
    def ingest(self, since: Optional[datetime] = None) -> int:
        """Ingest all OpenClaw session files."""
        total_count = 0
        
        with get_connection(self.db_path) as conn:
            source_id = self._get_or_create_source_id(conn)
            
            # Find all agent directories
            if not self.sessions_base.exists():
                return 0
            
            for agent_dir in self.sessions_base.iterdir():
                if not agent_dir.is_dir():
                    continue
                
                agent_id = agent_dir.name
                sessions_dir = agent_dir / "sessions"
                
                if not sessions_dir.exists():
                    continue
                
                # Process each session file
                for session_file in sessions_dir.glob("*.jsonl"):
                    file_path_str = str(session_file)
                    start_pos, _ = self._get_ingest_state(conn, file_path_str)
                    
                    records, final_pos, last_msg_id, session_id, cwd, started_at = \
                        self._parse_session_file(session_file, start_pos)
                    
                    if not records:
                        continue
                    
                    # Use filename as session_id if not found in file
                    if not session_id:
                        session_id = session_file.stem
                    
                    db_session_id = self._get_or_create_session_id(
                        conn, source_id, session_id, agent_id, started_at, cwd
                    )
                    
                    inserted = 0
                    for record in records:
                        model_id = self._get_or_create_model_id(
                            conn, record.provider, record.model
                        )
                        
                        try:
                            conn.execute(
                                """INSERT INTO usage (
                                    session_id, model_id, source_id,
                                    input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, total_tokens,
                                    cost_input, cost_output, cost_cache_read, cost_cache_write, cost_total,
                                    stop_reason, message_id, recorded_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (
                                    db_session_id, model_id, source_id,
                                    record.input_tokens, record.output_tokens,
                                    record.cache_read_tokens, record.cache_write_tokens, record.total_tokens,
                                    record.cost_input, record.cost_output,
                                    record.cost_cache_read, record.cost_cache_write, record.cost_total,
                                    record.stop_reason, record.message_id, record.timestamp
                                )
                            )
                            inserted += 1
                        except sqlite3.IntegrityError:
                            # Duplicate record, skip
                            pass
                    
                    if last_msg_id:
                        self._update_ingest_state(conn, file_path_str, final_pos, last_msg_id)
                    
                    total_count += inserted
            
            conn.commit()
        
        return total_count
