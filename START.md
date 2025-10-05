# 🚀 TimeOff Manager - Start Guide

**Aktualna wersja:** 1.0 (Production Ready)
**Data:** 2025-10-05
**Azure Subscription:** Pay-As-You-Go (radoslaw.broniszewski@powerbiit.com)

---

## 📋 Szybki przegląd

Masz skonfigurowane **2 środowiska Azure** z pełnym CI/CD i automatycznym oszczędzaniem kosztów:

```
┌──────────────────────────────────────────┐
│  DEV (Development/Testing)               │
│  • https://timeoff-manager-dev.azurewebsites.net
│  • Koszt: ~$40/m (lub $0 gdy zatrzymany) │
│  • Auto-deploy: branch develop          │
└──────────────────────────────────────────┘
              ↓ (merge develop → master)
┌──────────────────────────────────────────┐
│  PROD (Production)                       │
│  • https://timeoff-manager-20251004.azurewebsites.net
│  • Koszt: ~$565/m (lub $0 gdy zatrzymany)│
│  • Auto-deploy: branch master           │
└──────────────────────────────────────────┘
```

---

## ⚡ Najczęstsze komendy

### Sprawdzenie statusu środowisk
```bash
# DEV
az webapp show -n timeoff-manager-dev -g timeoff-manager-rg-dev --query state -o tsv
az postgres flexible-server show -n timeoff-db-dev -g timeoff-manager-rg-dev --query state -o tsv

# PROD
az webapp show -n timeoff-manager-20251004 -g timeoff-rg-prod --query state -o tsv
az postgres flexible-server show -n timeoff-db-20251004 -g timeoff-rg-prod --query state -o tsv
```

### Tryby pracy (oszczędzanie!)

**DEV-ONLY MODE** (podczas developmentu):
```bash
./scripts/dev-only-mode.sh
# Zatrzymuje PROD, uruchamia DEV
# Oszczędność: ~$565/m
```

**PRODUCTION MODE** (przed wdrożeniem):
```bash
./scripts/production-mode.sh
# Uruchamia PROD, zatrzymuje DEV
```

**Oba środowiska działają**:
```bash
az webapp start -n timeoff-manager-dev -g timeoff-manager-rg-dev
az webapp start -n timeoff-manager-20251004 -g timeoff-rg-prod
```

### Health checks
```bash
# DEV
curl https://timeoff-manager-dev.azurewebsites.net/health

# PROD
curl https://timeoff-manager-20251004.azurewebsites.net/health

# Oczekiwany wynik:
# {"app":"TimeOff Manager","status":"healthy"}
```

---

## 🔄 Workflow development → production

### 1. Development (nowa funkcja)
```bash
cd /home/radek/timeoff-manager

# Utwórz feature branch z develop
git checkout develop
git pull origin develop
git checkout -b feature/nowa-funkcja

# Kod...
# ... edytuj pliki ...

# Commit i push
git add .
git commit -m "feat: nowa funkcja XYZ"
git push origin feature/nowa-funkcja

# Pull Request na GitHub
# base: develop ← feature/nowa-funkcja
# Merge → GitHub Actions → Auto-deploy do DEV ✅
```

### 2. Test w DEV
```bash
# Otwórz DEV w przeglądarce
https://timeoff-manager-dev.azurewebsites.net

# Logowanie (konta testowe):
# Admin:    admin@firma.pl / admin123
# Manager:  manager@firma.pl / manager123
# Employee: jan@firma.pl / jan123
```

### 3. Release do PROD
```bash
# Merge develop → master
git checkout master
git pull origin master
git merge develop

# Tag wersji
git tag -a v1.1.0 -m "Release 1.1.0: Opis zmian"

# Push
git push origin master --tags

# GitHub Actions → Auto-deploy do PROD ✅
```

---

## 💰 Oszczędzanie kosztów

### Opcja 1: Idle Monitoring (AKTYWNE)

**Status:** ✅ Skonfigurowane
**Jak działa:** Automatyczne zatrzymanie po 30 min bez HTTP requestów

```bash
# Sprawdź logi
tail -f /var/log/idle-monitor.log

# Status
crontab -l | grep idle
```

**Oszczędności:**
- Użycie 2h/dzień: ~$50/m (oszczędność **92%**)
- Użycie 8h/dzień: ~$201/m (oszczędność **67%**)

### Opcja 2: Tryby DEV/PROD

**DEV-ONLY (podczas developmentu):**
```bash
./scripts/dev-only-mode.sh
```
- DEV: Działający
- PROD: **Zatrzymany** (oszczędność ~$565/m)
- **TOTAL: ~$40/m** (zamiast ~$605/m)

**PRODUCTION (gdy potrzebujesz PROD):**
```bash
./scripts/production-mode.sh
```
- PROD: Działający
- DEV: Zatrzymany
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

## 🗂️ Dokumentacja szczegółowa

| Plik | Co zawiera |
|------|------------|
| `IDLE-MONITORING.md` | Konfiguracja i troubleshooting idle monitoring |
| `TECHNICAL-DOCS.md` | Architektura, API, modele danych |
| `USER-GUIDE.md` | Instrukcja dla użytkowników końcowych |
| `TEST-PLAN-DETAILED.md` | Plan testów |
| `TEST-EXECUTION-REPORT.md` | Raport testów (100% PASS) |
| `INDEX.md` | Pełna nawigacja po dokumentacji |

---

## 🛠️ Skrypty pomocnicze

### Deployment
| Skrypt | Opis |
|--------|------|
| `scripts/deploy-dev-azure.sh` | Wdrożenie DEV przez Azure CLI |
| `scripts/init-dev-database.sh` | Inicjalizacja bazy DEV z testowymi danymi |

### Oszczędzanie kosztów
| Skrypt | Opis |
|--------|------|
| `scripts/dev-only-mode.sh` | Tryb DEV-ONLY (zatrzymaj PROD) |
| `scripts/production-mode.sh` | Tryb PRODUCTION (uruchom PROD) |
| `scripts/auto-stop-on-idle.sh` | Idle monitoring (auto-stop po 30 min) |
| `scripts/setup-idle-monitor.sh` | Instalator idle monitoring |
| `scripts/auto-stop-both.sh` | Harmonogram czasowy (alternatywa) |
| `scripts/setup-auto-stop.sh` | Instalator harmonogramu |

---

## 🔐 Konta i dane dostępowe

### DEV Environment
**URL:** https://timeoff-manager-dev.azurewebsites.net

**Konta testowe:**
- Admin: `admin@firma.pl` / `admin123`
- Manager: `manager@firma.pl` / `manager123`
- Employee: `jan@firma.pl` / `jan123`

**Baza danych:**
- Host: `timeoff-db-dev.postgres.database.azure.com`
- Database: `timeoffdb`
- User: `dbadmin`

### PROD Environment
**URL:** https://timeoff-manager-20251004.azurewebsites.net

**Konta:**
- Po wyczyszczeniu testowych danych: brak
- Pierwszy admin należy utworzyć przez UI

**Baza danych:**
- Host: `timeoff-db-20251004.postgres.database.azure.com`
- Database: `timeoffdb`
- User: `dbadmin`

---

## 📊 Koszty Azure (miesięcznie)

### BEZ oszczędzania
```
DEV:  App Service B1 (~$13) + PostgreSQL Standard_B1ms (~$27) = ~$40/m
PROD: App Service P1v2 (~$90) + PostgreSQL GP_Standard_D4s_v3 (~$475) = ~$565/m
───────────────────────────────────────────────────────────────────────
TOTAL: ~$605/m
```

### Z idle monitoring (sporadyczne użycie, 2h/dzień)
```
DEV:  ~$3/m
PROD: ~$47/m
───────────────────────────────────────────────────────────────────────
TOTAL: ~$50/m
OSZCZĘDNOŚĆ: ~$555/m (92%)! 💰
```

### Z DEV-ONLY mode (development)
```
DEV:  ~$40/m (działający)
PROD: $0/m (zatrzymany)
───────────────────────────────────────────────────────────────────────
TOTAL: ~$40/m
OSZCZĘDNOŚĆ: ~$565/m (93%)! 💰
```

---

## 🆘 Troubleshooting

### Problem: Aplikacja nie odpowiada
```bash
# Sprawdź status
az webapp show -n <app-name> -g <rg-name> --query state

# Jeśli Stopped - uruchom
az webapp start -n <app-name> -g <rg-name>

# Poczekaj 2-3 minuty i sprawdź health
curl https://<app-name>.azurewebsites.net/health
```

### Problem: Błąd połączenia z bazą
```bash
# Sprawdź czy DB działa
az postgres flexible-server show -n <db-name> -g <rg-name> --query state

# Jeśli Stopped - uruchom
az postgres flexible-server start -n <db-name> -g <rg-name>

# Poczekaj ~30 sekund
```

### Problem: GitHub Actions deployment fails
```bash
# Sprawdź logi
gh run list --limit 5
gh run view <run-id> --log

# Sprawdź czy secrets są skonfigurowane
gh secret list

# Powinno być:
# AZURE_WEBAPP_PUBLISH_PROFILE (PROD)
# AZURE_WEBAPP_PUBLISH_PROFILE_DEV (DEV)
```

### Problem: Za wysokie koszty
```bash
# Sprawdź czy środowiska są zatrzymane
az webapp show -n timeoff-manager-dev -g timeoff-manager-rg-dev --query state
az webapp show -n timeoff-manager-20251004 -g timeoff-rg-prod --query state

# Sprawdź czy idle monitoring działa
tail -50 /var/log/idle-monitor.log
crontab -l | grep idle

# Użyj DEV-ONLY mode
./scripts/dev-only-mode.sh
```

---

## 🚀 Następne kroki

### Teraz (development):
1. **Zatrzymaj PROD aby oszczędzić:**
   ```bash
   ./scripts/dev-only-mode.sh
   ```

2. **Rozwijaj aplikację:**
   - Twórz feature branches z `develop`
   - Push → Auto-deploy do DEV
   - Testuj w DEV

3. **Monitoruj koszty:**
   - Azure Portal → Cost Management → Cost Analysis
   - Filtruj po Resource Groups

### Przed wdrożeniem do klientów:
1. **Wyczyść dane testowe z PROD:**
   ```bash
   python3 clear_prod_data.py
   ```

2. **Uruchom PROD:**
   ```bash
   ./scripts/production-mode.sh
   ```

3. **Skonfiguruj SMTP** (Settings w UI)

4. **Utwórz pierwszego admina** produkcyjnego

5. **Deploy przez GitHub Actions:**
   ```bash
   git checkout master
   git merge develop
   git tag v1.0.0
   git push origin master --tags
   ```

---

## 📞 Pomoc

**Dokumentacja:**
- Pełna lista: `INDEX.md`
- Idle monitoring: `IDLE-MONITORING.md`
- Dla użytkowników: `USER-GUIDE.md`
- Techniczna: `TECHNICAL-DOCS.md`

**GitHub Actions:**
- Workflows: `.github/workflows/`
- Status: `gh run list`

**Azure:**
- Portal: https://portal.azure.com
- DEV Resource Group: `timeoff-manager-rg-dev`
- PROD Resource Group: `timeoff-rg-prod`

---

**Wersja dokumentacji:** 1.0
**Ostatnia aktualizacja:** 2025-10-05
**Status:** ✅ Production Ready z pełnym CI/CD i oszczędzaniem kosztów
