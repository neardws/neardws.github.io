"""SQLite connection manager."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from src.config import DB_PATH


def get_schema_sql() -> str:
    """Load schema SQL from file."""
    schema_path = Path(__file__).parent / "schema.sql"
    return schema_path.read_text()


def init_db(db_path: Path = DB_PATH) -> None:
    """Initialize database with schema."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(get_schema_sql())
        conn.commit()


@contextmanager
def get_connection(db_path: Path = DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    """Get database connection as context manager."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def db_exists(db_path: Path = DB_PATH) -> bool:
    """Check if database exists."""
    return db_path.exists()
