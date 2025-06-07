-- Initialize database with sample data for college management system

-- Create extension for UUID generation (if needed)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Sample data will be inserted after tables are created by SQLAlchemy
-- This file ensures the database is properly initialized

-- You can add any initial SQL commands here that need to run once
-- For example, creating indexes, setting up permissions, etc.

-- Create indexes for better performance
-- These will be created after the tables exist

DO $$
BEGIN
    -- Check if tables exist before creating indexes
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user') THEN
        -- Create indexes on commonly queried columns
        CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);
        CREATE INDEX IF NOT EXISTS idx_user_role ON "user"(role);
        CREATE INDEX IF NOT EXISTS idx_user_department ON "user"(department);
        CREATE INDEX IF NOT EXISTS idx_user_is_active ON "user"(is_active);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'attendance') THEN
        CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);
        CREATE INDEX IF NOT EXISTS idx_attendance_student_id ON attendance(student_id);
        CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance(status);
        CREATE INDEX IF NOT EXISTS idx_attendance_marked_by ON attendance(marked_by);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'department') THEN
        CREATE INDEX IF NOT EXISTS idx_department_code ON department(code);
        CREATE INDEX IF NOT EXISTS idx_department_is_active ON department(is_active);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'announcement') THEN
        CREATE INDEX IF NOT EXISTS idx_announcement_created_at ON announcement(created_at);
        CREATE INDEX IF NOT EXISTS idx_announcement_is_active ON announcement(is_active);
    END IF;
END $$;