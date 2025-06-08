-- WorkoutBuddy Database Setup Script
-- This script sets up proper permissions for the admin user

-- Connect to the workoutbuddy database as a superuser and run this script

-- Grant all privileges on database to admin user
GRANT ALL PRIVILEGES ON DATABASE workoutbuddy TO admin;

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO admin;

-- Grant all privileges on all tables in public schema
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;

-- Grant all privileges on all sequences in public schema
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;

-- Grant privileges on future tables (for new tables created later)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO admin;

-- If the exercises table already exists, grant specific permissions
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'exercises') THEN
        GRANT ALL PRIVILEGES ON TABLE exercises TO admin;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;
    END IF;
END $$;

-- Display current permissions for verification
\l workoutbuddy
\dp exercises 