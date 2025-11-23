#!/usr/bin/env python3
"""
Test script to verify PostgreSQL database connection
"""

import sys
import os

# Add the config directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

try:
    # Import the database connection
    from config import database
    
    # Test the connection by executing a simple query
    database.cur.execute("SELECT version();")
    version = database.cur.fetchone()
    
    print("✅ Database connection successful!")
    if version:
        print(f"📊 PostgreSQL version: {version[0]}")
    
    # Test if tables exist
    database.cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = database.cur.fetchall()
    
    print("\n📋 Database tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Close the connection
    database.cur.close()
    database.conn.close()
    
    print("\n✅ Database test completed successfully!")
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)