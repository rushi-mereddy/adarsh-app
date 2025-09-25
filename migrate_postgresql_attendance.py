#!/usr/bin/env python3
"""
PostgreSQL migration script to make course_id nullable in Attendance table
This script will be run inside the Docker container
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def migrate_attendance_table():
    """Migrate the Attendance table to make course_id nullable"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL', 'postgresql://college_user:college_pass@db:5432/college_db')
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            print("🔄 Starting PostgreSQL Attendance table migration...")
            
            # Check current constraint
            result = connection.execute(text("""
                SELECT column_name, is_nullable, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'attendance' 
                AND column_name = 'course_id'
            """))
            
            column_info = result.fetchone()
            if column_info:
                print(f"Current course_id column: {column_info[0]}, nullable: {column_info[1]}, type: {column_info[2]}")
                
                if column_info[1] == 'NO':
                    print("❌ course_id is currently NOT NULL, need to change it...")
                    
                    # Make course_id nullable
                    connection.execute(text("ALTER TABLE attendance ALTER COLUMN course_id DROP NOT NULL"))
                    print("✅ Successfully made course_id nullable in Attendance table")
                else:
                    print("✅ course_id is already nullable")
            else:
                print("❌ course_id column not found in attendance table")
                return False
            
            # Verify the change
            result = connection.execute(text("""
                SELECT column_name, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'attendance' 
                AND column_name = 'course_id'
            """))
            
            column_info = result.fetchone()
            if column_info and column_info[1] == 'YES':
                print("✅ Verification successful: course_id is now nullable")
            else:
                print("❌ Verification failed: course_id is still NOT NULL")
                return False
            
            connection.commit()
            print("✅ Migration completed successfully!")
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = migrate_attendance_table()
    if success:
        print("🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        print("💥 Migration failed!")
        sys.exit(1)
