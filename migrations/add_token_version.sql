-- Migration: Add token_version column to users table
-- Date: 2025-10-05
-- Purpose: Enable JWT token invalidation on password change

-- Add token_version column (default 0)
ALTER TABLE users ADD COLUMN IF NOT EXISTS token_version INTEGER DEFAULT 0;

-- Update existing users to have token_version = 0
UPDATE users SET token_version = 0 WHERE token_version IS NULL;

-- Verification query
SELECT COUNT(*) as total_users,
       COUNT(token_version) as users_with_token_version
FROM users;
