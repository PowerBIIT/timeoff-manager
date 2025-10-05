# GitHub Actions Setup - Instrukcja konfiguracji

**Data:** 2025-10-05

---

## 📋 Wymagania

- ✅ Środowisko DEV wdrożone (`timeoff-manager-dev`)
- ✅ Środowisko PROD wdrożone (`timeoff-manager-20251004`)
- ✅ Branch `develop` utworzony
- ✅ Branch `master` z kodem produkcyjnym

---

## 🔐 KROK 1: Pobierz Publish Profiles

### A) DEV Publish Profile

```bash
cd /home/radek/timeoff-manager

# Pobierz publish profile dla DEV
az webapp deployment list-publishing-profiles \
  -n timeoff-manager-dev \
  -g timeoff-manager-rg-dev \
  --xml > dev-publish-profile.xml

# Wyświetl zawartość (skopiuj do schowka)
cat dev-publish-profile.xml
```

### B) PROD Publish Profile (jeśli jeszcze nie masz)

```bash
# Pobierz publish profile dla PROD
az webapp deployment list-publishing-profiles \
  -n timeoff-manager-20251004 \
  -g timeoff-rg-prod \
  --xml > prod-publish-profile.xml

# Wyświetl zawartość (skopiuj do schowka)
cat prod-publish-profile.xml
```

---

## 🔑 KROK 2: Dodaj GitHub Secrets

### Sposób 1: Przez GitHub UI

1. Idź do: https://github.com/PowerBIIT/timeoff-manager
2. **Settings** → **Secrets and variables** → **Actions**
3. Kliknij **New repository secret**

**Secret 1: DEV Environment**
- **Name:** `AZURE_WEBAPP_PUBLISH_PROFILE_DEV`
- **Value:** `<zawartość dev-publish-profile.xml>`
- Kliknij **Add secret**

**Secret 2: PROD Environment** (jeśli nie ma)
- **Name:** `AZURE_WEBAPP_PUBLISH_PROFILE`
- **Value:** `<zawartość prod-publish-profile.xml>`
- Kliknij **Add secret**

### Sposób 2: Przez GitHub CLI

```bash
# Zainstaluj gh CLI (jeśli nie masz)
# sudo apt install gh

# Zaloguj się
gh auth login

# Dodaj DEV secret
gh secret set AZURE_WEBAPP_PUBLISH_PROFILE_DEV < dev-publish-profile.xml

# Dodaj PROD secret (jeśli nie ma)
gh secret set AZURE_WEBAPP_PUBLISH_PROFILE < prod-publish-profile.xml
```

---

## ✅ KROK 3: Weryfikacja Secrets

```bash
# Sprawdź czy secrets są dodane
gh secret list

# Powinno pokazać:
# AZURE_WEBAPP_PUBLISH_PROFILE_DEV
# AZURE_WEBAPP_PUBLISH_PROFILE
```

Lub przez GitHub UI:
- Settings → Secrets and variables → Actions
- Powinny być widoczne oba secrets (bez wartości)

---

## 🚀 KROK 4: Test GitHub Actions

### Test 1: Deploy do DEV

```bash
cd /home/radek/timeoff-manager
git checkout develop

# Zrób małą zmianę
echo "# DEV Test $(date)" >> DEV-TEST.md
git add DEV-TEST.md
git commit -m "test: GitHub Actions deploy do DEV"
git push origin develop
```

**Oczekiwany wynik:**
1. GitHub Actions uruchamia workflow: **Deploy to DEV**
2. Build i deploy na: `https://timeoff-manager-dev.azurewebsites.net`
3. Status: ✅ Success

**Sprawdź:**
- GitHub → Actions → Deploy to DEV
- Logi deployment
- Health check: `curl https://timeoff-manager-dev.azurewebsites.net/health`

### Test 2: Deploy do PROD

```bash
git checkout master
git merge develop

# Tag wersji
git tag -a v1.0.0 -m "Release 1.0.0: Initial production deployment"
git push origin master --tags
```

**Oczekiwany wynik:**
1. GitHub Actions uruchamia workflow: **Deploy to PRODUCTION**
2. Wymaga manual approval (jeśli skonfigurowano environment protection)
3. Build i deploy na: `https://timeoff-manager-20251004.azurewebsites.net`
4. Status: ✅ Success

**Sprawdź:**
- GitHub → Actions → Deploy to PRODUCTION
- Logi deployment
- Health check: `curl https://timeoff-manager-20251004.azurewebsites.net/health`

---

## 📊 KROK 5: Weryfikacja końcowa

### Checklist:

- [ ] **DEV Secret:** `AZURE_WEBAPP_PUBLISH_PROFILE_DEV` dodany
- [ ] **PROD Secret:** `AZURE_WEBAPP_PUBLISH_PROFILE` dodany
- [ ] **Branch develop:** Istnieje i jest połączony z DEV workflow
- [ ] **Branch master:** Istnieje i jest połączony z PROD workflow
- [ ] **Test DEV:** Push do develop → auto-deploy ✅
- [ ] **Test PROD:** Push do master → auto-deploy ✅
- [ ] **Health checks:** Oba środowiska odpowiadają 200 OK

---

## 🔄 Proces deployment (pełny workflow)

### Development:

```bash
# 1. Feature branch
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
# https://timeoff-manager-dev.azurewebsites.net
```

### Production:

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

## 🛠️ Troubleshooting

### Problem: Secret nie widoczny w GitHub

```bash
# Sprawdź czy jesteś zalogowany
gh auth status

# Re-login
gh auth logout
gh auth login

# Ponownie dodaj secret
gh secret set AZURE_WEBAPP_PUBLISH_PROFILE_DEV < dev-publish-profile.xml
```

### Problem: Workflow nie uruchamia się

**Sprawdź:**
1. Czy workflow file istnieje: `.github/workflows/deploy-dev.yml`
2. Czy branch jest poprawny: `develop` dla DEV, `master` dla PROD
3. Czy push był na właściwy branch

**Debug:**
```bash
# Sprawdź workflows
ls -la .github/workflows/

# Sprawdź branch
git branch -a

# Force trigger workflow
git commit --allow-empty -m "chore: trigger workflow"
git push
```

### Problem: Deploy fails - "Could not find publish profile"

**Rozwiązanie:**
1. Sprawdź nazwę secret w workflow file
2. Workflow DEV używa: `AZURE_WEBAPP_PUBLISH_PROFILE_DEV`
3. Workflow PROD używa: `AZURE_WEBAPP_PUBLISH_PROFILE`

```bash
# Sprawdź workflow
cat .github/workflows/deploy-dev.yml | grep publish-profile

# Powinno być:
# publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE_DEV }}
```

---

## 📚 Pliki workflow

### DEV: `.github/workflows/deploy-dev.yml`
- **Trigger:** Push do `develop`
- **Target:** `timeoff-manager-dev`
- **Secret:** `AZURE_WEBAPP_PUBLISH_PROFILE_DEV`

### PROD: `.github/workflows/azure-deploy.yml`
- **Trigger:** Push do `master`
- **Target:** `timeoff-manager-20251004`
- **Secret:** `AZURE_WEBAPP_PUBLISH_PROFILE`
- **Environment:** `production` (manual approval)

---

## ✅ Gotowe!

Po wykonaniu tych kroków masz:

✅ Automatyczny deployment DEV (develop → DEV)
✅ Automatyczny deployment PROD (master → PROD)
✅ Pełny CI/CD pipeline
✅ Git flow: feature → develop → master

**Następny krok:** Zacznij kodować i push przez Git! 🚀

---

**Data utworzenia:** 2025-10-05
**Wersja:** 1.0
