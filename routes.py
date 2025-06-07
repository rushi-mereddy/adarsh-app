import os
import json
from datetime import datetime, date
from flask import render_template, request, redirect, url_for, flash, jsonify, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func, and_, or_, case
from app import app, db
from models import *
from forms import *
from utils import admin_required, faculty_required, student_required, allowed_file, save_uploaded_file

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'faculty':
            return redirect(url_for('faculty_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            if user.is_active:
                login_user(user)
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('index'))
            else:
                flash('Your account has been deactivated. Please contact administrator.', 'error')
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email address already registered.', 'error')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken.', 'error')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(student_id=form.student_id.data).first():
            flash('Student ID already registered.', 'error')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            department=form.department.data,
            student_id=form.student_id.data,
            role='student'
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Student Routes
@app.route('/student/dashboard')
@login_required
@student_required
def student_dashboard():
    # Get recent announcements
    announcements = Announcement.query.filter(
        or_(Announcement.target_audience == 'all', Announcement.target_audience == 'students'),
        Announcement.is_active == True
    ).order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).limit(5).all()
    
    # Get upcoming events
    events = Event.query.filter(
        Event.event_date >= datetime.now(),
        Event.is_active == True
    ).order_by(Event.event_date).limit(5).all()
    
    # Get enrolled courses
    enrolled_courses = db.session.query(Course).join(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.is_active == True,
        Course.is_active == True
    ).all()
    
    # Get attendance summary
    attendance_summary = []
    for course in enrolled_courses:
        total_classes = Attendance.query.filter_by(
            student_id=current_user.id,
            course_id=course.id
        ).count()
        
        present_classes = Attendance.query.filter_by(
            student_id=current_user.id,
            course_id=course.id,
            status='present'
        ).count()
        
        percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        attendance_summary.append({
            'course': course,
            'total': total_classes,
            'present': present_classes,
            'percentage': round(percentage, 2)
        })
    
    return render_template('student/dashboard.html',
                         announcements=announcements,
                         events=events,
                         attendance_summary=attendance_summary)

@app.route('/student/profile', methods=['GET', 'POST'])
@login_required
@student_required
def student_profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.date_of_birth = form.date_of_birth.data
        current_user.department = form.department.data
        
        # Handle profile image upload
        if form.profile_image.data:
            filename = save_uploaded_file(form.profile_image.data, 'profiles')
            if filename:
                current_user.profile_image = filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student_profile'))
    
    return render_template('student/profile.html', form=form)

@app.route('/student/attendance')
@login_required
@student_required
def student_attendance():
    # Get enrolled courses
    enrolled_courses = db.session.query(Course).join(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.is_active == True,
        Course.is_active == True
    ).all()
    
    attendance_data = []
    for course in enrolled_courses:
        records = Attendance.query.filter_by(
            student_id=current_user.id,
            course_id=course.id
        ).order_by(Attendance.date.desc()).all()
        
        total_classes = len(records)
        present_classes = len([r for r in records if r.status == 'present'])
        percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        attendance_data.append({
            'course': course,
            'records': records,
            'total_classes': total_classes,
            'present_classes': present_classes,
            'percentage': round(percentage, 2)
        })
    
    return render_template('student/attendance.html', attendance_data=attendance_data)

# Faculty Routes
@app.route('/faculty/dashboard')
@login_required
@faculty_required
def faculty_dashboard():
    # Get courses taught by faculty
    courses = Course.query.filter_by(faculty_id=current_user.id, is_active=True).all()
    
    # Get recent announcements
    announcements = Announcement.query.filter(
        or_(Announcement.target_audience == 'all', Announcement.target_audience == 'faculty'),
        Announcement.is_active == True
    ).order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).limit(5).all()
    
    # Get upcoming events
    events = Event.query.filter(
        Event.event_date >= datetime.now(),
        Event.is_active == True
    ).order_by(Event.event_date).limit(5).all()
    
    # Calculate attendance statistics for each course
    course_stats = []
    for course in courses:
        total_students = db.session.query(Enrollment).filter_by(
            course_id=course.id, is_active=True
        ).count()
        
        recent_classes = Attendance.query.filter_by(course_id=course.id).filter(
            Attendance.date >= datetime.now().date().replace(day=1)
        ).count()
        
        course_stats.append({
            'course': course,
            'total_students': total_students,
            'recent_classes': recent_classes
        })
    
    return render_template('faculty/dashboard.html',
                         course_stats=course_stats,
                         announcements=announcements,
                         events=events)

@app.route('/faculty/attendance', methods=['GET', 'POST'])
@login_required
@faculty_required
def faculty_attendance():
    # Get courses taught by this faculty
    courses = Course.query.filter_by(faculty_id=current_user.id, is_active=True).all()
    
    form = AttendanceForm()
    form.course_id.choices = [(c.id, f"{c.code} - {c.name}") for c in courses]
    
    selected_course = None
    students = []
    existing_attendance = {}
    
    # Get filter parameters for classroom-based filtering
    department = request.args.get('department', '')
    year = request.args.get('year', type=int)
    semester = request.args.get('semester', type=int)
    section = request.args.get('section', '')
    course_id = request.args.get('course_id', type=int)
    attendance_date = request.args.get('date')
    
    if request.method == 'POST':
        if form.validate_on_submit():
            # Process attendance submission
            course_id = form.course_id.data
            attendance_date = form.date.data
            student_attendances = json.loads(form.student_attendances.data)
            
            # Delete existing attendance for this date and course
            Attendance.query.filter_by(
                course_id=course_id,
                date=attendance_date
            ).delete()
            
            # Add new attendance records
            for student_id, status in student_attendances.items():
                attendance = Attendance(
                    student_id=int(student_id),
                    course_id=course_id,
                    date=attendance_date,
                    status=status,
                    marked_by=current_user.id
                )
                db.session.add(attendance)
            
            db.session.commit()
            flash('Attendance marked successfully!', 'success')
            return redirect(url_for('faculty_attendance'))
    
    # Build student query based on classroom parameters
    if department or year or semester or section:
        student_query = User.query.filter(User.role == 'student', User.is_active == True)
        
        if department:
            student_query = student_query.filter(User.department == department)
        if year:
            student_query = student_query.filter(User.year == year)
        if semester:
            student_query = student_query.filter(User.semester == semester)
        if section:
            student_query = student_query.filter(User.section == section)
            
        students = student_query.order_by(User.first_name, User.last_name).all()
    
    # Handle course selection and existing attendance
    if course_id:
        selected_course = Course.query.get(course_id)
        if selected_course and selected_course.faculty_id == current_user.id:
            form.course_id.data = course_id
            
            # Get existing attendance for the date
            if attendance_date:
                try:
                    date_obj = datetime.strptime(attendance_date, '%Y-%m-%d').date()
                    attendance_records = Attendance.query.filter_by(
                        course_id=course_id,
                        date=date_obj
                    ).all()
                    existing_attendance = {str(a.student_id): a.status for a in attendance_records}
                    form.date.data = date_obj
                except:
                    pass
    
    # Get available filter options
    departments = db.session.query(User.department).filter(User.role == 'student', User.department.isnot(None)).distinct().all()
    years = db.session.query(User.year).filter(User.role == 'student', User.year.isnot(None)).distinct().order_by(User.year).all()
    semesters = db.session.query(User.semester).filter(User.role == 'student', User.semester.isnot(None)).distinct().order_by(User.semester).all()
    sections = db.session.query(User.section).filter(User.role == 'student', User.section.isnot(None)).distinct().order_by(User.section).all()
    
    return render_template('faculty/attendance.html',
                         form=form,
                         courses=courses,
                         selected_course=selected_course,
                         students=students,
                         existing_attendance=existing_attendance,
                         selected_date=attendance_date,
                         departments=[d[0] for d in departments if d[0]],
                         years=[y[0] for y in years if y[0]],
                         semesters=[s[0] for s in semesters if s[0]],
                         sections=[sec[0] for sec in sections if sec[0]],
                         filters={
                             'department': department,
                             'year': year,
                             'semester': semester,
                             'section': section
                         })

# Admin Routes
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # Get basic statistics
    total_students = User.query.filter_by(role='student', is_active=True).count()
    total_faculty = User.query.filter_by(role='faculty', is_active=True).count()
    total_courses = Course.query.filter_by(is_active=True).count()
    
    # Get recent activities
    recent_announcements = Announcement.query.filter_by(is_active=True).order_by(
        Announcement.created_at.desc()
    ).limit(5).all()
    
    recent_enquiries = Enquiry.query.filter_by(status='new').order_by(
        Enquiry.created_at.desc()
    ).limit(5).all()
    
    # Get attendance overview (last 30 days)
    from datetime import timedelta
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    
    attendance_stats = db.session.query(
        func.date(Attendance.date).label('date'),
        func.count(Attendance.id).label('total_records'),
        func.sum(case((Attendance.status == 'present', 1), else_=0)).label('present_count')
    ).filter(
        Attendance.date >= thirty_days_ago
    ).group_by(func.date(Attendance.date)).order_by(Attendance.date.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         total_faculty=total_faculty,
                         total_courses=total_courses,
                         recent_announcements=recent_announcements,
                         recent_enquiries=recent_enquiries,
                         attendance_stats=attendance_stats)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', 'all')
    search = request.args.get('search', '')
    
    query = User.query
    
    if role_filter != 'all':
        query = query.filter(User.role == role_filter)
    
    if search:
        query = query.filter(or_(
            User.username.contains(search),
            User.email.contains(search),
            User.first_name.contains(search),
            User.last_name.contains(search)
        ))
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users, role_filter=role_filter, search=search)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_user():
    form = UserForm()
    
    if form.validate_on_submit():
        # Check for existing users
        if User.query.filter_by(email=form.email.data).first():
            flash('Email address already exists.', 'error')
            return render_template('admin/users.html', form=form)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'error')
            return render_template('admin/users.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data,
            phone=form.phone.data,
            department=form.department.data,
            student_id=form.student_id.data if form.role.data == 'student' else None,
            faculty_id=form.faculty_id.data if form.role.data == 'faculty' else None,
            is_active=form.is_active.data,
            password_hash=generate_password_hash(form.password.data or 'defaultpass123')
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/users.html', form=form, action='add')

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        # Check for email conflicts
        existing_user = User.query.filter(User.email == form.email.data, User.id != user_id).first()
        if existing_user:
            flash('Email address already exists.', 'error')
            return render_template('admin/users.html', form=form, user=user, action='edit')
        
        # Update user
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.role = form.role.data
        user.phone = form.phone.data
        user.department = form.department.data
        user.student_id = form.student_id.data if form.role.data == 'student' else None
        user.faculty_id = form.faculty_id.data if form.role.data == 'faculty' else None
        user.is_active = form.is_active.data
        
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/users.html', form=form, user=user, action='edit')

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin_users'))
    
    # Soft delete by deactivating
    user.is_active = False
    db.session.commit()
    
    flash('User deactivated successfully!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/courses')
@login_required
@admin_required
def admin_courses():
    courses = Course.query.filter_by(is_active=True).order_by(Course.created_at.desc()).all()
    return render_template('admin/courses.html', courses=courses)

@app.route('/admin/courses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_course():
    form = CourseForm()
    
    # Populate faculty choices
    faculty_users = User.query.filter_by(role='faculty', is_active=True).all()
    form.faculty_id.choices = [(0, 'Select Faculty')] + [(f.id, f.get_full_name()) for f in faculty_users]
    
    if form.validate_on_submit():
        # Check for existing course code
        if Course.query.filter_by(code=form.code.data).first():
            flash('Course code already exists.', 'error')
            return render_template('admin/courses.html', form=form, action='add')
        
        course = Course(
            name=form.name.data,
            code=form.code.data,
            description=form.description.data,
            credits=form.credits.data,
            department=form.department.data,
            semester=form.semester.data,
            faculty_id=form.faculty_id.data if form.faculty_id.data > 0 else None
        )
        
        db.session.add(course)
        db.session.commit()
        
        flash('Course created successfully!', 'success')
        return redirect(url_for('admin_courses'))
    
    return render_template('admin/courses.html', form=form, action='add')

@app.route('/admin/announcements')
@login_required
@admin_required
def admin_announcements():
    announcements = Announcement.query.filter_by(is_active=True).order_by(
        Announcement.is_pinned.desc(), Announcement.created_at.desc()
    ).all()
    return render_template('admin/announcements.html', announcements=announcements)

@app.route('/admin/announcements/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_announcement():
    form = AnnouncementForm()
    
    if form.validate_on_submit():
        announcement = Announcement(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            target_audience=form.target_audience.data,
            expires_at=form.expires_at.data,
            is_pinned=form.is_pinned.data,
            created_by=current_user.id
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        flash('Announcement created successfully!', 'success')
        return redirect(url_for('admin_announcements'))
    
    return render_template('admin/announcements.html', form=form, action='add')

@app.route('/admin/banners')
@login_required
@admin_required
def admin_banners():
    banners = Banner.query.filter_by(is_active=True).order_by(Banner.display_order, Banner.created_at.desc()).all()
    return render_template('admin/banners.html', banners=banners)

@app.route('/admin/banners/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_banner():
    form = BannerForm()
    
    if form.validate_on_submit():
        # Save uploaded image
        filename = save_uploaded_file(form.image.data, 'banners')
        if filename:
            banner = Banner(
                title=form.title.data,
                image_path=filename,
                link_url=form.link_url.data,
                description=form.description.data,
                display_order=form.display_order.data or 0,
                created_by=current_user.id
            )
            
            db.session.add(banner)
            db.session.commit()
            
            flash('Banner uploaded successfully!', 'success')
            return redirect(url_for('admin_banners'))
        else:
            flash('Error uploading image.', 'error')
    
    return render_template('admin/banners.html', form=form, action='add')

@app.route('/admin/feedback')
@login_required
@admin_required
def admin_feedback():
    feedback_list = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('admin/feedback.html', feedback_list=feedback_list)

@app.route('/admin/feedback/<int:feedback_id>/respond', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_respond_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    form = FeedbackResponseForm()
    
    if form.validate_on_submit():
        feedback.response = form.response.data
        feedback.status = form.status.data
        feedback.responded_by = current_user.id
        feedback.responded_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Feedback response submitted successfully!', 'success')
        return redirect(url_for('admin_feedback'))
    
    return render_template('admin/feedback.html', feedback=feedback, form=form, action='respond')

@app.route('/admin/enquiries')
@login_required
@admin_required
def admin_enquiries():
    enquiries = Enquiry.query.order_by(Enquiry.created_at.desc()).all()
    return render_template('admin/enquiries.html', enquiries=enquiries)

@app.route('/admin/enquiries/<int:enquiry_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_update_enquiry(enquiry_id):
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    form = EnquiryUpdateForm(obj=enquiry)
    
    # Populate assignee choices
    staff_users = User.query.filter(User.role.in_(['admin', 'faculty']), User.is_active == True).all()
    form.assigned_to.choices = [(0, 'Unassigned')] + [(u.id, u.get_full_name()) for u in staff_users]
    
    if form.validate_on_submit():
        enquiry.status = form.status.data
        enquiry.assigned_to = form.assigned_to.data if form.assigned_to.data > 0 else None
        enquiry.notes = form.notes.data
        enquiry.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Enquiry updated successfully!', 'success')
        return redirect(url_for('admin_enquiries'))
    
    return render_template('admin/enquiries.html', enquiry=enquiry, form=form, action='update')

@app.route('/admin/notifications')
@login_required
@admin_required
def admin_notifications():
    notifications = Notification.query.filter_by(is_active=True).order_by(
        Notification.is_important.desc(), Notification.created_at.desc()
    ).all()
    return render_template('admin/notifications.html', notifications=notifications)

@app.route('/admin/notifications/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_notification():
    form = NotificationForm()
    
    if form.validate_on_submit():
        notification = Notification(
            title=form.title.data,
            content=form.content.data,
            notification_type=form.notification_type.data,
            document_url=form.document_url.data,
            reference_number=form.reference_number.data,
            issue_date=form.issue_date.data,
            is_important=form.is_important.data,
            created_by=current_user.id
        )
        
        db.session.add(notification)
        db.session.commit()
        
        flash('Notification created successfully!', 'success')
        return redirect(url_for('admin_notifications'))
    
    return render_template('admin/notifications.html', form=form, action='add')



# Public Routes (for enquiries)
@app.route('/enquiry', methods=['GET', 'POST'])
def public_enquiry():
    form = EnquiryForm()
    
    if form.validate_on_submit():
        enquiry = Enquiry(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            course_interested=form.course_interested.data,
            message=form.message.data
        )
        
        db.session.add(enquiry)
        db.session.commit()
        
        flash('Your enquiry has been submitted successfully! We will contact you soon.', 'success')
        return redirect(url_for('public_enquiry'))
    
    return render_template('enquiry.html', form=form)

# Student Feedback Route
@app.route('/student/feedback', methods=['GET', 'POST'])
@login_required
@student_required
def student_feedback():
    form = FeedbackForm()
    
    # Get courses the student is enrolled in
    enrolled_courses = db.session.query(Course).join(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.is_active == True,
        Course.is_active == True
    ).all()
    
    form.course_id.choices = [(0, 'General Feedback (not course specific)')] + [(c.id, f"{c.code} - {c.name}") for c in enrolled_courses]
    
    if form.validate_on_submit():
        feedback = Feedback(
            student_id=current_user.id,
            course_id=form.course_id.data if form.course_id.data > 0 else None,
            category=form.category.data,
            subject=form.subject.data,
            message=form.message.data,
            rating=form.rating.data
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        flash('Your feedback has been submitted successfully!', 'success')
        return redirect(url_for('student_feedback'))
    
    # Get user's previous feedback
    previous_feedback = Feedback.query.filter_by(student_id=current_user.id).order_by(
        Feedback.created_at.desc()
    ).limit(10).all()
    
    return render_template('student/feedback.html', form=form, previous_feedback=previous_feedback)

# Error handlers
# Admin - Classroom Management
@app.route('/admin/classrooms')
@login_required
@admin_required
def admin_classrooms():
    classrooms = Classroom.query.filter_by(is_active=True).order_by(Classroom.department, Classroom.year, Classroom.semester, Classroom.section).all()
    
    # Get statistics
    total_classrooms = len(classrooms)
    students_assigned = db.session.query(User).filter(User.classroom_id.isnot(None), User.role == 'student').count()
    faculty_assigned = db.session.query(User).filter(User.classroom_id.isnot(None), User.role == 'faculty').count()
    
    return render_template('admin/classrooms.html',
                         classrooms=classrooms,
                         total_classrooms=total_classrooms,
                         students_assigned=students_assigned,
                         faculty_assigned=faculty_assigned)

@app.route('/admin/classrooms/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_classroom():
    form = ClassroomForm()
    
    if form.validate_on_submit():
        # Auto-generate name if not provided
        if not form.name.data:
            form.name.data = f"{form.department.data} Year {form.year.data} Sem {form.semester.data} Section {form.section.data}"
        
        classroom = Classroom(
            name=form.name.data,
            department=form.department.data,
            year=form.year.data,
            semester=form.semester.data,
            section=form.section.data,
            academic_year=form.academic_year.data or f"{datetime.now().year}-{datetime.now().year + 1}",
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        try:
            db.session.add(classroom)
            db.session.commit()
            flash(f'Classroom "{classroom.name}" created successfully', 'success')
            return redirect(url_for('admin_classrooms'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating classroom. Please try again.', 'error')
    
    return render_template('admin/add_classroom.html', form=form)

@app.route('/admin/classrooms/<int:classroom_id>/assign', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_assign_classroom(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    form = ClassroomAssignmentForm()
    
    # Populate classroom choices (just this one)
    form.classroom_id.choices = [(classroom.id, classroom.get_classroom_name())]
    form.classroom_id.data = classroom.id
    
    # Get selected user type (default to students)
    user_type = request.form.get('user_type', 'student')
    form.user_type.data = user_type
    
    # Populate user choices based on selected type
    if user_type == 'student':
        users = User.query.filter_by(role='student', is_active=True, classroom_id=None).order_by(User.first_name, User.last_name).all()
    else:
        users = User.query.filter_by(role='faculty', is_active=True).order_by(User.first_name, User.last_name).all()
    
    form.user_ids.choices = [(u.id, f"{u.get_full_name()} ({u.student_id if u.role == 'student' else u.faculty_id})") for u in users]
    
    if request.method == 'POST' and form.validate_on_submit():
        user_ids = form.user_ids.data
        assigned_count = 0
        
        for user_id in user_ids:
            user = User.query.get(user_id)
            if user and user.role == user_type:
                user.classroom_id = classroom.id
                # Also update user's individual fields for filtering
                user.department = classroom.department
                user.year = classroom.year
                user.semester = classroom.semester
                user.section = classroom.section
                assigned_count += 1
        
        try:
            db.session.commit()
            flash(f'Successfully assigned {assigned_count} {user_type}s to {classroom.name}', 'success')
            return redirect(url_for('admin_classrooms'))
        except Exception as e:
            db.session.rollback()
            flash('Error assigning users to classroom. Please try again.', 'error')
    
    # Get current assignments
    current_students = User.query.filter_by(classroom_id=classroom.id, role='student').all()
    current_faculty = User.query.filter_by(classroom_id=classroom.id, role='faculty').all()
    
    return render_template('admin/assign_classroom.html', 
                         form=form, 
                         classroom=classroom,
                         current_students=current_students,
                         current_faculty=current_faculty)

@app.route('/admin/classrooms/<int:classroom_id>/remove/<int:user_id>')
@login_required
@admin_required
def admin_remove_from_classroom(classroom_id, user_id):
    user = User.query.get_or_404(user_id)
    classroom = Classroom.query.get_or_404(classroom_id)
    
    user.classroom_id = None
    user.department = None
    user.year = None
    user.semester = None
    user.section = None
    
    try:
        db.session.commit()
        flash(f'{user.get_full_name()} removed from {classroom.name}', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error removing user from classroom. Please try again.', 'error')
    
    return redirect(url_for('admin_assign_classroom', classroom_id=classroom_id))

# Admin - Course Enrollments (Keep existing for backward compatibility)
@app.route('/admin/enrollments')
@login_required
@admin_required
def admin_enrollments():
    # Get all enrollments with student and course details
    enrollments = db.session.query(Enrollment).join(User, Enrollment.student_id == User.id).join(Course, Enrollment.course_id == Course.id).filter(Enrollment.is_active == True).order_by(Course.name, User.first_name, User.last_name).all()
    
    # Get counts
    total_enrollments = len(enrollments)
    courses_with_students = db.session.query(Course.id).join(Enrollment).filter(Enrollment.is_active == True).distinct().count()
    students_enrolled = db.session.query(User.id).join(Enrollment).filter(Enrollment.is_active == True, User.role == 'student').distinct().count()
    
    return render_template('admin/enrollments.html',
                         enrollments=enrollments,
                         total_enrollments=total_enrollments,
                         courses_with_students=courses_with_students,
                         students_enrolled=students_enrolled)

@app.route('/admin/enrollments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_enrollment():
    form = BulkEnrollmentForm()
    
    # Populate course choices
    courses = Course.query.filter_by(is_active=True).order_by(Course.name).all()
    form.course_id.choices = [(c.id, f"{c.code} - {c.name}") for c in courses]
    
    # Populate student choices
    students = User.query.filter_by(role='student', is_active=True).order_by(User.first_name, User.last_name).all()
    form.student_ids.choices = [(s.id, f"{s.get_full_name()} ({s.student_id})") for s in students]
    
    if form.validate_on_submit():
        course_id = form.course_id.data
        student_ids = form.student_ids.data
        
        enrolled_count = 0
        already_enrolled = []
        
        for student_id in student_ids:
            # Check if already enrolled
            existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
            if existing:
                if existing.is_active:
                    student = User.query.get(student_id)
                    already_enrolled.append(student.get_full_name())
                else:
                    # Reactivate enrollment
                    existing.is_active = True
                    existing.enrollment_date = datetime.utcnow()
                    enrolled_count += 1
            else:
                # Create new enrollment
                enrollment = Enrollment(
                    student_id=student_id,
                    course_id=course_id,
                    enrollment_date=datetime.utcnow(),
                    is_active=True
                )
                db.session.add(enrollment)
                enrolled_count += 1
        
        try:
            db.session.commit()
            course = Course.query.get(course_id)
            flash(f'Successfully enrolled {enrolled_count} students in {course.name}', 'success')
            if already_enrolled:
                flash(f'Note: {", ".join(already_enrolled)} were already enrolled', 'info')
            return redirect(url_for('admin_enrollments'))
        except Exception as e:
            db.session.rollback()
            flash('Error enrolling students. Please try again.', 'error')
    
    return render_template('admin/add_enrollment.html', form=form)

@app.route('/admin/enrollments/remove/<int:enrollment_id>')
@login_required
@admin_required
def admin_remove_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    enrollment.is_active = False
    
    try:
        db.session.commit()
        flash('Student removed from course successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error removing enrollment. Please try again.', 'error')
    
    return redirect(url_for('admin_enrollments'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.route('/admin/attendance-overview')
@login_required
@admin_required
def admin_attendance_overview():
    from sqlalchemy import func, distinct
    from datetime import datetime, timedelta
    
    # Get filter parameters
    department = request.args.get('department', '')
    year = request.args.get('year', type=int)
    semester = request.args.get('semester', type=int)
    section = request.args.get('section', '')
    course_id = request.args.get('course_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Set default date range (last 30 days)
    if not date_from:
        date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = datetime.now().strftime('%Y-%m-%d')
    
    # Base query for attendance records
    query = db.session.query(
        Attendance.course_id,
        Course.name.label('course_name'),
        Course.code.label('course_code'),
        User.department,
        User.year,
        User.semester,
        User.section,
        func.count(Attendance.id).label('total_records'),
        func.sum(func.case((Attendance.status == 'present', 1), else_=0)).label('present_count'),
        func.sum(func.case((Attendance.status == 'absent', 1), else_=0)).label('absent_count'),
        func.sum(func.case((Attendance.status == 'late', 1), else_=0)).label('late_count'),
        func.count(distinct(Attendance.student_id)).label('total_students'),
        func.count(distinct(Attendance.date)).label('total_days')
    ).join(Course, Attendance.course_id == Course.id)\
     .join(User, Attendance.student_id == User.id)\
     .filter(Attendance.date >= date_from)\
     .filter(Attendance.date <= date_to)
    
    # Apply filters
    if department:
        query = query.filter(User.department == department)
    if year:
        query = query.filter(User.year == year)
    if semester:
        query = query.filter(User.semester == semester)
    if section:
        query = query.filter(User.section == section)
    if course_id:
        query = query.filter(Attendance.course_id == course_id)
    
    # Group by course and classroom parameters
    stats = query.group_by(
        Attendance.course_id,
        Course.name,
        Course.code,
        User.department,
        User.year,
        User.semester,
        User.section
    ).all()
    
    # Calculate percentages and format data
    attendance_stats = []
    for stat in stats:
        total = stat.total_records
        if total > 0:
            present_percentage = round((stat.present_count / total) * 100, 1)
            absent_percentage = round((stat.absent_count / total) * 100, 1)
            late_percentage = round((stat.late_count / total) * 100, 1)
        else:
            present_percentage = absent_percentage = late_percentage = 0
            
        attendance_stats.append({
            'course_id': stat.course_id,
            'course_name': stat.course_name,
            'course_code': stat.course_code,
            'department': stat.department or 'N/A',
            'year': stat.year or 'N/A',
            'semester': stat.semester or 'N/A',
            'section': stat.section or 'N/A',
            'classroom': f"{stat.department or 'N/A'} - Y{stat.year or 'N/A'}/S{stat.semester or 'N/A'}/{stat.section or 'N/A'}",
            'total_records': stat.total_records,
            'present_count': stat.present_count,
            'absent_count': stat.absent_count,
            'late_count': stat.late_count,
            'total_students': stat.total_students,
            'total_days': stat.total_days,
            'present_percentage': present_percentage,
            'absent_percentage': absent_percentage,
            'late_percentage': late_percentage,
            'attendance_rate': present_percentage + late_percentage  # Consider late as attended
        })
    
    # Get filter options
    departments = db.session.query(distinct(User.department)).filter(User.department.isnot(None)).all()
    departments = [dept[0] for dept in departments if dept[0]]
    
    years = db.session.query(distinct(User.year)).filter(User.year.isnot(None)).all()
    years = sorted([year[0] for year in years if year[0]])
    
    semesters = db.session.query(distinct(User.semester)).filter(User.semester.isnot(None)).all()
    semesters = sorted([sem[0] for sem in semesters if sem[0]])
    
    sections = db.session.query(distinct(User.section)).filter(User.section.isnot(None)).all()
    sections = sorted([sec[0] for sec in sections if sec[0]])
    
    courses = Course.query.all()
    
    # Calculate overall statistics
    total_attendance_records = sum(stat['total_records'] for stat in attendance_stats)
    total_present = sum(stat['present_count'] for stat in attendance_stats)
    total_absent = sum(stat['absent_count'] for stat in attendance_stats)
    total_late = sum(stat['late_count'] for stat in attendance_stats)
    
    overall_stats = {
        'total_records': total_attendance_records,
        'present_count': total_present,
        'absent_count': total_absent,
        'late_count': total_late,
        'present_percentage': round((total_present / total_attendance_records * 100), 1) if total_attendance_records > 0 else 0,
        'absent_percentage': round((total_absent / total_attendance_records * 100), 1) if total_attendance_records > 0 else 0,
        'late_percentage': round((total_late / total_attendance_records * 100), 1) if total_attendance_records > 0 else 0,
        'total_classes': len(set(f"{stat['department']}-{stat['year']}-{stat['semester']}-{stat['section']}" for stat in attendance_stats)),
        'total_courses': len(set(stat['course_id'] for stat in attendance_stats))
    }
    
    filters = {
        'department': department,
        'year': year,
        'semester': semester,
        'section': section,
        'course_id': course_id,
        'date_from': date_from,
        'date_to': date_to
    }
    
    return render_template('admin/attendance_overview.html',
                         attendance_stats=attendance_stats,
                         overall_stats=overall_stats,
                         departments=departments,
                         years=years,
                         semesters=semesters,
                         sections=sections,
                         courses=courses,
                         filters=filters)

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
