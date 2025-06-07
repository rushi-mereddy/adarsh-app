#!/bin/bash

# College Management System Deployment Script

set -e

echo "🚀 Starting College Management System Deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your production values before continuing."
    echo "   Especially change SESSION_SECRET and POSTGRES_PASSWORD"
    read -p "Press Enter to continue after editing .env file..."
fi

# Create upload directories
echo "📁 Creating upload directories..."
mkdir -p static/uploads/{banners,profiles,lecturers,student_reviews}

# Build and start the application
echo "🐳 Building Docker images..."
docker-compose build

echo "🗄️  Starting database..."
docker-compose up -d db

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Check if database is responding
until docker-compose exec db pg_isready -U college_user -d college_db; do
    echo "⏳ Waiting for database..."
    sleep 2
done

echo "🌐 Starting web application..."
docker-compose up -d web

echo "✅ Deployment completed!"
echo ""
echo "🌍 Your application is now running at:"
echo "   http://localhost:5000"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop the application:"
echo "   docker-compose down"
echo ""
echo "🔧 To restart the application:"
echo "   docker-compose restart"
echo ""
echo "📖 Default admin credentials:"
echo "   Email: admin@college.edu"
echo "   Password: admin123"
echo "   (Change these after first login!)"