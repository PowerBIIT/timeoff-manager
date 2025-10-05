# ⚡ Quick Start - TimeOff Manager (2 środowiska)

**Data:** 2025-10-05

---

## 🎯 Co masz:

```
┌──────────────────────────────────────┐
│  DEV (Development/Test)              │
│  - Resource Group: timeoff-rg-dev    │
│  - App: timeoff-manager-dev          │
│  - DB: timeoff-db-dev                │
│  - URL: https://timeoff-manager-dev.azurewebsites.net
│  - Koszt: ~$20/m (z auto-stop)       │
└──────────────────────────────────────┘
              ↓ (develop → master)
┌──────────────────────────────────────┐
│  PROD (Production)                   │
│  - Resource Group: timeoff-rg-prod   │
│  - App: timeoff-manager-20251004     │
│  - DB: timeoff-db-20251004           │
│  - URL: https://timeoff-manager-20251004.azurewebsites.net
│  - Koszt: ~$285/m (z auto-stop)      │
└──────────────────────────────────────┘

TOTAL: ~$305/m (zamiast $605/m - 50% oszczędności!)
```

---

## 🚀 START (po deploymencie DEV)

### 1. Konfiguracja auto-stop (OBYDWA środowiska)

```bash
cd /home/radek/timeoff-manager

# Automatyczna konfiguracja crontab
./scripts/setup-auto-stop.sh

# Lub manualnie:
crontab -e
# Dodaj:
0 * * * * /home/radek/timeoff-manager/scripts/auto-stop-both.sh >> /var/log/auto-stop.log 2>&1
```

**Efekt:**
- STOP: 18:00-08:00 + weekendy → Oszczędność ~$300/m
- START: 08:00-18:00 (pon-pt) → Automatyczne uruchomienie

### 2. Inicjalizacja bazy DEV

```bash
# Po zakończeniu deploymentu DEV
./scripts/init-dev-database.sh
```

**Konta testowe (DEV):**
- Admin: `admin@firma.pl` / `admin123`
- Manager: `manager@firma.pl` / `manager123`
- Employee: `jan@firma.pl` / `jan123`

### 3. Konfiguracja GitHub Actions

```bash
# Pobierz publish profile DEV
az webapp deployment list-publishing-profiles \
  -n timeoff-manager-dev \
  -g timeoff-manager-rg-dev \
  --xml > dev-publish-profile.xml

# Dodaj jako GitHub Secret
gh secret set AZURE_WEBAPP_PUBLISH_PROFILE_DEV < dev-publish-profile.xml

# Lub przez UI: GitHub → Settings → Secrets → Actions
# Name: AZURE_WEBAPP_PUBLISH_PROFILE_DEV
# Value: <zawartość pliku>
```

---

## 🔄 Workflow development → production

### Development (feature → DEV)

```bash
# 1. Feature branch
git checkout develop
git checkout -b feature/nowa-funkcja

# 2. Kod...
# ... edytuj ...

# 3. Commit i push
git add .
git commit -m "feat: nowa funkcja"
git push origin feature/nowa-funkcja

# 4. Pull Request → develop
# GitHub → Merge PR → Auto-deploy do DEV ✅

# 5. Test w DEV
open https://timeoff-manager-dev.azurewebsites.net
```

### Production (develop → PROD)

```bash
# 6. Merge do master
git checkout master
git merge develop

# 7. Tag wersji
git tag -a v1.1.0 -m "Release 1.1.0"

# 8. Push
git push origin master --tags

# 9. Auto-deploy do PROD ✅
```

---

## 🛠️ Zarządzanie środowiskami

### Start/Stop manualnie

**DEV:**
```bash
# Start
az webapp start -n timeoff-manager-dev -g timeoff-manager-rg-dev
az postgres flexible-server start -n timeoff-db-dev -g timeoff-manager-rg-dev

# Stop
az webapp stop -n timeoff-manager-dev -g timeoff-manager-rg-dev
az postgres flexible-server stop -n timeoff-db-dev -g timeoff-manager-rg-dev
```

**PROD:**
```bash
# Start
az webapp start -n timeoff-manager-20251004 -g timeoff-rg-prod
az postgres flexible-server start -n timeoff-db-20251004 -g timeoff-rg-prod

# Stop
az webapp stop -n timeoff-manager-20251004 -g timeoff-rg-prod
az postgres flexible-server stop -n timeoff-db-20251004 -g timeoff-rg-prod
```

### Status środowisk

```bash
# DEV
az webapp show -n timeoff-manager-dev -g timeoff-manager-rg-dev --query state
az postgres flexible-server show -n timeoff-db-dev -g timeoff-manager-rg-dev --query state

# PROD
az webapp show -n timeoff-manager-20251004 -g timeoff-rg-prod --query state
az postgres flexible-server show -n timeoff-db-20251004 -g timeoff-rg-prod --query state
```

---

## 📊 Monitorowanie kosztów

### Azure Portal

1. Cost Management → Cost Analysis
2. Filtruj po Resource Group:
   - `timeoff-manager-rg-dev`
   - `timeoff-rg-prod`

### Oczekiwane koszty

**BEZ auto-stop:**
- DEV: ~$40/m
- PROD: ~$565/m
- **TOTAL: ~$605/m**

**Z auto-stop (18:00-08:00 + weekendy):**
- DEV: ~$20/m
- PROD: ~$285/m
- **TOTAL: ~$305/m**
- **OSZCZĘDNOŚĆ: ~$300/m (50%)** 💰

---

## 🔍 Health checks

```bash
# DEV
curl https://timeoff-manager-dev.azurewebsites.net/health

# PROD
curl https://timeoff-manager-20251004.azurewebsites.net/health

# Oczekiwany wynik:
{"app":"TimeOff Manager","status":"healthy"}
```

---

## 📚 Dokumentacja

- **SETUP-COMPLETE.md** - Pełna instrukcja setup
- **GITHUB-ACTIONS-SETUP.md** - Konfiguracja CI/CD
- **DEPLOYMENT-WORKFLOW.md** - Proces DEV→PROD
- **README.md** - Główna dokumentacja
- **INDEX.md** - Nawigacja po dokumentach

---

## 🆘 Częste problemy

### Problem: Auto-stop nie działa

```bash
# Sprawdź cron
crontab -l

# Sprawdź logi
tail -f /var/log/auto-stop.log

# Test manualny
./scripts/auto-stop-both.sh
```

### Problem: GitHub Actions nie uruchamia się

```bash
# Sprawdź secrets
gh secret list

# Sprawdź branch
git branch -a

# Force trigger
git commit --allow-empty -m "chore: trigger workflow"
git push
```

### Problem: Za wysokie koszty

```bash
# Sprawdź czy środowiska są zatrzymane
az webapp show -n timeoff-manager-dev -g timeoff-manager-rg-dev --query state
az webapp show -n timeoff-manager-20251004 -g timeoff-rg-prod --query state

# Powinno być "Stopped" po godzinach pracy
```

---

## ✅ Checklist końcowy

- [ ] DEV deployed i działa
- [ ] PROD deployed i działa
- [ ] Auto-stop skonfigurowany (crontab)
- [ ] GitHub Secrets dodane (DEV + PROD)
- [ ] Branch develop utworzony
- [ ] Test workflow DEV (push do develop)
- [ ] Test workflow PROD (push do master)
- [ ] DEV database zainicjalizowany
- [ ] PROD database zweryfikowany

---

## 🚀 Następne kroki

1. **Zacznij kodować!** Utwórz feature branch i push
2. **Monitoruj koszty** przez pierwsze 2 tygodnie
3. **Przetestuj auto-stop** przez weekend
4. **Skonfiguruj SMTP** w Settings (opcjonalnie)
5. **Zaproś zespół** do testowania DEV

---

**Data utworzenia:** 2025-10-05
**Wersja:** 1.0
**Oszczędność:** 50% ($300/miesiąc) 💰
