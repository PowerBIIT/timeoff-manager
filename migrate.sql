-- Migration: Add supervisor_id column to users table

-- Check if column exists, if not add it
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='users' AND column_name='supervisor_id') THEN
        ALTER TABLE users ADD COLUMN supervisor_id INTEGER REFERENCES users(id);
        RAISE NOTICE 'Column supervisor_id added successfully';
    ELSE
        RAISE NOTICE 'Column supervisor_id already exists';
    END IF;
END $$;

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_users_supervisor_id ON users(supervisor_id);
