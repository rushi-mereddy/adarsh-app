#!/bin/bash

# Database initialization script for Docker container
echo "🚀 Starting College Management System..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    print('Database is ready!')
except:
    print('Database not ready yet...')
    exit(1)
"; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

# Initialize database schema
echo "🔧 Initializing database schema..."
python init_db.py

# Start the application
echo "🎉 Starting Flask application..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app
