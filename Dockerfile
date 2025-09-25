# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create directories for uploads
RUN mkdir -p static/uploads/banners static/uploads/profiles static/uploads/lecturers static/uploads/student_reviews

# Copy database initialization script and startup script
COPY init_db.py /app/
COPY start.sh /app/

# Make startup script executable
RUN chmod +x /app/start.sh

# Install psycopg2 for database connectivity
RUN pip install psycopg2-binary

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run the startup script
CMD ["/app/start.sh"]