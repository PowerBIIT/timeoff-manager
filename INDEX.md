# 📚 TimeOff Manager - Dokumentacja

## 🎯 Start Here

Jesteś tutaj po raz pierwszy? Zacznij od:

1. **Czytam README** → [README.md](README.md) - Ogólny opis aplikacji
2. **Chcę przetestować lokalnie** → [Local Development](#local-development)
3. **Chcę wdrożyć na produkcję** → [Production Deployment](#production-deployment)

---

## 📖 Dokumentacja

### Podstawowe

| Plik | Opis | Dla kogo |
|------|------|----------|
| [README.md](README.md) | Główna dokumentacja projektu | Wszyscy |
| [QUICKSTART-PRODUCTION.md](QUICKSTART-PRODUCTION.md) | Szybki start - wdrożenie w 15 min | DevOps, Admin |
| [requirements.txt](requirements.txt) | Zależności Python | Developerzy |

### Deployment i Konfiguracja

| Plik | Opis | Dla kogo |
|------|------|----------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | **Kompletny przewodnik wdrożenia** | DevOps, Admin |
| [PRODUCTION-CHECKLIST.md](PRODUCTION-CHECKLIST.md) | Checklist przed go-live | DevOps, PM |
| [azure-deploy.sh](azure-deploy.sh) | Skrypt automatycznego deploymentu | DevOps |
| [startup.sh](startup.sh) | Skrypt startowy dla Azure | DevOps |
| [production.env.example](production.env.example) | Template zmiennych produkcyjnych | DevOps |
| [.env.example](.env.example) | Template zmiennych development | Developerzy |

### Kod źródłowy

| Katalog/Plik | Opis |
|--------------|------|
| [app.py](app.py) | Główny entry point aplikacji Flask |
| [config.py](config.py) | Konfiguracja aplikacji |
| [models.py](models.py) | Modele bazy danych (SQLAlchemy) |
| [auth.py](auth.py) | JWT authentication & middleware |
| [security.py](security.py) | Dodatkowe zabezpieczenia produkcyjne |
| [init_db.py](init_db.py) | Inicjalizacja bazy danych |
| [routes/](routes/) | API endpoints (auth, requests, users, config) |
| [services/](services/) | Business logic (email, audit) |
| [static/index.html](static/index.html) | Frontend React SPA |

---

## 🚀 Quick Links

### Local Development

```bash
# 1. Zainstaluj zależności
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Konfiguracja
cp .env.example .env
# Edytuj .env (domyślnie SQLite)

# 3. Inicjalizacja bazy
python init_db.py

# 4. Uruchom aplikację
python app.py

# 5. Otwórz przeglądarkę
# http://localhost:5000
```

**Konta testowe:**
- Admin: `admin@firma.pl` / `admin123`
- Manager: `manager@firma.pl` / `manager123`
- Pracownik: `jan@firma.pl` / `jan123`

---

### Production Deployment

**Quick Start (15 min):**
```bash
export DB_PASSWORD="YourStrongPassword123!"
./azure-deploy.sh
```

**Szczegółowo:**
1. Przeczytaj [QUICKSTART-PRODUCTION.md](QUICKSTART-PRODUCTION.md)
2. Sprawdź [PRODUCTION-CHECKLIST.md](PRODUCTION-CHECKLIST.md)
3. Przejrzyj [DEPLOYMENT.md](DEPLOYMENT.md)
4. Uruchom deployment

---

## 🎯 Scenariusze użycia

### Jestem Developerem

**Chcę uruchomić lokalnie i rozwijać:**
1. Sklonuj repozytorium
2. Zainstaluj zależności: `pip install -r requirements.txt`
3. Konfiguruj: `cp .env.example .env`
4. Inicjalizuj DB: `python init_db.py`
5. Uruchom: `python app.py`

**Przydatne pliki:**
- [README.md](README.md) - API documentation
- [models.py](models.py) - Database schema
- [routes/](routes/) - API endpoints
- [static/index.html](static/index.html) - Frontend

---

### Jestem DevOps Engineer

**Chcę wdrożyć na Azure:**
1. Przeczytaj [DEPLOYMENT.md](DEPLOYMENT.md)
2. Sprawdź [PRODUCTION-CHECKLIST.md](PRODUCTION-CHECKLIST.md)
3. Ustaw zmienne środowiskowe
4. Uruchom [azure-deploy.sh](azure-deploy.sh)

**Przydatne pliki:**
- [DEPLOYMENT.md](DEPLOYMENT.md) - Pełny przewodnik
- [QUICKSTART-PRODUCTION.md](QUICKSTART-PRODUCTION.md) - Quick start
- [azure-deploy.sh](azure-deploy.sh) - Skrypt deploymentu
- [production.env.example](production.env.example) - Zmienne środowiskowe

---

### Jestem Product Owner / PM

**Chcę sprawdzić przed go-live:**
1. Przeczytaj [PRODUCTION-CHECKLIST.md](PRODUCTION-CHECKLIST.md)
2. Upewnij się, że wszystkie punkty są ✅
3. Zaakceptuj deployment (sign-off)

**Przydatne pliki:**
- [README.md](README.md) - Funkcje aplikacji
- [PRODUCTION-CHECKLIST.md](PRODUCTION-CHECKLIST.md) - Lista sprawdzająca

---

### Jestem End User (Admin)

**Chcę skonfigurować aplikację:**
1. Zaloguj się jako admin
2. Zmień hasło domyślne
3. Skonfiguruj SMTP (Ustawienia)
4. Dodaj użytkowników (Użytkownicy)

**Dokumentacja:**
- [README.md](README.md) - Jak używać aplikacji

---

## 🔍 FAQ

### Gdzie znaleźć...

**...API documentation?**
→ [README.md](README.md#api-endpoints)

**...instrukcje wdrożenia?**
→ [DEPLOYMENT.md](DEPLOYMENT.md)

**...checklist przed produkcją?**
→ [PRODUCTION-CHECKLIST.md](PRODUCTION-CHECKLIST.md)

**...jak uruchomić lokalnie?**
→ [README.md](README.md#instalacja)

**...jak skonfigurować SMTP?**
→ [DEPLOYMENT.md](DEPLOYMENT.md#4-konfiguruj-smtp-powiadomienia-email)

**...jak monitorować aplikację?**
→ [DEPLOYMENT.md](DEPLOYMENT.md#monitorowanie)

**...jak zrobić backup?**
→ [DEPLOYMENT.md](DEPLOYMENT.md#backup-i-recovery)

**...troubleshooting?**
→ [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting)

---

## 📂 Struktura Projektu

```
timeoff-manager/
├── 📄 README.md                    # Główna dokumentacja
├── 📄 INDEX.md                     # Ten plik - spis treści
├── 📄 DEPLOYMENT.md                # Przewodnik wdrożenia
├── 📄 QUICKSTART-PRODUCTION.md     # Quick start produkcja
├── 📄 PRODUCTION-CHECKLIST.md      # Checklist przed go-live
│
├── 🐍 app.py                       # Flask entry point
├── 🐍 config.py                    # Konfiguracja
├── 🐍 models.py                    # Database models
├── 🐍 auth.py                      # Authentication
├── 🐍 security.py                  # Security utils
├── 🐍 init_db.py                   # DB initialization
│
├── 📁 routes/                      # API endpoints
│   ├── auth_routes.py             # Login, logout, me
│   ├── request_routes.py          # Wnioski CRUD
│   ├── user_routes.py             # Zarządzanie użytkownikami
│   └── config_routes.py           # SMTP config, audit log
│
├── 📁 services/                    # Business logic
│   ├── email_service.py           # Email notifications
│   └── audit_service.py           # Audit logging
│
├── 📁 static/                      # Frontend
│   └── index.html                 # React SPA (all-in-one)
│
├── 🔧 requirements.txt             # Python dependencies
├── 🔧 .env.example                 # Env vars template (dev)
├── 🔧 production.env.example       # Env vars template (prod)
├── 🔧 .gitignore                   # Git ignore rules
│
├── 🚀 azure-deploy.sh              # Azure deployment script
└── 🚀 startup.sh                   # Azure startup script
```

---

## ✅ Checklist - Co muszę wiedzieć?

### Developer:
- [ ] Przeczytałem [README.md](README.md)
- [ ] Znam strukturę projektu
- [ ] Wiem jak uruchomić lokalnie
- [ ] Znam API endpoints

### DevOps:
- [ ] Przeczytałem [DEPLOYMENT.md](DEPLOYMENT.md)
- [ ] Znam proces deploymentu
- [ ] Wiem jak monitorować aplikację
- [ ] Znam procedury backup/recovery

### Product Owner:
- [ ] Znam funkcje aplikacji ([README.md](README.md))
- [ ] Sprawdziłem [PRODUCTION-CHECKLIST.md](PRODUCTION-CHECKLIST.md)
- [ ] Wiem kiedy można iść do produkcji

---

## 📞 Support

**W razie problemów:**

1. Sprawdź [DEPLOYMENT.md - Troubleshooting](DEPLOYMENT.md#troubleshooting)
2. Przejrzyj logi aplikacji
3. Sprawdź [FAQ](#faq)
4. Otwórz issue w repozytorium

---

**Powodzenia z TimeOff Manager! 🚀**
