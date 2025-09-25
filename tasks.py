from celery import Celery
from datetime import datetime, timedelta
import os

# Initialize Celery
celery = Celery('tasks', broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

# Configure Celery
celery.conf.update(
    result_backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery.task
def generate_attendance_report(classroom_id, date_range):
    """
    Generate attendance report for a classroom asynchronously
    """
    from app import app
    from models import Attendance, User
    from extensions import db
    
    with app.app_context():
        start_date, end_date = date_range
        
        # Query attendance data
        report_data = db.session.query(
            User.first_name,
            User.last_name,
            User.student_id,
            db.func.count(Attendance.id).label('total_days'),
            db.func.sum(db.case((Attendance.status == 'present', 1), else_=0)).label('present_days'),
            db.func.sum(db.case((Attendance.status == 'absent', 1), else_=0)).label('absent_days'),
            db.func.sum(db.case((Attendance.status == 'late', 1), else_=0)).label('late_days'),
        ).join(
            Attendance, User.id == Attendance.student_id
        ).filter(
            User.classroom_id == classroom_id,
            User.is_active == True,
            Attendance.date.between(start_date, end_date)
        ).group_by(
            User.id,
            User.first_name,
            User.last_name,
            User.student_id
        ).all()
        
        # Format report data
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'classroom_id': classroom_id,
            'date_range': [start_date.isoformat(), end_date.isoformat()],
            'students': [
                {
                    'name': f'{r.first_name} {r.last_name}',
                    'student_id': r.student_id,
                    'total_days': r.total_days,
                    'present_days': r.present_days,
                    'absent_days': r.absent_days,
                    'late_days': r.late_days,
                    'attendance_rate': round((r.present_days + r.late_days) / r.total_days * 100, 2) if r.total_days > 0 else 0
                }
                for r in report_data
            ]
        }
        
        return report

@celery.task
def cleanup_old_attendance():
    """
    Archive attendance records older than 1 year
    """
    from app import app
    from models import Attendance
    from extensions import db
    
    with app.app_context():
        cutoff_date = datetime.utcnow() - timedelta(days=365)
        
        # Get old records
        old_records = Attendance.query.filter(
            Attendance.date < cutoff_date
        ).all()
        
        # TODO: Implement archiving logic (e.g., move to archive table or export to file)
        
        return f'Processed {len(old_records)} old attendance records'

@celery.task
def send_attendance_reminder():
    """
    Send reminders to faculty who haven't marked attendance today
    """
    from app import app
    from models import User, Attendance, ClassroomAssignment
    from extensions import db
    from datetime import date
    
    with app.app_context():
        today = date.today()
        
        # Get faculty with assigned classrooms
        faculty_with_classes = db.session.query(User).join(
            ClassroomAssignment,
            User.id == ClassroomAssignment.user_id
        ).filter(
            User.role == 'faculty',
            User.is_active == True,
            ClassroomAssignment.is_active == True
        ).distinct().all()
        
        reminders_sent = 0
        for faculty in faculty_with_classes:
            # Check if attendance marked today
            marked_today = Attendance.query.filter(
                Attendance.marked_by == faculty.id,
                Attendance.date == today
            ).first()
            
            if not marked_today:
                # TODO: Implement notification logic
                reminders_sent += 1
        
        return f'Sent {reminders_sent} attendance reminders'

# Schedule periodic tasks
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Cleanup old attendance records every month
    sender.add_periodic_task(
        timedelta(days=30),
        cleanup_old_attendance.s(),
        name='cleanup-old-attendance'
    )
    
    # Send attendance reminders at 10 AM every weekday
    sender.add_periodic_task(
        crontab(hour=10, minute=0, day_of_week='1-5'),
        send_attendance_reminder.s(),
        name='send-attendance-reminders'
    )

