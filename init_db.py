#!/usr/bin/env python3
"""
Database initialization script for Docker container
This script will be run when the container starts to ensure proper database setup
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def init_database():
    """Initialize database with proper schema"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL', 'postgresql://college_user:college_pass@db:5432/college_db')
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            print("🔄 Initializing database...")
            
            # Check if attendance table exists and fix course_id constraint
            result = connection.execute(text("""
                SELECT column_name, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'attendance' 
                AND column_name = 'course_id'
            """))
            
            column_info = result.fetchone()
            if column_info:
                print(f"Found attendance table with course_id column (nullable: {column_info[1]})")
                
                if column_info[1] == 'NO':
                    print("🔧 Fixing course_id constraint...")
                    connection.execute(text("ALTER TABLE attendance ALTER COLUMN course_id DROP NOT NULL"))
                    print("✅ Made course_id nullable")
                else:
                    print("✅ course_id is already nullable")
            else:
                print("ℹ️  Attendance table not found or course_id column missing")
            
            connection.commit()
            print("✅ Database initialization completed!")
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    if success:
        print("🎉 Database initialization successful!")
        sys.exit(0)
    else:
        print("💥 Database initialization failed!")
        sys.exit(1)
