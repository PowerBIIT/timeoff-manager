# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TimeOff Manager to system zarządzania wnioskami o wyjścia służbowe z pełnym systemem ról (Pracownik, Manager, Administrator). Aplikacja jest wdrożona w środowisku produkcyjnym Azure.

**Production URL:** https://timeoff-manager-20251004.azurewebsites.net

## Tech Stack

- **Backend:** Flask 3.0.0, SQLAlchemy, PostgreSQL, JWT auth, bcrypt
- **Frontend:** React 18 (via CDN + Babel), Tailwind CSS, Axios - wszystko w jednym pliku HTML
- **Deployment:** Azure App Service + Azure Database for PostgreSQL

## Development Commands

### Initial Setup
```bash
# Utworzenie wirtualnego środowiska
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalacja zależności
pip install -r requirements.txt

# Konfiguracja środowiska
cp .env.example .env
# Edytuj .env i ustaw DATABASE_URL oraz SECRET_KEY

# Inicjalizacja bazy danych
python init_db.py
```

### Running the Application
```bash
# Development mode (domyślnie port 5000)
python app.py

# Production mode
export FLASK_ENV=production
python app.py

# Uruchomienie z gunicorn (production)
gunicorn app:app
```

### Database Operations
```bash
# Inicjalizacja/reset bazy danych z seed data
python init_db.py

# Migracja do nowego modelu z supervisor_id
python migrate_to_supervisor.py

# Ręczne uruchomienie migracji SQL
python run_migration.py
```

### Azure Deployment
```bash
# Start Azure services (są domyślnie zatrzymane aby nie generować kosztów)
az webapp start --resource-group timeoff-rg-prod --name timeoff-manager-20251004
az postgres flexible-server start --resource-group timeoff-rg-prod --name timeoff-db-20251004

# Stop Azure services
az webapp stop --resource-group timeoff-rg-prod --name timeoff-manager-20251004
az postgres flexible-server stop --resource-group timeoff-rg-prod --name timeoff-db-20251004

# Wdrożenie aplikacji
./azure-deploy.sh

# Konfiguracja SMTP w Azure
./setup_smtp_azure.sh
```

### Testing
```bash
# Nie ma dedykowanych testów jednostkowych
# Test plan znajduje się w: TEST-PLAN-DETAILED.md
# Test execution report: TEST-EXECUTION-REPORT.md (100% PASS)
```

## Architecture & Code Structure

### Application Entry Point
- `app.py` - Flask application factory (`create_app()`)
  - Rejestruje blueprints: auth, request, user, config
  - Konfiguruje CORS (różnie dla dev/prod)
  - Global error handler
  - Health check endpoint: `/health`

### Database Models (`models.py`)
- **User** - użytkownicy z rolami: 'pracownik', 'manager', 'admin'
  - `supervisor_id` - self-referencing FK (hierarchia organizacyjna)
  - `is_active` - soft delete zamiast usuwania
- **Request** - wnioski o wyjście
  - `employee_id` - kto składa wniosek
  - `manager_id` - kto zatwierdza (przypisane automatycznie z supervisor_id pracownika)
  - `status` - 'oczekujący', 'zaakceptowany', 'odrzucony', 'anulowany'
- **SmtpConfig** - konfiguracja email (jedna instancja w bazie)
- **AuditLog** - audit trail wszystkich akcji

### Authentication & Authorization (`auth.py`)
- JWT token-based authentication
- `@token_required` - decorator dla chronionych endpoints
- `@require_role('admin', 'manager')` - role-based access control
- Funkcje: `generate_token()`, `hash_password()`, `verify_password()`

### API Routes (Blueprints w `routes/`)

**auth_routes.py:**
- `POST /api/login` - logowanie
- `POST /api/logout` - wylogowanie
- `GET /api/me` - dane zalogowanego użytkownika

**request_routes.py:**
- `GET /api/requests` - lista wniosków (filtrowana wg roli)
- `POST /api/requests` - nowy wniosek (manager_id auto z supervisor_id)
- `PUT /api/requests/:id/accept` - akceptacja (manager/admin)
- `PUT /api/requests/:id/reject` - odrzucenie (manager/admin)
- `DELETE /api/requests/:id` - anulowanie (pracownik, tylko pending)

**user_routes.py:**
- `GET /api/users` - lista użytkowników (admin/manager)
- `POST /api/users` - nowy użytkownik (admin only)
- `PUT /api/users/:id` - edycja użytkownika (admin only)
- `DELETE /api/users/:id` - usunięcie użytkownika (admin only)
- `GET /api/users/:id/subordinates` - lista podwładnych
- `POST /api/users/:id/reassign-subordinates` - przepisanie podwładnych

**config_routes.py:**
- `GET /api/smtp-config` - konfiguracja SMTP
- `POST /api/smtp-config` - zapis konfiguracji SMTP
- `POST /api/smtp-config/test` - test połączenia SMTP
- `GET /api/audit-logs` - logi audytowe

### Services (`services/`)
- **email_service.py** - wysyłka emaili przez SMTP
  - `send_new_request_email()` - powiadomienie managera o nowym wniosku
  - `send_decision_email()` - powiadomienie pracownika o decyzji
  - SMTP config pobierany z bazy (model SmtpConfig)
- **audit_service.py** - logowanie akcji użytkowników
  - `log_action(user_id, action, details)` - zapis do AuditLog

### Frontend (`static/index.html`)
- Single Page Application - cały frontend w jednym pliku HTML
- React 18 + Tailwind CSS (via CDN)
- Komponenty: Login, Dashboard, NewRequest, RequestList, UserManagement, Settings
- Premium duotone SVG icons (2025 design trends)
- Mobile-first responsive design
- Glassmorphism UI

## Important Implementation Notes

### Hierarchia Organizacyjna
- System używa `supervisor_id` do budowania hierarchii
- Pracownik składa wniosek → automatycznie przypisywany do jego supervisora jako managera
- Admin może być supervisorem managerów
- Przy tworzeniu wniosku sprawdzane jest `current_user.supervisor_id`

### Role-Based Access Control
- **Pracownik**: widzi tylko swoje wnioski, może anulować pending
- **Manager**: widzi swoje wnioski + wnioski zespołu (gdzie jest manager_id), akceptuje/odrzuca
- **Admin**: widzi wszystko, zarządza użytkownikami, konfiguruje SMTP

### Soft Delete Pattern
- Użytkownicy mają flagę `is_active` zamiast usuwania
- Wnioski mają status 'anulowany' zamiast DELETE
- Chroni relacyjną integralność danych

### Email Notifications
- SMTP config przechowywany w bazie (nie w .env)
- Admin konfiguruje przez UI (Settings)
- Graceful degradation - jeśli SMTP nie skonfigurowane, app działa bez emaili
- HTML templates z branded design

### Environment Configuration
- `.env` dla local development
- `production.env.example` dla Azure deployment
- Wymagane zmienne: `DATABASE_URL`, `SECRET_KEY`
- Opcjonalne: `SMTP_*` (można skonfigurować przez UI)

### Azure Specific
- App Service: timeoff-manager-20251004
- PostgreSQL: timeoff-db-20251004
- Resource Group: timeoff-rg-prod
- Serwisy są ZATRZYMANE domyślnie (oszczędność kosztów)

### After Backend Changes
**WAŻNE:** Po zmianach w backendzie zawsze:
1. Testuj lokalnie: `python app.py`
2. Sprawdź endpointy przez `/health`
3. Jeśli zmiany w models.py: rozważ migrację
4. Deploy do Azure: `./azure-deploy.sh`

### Default Test Accounts (po init_db.py)
- Admin: admin@firma.pl / admin123 (no supervisor)
- Manager: manager@firma.pl / manager123 (supervisor: Admin)
- Employee: jan@firma.pl / jan123 (supervisor: Manager)

## Documentation Files
- `README.md` - główna dokumentacja z instrukcjami
- `INDEX.md` - pełna nawigacja po dokumentacji
- `PRODUCTION-READY.md` - przewodnik produkcyjny
- `DEPLOYMENT.md` - instrukcje wdrożenia Azure
- `USER-GUIDE.md` - instrukcja dla użytkowników końcowych
- `TECHNICAL-DOCS.md` - szczegółowa dokumentacja techniczna
- `TEST-PLAN-DETAILED.md` - szczegółowy plan testów
- `TEST-EXECUTION-REPORT.md` - raport wykonania testów (100% PASS)
