"""
NBA Game Outcome Prediction System — Backend: Database Connection Pool
Singleton MySQL connection pool using mysql-connector-python.
Configuration from environment variables.
"""

import os
import logging
import threading
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


class DatabasePool:
    """
    Singleton MySQL connection pool.
    Thread-safe initialization using a lock.
    """

    _instance = None
    _lock = threading.Lock()
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize_pool()
        return cls._instance

    def _initialize_pool(self) -> None:
        """Create the connection pool from environment variables."""
        config = {
            "pool_name": "nba_pool",
            "pool_size": 5,
            "pool_reset_session": True,
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": int(os.environ.get("DB_PORT", 3306)),
            "user": os.environ.get("DB_USER", "root"),
            "password": os.environ.get("DB_PASSWORD", ""),
            "database": os.environ.get("DB_NAME", "nba_predictions"),
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci",
            "autocommit": True,
        }

        try:
            self._pool = pooling.MySQLConnectionPool(**config)
            logger.info(
                "Database connection pool created: %s@%s:%s/%s (pool_size=%d)",
                config["user"], config["host"], config["port"],
                config["database"], config["pool_size"],
            )
        except mysql.connector.Error as err:
            logger.error("Failed to create connection pool: %s", err)
            raise

    def get_connection(self):
        """
        Acquire a connection from the pool.
        Returns a PooledMySQLConnection.
        """
        try:
            conn = self._pool.get_connection()
            logger.debug("Connection acquired from pool.")
            return conn
        except mysql.connector.Error as err:
            logger.error("Failed to acquire connection: %s", err)
            raise

    @staticmethod
    def release_connection(conn) -> None:
        """
        Release a connection back to the pool.
        For mysql-connector-python, closing the pooled connection returns it.
        """
        if conn and conn.is_connected():
            try:
                conn.close()
                logger.debug("Connection released back to pool.")
            except mysql.connector.Error as err:
                logger.warning("Error releasing connection: %s", err)


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------

_db_pool = DatabasePool()


def get_connection():
    """Get a connection from the singleton pool."""
    return _db_pool.get_connection()


def release_connection(conn) -> None:
    """Release a connection back to the singleton pool."""
    _db_pool.release_connection(conn)
