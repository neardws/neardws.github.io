"""Droid (Factory) log ingestor.

Parses ~/.factory/logs/droid-log-single.log to extract token usage from
[Agent] Streaming result lines.

Log format:
[timestamp] INFO: [Agent] Streaming result | Context: {"count":9,"cacheReadInputTokens":15200,...,"outputTokens":843,"tags":{..."sessionId":"...","modelId":"..."}}
"""
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
import hashlib

from src.config import DB_PATH, DROID_LOG
from src.db.connection import get_connection
from src.ingestors.base import BaseIngestor, UsageRecord


LOG_LINE_PATTERN = re.compile(
    r'^\[([^\]]+)\]\s+INFO:\s+\[Agent\]\s+Streaming result\s+\|\s+Context:\s+(.+)$'
)


class DroidIngestor(BaseIngestor):
    """Ingest token usage from Factory Droid logs."""
    
    source_name = "droid"
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.log_path = DROID_LOG
    
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
            (self.source_name, "Factory Droid")
        )
        return cursor.lastrowid
    
    def _get_or_create_model_id(
        self, conn: sqlite3.Connection, model: str
    ) -> int:
        """Get or create model ID for Anthropic provider."""
        cursor = conn.execute(
            "SELECT id FROM providers WHERE name = ?", ("anthropic",)
        )
        row = cursor.fetchone()
        if row:
            provider_id = row[0]
        else:
            cursor = conn.execute(
                "INSERT INTO providers (name, display_name) VALUES (?, ?)",
                ("anthropic", "Anthropic")
            )
            provider_id = cursor.lastrowid
        
        cursor = conn.execute(
            "SELECT id FROM models WHERE provider_id = ? AND model_id = ?",
            (provider_id, model)
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        
        display_name = model.replace("-", " ").title()
        cursor = conn.execute(
            "INSERT INTO models (provider_id, model_id, display_name) VALUES (?, ?, ?)",
            (provider_id, model, display_name)
        )
        return cursor.lastrowid
    
    def _get_or_create_session_id(
        self, conn: sqlite3.Connection, source_id: int, session_id: str,
        started_at: Optional[datetime] = None
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
            "INSERT INTO sessions (source_id, session_id, started_at) VALUES (?, ?, ?)",
            (source_id, session_id, started_at)
        )
        return cursor.lastrowid
    
    def _get_ingest_state(self, conn: sqlite3.Connection, file_path: str) -> tuple[int, Optional[str]]:
        """Get last processed position and message ID for the log file."""
        cursor = conn.execute(
            "SELECT last_position, last_message_id FROM ingest_state WHERE source = ? AND file_path = ?",
            (self.source_name, file_path)
        )
        row = cursor.fetchone()
        if row:
            return row[0], row[1]
        return 0, None
    
    def _update_ingest_state(
        self, conn: sqlite3.Connection, file_path: str, position: int,
        last_message_id: Optional[str] = None
    ) -> None:
        """Update ingest state for the log file."""
        conn.execute(
            """INSERT INTO ingest_state (source, file_path, last_position, last_message_id, updated_at)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(source, file_path) DO UPDATE SET
               last_position = excluded.last_position,
               last_message_id = excluded.last_message_id,
               updated_at = CURRENT_TIMESTAMP""",
            (self.source_name, file_path, position, last_message_id)
        )
    
    def _generate_message_id(self, timestamp: str, session_id: str, output_tokens: int) -> str:
        """Generate unique message ID from log line data."""
        data = f"{timestamp}:{session_id}:{output_tokens}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    def _parse_log_line(self, line: str) -> Optional[dict]:
        """Parse a single log line for streaming result data."""
        match = LOG_LINE_PATTERN.match(line)
        if not match:
            return None
        
        timestamp_str = match.group(1)
        context_str = match.group(2)
        
        try:
            context = json.loads(context_str)
        except json.JSONDecodeError:
            return None
        
        tags = context.get("tags", {})
        session_id = tags.get("sessionId")
        model_id = tags.get("modelId")
        
        if not session_id:
            return None
        
        cache_read = context.get("cacheReadInputTokens", 0)
        output_tokens = context.get("outputTokens", 0)
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except ValueError:
            timestamp = datetime.now()
        
        message_id = self._generate_message_id(timestamp_str, session_id, output_tokens)
        
        return {
            "timestamp": timestamp,
            "session_id": session_id,
            "model_id": model_id or "claude-opus-4-5-20251101",
            "cache_read_tokens": cache_read,
            "output_tokens": output_tokens,
            "message_id": message_id,
        }
    
    def ingest(self, since: Optional[datetime] = None) -> int:
        """Ingest Droid log data.
        
        Parses [Agent] Streaming result lines to extract:
        - cacheReadInputTokens
        - outputTokens
        - sessionId
        - modelId
        """
        if not self.log_path.exists():
            return 0
        
        total_count = 0
        
        with get_connection(self.db_path) as conn:
            source_id = self._get_or_create_source_id(conn)
            file_path_str = str(self.log_path)
            start_pos, _ = self._get_ingest_state(conn, file_path_str)
            
            current_size = self.log_path.stat().st_size
            if current_size < start_pos:
                start_pos = 0
            
            last_message_id = None
            final_position = start_pos
            
            with open(self.log_path, "r", errors="replace") as f:
                if start_pos > 0:
                    f.seek(start_pos)
                
                for line in f:
                    line = line.strip()
                    if not line or "Streaming result" not in line:
                        continue
                    
                    data = self._parse_log_line(line)
                    if not data:
                        continue
                    
                    if since and data["timestamp"].replace(tzinfo=None) < since:
                        continue
                    
                    model_id = self._get_or_create_model_id(conn, data["model_id"])
                    db_session_id = self._get_or_create_session_id(
                        conn, source_id, data["session_id"], data["timestamp"]
                    )
                    
                    total_tokens = data["cache_read_tokens"] + data["output_tokens"]
                    
                    try:
                        conn.execute(
                            """INSERT INTO usage (
                                session_id, model_id, source_id,
                                input_tokens, output_tokens, cache_read_tokens,
                                cache_write_tokens, total_tokens,
                                cost_input, cost_output, cost_cache_read,
                                cost_cache_write, cost_total,
                                stop_reason, message_id, recorded_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (
                                db_session_id, model_id, source_id,
                                0, data["output_tokens"], data["cache_read_tokens"],
                                0, total_tokens,
                                0, 0, 0, 0, 0,
                                None, data["message_id"], data["timestamp"]
                            )
                        )
                        total_count += 1
                        last_message_id = data["message_id"]
                    except sqlite3.IntegrityError:
                        pass
                
                final_position = f.tell()
            
            self._update_ingest_state(conn, file_path_str, final_position, last_message_id)
            conn.commit()
        
        return total_count
