"""Database initialization script with seed data"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User
import bcrypt


def init_database():
    """Initialize database with tables and seed data"""
    app = create_app()

    with app.app_context():
        print("🔧 Creating database tables...")
        db.create_all()
        print("✅ Database tables created!")

        # Check if admin exists
        admin = User.query.filter_by(email='admin@firma.pl').first()

        if admin:
            print("⚠️  Database already contains seed data. Skipping...")
            return

        print("🌱 Creating seed data...")

        # Create admin user (top of hierarchy - no supervisor)
        admin = User(
            email='admin@firma.pl',
            password_hash=bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode(),
            first_name='Admin',
            last_name='System',
            role='admin',
            supervisor_id=None  # Top-level user
        )
        db.session.add(admin)

        # Commit to get admin ID
        db.session.commit()

        # Create test manager (supervisor is admin)
        manager = User(
            email='manager@firma.pl',
            password_hash=bcrypt.hashpw('manager123'.encode(), bcrypt.gensalt()).decode(),
            first_name='Anna',
            last_name='Kowalska',
            role='manager',
            supervisor_id=admin.id  # Manager reports to Admin
        )
        db.session.add(manager)

        # Commit to get manager ID
        db.session.commit()

        # Create test employee (supervisor is manager)
        employee = User(
            email='jan@firma.pl',
            password_hash=bcrypt.hashpw('jan123'.encode(), bcrypt.gensalt()).decode(),
            first_name='Jan',
            last_name='Nowak',
            role='pracownik',
            supervisor_id=manager.id  # Employee reports to Manager
        )
        db.session.add(employee)

        db.session.commit()

        print("✅ Seed data created successfully!")
        print("\n📋 Test accounts:")
        print("   Admin:     admin@firma.pl    / admin123  (no supervisor)")
        print("   Manager:   manager@firma.pl  / manager123  (supervisor: Admin)")
        print("   Employee:  jan@firma.pl      / jan123      (supervisor: Manager)")
        print("\n🔗 Hierarchy:")
        print("   Admin (CEO)")
        print("   └─ Manager Anna")
        print("      └─ Employee Jan")
        print("\n🚀 Database ready!")


if __name__ == '__main__':
    init_database()
