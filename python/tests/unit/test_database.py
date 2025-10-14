"""
Unit tests for GhostWire Refractory - Database Connection
"""

import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from python.src.ghostwire.database.connection import ConnectionPool, get_db_connection


class TestConnectionPool:
    def test_create_connection(self):
        """Test that connection pool creates connections properly"""
        pool = ConnectionPool(":memory:", pool_size=2)

        # Test getting a connection
        conn = pool._create_connection()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)

        conn.close()

    def test_get_connection_context(self):
        """Test getting connection through context manager"""
        pool = ConnectionPool(":memory:", pool_size=2)

        with pool.get_connection() as conn:
            assert conn is not None
            assert isinstance(conn, sqlite3.Connection)

            # Execute a simple query to verify it works
            cursor = conn.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1


def test_get_db_connection():
    """Test the global get_db_connection function"""
    with get_db_connection() as conn:
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)

        # Execute a simple query to verify it works
        cursor = conn.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
