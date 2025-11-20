#!/usr/bin/env python3
"""
Database initialization script for AIREX project.
Reads and executes schema.sql to create all necessary tables.
"""

import os
import sys
from dotenv import load_dotenv
from db import get_connection, close_connection, test_connection
import logging

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def init_database():
    """
    Initializes the database by executing the schema.sql file.

    Returns:
        bool: True if initialization was successful, False otherwise
    """
    # First, test the connection
    logger.info("Testing database connection...")
    if not test_connection():
        logger.error("Database connection failed. Please check your DATABASE_URL.")
        return False

    # Read schema.sql
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

    if not os.path.exists(schema_path):
        logger.error(f"Schema file not found at: {schema_path}")
        return False

    logger.info(f"Reading schema from: {schema_path}")
    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    # Execute schema
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            logger.info("Executing schema.sql...")
            cursor.execute(schema_sql)
            conn.commit()
            logger.info("✓ Database schema initialized successfully!")
            logger.info("✓ All tables created:")
            logger.info("  - models")
            logger.info("  - techniques")
            logger.info("  - model_techniques")
            logger.info("  - experiments")
            logger.info("  - improvements")
            return True
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Failed to initialize database: {e}")
        return False
    finally:
        close_connection(conn)


def verify_tables():
    """
    Verifies that all required tables exist in the database.

    Returns:
        bool: True if all tables exist, False otherwise
    """
    required_tables = ['models', 'techniques', 'model_techniques', 'experiments', 'improvements']

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """)
            existing_tables = [row['table_name'] for row in cursor.fetchall()]

            logger.info("Verifying database tables...")
            all_exist = True
            for table in required_tables:
                if table in existing_tables:
                    logger.info(f"✓ Table '{table}' exists")
                else:
                    logger.error(f"✗ Table '{table}' is missing")
                    all_exist = False

            return all_exist
    except Exception as e:
        logger.error(f"Failed to verify tables: {e}")
        return False
    finally:
        close_connection(conn)


def main():
    """Main entry point for the initialization script."""
    logger.info("=" * 60)
    logger.info("AIREX Database Initialization")
    logger.info("=" * 60)

    # Check for DATABASE_URL
    if not os.getenv('DATABASE_URL'):
        logger.error("DATABASE_URL environment variable is not set!")
        logger.info("Please set it in your .env file or environment:")
        logger.info("  export DATABASE_URL='postgresql://user:password@host:port/database'")
        sys.exit(1)

    # Initialize database
    if init_database():
        logger.info("\n" + "=" * 60)
        logger.info("Verification Phase")
        logger.info("=" * 60)
        if verify_tables():
            logger.info("\n✓ Database is ready for use!")
            sys.exit(0)
        else:
            logger.error("\n✗ Some tables are missing. Please check the errors above.")
            sys.exit(1)
    else:
        logger.error("\n✗ Database initialization failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
