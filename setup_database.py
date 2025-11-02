#!/usr/bin/env python3
"""
Database setup script for Napocalypse
Run this script to create all necessary database tables
"""

import os
import psycopg2
from urllib.parse import urlparse

def setup_database():
    # Get database URL from environment or user input
    database_url = input("Enter your PostgreSQL connection string from Render: ")
    
    # Parse the database URL
    parsed = urlparse(database_url)
    
    # Read schema file
    with open('database/schema.sql', 'r') as f:
        schema_sql = f.read()
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password,
            port=parsed.port
        )
        
        # Execute schema
        cursor = conn.cursor()
        cursor.execute(schema_sql)
        conn.commit()
        
        print("✅ Database setup completed successfully!")
        print("✅ All tables created")
        print("✅ Indexes created")
        print("✅ Your Napocalypse database is ready!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_database()