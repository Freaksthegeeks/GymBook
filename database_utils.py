#!/usr/bin/env python3
"""
Utility functions for database operations
"""

import psycopg2
import psycopg2.extras
import os
from typing import Optional, Any

def get_db_connection():
    """
    Create and return a database connection
    
    Returns:
        tuple: (connection, cursor) or (None, None) if connection fails
    """
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'gym'),
            user=os.getenv('DB_USER', 'skvar'),
            password=os.getenv('DB_PASSWORD', 'Root1234'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return conn, cur
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None, None

def close_db_connection(conn, cur):
    """
    Close database connection and cursor
    
    Args:
        conn: Database connection object
        cur: Database cursor object
    """
    try:
        if cur:
            cur.close()
        if conn:
            conn.close()
    except Exception as e:
        print(f"❌ Error closing database connection: {e}")

def test_connection():
    """
    Test database connection
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    conn, cur = get_db_connection()
    
    if not conn or not cur:
        return False
    
    try:
        cur.execute("SELECT version();")
        version = cur.fetchone()
        if version:
            print("✅ Database connection successful!")
            print(f"📊 PostgreSQL version: {version[0]}")
            return True
        else:
            print("❌ Failed to fetch PostgreSQL version")
            return False
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        return False
    finally:
        close_db_connection(conn, cur)

def list_tables():
    """
    List all tables in the database
    """
    conn, cur = get_db_connection()
    
    if not conn or not cur:
        return
    
    try:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        print("\n📋 Database tables:")
        for table in tables:
            print(f"  - {table[0]}")
            
    except Exception as e:
        print(f"❌ Failed to list tables: {e}")
    finally:
        close_db_connection(conn, cur)

if __name__ == "__main__":
    # Test the database connection
    if test_connection():
        list_tables()
        print("\n✅ Database utilities test completed successfully!")
    else:
        print("\n❌ Database utilities test failed!")