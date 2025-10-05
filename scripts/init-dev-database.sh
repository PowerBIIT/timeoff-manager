#!/bin/bash
# Inicjalizacja bazy danych DEV z testowymi danymi
# Użycie: ./init-dev-database.sh

set -e

echo "🗄️  Inicjalizacja bazy danych DEV..."
echo "===================================="
echo ""

# Zmienne
DB_HOST="timeoff-db-dev.postgres.database.azure.com"
DB_NAME="timeoffdb"
DB_USER="dbadmin"
DB_PASSWORD="Vcte9IKmHO+80QvRS3HFIg=="
SECRET_KEY="106e600452304fd169651b2451eca236f7e04ad728f419040738a57bc03b3d47"

# Connection string
DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}?sslmode=require"

echo "📋 Konfiguracja:"
echo "   Host: $DB_HOST"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo ""

# Export zmiennych środowiskowych
export DATABASE_URL="$DATABASE_URL"
export SECRET_KEY="$SECRET_KEY"
export FLASK_ENV="development"

echo "🔄 Uruchamianie init_db.py..."
echo ""

# Uruchom inicjalizację
cd /home/radek/timeoff-manager
python3 init_db.py

echo ""
echo "✅ Baza danych DEV zainicjalizowana!"
echo "===================================="
echo ""
echo "👥 Konta testowe:"
echo "   Admin: admin@firma.pl / admin123"
echo "   Manager: manager@firma.pl / manager123"
echo "   Employee: jan@firma.pl / jan123"
echo ""
echo "🔗 URL: https://timeoff-manager-dev.azurewebsites.net"
echo ""
