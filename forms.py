from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SelectMultipleField, DateField, IntegerField, BooleanField, DateTimeField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    department = StringField('Department', validators=[DataRequired(), Length(max=100)])
    student_id = StringField('Student ID', validators=[DataRequired(), Length(max=50)])

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional()])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    department = StringField('Department', validators=[Optional(), Length(max=100)])
    profile_image = FileField('Profile Image', 
                            validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])

class CourseForm(FlaskForm):
    name = StringField('Course Name', validators=[DataRequired(), Length(max=200)])
    code = StringField('Course Code', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Description', validators=[Optional()])
    credits = IntegerField('Credits', validators=[DataRequired(), NumberRange(min=1, max=10)])
    department = StringField('Department', validators=[DataRequired(), Length(max=100)])
    semester = StringField('Semester', validators=[Optional(), Length(max=20)])
    faculty_id = SelectField('Faculty', coerce=int, validators=[DataRequired()])

class AttendanceForm(FlaskForm):
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    student_attendances = HiddenField('Student Attendances')

class AnnouncementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()], widget=TextArea())
    category = SelectField('Category', 
                         choices=[('general', 'General'), ('academic', 'Academic'), 
                                ('event', 'Event'), ('urgent', 'Urgent')],
                         default='general')
    target_audience = SelectField('Target Audience',
                                choices=[('all', 'All'), ('students', 'Students Only'), 
                                       ('faculty', 'Faculty Only')],
                                default='all')
    expires_at = DateTimeField('Expires At', validators=[Optional()])
    is_pinned = BooleanField('Pin this announcement')

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    event_date = DateTimeField('Event Date & Time', validators=[DataRequired()])
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    category = SelectField('Category',
                         choices=[('academic', 'Academic'), ('cultural', 'Cultural'),
                                ('sports', 'Sports'), ('seminar', 'Seminar')],
                         default='academic')

class BannerForm(FlaskForm):
    title = StringField('Banner Title', validators=[DataRequired(), Length(max=200)])
    image = FileField('Banner Image', 
                     validators=[DataRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    link_url = StringField('Link URL', validators=[Optional(), Length(max=500)])
    description = TextAreaField('Description', validators=[Optional()])
    display_order = IntegerField('Display Order', validators=[Optional(), NumberRange(min=0)])

class FeedbackResponseForm(FlaskForm):
    response = TextAreaField('Response', validators=[DataRequired()], widget=TextArea())
    status = SelectField('Status',
                        choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), 
                               ('resolved', 'Resolved')],
                        default='reviewed')

class FeedbackForm(FlaskForm):
    course_id = SelectField('Course (Optional)', coerce=int, validators=[Optional()])
    category = SelectField('Category',
                         choices=[('course', 'Course'), ('faculty', 'Faculty'),
                                ('infrastructure', 'Infrastructure'), ('general', 'General')],
                         validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired()], widget=TextArea())
    rating = SelectField('Rating (Optional)',
                        choices=[('', 'Select Rating'), ('5', '5 - Excellent'), 
                               ('4', '4 - Good'), ('3', '3 - Average'),
                               ('2', '2 - Poor'), ('1', '1 - Very Poor')],
                        coerce=int, validators=[Optional()])

class EnquiryForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    course_interested = StringField('Course Interested In', validators=[Optional(), Length(max=100)])
    message = TextAreaField('Message', validators=[DataRequired()], widget=TextArea())

class EnquiryUpdateForm(FlaskForm):
    status = SelectField('Status',
                        choices=[('new', 'New'), ('contacted', 'Contacted'),
                               ('converted', 'Converted'), ('closed', 'Closed')],
                        validators=[DataRequired()])
    assigned_to = SelectField('Assign To', coerce=int, validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])

class NotificationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()], widget=TextArea())
    notification_type = SelectField('Type',
                                  choices=[('aicte', 'AICTE'), ('jntu', 'JNTU'),
                                         ('university', 'University'), ('government', 'Government')],
                                  validators=[DataRequired()])
    document_url = StringField('Document URL', validators=[Optional(), Length(max=500)])
    reference_number = StringField('Reference Number', validators=[Optional(), Length(max=100)])
    issue_date = DateField('Issue Date', validators=[Optional()])
    is_important = BooleanField('Mark as Important')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    role = SelectField('Role',
                      choices=[('student', 'Student'), ('faculty', 'Faculty'), ('admin', 'Admin')],
                      validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    department = StringField('Department', validators=[Optional(), Length(max=100)])
    student_id = StringField('Student ID', validators=[Optional(), Length(max=50)])
    faculty_id = StringField('Faculty ID', validators=[Optional(), Length(max=50)])
    is_active = BooleanField('Active', default=True)
    password = PasswordField('Password (leave blank to keep current)', validators=[Optional(), Length(min=6)])

class EnrollmentForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    course_ids = SelectMultipleField('Courses', coerce=int, validators=[DataRequired()])
    
class BulkEnrollmentForm(FlaskForm):
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    student_ids = SelectMultipleField('Students', coerce=int, validators=[DataRequired()])

class ClassroomForm(FlaskForm):
    name = StringField('Classroom Name', validators=[DataRequired(), Length(max=100)])
    department = SelectField('Department', validators=[DataRequired()],
                             choices=[('CSE', 'Computer Science Engineering'),
                                    ('ECE', 'Electronics & Communication'),
                                    ('EEE', 'Electrical & Electronics'),
                                    ('MECH', 'Mechanical Engineering'),
                                    ('CIVIL', 'Civil Engineering'),
                                    ('IT', 'Information Technology')])
    year = SelectField('Year', coerce=int, validators=[DataRequired()],
                      choices=[(1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')])
    semester = SelectField('Semester', coerce=int, validators=[DataRequired()],
                          choices=[(1, '1st Semester'), (2, '2nd Semester'), (3, '3rd Semester'),
                                 (4, '4th Semester'), (5, '5th Semester'), (6, '6th Semester'),
                                 (7, '7th Semester'), (8, '8th Semester')])
    section = SelectField('Section', validators=[DataRequired()],
                         choices=[('A', 'Section A'), ('B', 'Section B'), ('C', 'Section C'),
                                ('D', 'Section D'), ('E', 'Section E')])
    academic_year = StringField('Academic Year', validators=[Optional(), Length(max=20)])

class ClassroomAssignmentForm(FlaskForm):
    classroom_id = SelectField('Classroom', coerce=int, validators=[DataRequired()])
    user_ids = SelectMultipleField('Students/Faculty', coerce=int, validators=[DataRequired()])
    user_type = SelectField('User Type', validators=[DataRequired()],
                           choices=[('student', 'Students'), ('faculty', 'Faculty')])

class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired(), Length(max=100)])
    code = StringField('Department Code', validators=[DataRequired(), Length(max=10)])
    program = SelectField('Program Type', validators=[DataRequired()],
                         choices=[('UG', 'Undergraduate (UG)'), ('PG', 'Postgraduate (PG)'), ('Diploma', 'Diploma')])
    description = TextAreaField('Description', validators=[Optional()])
    image = FileField('Department Image', 
                     validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    established_year = IntegerField('Established Year', validators=[Optional(), NumberRange(min=1900, max=2030)])
    submit = SubmitField('Save Department')

class LecturerForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    photo = FileField('Profile Photo', 
                     validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    experience = StringField('Experience', validators=[Optional(), Length(max=100)])
    qualification = StringField('Educational Qualification', validators=[Optional(), Length(max=200)])
    specialization = StringField('Specialization/Area of Expertise', validators=[Optional(), Length(max=200)])
    designation = StringField('Designation', validators=[Optional(), Length(max=100)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    display_order = IntegerField('Display Order', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Save Lecturer')

class StudentReviewForm(FlaskForm):
    student_name = StringField('Student Name', validators=[DataRequired(), Length(max=100)])
    photo = FileField('Student Photo', 
                     validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    review_text = TextAreaField('Review/Testimonial', validators=[DataRequired()])
    rating = SelectField('Rating', coerce=int, validators=[DataRequired()],
                        choices=[(5, '5 Stars - Excellent'), (4, '4 Stars - Very Good'), 
                               (3, '3 Stars - Good'), (2, '2 Stars - Fair'), (1, '1 Star - Poor')])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    student_batch = StringField('Student Batch', validators=[Optional(), Length(max=20)])
    current_position = StringField('Current Position/Job', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Save Review')
