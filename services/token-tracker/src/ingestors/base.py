"""Base ingestor class."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UsageRecord:
    """A single usage record."""
    message_id: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    total_tokens: int
    cost_input: float
    cost_output: float
    cost_cache_read: float
    cost_cache_write: float
    cost_total: float
    stop_reason: Optional[str]
    timestamp: datetime
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    cwd: Optional[str] = None


class BaseIngestor(ABC):
    """Base class for data ingestors."""
    
    source_name: str = "unknown"
    
    @abstractmethod
    def ingest(self, since: Optional[datetime] = None) -> int:
        """Ingest data and return count of new records."""
        pass
