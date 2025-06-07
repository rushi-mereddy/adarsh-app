# College Management System

A comprehensive role-based college management system built with Flask, featuring modern UI design and classroom-based attendance tracking.

## Features

### Core Functionality
- **Role-based Access Control**: Student, Faculty, and Admin roles
- **Classroom-based Attendance**: Filter students by department, year, semester, section
- **Department Management**: Complete department profiles with lecturer information
- **Student Management**: Bulk import via Excel, classroom assignments
- **Announcement System**: Targeted announcements for different user groups
- **Enquiry Management**: Handle prospective student enquiries
- **Modern UI**: Ultra-light theme with glassmorphism effects

### User Roles

#### Admin Features
- User management (Students, Faculty, Admin)
- Department and lecturer management
- Classroom creation and management
- Attendance overview and analytics
- Announcement and notification management
- Excel import for bulk student creation

#### Faculty Features
- Classroom-based attendance marking
- Student filtering by classroom parameters
- Dashboard with attendance statistics
- Announcement viewing

#### Student Features
- Personal attendance tracking
- Announcement viewing
- Profile management

## Technology Stack

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **Frontend**: Bootstrap 5, Custom CSS with glassmorphism
- **Authentication**: Flask-Login
- **File Handling**: Excel import/export
- **Deployment**: Docker, Docker Compose, Nginx

## Quick Start with Docker

### Prerequisites
- Docker
- Docker Compose

### Deployment Steps

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd college-management-system
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your production values
   ```

3. **Deploy**
   ```bash
   ./deploy.sh
   ```

4. **Access Application**
   - Open http://localhost:5000
   - Default admin login:
     - Email: admin@college.edu
     - Password: admin123

### Manual Docker Setup

1. **Build and Start**
   ```bash
   docker-compose up -d
   ```

2. **View Logs**
   ```bash
   docker-compose logs -f
   ```

3. **Stop Application**
   ```bash
   docker-compose down
   ```

## Production Deployment

For production deployment with Nginx and SSL:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

Key environment variables to configure:

```env
DATABASE_URL=postgresql://user:password@host:port/database
SESSION_SECRET=your-secure-secret-key
POSTGRES_PASSWORD=secure-database-password
```

## Database Schema

### Key Models
- **User**: Students, Faculty, Admins with role-based permissions
- **Department**: Department information with lecturer profiles
- **Attendance**: Classroom-based attendance records
- **Classroom**: Class organization by department/year/semester/section
- **Announcement**: System-wide communications

## API Endpoints

- `GET /api/departments` - List all departments
- `POST /api/enquiry` - Submit enquiry form

## File Structure

```
├── app.py              # Flask application factory
├── models.py           # Database models
├── routes.py           # Application routes
├── forms.py            # WTForms definitions
├── templates/          # Jinja2 templates
├── static/             # CSS, JS, images
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Development setup
├── nginx.conf          # Nginx configuration
└── deploy.sh           # Deployment script
```

## Attendance System

The system uses classroom-based attendance instead of course-based:

### Faculty Workflow
1. Access attendance page
2. Filter students by:
   - Department (CSE, ECE, EEE, etc.)
   - Year (1st, 2nd, 3rd, 4th)
   - Semester (1-8)
   - Section (A, B, C, etc.)
3. Select date
4. Mark attendance (Present/Absent/Late)

### Admin Analytics
- View attendance statistics by classroom
- Filter by date ranges
- Export attendance reports
- Monitor attendance trends

## Security Features

- Password hashing with Werkzeug
- Session management
- CSRF protection
- Input validation
- File upload restrictions
- SQL injection prevention

## Backup and Maintenance

### Database Backup
```bash
docker-compose exec db pg_dump -U college_user college_db > backup.sql
```

### Database Restore
```bash
docker-compose exec -T db psql -U college_user college_db < backup.sql
```

### Log Management
```bash
# View application logs
docker-compose logs web

# View database logs
docker-compose logs db
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check DATABASE_URL in .env
   - Ensure PostgreSQL container is running
   - Verify database credentials

2. **File Upload Issues**
   - Check upload directory permissions
   - Verify file size limits
   - Ensure supported file formats

3. **Performance Issues**
   - Monitor Docker resource usage
   - Check database query performance
   - Review application logs

### Support

For issues and support:
1. Check application logs
2. Review database connectivity
3. Verify environment configuration
4. Check Docker container status

## License

This project is licensed under the MIT License.