from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SelectMultipleField, DateField, IntegerField, BooleanField, DateTimeField, HiddenField
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
