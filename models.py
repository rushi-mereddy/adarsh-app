from extensions import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # student, faculty, admin
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    profile_image = db.Column(db.String(200))
    department = db.Column(db.String(100))
    year = db.Column(db.Integer)  # 1, 2, 3, 4 for students
    semester = db.Column(db.Integer)  # 1, 2, 3, 4, 5, 6, 7, 8
    section = db.Column(db.String(10))  # A, B, C, etc.
    student_id = db.Column(db.String(50), unique=True)
    faculty_id = db.Column(db.String(50), unique=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Add indexes for common queries
    __table_args__ = (
        # For role-based queries
        db.Index('idx_user_role_active', role, is_active),
        # For classroom student lists
        db.Index('idx_user_classroom_role', classroom_id, role),
        # For department filtering
        db.Index('idx_user_department_role', department, role),
        # For student filtering
        db.Index('idx_user_year_semester_section', year, semester, section),
        # For name searching
        db.Index('idx_user_names', first_name, last_name),
    )
    
    # Relationships
    taught_courses = db.relationship('Course', backref='faculty', lazy=True, foreign_keys='Course.faculty_id')
    feedback_given = db.relationship('Feedback', backref='student_feedback', lazy=True, foreign_keys='Feedback.student_id')
    attendance_as_student = db.relationship(
        'Attendance',
        primaryjoin='User.id==Attendance.student_id',
        foreign_keys='Attendance.student_id',
        lazy=True,
        viewonly=True
    )
    attendance_as_marker = db.relationship(
        'Attendance',
        primaryjoin='User.id==Attendance.marked_by',
        foreign_keys='Attendance.marked_by',
        lazy=True,
        viewonly=True
    )

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f'<User {self.username}>'

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # e.g., "Computer Science Engineering"
    code = db.Column(db.String(10), nullable=False, unique=True)  # e.g., "CSE"
    program = db.Column(db.String(20), nullable=False)  # UG, PG, Diploma
    description = db.Column(db.Text)
    image = db.Column(db.String(200))  # Department image for website
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    lecturers = db.relationship('Lecturer', backref='department', lazy=True, cascade='all, delete-orphan')
    student_reviews = db.relationship('StudentReview', backref='department', lazy=True, cascade='all, delete-orphan')
    
    def get_lecturer_count(self):
        return len([l for l in self.lecturers if l.is_active])
    
    def get_average_rating(self):
        if not self.student_reviews:
            return 0
        total_rating = sum(review.rating for review in self.student_reviews if review.is_approved)
        approved_reviews = len([r for r in self.student_reviews if r.is_approved])
        return round(total_rating / approved_reviews, 1) if approved_reviews > 0 else 0
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Lecturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(200))  # Profile photo
    experience = db.Column(db.String(100))  # e.g., "5 years"
    qualification = db.Column(db.String(200))  # Educational qualification
    specialization = db.Column(db.String(200))  # Area of expertise
    designation = db.Column(db.String(100))  # Professor, Assistant Professor, etc.
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    display_order = db.Column(db.Integer, default=0)  # For ordering on website
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Lecturer {self.name}>'

class StudentReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(200))  # Student photo
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5 stars
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    student_batch = db.Column(db.String(20))  # e.g., "2020-2024"
    current_position = db.Column(db.String(200))  # Current job/position
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)  # Admin approval
    
    def get_star_rating(self):
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    def __repr__(self):
        return f'<StudentReview {self.student_name}>'

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "CSE 2nd Year Sem 3 Section A"
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    semester = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4, 5, 6, 7, 8
    section = db.Column(db.String(10), nullable=False)  # A, B, C, etc.
    academic_year = db.Column(db.String(20))  # e.g., "2023-24"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Add unique constraint to prevent duplicate classrooms
    __table_args__ = (
        db.UniqueConstraint('department', 'year', 'semester', 'section', 
                           name='unique_classroom_params'),
    )
    
    # Relationships
    students = db.relationship('User', backref='assigned_classroom', lazy=True, 
                              foreign_keys='User.classroom_id',
                              primaryjoin='and_(Classroom.id==User.classroom_id, User.role=="student")')
    
    def get_classroom_name(self):
        # Get department code from department name
        department = Department.query.filter_by(name=self.department).first()
        dept_code = department.code if department else self.department[:3].upper()
        return f"{dept_code} {self.section} {self.year}-{self.semester}"
    
    def __repr__(self):
        return f'<Classroom {self.get_classroom_name()}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, default=3)
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(20))
    faculty_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    course_attendance = db.relationship('Attendance', backref='course', lazy=True)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    student = db.relationship('User', backref=db.backref('course_enrollments', lazy=True), foreign_keys=[student_id])

    __table_args__ = (db.UniqueConstraint('student_id', 'course_id'),)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)  # Made nullable for classroom-based attendance
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='present')  # present, absent, late
    marked_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    marker = db.relationship('User', foreign_keys=[marked_by], viewonly=True)
    student = db.relationship('User', foreign_keys=[student_id], viewonly=True)

    # Add indexes for common queries
    __table_args__ = (
        # For date-based queries
        db.Index('idx_attendance_date', date),
        # For student attendance history
        db.Index('idx_attendance_student_date', student_id, date),
        # For faculty marking history
        db.Index('idx_attendance_marked_by_date', marked_by, date),
        # For status-based queries
        db.Index('idx_attendance_status_date', status, date),
        # For course attendance
        db.Index('idx_attendance_course_date', course_id, date),
    )

    def __repr__(self):
        return f'<Attendance {self.student_id}-{self.course_id}-{self.date}>'

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='general')  # general, academic, event, urgent
    target_audience = db.Column(db.String(50), default='all')  # all, students, faculty
    event_date = db.Column(db.DateTime)  # Optional event date
    link = db.Column(db.String(500))  # Optional link
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_pinned = db.Column(db.Boolean, default=False)
    
    # Relationships
    creator = db.relationship('User', backref='announcements')

    def __repr__(self):
        return f'<Announcement {self.title}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    category = db.Column(db.String(50), default='academic')  # academic, cultural, sports, seminar
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    creator = db.relationship('User', backref='events')

    def __repr__(self):
        return f'<Event {self.title}>'

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)
    link_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    creator = db.relationship('User', backref='banners')

    def __repr__(self):
        return f'<Banner {self.title}>'

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    category = db.Column(db.String(50), nullable=False)  # course, faculty, infrastructure, general
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)  # 1-5 scale
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, resolved
    response = db.Column(db.Text)
    responded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
    
    # Relationships
    responder = db.relationship('User', foreign_keys=[responded_by])

    def __repr__(self):
        return f'<Feedback {self.subject}>'

class Enquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    course_interested = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new')  # new, contacted, converted, closed
    source = db.Column(db.String(50), default='website')  # website, phone, walk-in, referral
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    assignee = db.relationship('User', backref='assigned_enquiries')

    def __repr__(self):
        return f'<Enquiry {self.name} - {self.course_interested}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # aicte, jntu, university, government
    document_url = db.Column(db.String(500))
    reference_number = db.Column(db.String(100))
    issue_date = db.Column(db.Date)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_important = db.Column(db.Boolean, default=False)
    
    # Relationships
    creator = db.relationship('User', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.title}>'

class ClassroomAssignment(db.Model):
    """Many-to-many relationship between users and classrooms"""
    __tablename__ = 'classroom_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('assigned_to_classrooms', lazy=True))
    classroom = db.relationship('Classroom', backref=db.backref('assigned_users', lazy=True))
    assigner = db.relationship('User', foreign_keys=[assigned_by], backref=db.backref('classroom_assignments_made', lazy=True))
    
    # Indexes and constraints
    __table_args__ = (
        # Unique constraint to prevent duplicate assignments
        db.UniqueConstraint('user_id', 'classroom_id', name='unique_user_classroom'),
        # For active assignment queries
        db.Index('idx_assignment_user_active', user_id, is_active),
        # For classroom assignment queries
        db.Index('idx_assignment_classroom_active', classroom_id, is_active),
        # For assignment history
        db.Index('idx_assignment_assigned_at', assigned_at),
        # For assigner queries
        db.Index('idx_assignment_assigned_by', assigned_by),
    )
    
    def __repr__(self):
        return f'<ClassroomAssignment user_id={self.user_id} classroom_id={self.classroom_id}>'
