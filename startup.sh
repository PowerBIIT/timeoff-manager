#!/bin/bash
# Azure App Service startup script

echo "🚀 Starting TimeOff Manager..."

# Run database migration first
echo "📦 Running database migrations..."
python run_migration.py || echo "⚠️  Migration script not available or failed"

# Initialize database if needed
echo "📦 Initializing database..."
python init_db.py

# Start Gunicorn
echo "🔧 Starting Gunicorn..."
gunicorn --bind=0.0.0.0:8000 \
         --workers=4 \
         --timeout=600 \
         --access-logfile '-' \
         --error-logfile '-' \
         'app:create_app()'
