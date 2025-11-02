#!/usr/bin/env python3
"""
Database migration script to add missing columns
Run this to update the production database schema
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
import psycopg2
from psycopg2 import sql

def migrate_database():
    """Add missing columns to existing database"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check if baby_name column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='customers' AND column_name='baby_name';
        """)
        
        if not cursor.fetchone():
            print("Adding baby_name column...")
            cursor.execute("ALTER TABLE customers ADD COLUMN baby_name VARCHAR(255);")
            print("✅ baby_name column added")
        else:
            print("✅ baby_name column already exists")
        
        # Check if stripe_session_id column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='customers' AND column_name='stripe_session_id';
        """)
        
        if not cursor.fetchone():
            print("Adding stripe_session_id column...")
            cursor.execute("ALTER TABLE customers ADD COLUMN stripe_session_id VARCHAR(255);")
            print("✅ stripe_session_id column added")
        else:
            print("✅ stripe_session_id column already exists")
        
        # Commit changes
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    success = migrate_database()
    
    if success:
        print("🎉 Migration completed! Your app should work now.")
    else:
        print("💥 Migration failed. Check the error above.")
        sys.exit(1)