#!/usr/bin/env python3
"""Setup SMTP configuration in database"""
import os
import sys
from app import create_app
from models import db, SmtpConfig

def setup_smtp():
    """Configure SMTP settings in database"""
    app = create_app()

    with app.app_context():
        try:
            # Check if SMTP config exists
            config = SmtpConfig.query.first()

            if not config:
                config = SmtpConfig()
                db.session.add(config)
                print("✨ Creating new SMTP configuration...")
            else:
                print("🔄 Updating existing SMTP configuration...")

            # Set SMTP configuration
            config.server = 'smtp.gmail.com'
            config.port = 587
            config.use_ssl = True
            config.login = 'radekbroniszewski@gmail.com'
            config.password = 'grukmitfngygmhvn'  # App Password
            config.email_from = 'system@firma.pl'

            db.session.commit()

            print("✅ SMTP configuration saved successfully!")
            print(f"   Server: {config.server}:{config.port}")
            print(f"   Login: {config.login}")
            print(f"   From: {config.email_from}")
            print(f"   SSL: {config.use_ssl}")

            return 0

        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return 1

if __name__ == '__main__':
    sys.exit(setup_smtp())
