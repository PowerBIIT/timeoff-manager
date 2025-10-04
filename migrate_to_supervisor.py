"""
Migration script: Rename manager_id to supervisor_id in users table
This allows hierarchical structure where managers can also have supervisors
"""
from app import create_app
from models import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        try:
            # Check if supervisor_id column already exists (SQLite)
            result = db.session.execute(text("""
                PRAGMA table_info(users)
            """))

            columns = [row[1] for row in result.fetchall()]
            if 'supervisor_id' in columns:
                print("✅ Column 'supervisor_id' already exists. Migration not needed.")
                return

            print("🔄 Starting migration: manager_id → supervisor_id")

            # Step 1: Add new supervisor_id column
            print("  Adding supervisor_id column...")
            db.session.execute(text("""
                ALTER TABLE users
                ADD COLUMN supervisor_id INTEGER REFERENCES users(id)
            """))
            db.session.commit()
            print("  ✅ supervisor_id column added")

            # Step 2: Copy data from manager_id to supervisor_id
            print("  Copying data from manager_id to supervisor_id...")
            db.session.execute(text("""
                UPDATE users
                SET supervisor_id = manager_id
            """))
            db.session.commit()
            print("  ✅ Data copied")

            # Step 3: Note about manager_id column
            # SQLite doesn't support DROP COLUMN easily, so we keep both columns
            # The application will use supervisor_id going forward
            print("  ℹ️  Note: manager_id column kept for compatibility (SQLite limitation)")
            print("  ℹ️  Application will use supervisor_id from now on")

            print("\n✅ Migration completed successfully!")
            print("\nHierarchy structure:")
            print("  - All users (pracownik, manager, admin) can now have a supervisor")
            print("  - Top-level users have supervisor_id = NULL")
            print("  - supervisor_id contains same data as manager_id")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    migrate()
