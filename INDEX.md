# 📚 TimeOff Manager - Nawigacja dokumentacji

## 🚀 Start tutaj

**Nowy w projekcie?** Zacznij od tego:

**👉 [START.md](START.md) ← Kompletny przewodnik (wszystko w jednym miejscu!)**

Zawiera:
- Komendy Azure (sprawdzanie statusu, uruchamianie, zatrzymywanie)
- Workflow develop → PROD
- Oszczędzanie kosztów (3 opcje)
- Troubleshooting
- Wszystkie najważniejsze informacje

---

## 📖 Dokumentacja główna

| Plik | Opis | Dla kogo |
|------|------|----------|
| [README.md](README.md) | Przegląd projektu, tech stack, API | Wszyscy |
| [START.md](START.md) | **Kompletny przewodnik start-to-finish** | Wszyscy |
| [IDLE-MONITORING.md](IDLE-MONITORING.md) | Oszczędzanie kosztów, idle monitoring | DevOps, Admin |
| [USER-GUIDE.md](USER-GUIDE.md) | Instrukcja dla użytkowników końcowych | End Users |
| [TECHNICAL-DOCS.md](TECHNICAL-DOCS.md) | Architektura, API, modele danych | Developerzy |
| [CLAUDE.md](CLAUDE.md) | Instrukcje dla AI (Claude Code) | AI/Developerzy |

---

## 🌐 Środowiska

### DEV (Development)
- **URL:** https://timeoff-manager-dev.azurewebsites.net
- **Koszt:** ~$40/m (lub $0 gdy zatrzymany)
- **Auto-deploy:** branch `develop`
- **Resource Group:** `timeoff-manager-rg-dev`

```bash
# Sprawdź status
az webapp show -n timeoff-manager-dev -g timeoff-manager-rg-dev --query state -o tsv

# Health check
curl https://timeoff-manager-dev.azurewebsites.net/health
```

### PROD (Production)
- **URL:** https://timeoff-manager-20251004.azurewebsites.net
- **Koszt:** ~$565/m (lub $0 gdy zatrzymany)
- **Auto-deploy:** branch `master`
- **Resource Group:** `timeoff-rg-prod`

```bash
# Sprawdź status
az webapp show -n timeoff-manager-20251004 -g timeoff-rg-prod --query state -o tsv

# Health check
curl https://timeoff-manager-20251004.azurewebsites.net/health
```

---

## 💰 Oszczędzanie kosztów

### Opcja 1: Idle Monitoring (✅ AKTYWNE)
**Status:** Skonfigurowane w crontab
**Jak działa:** Automatyczne zatrzymanie po 30 min bez HTTP requestów

```bash
# Sprawdź logi
tail -f /var/log/idle-monitor.log

# Sprawdź konfigurację cron
crontab -l | grep idle
```

**Oszczędności:**
- Użycie 2h/dzień: ~$50/m (oszczędność **92%**)
- Użycie 8h/dzień: ~$201/m (oszczędność **67%**)

**Dokumentacja:** [IDLE-MONITORING.md](IDLE-MONITORING.md)

### Opcja 2: Tryby DEV/PROD

**DEV-ONLY MODE** (podczas developmentu):
```bash
./scripts/dev-only-mode.sh
```
- Zatrzymuje PROD (oszczędność ~$565/m)
- Uruchamia DEV
- **TOTAL: ~$40/m**

**PRODUCTION MODE** (przed wdrożeniem):
```bash
./scripts/production-mode.sh
```
- Uruchamia PROD
- Zatrzymuje DEV
- **TOTAL: ~$565/m**

### Opcja 3: Wszystko STOP
```bash
# Zatrzymaj wszystko gdy nie pracujesz
az webapp stop -n timeoff-manager-dev -g timeoff-manager-rg-dev
az postgres flexible-server stop -n timeoff-db-dev -g timeoff-manager-rg-dev
az webapp stop -n timeoff-manager-20251004 -g timeoff-rg-prod
az postgres flexible-server stop -n timeoff-db-20251004 -g timeoff-rg-prod

# Koszt: $0/m! 🎉
```

---

## 🔄 Workflow (develop → PROD)

### 1. Development
```bash
git checkout develop
git pull origin develop
git checkout -b feature/nowa-funkcja

# ... kod ...

git add .
git commit -m "feat: nowa funkcja"
git push origin feature/nowa-funkcja

# Pull Request → develop
# Merge → Auto-deploy do DEV ✅
```

### 2. Test w DEV
```
https://timeoff-manager-dev.azurewebsites.net

Konta testowe:
- Admin: admin@firma.pl / admin123
- Manager: manager@firma.pl / manager123
- Employee: jan@firma.pl / jan123
```

### 3. Release do PROD
```bash
git checkout master
git pull origin master
git merge develop
git tag -a v1.1.0 -m "Release 1.1.0"
git push origin master --tags

# Auto-deploy do PROD ✅
```

---

## 🛠️ Skrypty pomocnicze

| Skrypt | Opis |
|--------|------|
| `scripts/dev-only-mode.sh` | Tryb DEV-ONLY (zatrzymaj PROD) |
| `scripts/production-mode.sh` | Tryb PRODUCTION (uruchom PROD) |
| `scripts/auto-stop-on-idle.sh` | Idle monitoring (auto-stop) |
| `scripts/setup-idle-monitor.sh` | Instalator idle monitoring |
| `scripts/deploy-dev-azure.sh` | Wdrożenie DEV |
| `scripts/init-dev-database.sh` | Inicjalizacja bazy DEV |

---

## 📂 Struktura projektu

```
timeoff-manager/
├── 📄 README.md              # Przegląd projektu
├── 📄 START.md               # Kompletny przewodnik
├── 📄 INDEX.md               # Ten plik - nawigacja
├── 📄 IDLE-MONITORING.md     # Oszczędzanie kosztów
├── 📄 USER-GUIDE.md          # Dla użytkowników
├── 📄 TECHNICAL-DOCS.md      # Dokumentacja techniczna
├── 📄 CLAUDE.md              # Instrukcje dla AI
│
├── 🐍 app.py                 # Flask application
├── 🐍 models.py              # Database models
├── 🐍 auth.py                # JWT authentication
├── 🐍 init_db.py             # Database initialization
│
├── 📁 routes/                # API endpoints
│   ├── auth_routes.py
│   ├── request_routes.py
│   ├── user_routes.py
│   └── config_routes.py
│
├── 📁 services/              # Business logic
│   ├── email_service.py
│   └── audit_service.py
│
├── 📁 static/
│   └── index.html            # React SPA frontend
│
├── 📁 scripts/               # Utility scripts
│   ├── dev-only-mode.sh
│   ├── production-mode.sh
│   ├── auto-stop-on-idle.sh
│   └── setup-idle-monitor.sh
│
└── 📁 docs/                  # Additional documentation
    └── archive/              # Archived old docs
```

---

## 🎯 Scenariusze użycia

### Jestem Developerem

**Chcę rozwijać aplikację lokalnie:**
1. Sklonuj repo: `git clone https://github.com/PowerBIIT/timeoff-manager.git`
2. Setup: patrz [START.md](START.md#local-development)
3. Przeczytaj: [TECHNICAL-DOCS.md](TECHNICAL-DOCS.md)

### Jestem DevOps Engineer

**Chcę zarządzać środowiskami Azure:**
1. Przeczytaj: [START.md](START.md)
2. Konfiguracja kosztów: [IDLE-MONITORING.md](IDLE-MONITORING.md)
3. Deployment: [README.md](README.md#workflow-develop--prod)

### Jestem End User

**Chcę używać aplikacji:**
1. Zaloguj się do środowiska
2. Przeczytaj: [USER-GUIDE.md](USER-GUIDE.md)
3. Skonfiguruj SMTP (jako admin)

---

## 🔍 FAQ

### Gdzie znaleźć...

**...główny przewodnik?**
→ [START.md](START.md)

**...komendy Azure?**
→ [START.md](START.md#najczęstsze-komendy)

**...jak oszczędzać na kosztach?**
→ [IDLE-MONITORING.md](IDLE-MONITORING.md)
→ [START.md](START.md#oszczędzanie-kosztów)

**...API documentation?**
→ [README.md](README.md#api-endpoints)
→ [TECHNICAL-DOCS.md](TECHNICAL-DOCS.md)

**...workflow deployment?**
→ [START.md](START.md#workflow-development--production)
→ [README.md](README.md#workflow-develop--prod)

**...troubleshooting?**
→ [START.md](START.md#troubleshooting)
→ [IDLE-MONITORING.md](IDLE-MONITORING.md#troubleshooting)

**...instrukcja dla użytkowników?**
→ [USER-GUIDE.md](USER-GUIDE.md)

**...architektura systemu?**
→ [TECHNICAL-DOCS.md](TECHNICAL-DOCS.md)

---

## 💡 Koszty Azure (miesięcznie)

### BEZ oszczędzania
```
DEV:  ~$40/m
PROD: ~$565/m
───────────────────
TOTAL: ~$605/m
```

### Z idle monitoring (2h/dzień użycia)
```
DEV:  ~$3/m
PROD: ~$47/m
───────────────────
TOTAL: ~$50/m
OSZCZĘDNOŚĆ: ~$555/m (92%)! 💰
```

### Z DEV-ONLY mode (development)
```
DEV:  ~$40/m (działający)
PROD: $0/m (zatrzymany)
───────────────────
TOTAL: ~$40/m
OSZCZĘDNOŚĆ: ~$565/m (93%)! 💰
```

Szczegóły: [IDLE-MONITORING.md](IDLE-MONITORING.md)

---

## 📞 Support i Troubleshooting

**W razie problemów:**

1. **Środowisko nie odpowiada?** → [START.md - Troubleshooting](START.md#troubleshooting)
2. **Za wysokie koszty?** → [IDLE-MONITORING.md](IDLE-MONITORING.md)
3. **GitHub Actions fails?** → [START.md - Troubleshooting](START.md#problem-github-actions-deployment-fails)
4. **Pytania techniczne?** → [TECHNICAL-DOCS.md](TECHNICAL-DOCS.md)

**Azure Portal:**
- DEV: Resource Group `timeoff-manager-rg-dev`
- PROD: Resource Group `timeoff-rg-prod`

---

## 📁 Archiwum dokumentacji

Stare pliki przeniesione do `docs/archive/`:
- Deployment guides (old versions)
- Test plans and reports
- Production checklists (archived)

---

**Wersja:** 1.0 Production Ready
**Ostatnia aktualizacja:** 2025-10-05
**Status:** ✅ Deployed z pełnym CI/CD i oszczędzaniem kosztów

**Powodzenia! 🚀**
