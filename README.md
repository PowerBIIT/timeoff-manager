# TimeOff Manager

System zarządzania wnioskami o wyjścia służbowe z pełnym systemem ról (Pracownik, Manager, Administrator).

**🚀 PRODUCTION URL:** https://timeoff-manager-20251004.azurewebsites.net

⚠️ **UWAGA:** Serwisy Azure są ZATRZYMANE (aby nie generować kosztów na prywatnej subskrypcji).

**Aby uruchomić aplikację:**
```bash
# 1. Uruchom App Service
az webapp start --resource-group timeoff-rg-prod --name timeoff-manager-20251004

# 2. Uruchom PostgreSQL Database
az postgres flexible-server start --resource-group timeoff-rg-prod --name timeoff-db-20251004

# 3. Poczekaj ~2 minuty na pełne uruchomienie
# 4. Aplikacja dostępna pod: https://timeoff-manager-20251004.azurewebsites.net
```

**Aby ZATRZYMAĆ serwisy (oszczędzanie kosztów):**
```bash
# 1. Zatrzymaj App Service
az webapp stop --resource-group timeoff-rg-prod --name timeoff-manager-20251004

# 2. Zatrzymaj PostgreSQL Database
az postgres flexible-server stop --resource-group timeoff-rg-prod --name timeoff-db-20251004
```

> 📚 **Szukasz czegoś konkretnego?** → [INDEX.md](INDEX.md) - Pełna dokumentacja i nawigacja

## 🎯 Funkcje

### Role użytkowników
- **Pracownik**: składa wnioski, widzi swoje wnioski, może anulować przed akceptacją
- **Manager**: akceptuje/odrzuca wnioski swojego zespołu, widzi historię zespołu
- **Administrator**: zarządza użytkownikami, konfiguruje system, widzi wszystko

### Funkcjonalności
- ✅ Składanie wniosków o wyjście (data, godziny, powód)
- ✅ Akceptacja/odrzucenie wniosków przez managera
- ✅ Powiadomienia email (manager przy nowym wniosku, pracownik po decyzji)
- ✅ Zarządzanie użytkownikami (admin)
- ✅ Deaktywacja użytkowników (zamiast usuwania)
- ✅ Konfiguracja SMTP (admin)
- ✅ Audit log wszystkich akcji
- ✅ Walidacja dat i godzin
- ✅ **Interaktywny dashboard z KPI**
- ✅ **Premium duotone icons (2025 design)**
- ✅ **Responsive design (desktop + mobile)** - mobile-first UI

## 🏗️ Tech Stack

**Backend:**
- Python 3.11
- Flask 3.0.0
- PostgreSQL (SQLAlchemy)
- JWT Authentication
- bcrypt (haszowanie haseł)

**Frontend:**
- React 18 (via CDN + Babel)
- Tailwind CSS 3.4
- Custom duotone SVG icons (2025 design trends)
- Glassmorphism UI
- Mobile-first responsive design
- Axios

**Deployment:**
- Azure App Service
- Azure Database for PostgreSQL

## 📦 Instalacja

### 1. Klonowanie repozytorium
```bash
git clone <repository-url>
cd timeoff-manager
```

### 2. Instalacja zależności
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Konfiguracja
```bash
cp .env.example .env
# Edytuj .env i ustaw DATABASE_URL oraz inne zmienne
```

### 4. Inicjalizacja bazy danych
```bash
python init_db.py
```

### 5. Uruchomienie aplikacji
```bash
python app.py
```

Aplikacja dostępna pod: http://localhost:5000

## 👥 Domyślne konta testowe

Po inicjalizacji bazy danych dostępne są następujące konta:

| Rola | Email | Hasło |
|------|-------|-------|
| Admin | admin@firma.pl | admin123 |
| Manager | manager@firma.pl | manager123 |
| Pracownik | jan@firma.pl | jan123 |

⚠️ **WAŻNE:** Zmień hasła po pierwszym logowaniu!

## 🚀 Production Deployment

**✅ APLIKACJA WDROŻONA:** https://timeoff-manager-20251004.azurewebsites.net

### 📋 Po wdrożeniu (KRYTYCZNE):
1. **Zmień hasła domyślnych kont** ⚠️
   - admin@firma.pl → użyj silnego hasła
   - manager@firma.pl → użyj silnego hasła
   - jan@firma.pl → użyj silnego hasła

2. **Skonfiguruj SMTP dla powiadomień email** ⚠️
   - Gmail: smtp.gmail.com:587 (użyj App Password)
   - Office365: smtp.office365.com:587
   - SendGrid: smtp.sendgrid.net:587

3. **Dodaj prawdziwych użytkowników**
   - Usuń konta testowe (opcjonalnie)
   - Przypisz managerów

### 📚 Szczegółowa dokumentacja:
- 📘 [PRODUCTION-READY.md](PRODUCTION-READY.md) - Kompletny przewodnik produkcyjny
- 📘 [DEPLOYMENT.md](DEPLOYMENT.md) - Instrukcje wdrożenia Azure
- 📘 [USER-GUIDE.md](USER-GUIDE.md) - Instrukcja dla użytkowników

## 📡 API Endpoints

### Authentication
- `POST /api/login` - Logowanie
- `POST /api/logout` - Wylogowanie
- `GET /api/me` - Informacje o zalogowanym użytkowniku

### Requests (Wnioski)
- `GET /api/requests` - Lista wniosków (filtrowana wg roli)
- `POST /api/requests` - Nowy wniosek
- `PUT /api/requests/:id/accept` - Akceptacja (manager/admin)
- `PUT /api/requests/:id/reject` - Odrzucenie (manager/admin)
- `DELETE /api/requests/:id` - Anulowanie (pracownik)

### Users (Admin only)
- `GET /api/users` - Lista użytkowników
- `POST /api/users` - Dodaj użytkownika
- `PUT /api/users/:id` - Edytuj użytkownika
- `DELETE /api/users/:id` - Usuń użytkownika
- `GET /api/users/:id` - Szczegóły użytkownika

### Configuration (Admin only)
- `GET /api/smtp-config` - Pobierz konfigurację SMTP
- `POST /api/smtp-config` - Zapisz konfigurację SMTP
- `POST /api/smtp-config/test` - Test połączenia SMTP
- `GET /api/audit-logs` - Logi audytowe

## 🔐 Bezpieczeństwo

- JWT token-based authentication
- Hasła haszowane bcrypt
- Role-based access control (middleware)
- SQL injection protection (SQLAlchemy parametryzowane zapytania)
- CORS skonfigurowany dla środowisk dev/prod

## 📧 Konfiguracja Email

Aby włączyć powiadomienia email:

1. Zaloguj się jako **admin** (admin@firma.pl / admin123)
2. Przejdź do **Ustawienia**
3. Skonfiguruj SMTP:
   - Server: smtp.gmail.com (dla Gmail)
   - Port: 587
   - Login: twój email
   - Password: hasło aplikacji (nie hasło do konta!)
   - Email From: adres nadawcy

**Gmail:** Użyj [App Passwords](https://myaccount.google.com/apppasswords)

## 🛠️ Development

### Uruchomienie w trybie development
```bash
export FLASK_ENV=development
python app.py
```

### Struktura projektu
```
timeoff-manager/
├── app.py              # Flask entry point
├── config.py           # Configuration
├── models.py           # Database models
├── auth.py             # Authentication
├── init_db.py          # Database initialization
├── routes/             # API routes
│   ├── auth_routes.py
│   ├── request_routes.py
│   ├── user_routes.py
│   └── config_routes.py
├── services/           # Business logic
│   ├── email_service.py
│   └── audit_service.py
└── static/
    └── index.html      # Frontend React SPA
```

## 📝 License

MIT

## 🤝 Contributing

Pull requests are welcome!

## 📞 Support

W razie problemów otwórz issue w repozytorium.
