#!/bin/bash
# Inicjalizacja bazy produkcyjnej
# Czyści testowe dane i tworzy pierwszego admina
#
# Użycie: ./scripts/init-prod-database.sh

set -e

echo "🚀 INICJALIZACJA BAZY PRODUKCYJNEJ"
echo "===================================="
echo ""

PROD_APP="timeoff-manager-20251004"
PROD_RG="timeoff-rg-prod"

# Dane pierwszego admina (domyślne)
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@powerbiit.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-PowerBI2025!}"
ADMIN_FIRST_NAME="${ADMIN_FIRST_NAME:-Admin}"
ADMIN_LAST_NAME="${ADMIN_LAST_NAME:-PowerBIIT}"

echo "📋 Skrypt wykona:"
echo "   1. Wyczyści wszystkie testowe dane z bazy PROD"
echo "   2. Utworzy pierwszego administratora:"
echo "      - Email: $ADMIN_EMAIL"
echo "      - Imię: $ADMIN_FIRST_NAME $ADMIN_LAST_NAME"
echo ""
echo "⚠️  UWAGA: To usunie WSZYSTKIE dane z bazy produkcyjnej!"
echo ""

read -p "Czy kontynuować? (tak/nie): " confirm
if [ "$confirm" != "tak" ]; then
    echo "❌ Operacja anulowana"
    exit 0
fi

echo ""
echo "📤 Przesyłanie skryptu init do PROD..."

# Create init script
cat > /tmp/init_prod_remote.py << 'EOFSCRIPT'
import sys
import os
sys.path.insert(0, '/home/site/wwwroot')

from app import create_app
from models import db, User, Request, SmtpConfig, AuditLog
from auth import hash_password

def init_production():
    app = create_app()
    with app.app_context():
        print("🗑️  Czyszczenie bazy...")
        try:
            deleted_requests = Request.query.delete()
            deleted_logs = AuditLog.query.delete()
            deleted_smtp = SmtpConfig.query.delete()
            deleted_users = User.query.delete()
            print(f"✅ Usunięto: {deleted_users} użytkowników, {deleted_requests} wniosków")

            admin_email = os.getenv('ADMIN_EMAIL', 'admin@powerbiit.com')
            admin_password = os.getenv('ADMIN_PASSWORD', 'PowerBI2025!')
            admin_first_name = os.getenv('ADMIN_FIRST_NAME', 'Admin')
            admin_last_name = os.getenv('ADMIN_LAST_NAME', 'PowerBIIT')

            print(f"👤 Tworzenie admina: {admin_email}")
            admin = User(
                email=admin_email,
                first_name=admin_first_name,
                last_name=admin_last_name,
                password_hash=hash_password(admin_password),
                role='admin',
                supervisor_id=None,
                is_active=True
            )

            db.session.add(admin)
            db.session.commit()

            print(f"✅ Admin utworzony!")
            print(f"   Email: {admin_email}")
            print(f"   Hasło: {admin_password}")
            print("⚠️  Zmień hasło po pierwszym logowaniu!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Błąd: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = init_production()
    sys.exit(0 if success else 1)
EOFSCRIPT

# Upload and run script via Azure
echo "🔄 Wykonywanie skryptu na PROD..."
echo ""

az webapp ssh --name $PROD_APP --resource-group $PROD_RG << 'EOFSSH'
cd /home/site/wwwroot

# Create init script
cat > init_prod.py << 'EOFPY'
import sys
import os
sys.path.insert(0, '/home/site/wwwroot')

from app import create_app
from models import db, User, Request, SmtpConfig, AuditLog
from auth import hash_password

def init_production():
    app = create_app()
    with app.app_context():
        print("🗑️  Czyszczenie bazy...")
        try:
            deleted_requests = Request.query.delete()
            deleted_logs = AuditLog.query.delete()
            deleted_smtp = SmtpConfig.query.delete()
            deleted_users = User.query.delete()
            print(f"✅ Usunięto: {deleted_users} użytkowników, {deleted_requests} wniosków, {deleted_logs} logów")

            admin_email = os.getenv('ADMIN_EMAIL', 'admin@powerbiit.com')
            admin_password = os.getenv('ADMIN_PASSWORD', 'PowerBI2025!')
            admin_first_name = os.getenv('ADMIN_FIRST_NAME', 'Admin')
            admin_last_name = os.getenv('ADMIN_LAST_NAME', 'PowerBIIT')

            print(f"👤 Tworzenie admina: {admin_email}")
            admin = User(
                email=admin_email,
                first_name=admin_first_name,
                last_name=admin_last_name,
                password_hash=hash_password(admin_password),
                role='admin',
                supervisor_id=None,
                is_active=True
            )

            db.session.add(admin)
            db.session.commit()

            print("")
            print("=" * 60)
            print("🎉 BAZA PRODUKCYJNA GOTOWA!")
            print("=" * 60)
            print(f"✅ Dane logowania admina:")
            print(f"   Email: {admin_email}")
            print(f"   Hasło: {admin_password}")
            print("")
            print("⚠️  WAŻNE: Zmień hasło po pierwszym logowaniu!")
            print("")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Błąd: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = init_production()
    sys.exit(0 if success else 1)
EOFPY

# Run the script
python3 init_prod.py

# Cleanup
rm init_prod.py

exit
EOFSSH

echo ""
echo "✅ Gotowe!"
echo ""
echo "🌐 URL PROD: https://$PROD_APP.azurewebsites.net"
echo ""
echo "📝 Dane logowania:"
echo "   Email: $ADMIN_EMAIL"
echo "   Hasło: $ADMIN_PASSWORD"
echo ""
echo "⚠️  Zmień hasło po pierwszym logowaniu!"
echo ""
