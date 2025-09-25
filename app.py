import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf.csrf import CSRFProtect
from extensions import db, login_manager, cache
from werkzeug.security import generate_password_hash

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
database_url = os.environ.get("DATABASE_URL", "sqlite:///college_management.db")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url

# Only set PostgreSQL-specific options if using PostgreSQL
if database_url.startswith("postgresql"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "connect_args": {
            "sslmode": "disable",  # Disable SSL for local development
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000"
        }
    }
else:
    # SQLite configuration
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True
    }
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Initialize caching
cache.init_app(app)

# Initialize CSRF protection
csrf = CSRFProtect(app)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

def init_db():
    with app.app_context():
        # Import models to ensure they are registered with SQLAlchemy
        from models import User
        
        # Create tables if they don't exist
        try:
            db.create_all()
            logging.info("Database tables created successfully")
        except Exception as e:
            logging.warning(f"Error creating tables: {str(e)}")
            # If tables already exist, that's fine
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(email='admin@college.edu').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@college.edu',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                first_name='System',
                last_name='Administrator'
            )
            db.session.add(admin_user)
            try:
                db.session.commit()
                logging.info("Default admin user created: admin@college.edu / admin123")
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error creating admin user: {str(e)}")

# Initialize database
init_db()

# Import routes after app initialization
from routes import *
