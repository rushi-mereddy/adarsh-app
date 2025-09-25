#!/bin/bash

# College Application Manager - Deployment Script
# This script handles the deployment process on EC2

set -e  # Exit on any error

echo "🚀 Starting College Application Manager Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating default one..."
    cat > .env << 'EOF'
POSTGRES_PASSWORD=College2024!SecureDBPass
SESSION_SECRET=super-secret-random-key-change-this-in-production-2024
FLASK_ENV=production
DOMAIN=localhost
EOF
    print_status ".env file created with default values"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p static/uploads ssl logs
chmod 755 static/uploads

# Stop existing services
print_status "Stopping existing services..."
docker-compose -f docker-compose.prod.yml down || true

# Clean up old images
print_status "Cleaning up Docker system..."
docker system prune -f || true

# Build and start services
print_status "Building and starting services..."
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check if services are running
print_status "Checking service status..."
if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    print_error "Some services failed to start!"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi

# Initialize database
print_status "Initializing database..."
docker-compose -f docker-compose.prod.yml exec -T web python -c "
import sys
sys.path.append('/app')

try:
    from app import app, db
    from models import User
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        print('🔄 Creating database tables...')
        db.create_all()
        print('✅ Database tables created successfully!')
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@college.edu').first()
        if not admin:
            admin_user = User(
                first_name='System',
                last_name='Administrator', 
                email='admin@college.edu',
                password=generate_password_hash('admin123'),
                role='admin',
                is_active=True,
                phone='1234567890',
                department='Administration'
            )
            db.session.add(admin_user)
            db.session.commit()
            print('✅ Admin user created: admin@college.edu / admin123')
        else:
            print('ℹ️ Admin user already exists')
            
        # Verify database connection
        user_count = User.query.count()
        print(f'📊 Total users in database: {user_count}')
        
except Exception as e:
    print(f'❌ Database initialization error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" || {
    print_error "Database initialization failed!"
    docker-compose -f docker-compose.prod.yml logs web
    exit 1
}

# Health check
print_status "Performing health check..."
sleep 10

# Check if application is responding
if curl -f -s http://localhost/health > /dev/null 2>&1; then
    print_status "✅ Health check passed!"
elif curl -f -s http://localhost > /dev/null 2>&1; then
    print_status "✅ Application is responding!"
else
    print_warning "Health check endpoint not responding, but continuing..."
fi

# Show final status
print_status "📊 Final Service Status:"
docker-compose -f docker-compose.prod.yml ps

print_status "📋 Recent Application Logs:"
docker-compose -f docker-compose.prod.yml logs web --tail=10

echo ""
echo -e "${GREEN}🎉 Deployment Completed Successfully!${NC}"
echo -e "${BLUE}🌐 Application URL: http://$(curl -s http://checkip.amazonaws.com || echo 'localhost')${NC}"
echo -e "${BLUE}👤 Admin Login: admin@college.edu / admin123${NC}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Update your security group to allow HTTP (port 80) traffic"
echo "2. Configure your domain name (if you have one)"
echo "3. Set up SSL certificate for HTTPS"
echo "4. Change default admin password after first login"
echo ""

print_status "Deployment script completed!"