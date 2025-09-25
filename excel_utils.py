import pandas as pd
import re
from werkzeug.security import generate_password_hash
from models import User, Classroom
from app import db

def validate_email(email):
    """Validate email format"""
    if not email or pd.isna(email):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, str(email).strip()))

def validate_student_id(student_id):
    """Validate student ID format"""
    if not student_id or pd.isna(student_id):
        return False
    # Remove any whitespace and check if it's not empty
    student_id = str(student_id).strip()
    return len(student_id) > 0

def generate_username_from_email(email):
    """Generate username from email"""
    if not email or pd.isna(email):
        return None
    return str(email).split('@')[0].lower()

def process_excel_file(file_path, default_password, default_department, classroom_id=None):
    """
    Process Excel file and validate student data
    Expected columns: first_name, last_name, email, student_id, phone (optional)
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Clean column names (remove extra spaces, convert to lowercase)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Required columns
        required_cols = ['first_name', 'last_name', 'email', 'student_id']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return {
                'success': False,
                'error': f'Missing required columns: {", ".join(missing_cols)}',
                'valid_data': [],
                'errors': []
            }
        
        # Clean data
        df = df.fillna('')
        
        valid_data = []
        errors = []
        
        for index, row in df.iterrows():
            row_num = index + 2  # Excel row number (header is row 1)
            student_errors = []
            
            # Validate required fields
            first_name = str(row['first_name']).strip()
            last_name = str(row['last_name']).strip()
            email = str(row['email']).strip().lower()
            student_id = str(row['student_id']).strip()
            phone = str(row.get('phone', '')).strip() if 'phone' in row else ''
            
            # Year, semester, and section will be assigned from classroom selection
            
            # Check if row is completely empty
            if not any([first_name, last_name, email, student_id]):
                continue  # Skip empty rows
            
            # Validate fields
            if not first_name:
                student_errors.append("First name is required")
            
            if not last_name:
                student_errors.append("Last name is required")
            
            if not validate_email(email):
                student_errors.append("Invalid email format")
            
            if not validate_student_id(student_id):
                student_errors.append("Student ID is required")
            
            # Check for existing users
            if email and User.query.filter_by(email=email).first():
                student_errors.append(f"Email {email} already exists")
            
            if student_id and User.query.filter_by(student_id=student_id).first():
                student_errors.append(f"Student ID {student_id} already exists")
            
            # Generate username from email
            username = generate_username_from_email(email)
            if username and User.query.filter_by(username=username).first():
                # If username exists, append a number
                base_username = username
                counter = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
            
            if student_errors:
                errors.append({
                    'row': row_num,
                    'data': {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'student_id': student_id
                    },
                    'errors': student_errors
                })
            else:
                valid_data.append({
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'username': username,
                    'student_id': student_id,
                    'phone': phone,
                    'department': default_department,
                    'password_hash': generate_password_hash(default_password),
                    'classroom_id': classroom_id if classroom_id and classroom_id != 0 else None
                })
        
        return {
            'success': True,
            'valid_data': valid_data,
            'errors': errors,
            'total_rows': len(df),
            'valid_count': len(valid_data),
            'error_count': len(errors)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error processing Excel file: {str(e)}',
            'valid_data': [],
            'errors': []
        }

def create_students_from_data(valid_data):
    """Create student users from validated data"""
    from models import Classroom
    
    created_students = []
    failed_students = []
    
    print(f"DEBUG: create_students_from_data called with {len(valid_data)} students")
    
    try:
        for i, student_data in enumerate(valid_data):
            print(f"DEBUG: Processing student {i+1}: {student_data.get('first_name')} {student_data.get('last_name')}")
            try:
                # Get classroom info if classroom_id is provided
                year = None
                semester = None
                section = None
                
                print(f"DEBUG: Student classroom_id: {student_data.get('classroom_id')}")
                if student_data.get('classroom_id'):
                    classroom = Classroom.query.get(student_data['classroom_id'])
                    print(f"DEBUG: Found classroom: {classroom}")
                    if classroom:
                        year = classroom.year
                        semester = classroom.semester
                        section = classroom.section
                        print(f"DEBUG: Assigned year={year}, semester={semester}, section={section} from classroom {classroom.name}")
                    else:
                        print(f"DEBUG: Classroom not found for ID {student_data['classroom_id']}")
                else:
                    print("DEBUG: No classroom_id provided")
                
                # Create new user
                user = User(
                    username=student_data['username'],
                    email=student_data['email'],
                    password_hash=student_data['password_hash'],
                    first_name=student_data['first_name'],
                    last_name=student_data['last_name'],
                    phone=student_data['phone'] if student_data['phone'] else None,
                    department=student_data['department'],
                    student_id=student_data['student_id'],
                    role='student',
                    is_active=True,
                    classroom_id=student_data['classroom_id'],
                    year=year,
                    semester=semester,
                    section=section
                )
                
                print(f"DEBUG: Created user object for {student_data['first_name']} {student_data['last_name']}")
                db.session.add(user)
                created_students.append({
                    'name': f"{student_data['first_name']} {student_data['last_name']}",
                    'email': student_data['email'],
                    'student_id': student_data['student_id']
                })
                
            except Exception as e:
                print(f"DEBUG: Error creating student {i+1}: {str(e)}")
                failed_students.append({
                    'name': f"{student_data['first_name']} {student_data['last_name']}",
                    'email': student_data['email'],
                    'error': str(e)
                })
        
        print(f"DEBUG: Committing {len(created_students)} students to database...")
        # Commit all changes
        db.session.commit()
        print(f"DEBUG: Successfully committed {len(created_students)} students")
        
        return {
            'success': True,
            'created_count': len(created_students),
            'failed_count': len(failed_students),
            'created_students': created_students,
            'failed_students': failed_students
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}',
            'created_count': 0,
            'failed_count': len(valid_data)
        }

def create_sample_excel_template():
    """Create a sample Excel template for reference"""
    sample_data = {
        'first_name': ['John', 'Jane', 'Mike'],
        'last_name': ['Doe', 'Smith', 'Johnson'],
        'email': ['john.doe@example.com', 'jane.smith@example.com', 'mike.johnson@example.com'],
        'student_id': ['CSE001', 'CSE002', 'CSE003'],
        'phone': ['9876543210', '9876543211', '9876543212']
    }
    
    df = pd.DataFrame(sample_data)
    return df