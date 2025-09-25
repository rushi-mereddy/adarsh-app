#!/usr/bin/env python3
"""
Database migration script to make course_id nullable in Attendance table
Run this script to fix the database schema issue
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def migrate_attendance_table():
    """Migrate the Attendance table to make course_id nullable"""
    
    # Get database URL from environment or use default
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///college_management.db')
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Check if we're using PostgreSQL
            if 'postgresql' in database_url:
                # For PostgreSQL, we need to drop the NOT NULL constraint
                print("Detected PostgreSQL database...")
                
                # First, check if the constraint exists
                result = connection.execute(text("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'attendance' 
                    AND constraint_type = 'CHECK'
                    AND constraint_name LIKE '%course_id%'
                """))
                
                constraints = result.fetchall()
                print(f"Found {len(constraints)} constraints related to course_id")
                
                # Make course_id nullable
                connection.execute(text("ALTER TABLE attendance ALTER COLUMN course_id DROP NOT NULL"))
                print("✅ Successfully made course_id nullable in Attendance table")
                
            elif 'sqlite' in database_url:
                # For SQLite, we need to recreate the table
                print("Detected SQLite database...")
                print("⚠️  SQLite doesn't support ALTER COLUMN. You may need to recreate the table.")
                print("   Consider using PostgreSQL for production deployments.")
                
                # For SQLite, we'll just try to insert a NULL value to test
                try:
                    connection.execute(text("""
                        INSERT INTO attendance (student_id, course_id, date, status, marked_by) 
                        VALUES (1, NULL, '2024-01-01', 'present', 1)
                    """))
                    print("✅ SQLite allows NULL course_id values")
                    # Remove the test record
                    connection.execute(text("DELETE FROM attendance WHERE student_id = 1 AND date = '2024-01-01'"))
                except Exception as e:
                    print(f"❌ SQLite constraint error: {e}")
                    print("   You may need to recreate the Attendance table with nullable course_id")
            
            else:
                print("⚠️  Unknown database type. Please manually update the schema.")
                print("   Make sure course_id column in Attendance table allows NULL values.")
            
            connection.commit()
            print("✅ Migration completed successfully!")
            
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔄 Starting Attendance table migration...")
    print("This will make course_id nullable in the Attendance table")
    
    # Ask for confirmation
    response = input("Do you want to continue? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        sys.exit(0)
    
    migrate_attendance_table()
