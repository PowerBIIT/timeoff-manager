"""
Production Database Cleanup Script
Usuwa wszystkie testowe dane i pozostawia pustą bazę gotową do produkcji

UWAGA: Ten skrypt usuwa WSZYSTKIE dane!
Użyj TYLKO podczas pierwszego wdrożenia produkcyjnego.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Request, SmtpConfig, AuditLog


def confirm_cleanup():
    """Confirm dangerous operation"""
    print("=" * 60)
    print("⚠️  OSTRZEŻENIE: USUNIĘCIE WSZYSTKICH DANYCH Z BAZY")
    print("=" * 60)
    print("\nTen skrypt usunie:")
    print("  - Wszystkich użytkowników")
    print("  - Wszystkie wnioski")
    print("  - Wszystkie logi audytowe")
    print("  - Konfigurację SMTP")
    print("\nBaza będzie PUSTA i gotowa do produkcji.\n")

    confirmation = input("Czy na pewno kontynuować? Wpisz 'TAK' aby potwierdzić: ")
    return confirmation == 'TAK'


def clear_production_data():
    """Clear all data from database"""
    app = create_app()

    with app.app_context():
        if not confirm_cleanup():
            print("\n❌ Operacja anulowana przez użytkownika")
            return False

        print("\n🗑️  Usuwanie danych z bazy...")

        try:
            # Delete all records
            deleted_requests = Request.query.delete()
            deleted_logs = AuditLog.query.delete()
            deleted_smtp = SmtpConfig.query.delete()
            deleted_users = User.query.delete()

            db.session.commit()

            print(f"\n✅ Usunięto dane:")
            print(f"   - {deleted_users} użytkowników")
            print(f"   - {deleted_requests} wniosków")
            print(f"   - {deleted_logs} logów audytowych")
            print(f"   - {deleted_smtp} konfiguracji SMTP")

            print("\n🎉 Baza danych wyczyszczona!")
            print("\n📋 Następne kroki:")
            print("   1. Utwórz pierwszego użytkownika admin przez API:")
            print("      POST /api/users")
            print('      {"email": "admin@twojafirma.pl", "password": "...", ')
            print('       "first_name": "Admin", "last_name": "System", ')
            print('       "role": "admin", "supervisor_id": null}')
            print("\n   2. Zaloguj się jako admin")
            print("   3. Skonfiguruj SMTP w Settings")
            print("   4. Dodaj użytkowników przez UI\n")

            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Błąd podczas czyszczenia: {str(e)}")
            return False


if __name__ == '__main__':
    # Check if running in production
    if os.getenv('FLASK_ENV') != 'production':
        print("\n⚠️  UWAGA: FLASK_ENV nie jest ustawione na 'production'")
        print(f"   Obecna wartość: {os.getenv('FLASK_ENV', 'brak')}")
        cont = input("\nCzy mimo to kontynuować? (tak/nie): ")
        if cont.lower() != 'tak':
            print("❌ Operacja anulowana")
            sys.exit(0)

    success = clear_production_data()
    sys.exit(0 if success else 1)
