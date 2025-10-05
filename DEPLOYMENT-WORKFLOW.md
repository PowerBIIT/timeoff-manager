# 🚀 Deployment Workflow - DEV → PROD

**2 środowiska:** Development (testowanie) + Production (live)
**Pełny proces od kodu do produkcji**

---

## 🌍 Architektura środowisk

```
┌──────────────────────────────────────────────────────────────┐
│  LOCAL (Twoja maszyna)                                       │
│  - Python 3.9 + PostgreSQL                                   │
│  - http://localhost:5000                                     │
│  - DEBUG=True                                                │
└──────────────────┬───────────────────────────────────────────┘
                   │ git push origin develop
                   ▼
┌──────────────────────────────────────────────────────────────┐
│  DEV Environment (Azure)                                     │
│  - timeoff-manager-dev.azurewebsites.net                    │
│  - Basic tier (~$40/m)                                       │
│  - Auto-deploy z branch: develop                            │
│  - GitHub Actions: deploy-dev.yml                            │
└──────────────────┬───────────────────────────────────────────┘
                   │ Testy OK? Merge develop → master
                   ▼
┌──────────────────────────────────────────────────────────────┐
│  PRODUCTION (Azure)                                          │
│  - timeoff-manager-20251004.azurewebsites.net               │
│  - Premium tier + HA (~$565/m)                               │
│  - Manual approval required                                  │
│  - GitHub Actions: azure-deploy.yml                          │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 Kompletny proces (krok po kroku)

### 1️⃣ Praca lokalna (Development)

```bash
# Pobierz najnowszy kod
git checkout develop
git pull origin develop

# Utwórz branch dla nowej funkcji
git checkout -b feature/nazwa-funkcji

# Praca nad kodem...
# Edytuj pliki, dodaj funkcje, popraw błędy

# Testowanie lokalne
python app.py
# Otwórz http://localhost:5000
# Sprawdź czy wszystko działa

# Commit zmian
git add .
git commit -m "feat: dodano nową funkcję XYZ"
git push origin feature/nazwa-funkcji
```

---

### 2️⃣ Pull Request do DEV

```bash
# Na GitHub:
# 1. Przejdź do repo: https://github.com/PowerBIIT/timeoff-manager
# 2. Kliknij "Pull requests" → "New pull request"
# 3. Base: develop ← Compare: feature/nazwa-funkcji
# 4. Kliknij "Create pull request"
# 5. Opisz zmiany
# 6. Kliknij "Create pull request"

# Review kodu przez zespół
# Po zatwierdzeniu: "Merge pull request"
```

**Co się dzieje po merge:**
```
GitHub Actions automatycznie:
1. ✅ Buduje aplikację (pip install)
2. ✅ Uruchamia testy (jeśli są)
3. ✅ Tworzy package (deploy.zip)
4. ✅ Wdraża do DEV Azure
5. ✅ DEV URL: https://timeoff-manager-dev.azurewebsites.net
```

**Czas:** ~2-3 minuty

---

### 3️⃣ Testowanie w DEV

```bash
# URL DEV
https://timeoff-manager-dev.azurewebsites.net

# Testy do wykonania:
```

#### Checklist testów DEV:
- [ ] **Health check:** GET /health → 200 OK
- [ ] **Login:** Zaloguj się jako admin/manager/pracownik
- [ ] **Nowa funkcja:** Sprawdź czy działa poprawnie
- [ ] **Regression tests:** Sprawdź czy nie zepsuło starych funkcji
- [ ] **UI/UX:** Sprawdź responsywność, design
- [ ] **Performance:** Czy aplikacja jest szybka?
- [ ] **Errors:** Sprawdź logi błędów

```bash
# Sprawdź logi DEV
az webapp log tail \
  -n timeoff-manager-dev \
  -g timeoff-manager-rg-dev
```

#### Jeśli błędy:
```bash
# Fix w tym samym branchu
git checkout feature/nazwa-funkcji
# Popraw błędy
git commit -m "fix: poprawiono XYZ"
git push origin feature/nazwa-funkcji

# Merge ponownie do develop
# GitHub Actions znowu wdroży do DEV
```

---

### 4️⃣ Release do PRODUCTION

**UWAGA:** Tylko po pełnym zatwierdzeniu w DEV!

```bash
# Przełącz się na develop
git checkout develop
git pull origin develop

# Merge develop → master
git checkout master
git pull origin master
git merge develop

# Utwórz tag wersji
git tag -a v1.2.0 -m "Release 1.2.0: Dodano funkcję XYZ"

# Push do GitHub
git push origin master
git push origin v1.2.0
```

**Co się dzieje po push do master:**
```
GitHub Actions automatycznie:
1. ✅ Wymaga manual approval (Protection Rules)
2. ⏸️  Czeka na zatwierdzenie przez administratora
3. ✅ Po zatwierdzeniu: buduje aplikację
4. ✅ Uruchamia testy
5. ✅ Wdraża do PRODUCTION Azure
6. ✅ PROD URL: https://timeoff-manager-20251004.azurewebsites.net
```

---

### 5️⃣ Manual Approval (PRODUCTION)

```
GitHub → Actions → Deploy to PRODUCTION → Review deployment

Administrator musi:
1. Przejrzeć zmiany
2. Sprawdzić czy testy DEV przeszły
3. Kliknąć "Approve and deploy"

Dopiero wtedy deployment do PROD się uruchomi!
```

**Jak skonfigurować Protection Rules:**
```bash
# Na GitHub:
Settings → Environments → New environment
Name: production

Required reviewers: [wybierz administratorów]
Save protection rules
```

---

### 6️⃣ Weryfikacja PRODUCTION

```bash
# URL PRODUCTION
https://timeoff-manager-20251004.azurewebsites.net

# Smoke tests:
curl https://timeoff-manager-20251004.azurewebsites.net/health

# Monitor przez pierwsze 15 minut:
az webapp log tail \
  -n timeoff-manager-20251004 \
  -g timeoff-manager-rg-prod
```

#### Post-deployment checklist:
- [ ] Health endpoint odpowiada (200 OK)
- [ ] Login działa
- [ ] Nowa funkcja widoczna
- [ ] Brak błędów 500
- [ ] Brak błędów w logach
- [ ] Wydajność OK (< 2s response time)

---

## 🔄 Hotfix Process (Pilna naprawa produkcji)

```bash
# Jeśli krytyczny bug na PROD:

# 1. Utwórz hotfix branch z master
git checkout master
git checkout -b hotfix/critical-bug

# 2. Popraw błąd
# ... edytuj pliki ...

# 3. Commit
git commit -m "fix: critical bug XYZ"

# 4. Merge do master (PROD)
git checkout master
git merge hotfix/critical-bug
git tag -a v1.2.1 -m "Hotfix: Critical bug"
git push origin master --tags

# 5. Merge z powrotem do develop
git checkout develop
git merge hotfix/critical-bug
git push origin develop

# 6. Usuń hotfix branch
git branch -d hotfix/critical-bug
```

---

## 💰 Oszczędności - Zatrzymywanie DEV

### Automatyczne zatrzymanie po godzinach

```bash
# Utwórz skrypt
nano scripts/dev-schedule.sh
```

**Zawartość:**
```bash
#!/bin/bash
# Zatrzymaj DEV poza godzinami pracy (18:00-08:00)

HOUR=$(date +%H)

if [ $HOUR -ge 18 ] || [ $HOUR -lt 8 ]; then
    echo "🌙 Stopping DEV environment..."
    az webapp stop -n timeoff-manager-dev -g timeoff-manager-rg-dev
    az postgres flexible-server stop -n timeoff-manager-db-dev -g timeoff-manager-rg-dev
    echo "✅ DEV stopped. Saving ~$20/month!"
else
    echo "☀️ Starting DEV environment..."
    az webapp start -n timeoff-manager-dev -g timeoff-manager-rg-dev
    az postgres flexible-server start -n timeoff-manager-db-dev -g timeoff-manager-rg-dev
    echo "✅ DEV started and ready!"
fi
```

```bash
# Nadaj uprawnienia
chmod +x scripts/dev-schedule.sh

# Dodaj do cron (wykonuj co godzinę)
crontab -e

# Dodaj linię:
0 * * * * /path/to/timeoff-manager/scripts/dev-schedule.sh >> /var/log/dev-schedule.log 2>&1
```

**Oszczędność:** ~50% kosztów DEV (~$20/m)

---

## 🎯 Git Branching Strategy

```
master (PRODUCTION)
  │
  ├── v1.0.0 (tag)
  ├── v1.1.0 (tag)
  └── v1.2.0 (tag)

develop (DEV)
  │
  ├── feature/nowa-funkcja-A
  ├── feature/nowa-funkcja-B
  └── hotfix/critical-bug
```

### Nazewnictwo branches:
- `feature/nazwa` - nowe funkcje
- `fix/nazwa` - poprawki błędów
- `hotfix/nazwa` - pilne naprawy PROD
- `refactor/nazwa` - refactoring kodu

### Nazewnictwo commitów:
```
feat: dodano nową funkcję X
fix: poprawiono błąd Y
refactor: przepisano moduł Z
docs: zaktualizowano dokumentację
test: dodano testy dla A
```

---

## 📊 Monitoring & Alerts

### Application Insights (PROD)

```bash
# Konfiguracja w Azure Portal:
# 1. Application Insights → timeoff-insights-prod
# 2. Alerts → New alert rule
# 3. Condition: HTTP 5xx > 5 in 5 minutes
# 4. Action: Email admin@firma.pl
```

### Logi na żywo

```bash
# DEV
az webapp log tail -n timeoff-manager-dev -g timeoff-manager-rg-dev

# PROD
az webapp log tail -n timeoff-manager-20251004 -g timeoff-manager-rg-prod
```

---

## 🆘 Rollback (Cofnij deployment)

### Jeśli deployment poszedł źle:

```bash
# Opcja 1: Rollback przez Azure CLI
az webapp deployment slot swap \
  -g timeoff-manager-rg-prod \
  -n timeoff-manager-20251004 \
  --slot staging \
  --action swap

# Opcja 2: Rollback przez Git
git revert HEAD
git push origin master

# Opcja 3: Deploy poprzedniej wersji
git checkout v1.1.0
git tag -a v1.1.1 -m "Rollback to v1.1.0"
git push origin v1.1.1
# Ręcznie trigger GitHub Actions
```

---

## 📚 Dokumentacja

- [terraform/README.md](terraform/README.md) - Infrastructure as Code
- [PRODUCTION-DEPLOYMENT-GUIDE.md](PRODUCTION-DEPLOYMENT-GUIDE.md) - Przygotowanie produkcji
- [TECHNICAL-DOCS.md](TECHNICAL-DOCS.md) - Dokumentacja techniczna
- [TEST-PLAN-DETAILED.md](TEST-PLAN-DETAILED.md) - Plan testów

---

## ✅ Summary Checklist

### Przed każdym release:
- [ ] Wszystkie testy DEV przeszły
- [ ] Code review zakończony
- [ ] Dokumentacja zaktualizowana
- [ ] Changelog zaktualizowany
- [ ] Tag wersji utworzony
- [ ] Manual approval uzyskany
- [ ] Backup produkcyjnej bazy wykonany

### Po deployment PROD:
- [ ] Smoke tests wykonane
- [ ] Logi bez błędów
- [ ] Monitoring włączony
- [ ] Zespół poinformowany
- [ ] Release notes opublikowane

---

**Ostatnia aktualizacja:** 2025-10-05
**Wersja:** 2.0 (2 środowiska: DEV + PROD)
