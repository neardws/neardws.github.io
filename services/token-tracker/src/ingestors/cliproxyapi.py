"""CLIProxyAPI usage ingestor.

Fetches usage data from CLIProxyAPI management endpoint.
API endpoint: http://localhost:8317/v0/management/usage
Auth header: X-Management-Key

Response format:
{
    "failed_requests": 0,
    "usage": {
        "total_requests": 100,
        "success_count": 95,
        "failure_count": 5,
        "total_tokens": 50000,
        "apis": {
            "anthropic": {"requests": 50, "tokens": 25000},
            "openai": {"requests": 50, "tokens": 25000}
        },
        "requests_by_day": {"2026-02-04": 100},
        "tokens_by_day": {"2026-02-04": 50000}
    }
}
"""
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

from src.config import DB_PATH, CLIPROXYAPI_URL, CLIPROXYAPI_KEY
from src.db.connection import get_connection
from src.ingestors.base import BaseIngestor


class CLIProxyAPIIngestor(BaseIngestor):
    """Ingest token usage from CLIProxyAPI management endpoint."""
    
    source_name = "cliproxyapi"
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.api_url = CLIPROXYAPI_URL
        self.api_key = CLIPROXYAPI_KEY
    
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
            (self.source_name, "CLIProxyAPI")
        )
        return cursor.lastrowid
    
    def _get_or_create_model_id(
        self, conn: sqlite3.Connection, provider: str, model: str
    ) -> int:
        """Get or create model ID."""
        cursor = conn.execute(
            "SELECT id FROM providers WHERE name = ?", (provider,)
        )
        row = cursor.fetchone()
        if row:
            provider_id = row[0]
        else:
            cursor = conn.execute(
                "INSERT INTO providers (name, display_name) VALUES (?, ?)",
                (provider, provider.title())
            )
            provider_id = cursor.lastrowid
        
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
    
    def _generate_message_id(self, provider: str, date: str, tokens: int) -> str:
        """Generate unique message ID from aggregated data."""
        data = f"{provider}:{date}:{tokens}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    def _fetch_usage(self) -> Optional[dict]:
        """Fetch usage data from CLIProxyAPI."""
        try:
            response = requests.get(
                self.api_url,
                headers={"X-Management-Key": self.api_key},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
    
    def ingest(self, since: Optional[datetime] = None) -> int:
        """Ingest CLIProxyAPI usage data.
        
        The API returns aggregated data by day and by API provider.
        We create one record per provider per day.
        """
        data = self._fetch_usage()
        if not data:
            return 0
        
        usage = data.get("usage", {})
        apis = usage.get("apis", {})
        tokens_by_day = usage.get("tokens_by_day", {})
        requests_by_day = usage.get("requests_by_day", {})
        
        if not apis and not tokens_by_day:
            return 0
        
        total_count = 0
        
        with get_connection(self.db_path) as conn:
            source_id = self._get_or_create_source_id(conn)
            
            session_id = "cliproxyapi-aggregate"
            db_session_id = self._get_or_create_session_id(
                conn, source_id, session_id, datetime.now()
            )
            
            for date_str, day_tokens in tokens_by_day.items():
                if not day_tokens:
                    continue
                
                try:
                    record_date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    continue
                
                if since and record_date < since:
                    continue
                
                day_requests = requests_by_day.get(date_str, 1)
                
                for provider, api_data in apis.items():
                    api_tokens = api_data.get("tokens", 0)
                    api_requests = api_data.get("requests", 0)
                    
                    if not api_tokens:
                        continue
                    
                    ratio = api_tokens / usage.get("total_tokens", 1) if usage.get("total_tokens") else 1
                    estimated_day_tokens = int(day_tokens * ratio)
                    estimated_day_requests = max(1, int(day_requests * ratio))
                    
                    model_name = f"{provider}-aggregate"
                    model_id = self._get_or_create_model_id(conn, provider, model_name)
                    message_id = self._generate_message_id(provider, date_str, estimated_day_tokens)
                    
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
                                0, 0, 0, 0, estimated_day_tokens,
                                0, 0, 0, 0, 0,
                                None, message_id, record_date
                            )
                        )
                        total_count += 1
                    except sqlite3.IntegrityError:
                        pass
                
                if not apis:
                    model_id = self._get_or_create_model_id(conn, "unknown", "cliproxyapi-aggregate")
                    message_id = self._generate_message_id("unknown", date_str, day_tokens)
                    
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
                                0, 0, 0, 0, day_tokens,
                                0, 0, 0, 0, 0,
                                None, message_id, record_date
                            )
                        )
                        total_count += 1
                    except sqlite3.IntegrityError:
                        pass
            
            conn.commit()
        
        return total_count
