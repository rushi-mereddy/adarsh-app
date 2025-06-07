#!/usr/bin/env python3

# Test script to debug Excel import functionality
import sys
import os
sys.path.append('.')

from app import app, db
from models import User, Classroom
from excel_utils import process_excel_file, create_students_from_data
from werkzeug.security import generate_password_hash
import pandas as pd

def test_excel_import():
    with app.app_context():
        print("=== Testing Excel Import Functionality ===")
        
        # Create test data
        test_data = {
            'first_name': ['Alice', 'Bob', 'Charlie'],
            'last_name': ['Test', 'Test', 'Test'],
            'email': ['alice.test@example.com', 'bob.test@example.com', 'charlie.test@example.com'],
            'student_id': ['TEST001', 'TEST002', 'TEST003'],
            'phone': ['1111111111', '2222222222', '3333333333']
        }
        
        df = pd.DataFrame(test_data)
        test_file = 'debug_test.xlsx'
        df.to_excel(test_file, index=False)
        
        print(f"Created test Excel file: {test_file}")
        
        # Test processing
        result = process_excel_file(test_file, 'test123', 'CSE', 1)
        print(f"Processing result: {result}")
        
        if result['success'] and result['valid_data']:
            print(f"Valid data count: {len(result['valid_data'])}")
            
            # Test creation
            creation_result = create_students_from_data(result['valid_data'])
            print(f"Creation result: {creation_result}")
            
            # Check database
            users = User.query.filter(User.email.like('%test@example.com')).all()
            print(f"Users found in database: {len(users)}")
            for user in users:
                print(f"  - {user.username}: {user.first_name} {user.last_name} ({user.email})")
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
        
        print("=== Test Complete ===")

if __name__ == "__main__":
    test_excel_import()