"""
Database connection module for AIREX project.
Uses PostgreSQL on Railway via DATABASE_URL environment variable.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.

    The connection uses the DATABASE_URL environment variable which should be
    in the format: postgresql://user:password@host:port/database

    Returns:
        psycopg2.connection: Active database connection with RealDictCursor

    Raises:
        ValueError: If DATABASE_URL is not set
        psycopg2.Error: If connection fails
    """
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        raise ValueError(
            "DATABASE_URL environment variable is not set. "
            "Please configure it with your Railway PostgreSQL connection string."
        )

    try:
        connection = psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor,
            connect_timeout=10
        )
        logger.info("Database connection established successfully")
        return connection
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def test_connection() -> bool:
    """
    Tests the database connection.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        conn.close()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def close_connection(connection):
    """
    Safely closes a database connection.

    Args:
        connection: The database connection to close
    """
    if connection:
        try:
            connection.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
