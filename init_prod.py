"""
Production Database Initialization Script
Czyści bazę z testowych danych i tworzy pierwszego admina

UWAGA: Użyj TYLKO podczas pierwszego wdrożenia produkcyjnego.
"""
import sys
import os
import getpass

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Request, SmtpConfig, AuditLog
from auth import hash_password


def get_admin_credentials():
    """Get admin credentials from user input"""
    print("\n" + "=" * 60)
    print("📝 DANE PIERWSZEGO ADMINISTRATORA")
    print("=" * 60)

    email = input("\nEmail admina: ").strip()
    while not email or '@' not in email:
        print("❌ Podaj poprawny email")
        email = input("Email admina: ").strip()

    first_name = input("Imię: ").strip()
    while not first_name:
        print("❌ Imię nie może być puste")
        first_name = input("Imię: ").strip()

    last_name = input("Nazwisko: ").strip()
    while not last_name:
        print("❌ Nazwisko nie może być puste")
        last_name = input("Nazwisko: ").strip()

    password = getpass.getpass("Hasło (min 6 znaków): ")
    while len(password) < 6:
        print("❌ Hasło musi mieć min 6 znaków")
        password = getpass.getpass("Hasło (min 6 znaków): ")

    password_confirm = getpass.getpass("Powtórz hasło: ")
    while password != password_confirm:
        print("❌ Hasła się nie zgadzają")
        password = getpass.getpass("Hasło (min 6 znaków): ")
        password_confirm = getpass.getpass("Powtórz hasło: ")

    return {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'password': password
    }


def confirm_cleanup():
    """Confirm dangerous operation"""
    print("\n" + "=" * 60)
    print("⚠️  OSTRZEŻENIE: USUNIĘCIE WSZYSTKICH DANYCH Z BAZY")
    print("=" * 60)
    print("\nTen skrypt:")
    print("  1. Usunie wszystkie testowe dane")
    print("  2. Utworzy pierwszego administratora")
    print("  3. Pozostawi pustą bazę gotową do produkcji\n")

    confirmation = input("Czy na pewno kontynuować? Wpisz 'TAK' aby potwierdzić: ")
    return confirmation == 'TAK'


def init_production():
    """Initialize production database"""
    app = create_app()

    with app.app_context():
        if not confirm_cleanup():
            print("\n❌ Operacja anulowana przez użytkownika")
            return False

        # Get admin credentials
        admin_data = get_admin_credentials()

        print("\n🗑️  Czyszczenie bazy danych...")

        try:
            # Delete all records
            deleted_requests = Request.query.delete()
            deleted_logs = AuditLog.query.delete()
            deleted_smtp = SmtpConfig.query.delete()
            deleted_users = User.query.delete()

            print(f"   ✅ Usunięto: {deleted_users} użytkowników, {deleted_requests} wniosków, {deleted_logs} logów")

            # Create first admin
            print("\n👤 Tworzenie pierwszego administratora...")
            admin = User(
                email=admin_data['email'],
                first_name=admin_data['first_name'],
                last_name=admin_data['last_name'],
                password_hash=hash_password(admin_data['password']),
                role='admin',
                supervisor_id=None,
                is_active=True
            )

            db.session.add(admin)
            db.session.commit()

            print(f"   ✅ Admin utworzony: {admin_data['first_name']} {admin_data['last_name']} ({admin_data['email']})")

            print("\n" + "=" * 60)
            print("🎉 BAZA PRODUKCYJNA GOTOWA!")
            print("=" * 60)
            print(f"\n✅ Dane logowania admina:")
            print(f"   Email: {admin_data['email']}")
            print(f"   Hasło: [podane przez Ciebie]")
            print("\n📋 Następne kroki:")
            print("   1. Zaloguj się jako admin")
            print("   2. Skonfiguruj SMTP w Settings")
            print("   3. Dodaj użytkowników (managery, pracowników)")
            print("   4. System gotowy do użycia!\n")

            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Błąd: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    # Check DATABASE_URL
    if not os.getenv('DATABASE_URL'):
        print("\n❌ Brak DATABASE_URL w zmiennych środowiskowych")
        print("   Ustaw DATABASE_URL przed uruchomieniem tego skryptu")
        sys.exit(1)

    # Show database info
    db_url = os.getenv('DATABASE_URL', '')
    if 'postgres' in db_url:
        # Extract host from connection string (hide password)
        if '@' in db_url:
            host_part = db_url.split('@')[1].split('/')[0]
            print(f"\n🔌 Połączenie z bazą: {host_part}")

    success = init_production()
    sys.exit(0 if success else 1)
