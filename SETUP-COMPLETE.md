# ✅ Kompletny setup - 2 środowiska (DEV + PROD) z auto-stop

**Data:** 2025-10-05
**Subskrypcja:** Pay-As-You-Go (radoslaw.broniszewski@powerbiit.com)

---

## 🎯 Co masz teraz:

### **2 środowiska na tej samej subskrypcji:**

```
┌─────────────────────────────────────┐
│  DEV (Development/Test)             │
│  - Resource Group: timeoff-rg-dev   │
│  - App: timeoff-manager-dev         │
│  - DB: timeoff-db-dev               │
│  - URL: https://timeoff-manager-dev.azurewebsites.net
│  - Koszt: ~$40/m                    │
│  - Auto-stop: 18:00-08:00 + weekend │
│  - Oszczędność: ~$20/m              │
└─────────────────────────────────────┘
              ↓ (develop → master)
┌─────────────────────────────────────┐
│  PROD (Production)                  │
│  - Resource Group: timeoff-rg-prod  │
│  - App: timeoff-manager-20251004    │
│  - DB: timeoff-db-20251004          │
│  - URL: https://timeoff-manager-20251004.azurewebsites.net
│  - Koszt: ~$565/m                   │
│  - Auto-stop: 18:00-08:00 + weekend │
│  - Oszczędność: ~$280/m             │
└─────────────────────────────────────┘
```

**TOTAL koszt BEZ auto-stop:** ~$605/m
**TOTAL koszt Z auto-stop:** ~$305/m
**OSZCZĘDNOŚĆ:** ~$300/m (50%!) 💰

---

## 🚀 KROK 1: Weryfikacja deployment DEV

```bash
# Sprawdź status (deployment trwa ~10-15 minut)
az group show -n timeoff-manager-rg-dev

# Kiedy gotowe, sprawdź zasoby:
az resource list -g timeoff-manager-rg-dev --output table

# Test health check:
curl https://timeoff-manager-dev.azurewebsites.net/health
```

**Oczekiwany wynik:**
```json
{"app":"TimeOff Manager","status":"healthy"}
```

---

## 🔧 KROK 2: Konfiguracja auto-stop dla OBUICH środowisk

### Automatyczne zatrzymywanie/uruchamianie:
- **STOP:** 18:00 - 08:00 + weekendy (sobota, niedziela)
- **START:** 08:00 - 18:00 (poniedziałek-piątek)

```bash
# Konfiguruj auto-stop
cd /home/radek/timeoff-manager

# Edytuj crontab
crontab -e

# Dodaj linię (uruchamia co godzinę):
0 * * * * /home/radek/timeoff-manager/scripts/auto-stop-both.sh >> /var/log/auto-stop.log 2>&1
```

### Test manualny:

```bash
# Test zatrzymania
./scripts/auto-stop-both.sh

# Sprawdź logi
tail -f /var/log/auto-stop.log
```

**Co robi skrypt:**
- Sprawdza godzinę i dzień tygodnia
- Jeśli po godzinach lub weekend → **STOP** (DEV + PROD)
- Jeśli godziny pracy (8-18, pon-pt) → **START** (DEV + PROD)

---

## 📦 KROK 3: Konfiguracja GitHub Actions

### A) Pobierz publish profiles

```bash
# DEV publish profile
az webapp deployment list-publishing-profiles \
  -n timeoff-manager-dev \
  -g timeoff-manager-rg-dev \
  --xml > dev-publish-profile.xml

# PROD publish profile (jeśli jeszcze nie masz)
az webapp deployment list-publishing-profiles \
  -n timeoff-manager-20251004 \
  -g timeoff-rg-prod \
  --xml > prod-publish-profile.xml
```

### B) Dodaj jako GitHub Secrets

```bash
# GitHub → Settings → Secrets and variables → Actions

# 1. New repository secret
Name: AZURE_WEBAPP_PUBLISH_PROFILE_DEV
Value: <zawartość dev-publish-profile.xml>

# 2. New repository secret (jeśli nie ma)
Name: AZURE_WEBAPP_PUBLISH_PROFILE
Value: <zawartość prod-publish-profile.xml>
```

---

## 🌳 KROK 4: Utwórz branch `develop`

```bash
cd /home/radek/timeoff-manager

# Utwórz branch develop z master
git checkout master
git pull origin master
git checkout -b develop
git push -u origin develop

# Ustaw develop jako default branch dla PRs (opcjonalnie)
# GitHub → Settings → Branches → Default branch → develop
```

---

## 🔄 KROK 5: Proces deployment (pełny workflow)

### **Development:**

```bash
# 1. Utwórz feature branch
git checkout develop
git pull origin develop
git checkout -b feature/nowa-funkcja

# 2. Kod...
# ... edytuj pliki ...

# 3. Commit
git add .
git commit -m "feat: dodano nową funkcję XYZ"
git push origin feature/nowa-funkcja

# 4. Pull Request
# GitHub → New PR → base: develop ← feature/nowa-funkcja
# Merge → GitHub Actions → Auto-deploy do DEV

# 5. Test w DEV
https://timeoff-manager-dev.azurewebsites.net
# Testy funkcjonalne, regression, performance
```

### **Production:**

```bash
# 6. Release do PROD
git checkout master
git pull origin master
git merge develop

# 7. Tag wersji
git tag -a v1.2.0 -m "Release 1.2.0: Nowa funkcja XYZ"

# 8. Push
git push origin master --tags

# 9. GitHub Actions → Deploy do PROD
# (opcjonalnie: wymaga manual approval jeśli skonfigurujesz)
```

---

## 💰 KROK 6: Monitorowanie kosztów

### Sprawdź aktualny koszt:

```bash
# Azure Portal → Cost Management → Cost Analysis
# Filtruj po Resource Group:
# - timeoff-manager-rg-dev
# - timeoff-rg-prod
```

### Oczekiwane koszty:

**BEZ auto-stop:**
- DEV: ~$40/m
- PROD: ~$565/m
- **TOTAL:** ~$605/m

**Z auto-stop (18:00-08:00 + weekendy):**
- DEV: ~$20/m (50% oszczędności)
- PROD: ~$285/m (50% oszczędności)
- **TOTAL:** ~$305/m

**OSZCZĘDNOŚĆ:** ~$300/m 💰

---

## 🔍 KROK 7: Inicjalizacja baz danych

### DEV Database:

```bash
cd /home/radek/timeoff-manager

# Connection string z DEV
export DATABASE_URL="postgresql://dbadmin:Vcte9IKmHO+80QvRS3HFIg==@timeoff-db-dev.postgres.database.azure.com:5432/timeoffdb?sslmode=require"
export SECRET_KEY="106e600452304fd169651b2451eca236f7e04ad728f419040738a57bc03b3d47"

# Inicjalizuj z testowymi danymi
python3 init_db.py
```

### PROD Database:

```bash
# PROD już ma dane - jeśli chcesz wyczyścić:
export DATABASE_URL="<prod-connection-string>"
export SECRET_KEY="<prod-secret-key>"

# Wyczyść testowe dane
python3 clear_prod_data.py

# Utwórz pierwszego admina produkcyjnego (przez UI lub API)
```

---

## 📊 KROK 8: Weryfikacja końcowa

### Checklist:

- [ ] **DEV deployed:** `curl https://timeoff-manager-dev.azurewebsites.net/health`
- [ ] **PROD works:** `curl https://timeoff-manager-20251004.azurewebsites.net/health`
- [ ] **Auto-stop configured:** `crontab -l | grep auto-stop`
- [ ] **GitHub Secrets added:** DEV + PROD publish profiles
- [ ] **Branch develop created:** `git branch -a`
- [ ] **Workflows work:** Push to develop → DEV, push to master → PROD
- [ ] **DEV database initialized:** Testowe konta działają
- [ ] **PROD database clean:** Usunięto testowe dane

---

## 🛠️ Komendy pomocnicze

### Manualne stop/start środowisk:

```bash
# Stop DEV
az webapp stop -n timeoff-manager-dev -g timeoff-manager-rg-dev
az postgres flexible-server stop -n timeoff-db-dev -g timeoff-manager-rg-dev

# Start DEV
az webapp start -n timeoff-manager-dev -g timeoff-manager-rg-dev
az postgres flexible-server start -n timeoff-db-dev -g timeoff-manager-rg-dev

# Stop PROD
az webapp stop -n timeoff-manager-20251004 -g timeoff-rg-prod
az postgres flexible-server stop -n timeoff-db-20251004 -g timeoff-rg-prod

# Start PROD
az webapp start -n timeoff-manager-20251004 -g timeoff-rg-prod
az postgres flexible-server start -n timeoff-db-20251004 -g timeoff-rg-prod
```

### Sprawdź status:

```bash
# DEV
az webapp show -n timeoff-manager-dev -g timeoff-manager-rg-dev --query state
az postgres flexible-server show -n timeoff-db-dev -g timeoff-manager-rg-dev --query state

# PROD
az webapp show -n timeoff-manager-20251004 -g timeoff-rg-prod --query state
az postgres flexible-server show -n timeoff-db-20251004 -g timeoff-rg-prod --query state
```

---

## 🆘 Troubleshooting

### Problem: Auto-stop nie działa

```bash
# Sprawdź cron
crontab -l

# Sprawdź logi
tail -100 /var/log/auto-stop.log

# Test manualny
./scripts/auto-stop-both.sh
```

### Problem: DEV nie deploy się

```bash
# Sprawdź GitHub Actions
# Repo → Actions → Deploy to DEV

# Sprawdź logi Azure
az webapp log tail -n timeoff-manager-dev -g timeoff-manager-rg-dev
```

### Problem: Za wysokie koszty

```bash
# Sprawdź czy auto-stop działa:
az webapp show -n timeoff-manager-dev -g timeoff-manager-rg-dev --query state
az webapp show -n timeoff-manager-20251004 -g timeoff-rg-prod --query state

# Powinno być "Stopped" poza godzinami pracy
```

---

## 📚 Dokumentacja

- **DEPLOYMENT-WORKFLOW.md** - Pełny proces DEV→PROD
- **terraform/README.md** - Infrastructure as Code
- **PRODUCTION-DEPLOYMENT-GUIDE.md** - Przygotowanie produkcji
- **scripts/** - Wszystkie skrypty pomocnicze

---

## ✅ Gratulacje!

Masz teraz **profesjonalny setup 2 środowisk** z:

- ✅ Automatycznym deployment (GitHub Actions)
- ✅ Automatycznym oszczędzaniem kosztów (auto-stop)
- ✅ Pełnym workflow DEV→PROD
- ✅ Oszczędnością ~$300/miesiąc (50%!)

**Następny krok:** Zacznij kodować i deploy przez Git! 🚀

---

**Data utworzenia:** 2025-10-05
**Wersja:** 1.0
