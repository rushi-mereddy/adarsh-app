#!/usr/bin/env python3
"""
Test script to verify attendance functionality works
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def test_attendance_insert():
    """Test inserting attendance record with NULL course_id"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL', 'postgresql://college_user:college_pass@db:5432/college_db')
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            print("🧪 Testing attendance insert with NULL course_id...")
            
            # Try to insert a test attendance record
            result = connection.execute(text("""
                INSERT INTO attendance (student_id, course_id, date, status, marked_by, marked_at) 
                VALUES (1, NULL, CURRENT_DATE, 'present', 1, NOW())
                RETURNING id
            """))
            
            attendance_id = result.fetchone()[0]
            print(f"✅ Successfully inserted attendance record with ID: {attendance_id}")
            
            # Clean up test record
            connection.execute(text("DELETE FROM attendance WHERE id = :id"), {"id": attendance_id})
            print("🧹 Cleaned up test record")
            
            connection.commit()
            print("✅ Attendance functionality test passed!")
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_attendance_insert()
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Tests failed!")
        sys.exit(1)
