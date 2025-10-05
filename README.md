# TimeOff Manager

**System zarządzania wnioskami o wyjścia służbowe** z pełnym systemem ról, automatycznym workflow i powiadomieniami email.

## 🌐 Środowiska

| Środowisko | URL | Przeznaczenie |
|------------|-----|---------------|
| **DEV** | https://timeoff-manager-dev.azurewebsites.net | Development i testy |
| **PROD** | https://timeoff-manager-20251004.azurewebsites.net | Produkcja (klienci) |

## ⚡ Quick Start

### Nowy użytkownik? Zacznij tutaj:

**👉 [START.md](START.md) ← Wszystko czego potrzebujesz w jednym miejscu!**

### Najczęstsze komendy

```bash
# Podczas developmentu (zatrzymaj PROD, oszczędź ~$565/m)
./scripts/dev-only-mode.sh

# Przed wdrożeniem (uruchom PROD)
./scripts/production-mode.sh

# Sprawdź co działa
az webapp show -n timeoff-manager-dev -g timeoff-manager-rg-dev --query state
az webapp show -n timeoff-manager-20251004 -g timeoff-rg-prod --query state
```

## 🎯 Główne funkcje

✅ **System ról:** Pracownik, Manager, Administrator
✅ **Wnioski:** Składanie, akceptacja, odrzucanie, anulowanie
✅ **Powiadomienia:** Email do managera i pracownika
✅ **Dashboard:** Interaktywne KPI z wykresami
✅ **Hierarchia:** Supervisor-based (pracownik → manager → admin)
✅ **Audit log:** Pełna historia wszystkich akcji
✅ **Mobile-first:** Responsive design (desktop + mobile)
✅ **Premium UI:** Duotone icons, glassmorphism, nowoczesny design
✅ **Bezpieczeństwo:** CSP, password requirements, timing attack prevention

## 🧪 Testowanie

**Automatyczne testy E2E:** `python3 run_tests.py`

**Ostatni wynik: 100% (11/11 testów) ✅**
- ✅ Logowanie (Pracownik, Manager, Admin)
- ✅ Dashboard i statystyki
- ✅ Tworzenie i walidacja wniosków
- ✅ Lista wniosków z decision_date
- ✅ Zarządzanie użytkownikami
- ✅ CSP headers (bez unsafe-eval)

**Szczegóły testów:** [START.md](START.md#-testowanie-aplikacji)

## 💰 Oszczędzanie kosztów

**Automatyczne oszczędzanie skonfigurowane!**

✅ **Idle Monitoring** - zatrzymanie po 30 min bezczynności
✅ **DEV-ONLY mode** - wyłącz PROD podczas developmentu

**Potencjalne oszczędności:**
- Bez auto-stop: **~$605/miesiąc**
- Z idle monitoring: **~$50-200/m** (67-92% taniej!)
- DEV-ONLY mode: **~$40/m** (93% taniej!)

Więcej: [IDLE-MONITORING.md](IDLE-MONITORING.md)

## 🔄 Workflow (develop → prod)

```bash
# 1. Feature development (branch develop)
git checkout -b feature/xxx
# ... kod ...
git push origin feature/xxx

# 2. PR → develop
# → Auto-deploy do DEV ✅

# 3. Test w DEV (Ctrl+F5 dla hard refresh)
https://timeoff-manager-dev.azurewebsites.net

# Sprawdź wersję wdrożenia:
./check_deployment_version.sh dev

# 4. Merge develop → master
git checkout master && git merge develop
git push origin master --tags

# 5. Auto-deploy do PROD ✅ (~2-3 min)
# PROD automatycznie wyłączy się po 30 min bezczynności

# Sprawdź wersję wdrożenia PROD:
./check_deployment_version.sh prod
```

**WAŻNE:**
- Po deployment frontend: **Ctrl+F5** (hard refresh) w przeglądarce
- Sprawdź wersję: `./check_deployment_version.sh dev` lub `./check_deployment_version.sh prod`
- Stopka na dole strony (desktop) pokazuje aktualny commit hash
- PROD wyłącza się automatycznie po 30 min bez użycia (oszczędność ~$565/m)

## 🛠️ Tech Stack

**Backend:**
- Flask 3.0.0
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- bcrypt

**Frontend:**
- React 18 (via CDN)
- Tailwind CSS
- Axios
- Single-page application

**Infrastructure:**
- Azure App Service (Linux, Python 3.9)
- Azure Database for PostgreSQL
- GitHub Actions (CI/CD)
- Azure CLI (management)

## 📚 Dokumentacja

| Dokument | Co znajdziesz |
|----------|---------------|
| **[START.md](START.md)** | **← GŁÓWNY PRZEWODNIK** - komendy, workflow, troubleshooting |
| **[MIGRATIONS.md](MIGRATIONS.md)** | **Migracje bazy PROD** - jak bezpiecznie aktualizować DB |
| [IDLE-MONITORING.md](IDLE-MONITORING.md) | Auto-stop, oszczędzanie kosztów |
| [USER-GUIDE.md](USER-GUIDE.md) | Instrukcja dla użytkowników końcowych |
| [TECHNICAL-DOCS.md](TECHNICAL-DOCS.md) | Architektura, API, modele danych |
| [INDEX.md](INDEX.md) | Pełna nawigacja po dokumentacji |

## 🚀 Szybki setup (dla nowego developera)

```bash
# 1. Clone repo
git clone https://github.com/PowerBIIT/timeoff-manager.git
cd timeoff-manager

# 2. Przeczytaj dokumentację
cat START.md

# 3. Local development
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edytuj .env
python init_db.py
python app.py

# 4. Otwórz http://localhost:5000
# Login: admin@firma.pl / admin123
```

## 📊 Struktura projektu

```
timeoff-manager/
├── app.py                  # Aplikacja Flask
├── models.py               # Modele bazy danych
├── auth.py                 # Autentykacja JWT
├── routes/                 # API endpoints
│   ├── auth_routes.py
│   ├── request_routes.py
│   ├── user_routes.py
│   └── config_routes.py
├── services/               # Logika biznesowa
│   ├── email_service.py
│   └── audit_service.py
├── static/
│   └── index.html          # Frontend (React SPA)
├── scripts/                # Skrypty pomocnicze
│   ├── dev-only-mode.sh    # Zatrzymaj PROD
│   ├── production-mode.sh  # Uruchom PROD
│   └── auto-stop-on-idle.sh # Idle monitoring
└── docs/                   # Dokumentacja
```

## 🔐 Domyślne konta (DEV)

Po `python init_db.py`:

| Email | Hasło | Rola | Supervisor |
|-------|-------|------|------------|
| admin@firma.pl | admin123 | Admin | - |
| manager@firma.pl | manager123 | Manager | Admin |
| jan@firma.pl | jan123 | Employee | Manager |

⚠️ **PROD:** Usuń testowe dane przed wdrożeniem: `python3 clear_prod_data.py`

## 🔧 Zmienne środowiskowe

```bash
# Wymagane
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
SECRET_KEY=your-secret-key-here

# Opcjonalne (można skonfigurować przez UI)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
```

## 🧪 Testowanie

```bash
# Local
python app.py
# Test: http://localhost:5000

# DEV
curl https://timeoff-manager-dev.azurewebsites.net/health

# PROD
curl https://timeoff-manager-20251004.azurewebsites.net/health

# Oczekiwany wynik:
# {"app":"TimeOff Manager","status":"healthy"}
```

## 📝 API Endpoints

### Public
- `POST /api/login` - Logowanie
- `POST /api/logout` - Wylogowanie

### Protected (wymaga JWT token)
- `GET /api/me` - Dane zalogowanego użytkownika
- `GET /api/requests` - Lista wniosków (filtrowana wg roli)
- `POST /api/requests` - Nowy wniosek
- `PUT /api/requests/:id/accept` - Akceptacja (manager/admin)
- `PUT /api/requests/:id/reject` - Odrzucenie (manager/admin)
- `DELETE /api/requests/:id` - Anulowanie (pracownik)
- `GET /api/users` - Lista użytkowników (admin/manager)
- `POST /api/users` - Nowy użytkownik (admin)
- `PUT /api/users/:id` - Edycja użytkownika (admin)
- `DELETE /api/users/:id` - Usunięcie użytkownika (admin)
- `GET /api/smtp-config` - Konfiguracja SMTP (admin)
- `POST /api/smtp-config` - Zapis SMTP (admin)
- `GET /api/audit-logs` - Logi audytowe (admin)

Szczegóły: [TECHNICAL-DOCS.md](TECHNICAL-DOCS.md)

## 🤝 Contributing

1. Fork repo
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m 'feat: Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open Pull Request do `develop`

## 📄 License

Private project - PowerBIIT

## 👥 Authors

- **Radosław Broniszewski** - PowerBIIT
- Built with **Claude Code** (claude.com/code)

## 🆘 Pomoc

**Pytania? Problemy?**
1. Sprawdź [START.md](START.md)
2. Zobacz [IDLE-MONITORING.md](IDLE-MONITORING.md) dla problemów z kosztami
3. GitHub Issues: https://github.com/PowerBIIT/timeoff-manager/issues

**Azure Portal:**
- DEV: Resource Group `timeoff-manager-rg-dev`
- PROD: Resource Group `timeoff-rg-prod`

---

**Wersja:** 1.0 Production Ready
**Status:** ✅ Deployed z pełnym CI/CD i oszczędzaniem kosztów
**Ostatnia aktualizacja:** 2025-10-05
