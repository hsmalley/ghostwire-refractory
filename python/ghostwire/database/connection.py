"""
Database connection management for GhostWire Refractory
"""

import sqlite3
import threading
from collections.abc import Generator
from contextlib import contextmanager
from queue import Empty, Queue

from ..config.settings import settings
from ..models.memory import DATABASE_SCHEMA


class ConnectionPool:
    """Thread-safe SQLite connection pool"""

    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.active_connections = 0
        self.lock = threading.Lock()
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize the connection pool with connections"""
        for _ in range(self.pool_size):
            conn = self._create_connection()
            self.pool.put(conn)

        # Ensure database schema exists
        with self.get_connection() as conn:
            conn.executescript(DATABASE_SCHEMA)

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
        conn.execute("PRAGMA synchronous=NORMAL")  # Better performance
        conn.execute("PRAGMA cache_size=1000")  # Increase cache size
        conn.execute("PRAGMA temp_store=memory")  # Store temp tables in memory

        return conn

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a connection from the pool, yield it, and return it to the pool"""
        conn = None
        try:
            # Try to get connection from pool with timeout
            conn = self.pool.get(timeout=10)
        except Empty:
            # If pool is empty, create a new connection (up to max limit)
            with self.lock:
                if self.active_connections < self.pool_size * 2:  # Allow some overflow
                    conn = self._create_connection()
                    self.active_connections += 1
                else:
                    raise Exception(
                        "Database pool exhausted and max connections reached"
                    )

        try:
            yield conn
            # Only commit if auto-commit is not disabled
            if conn.total_changes > 0:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            if conn:
                try:
                    # Return connection to pool
                    self.pool.put(conn, timeout=1)
                except Exception:
                    # If pool is full, close connection
                    conn.close()
                    with self.lock:
                        self.active_connections -= 1

    def close_all(self):
        """Close all connections in the pool"""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except Empty:
                break


# Global connection pool instance
_pool: ConnectionPool = None


def init_db_pool():
    """Initialize the database connection pool"""
    global _pool
    _pool = ConnectionPool(db_path=settings.DB_PATH, pool_size=settings.DB_POOL_SIZE)


def get_db_connection():
    """Get a database connection from the pool"""
    if _pool is None:
        init_db_pool()
    return _pool.get_connection()


def close_db_pool():
    """Close all connections in the pool"""
    global _pool
    if _pool:
        _pool.close_all()
        _pool = None


# Context manager for easy use
@contextmanager
def db_transaction():
    """Context manager for database transactions"""
    with get_db_connection() as conn:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
