"""Manual database migration - add supervisor_id column"""
import os
from sqlalchemy import create_engine, text

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL not set!")
    print("Set it: export DATABASE_URL='postgresql://...'")
    exit(1)

print(f"🔧 Connecting to database...")
engine = create_engine(DATABASE_URL)

migration_sql = """
-- Add supervisor_id column if it doesn't exist
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

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_users_supervisor_id ON users(supervisor_id);
"""

try:
    with engine.connect() as conn:
        print("📝 Running migration...")
        conn.execute(text(migration_sql))
        conn.commit()
        print("✅ Migration completed successfully!")

        # Verify column exists
        result = conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'supervisor_id'
        """))
        row = result.fetchone()
        if row:
            print(f"✅ Verified: supervisor_id column exists ({row[1]})")
        else:
            print("⚠️  Warning: Could not verify column")

except Exception as e:
    print(f"❌ Migration failed: {e}")
    exit(1)
