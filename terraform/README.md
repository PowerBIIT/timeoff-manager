# TimeOff Manager - Infrastructure as Code (Terraform)

**2 środowiska:** Development + Production
**Gotowe do wdrożenia na dowolną subskrypcję Azure**

---

## 📁 Struktura projektu

```
terraform/
├── main.tf                      # Główna konfiguracja Terraform
├── variables.tf                 # Zmienne globalne
├── modules/                     # Moduły reużywalne
│   ├── app-service/            # Azure App Service + Plan
│   └── database/               # PostgreSQL Flexible Server
└── environments/               # Konfiguracje per środowisko
    ├── dev/                   # Development/Testing
    └── prod/                  # Production
```

---

## 🌍 Architektura środowisk

### Development (DEV)
**Cel:** Szybkie testowanie nowych funkcji przed produkcją

- **App Service:** B1 (Basic tier)
- **Database:** B_Standard_B1ms (1 vCore, 2GB RAM)
- **Storage:** 32 GB
- **Backup:** 7 dni, bez geo-redundancji
- **HA:** Wyłączone
- **Koszt:** ~$40/miesiąc
- **Optymalizacja:** Zatrzymuj po godzinach!

### Production (PROD)
**Cel:** Środowisko produkcyjne dla użytkowników końcowych

- **App Service:** P1v2 (Premium tier) + staging slot
- **Database:** GP_Standard_D4s_v3 (4 vCores, 16GB RAM)
- **Storage:** 128 GB
- **Backup:** 35 dni + geo-redundancja
- **HA:** Zone-redundant
- **Monitoring:** Application Insights
- **Security:** Azure Key Vault
- **Koszt:** ~$565/miesiąc

---

## 🚀 Wdrożenie na nową subskrypcję Azure

### Krok 0: Wymagania

```bash
# Terraform
terraform --version  # >= 1.0

# Azure CLI
az --version        # >= 2.0
az login
az account list --output table
az account set --subscription "Nazwa-lub-ID-subskrypcji"
```

### Krok 1: Przygotowanie zmiennych środowiska

#### Development
```bash
cd terraform/environments/dev

# Skopiuj template
cp terraform.tfvars.example terraform.tfvars

# Edytuj wartości
nano terraform.tfvars
```

**`terraform.tfvars` (DEV):**
```hcl
db_admin_username = "dbadmin"
db_admin_password = "DevPassword123!"  # Min 8 znaków

# Generuj: openssl rand -hex 32
secret_key = "dev-secret-key-change-this-32-chars-minimum"

# Opcjonalnie: IP do dostępu do bazy
developer_ips = ["1.2.3.4"]  # Twoje IP
```

#### Production
```bash
cd terraform/environments/prod

cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

**`terraform.tfvars` (PROD):**
```hcl
db_admin_username = "dbadmin"
db_admin_password = "SILNE-HASLO-MIN-16-CHARS!"  # Min 16 znaków!

# Generuj: openssl rand -hex 32
secret_key = "prod-unique-secret-key-64-chars-recommended"
```

**Generowanie bezpiecznych wartości:**
```bash
# SECRET_KEY (hex, 64 znaki dla prod)
openssl rand -hex 32

# DB Password (base64, ~24 znaki)
openssl rand -base64 24
```

---

### Krok 2: Wdrożenie Development

```bash
cd terraform/environments/dev

# Inicjalizacja
terraform init

# Sprawdź co zostanie utworzone
terraform plan

# Wdróż (potwierdź: yes)
terraform apply

# Zapisz outputs
terraform output > dev-outputs.txt
terraform output -raw connection_string > dev-db-connection.txt
```

**Co zostanie utworzone:**
- Resource Group: `timeoff-manager-rg-dev`
- App Service Plan: `timeoff-manager-plan-dev`
- App Service: `timeoff-manager-dev`
- PostgreSQL Server: `timeoff-manager-db-dev`
- PostgreSQL Database: `timeoffdb`
- Firewall rules

**Czas:** ~10-15 minut

---

### Krok 3: Konfiguracja Development

```bash
# Pobierz URL aplikacji
DEV_URL=$(terraform output -raw app_service_url)
echo "DEV URL: $DEV_URL"

# Start Azure services (jeśli zatrzymane)
az webapp start -n timeoff-manager-dev -g timeoff-manager-rg-dev
az postgres flexible-server start -n timeoff-manager-db-dev -g timeoff-manager-rg-dev

# Test health check
curl $DEV_URL/health
```

---

### Krok 4: Wdrożenie Production

```bash
cd terraform/environments/prod

# Inicjalizacja
terraform init

# Plan - SPRAWDŹ DOKŁADNIE!
terraform plan

# Wdróż (OSTROŻNIE!)
terraform apply

# Zapisz outputs
terraform output > prod-outputs.txt
terraform output -raw connection_string > prod-db-connection.txt
terraform output -raw application_insights_key > prod-insights-key.txt
```

**Co zostanie utworzone:**
- Resource Group: `timeoff-manager-rg-prod`
- App Service Plan: `timeoff-manager-plan-prod`
- App Service: `timeoff-manager-prod` + staging slot
- PostgreSQL Server: `timeoff-manager-db-prod` (HA)
- PostgreSQL Database: `timeoffdb`
- Application Insights
- Azure Key Vault
- Firewall rules

**Czas:** ~20-30 minut (HA database trwa dłużej)

---

### Krok 5: Inicjalizacja bazy danych

```bash
# Development
cd /home/radek/timeoff-manager
export DATABASE_URL="postgresql://dbadmin:password@timeoff-manager-db-dev.postgres.database.azure.com:5432/timeoffdb?sslmode=require"
export SECRET_KEY="dev-secret-key"
python3 init_db.py

# Production
export DATABASE_URL="postgresql://dbadmin:password@timeoff-manager-db-prod.postgres.database.azure.com:5432/timeoffdb?sslmode=require"
export SECRET_KEY="prod-secret-key"
python3 clear_prod_data.py  # Czyści testowe dane
# Następnie utwórz admina produkcyjnego
```

---

### Krok 6: Deployment aplikacji

#### Opcja A: GitHub Actions (zalecane)

```bash
# 1. Pobierz publish profiles z Azure
az webapp deployment list-publishing-profiles \
  -n timeoff-manager-dev \
  -g timeoff-manager-rg-dev \
  --xml > dev-publish-profile.xml

az webapp deployment list-publishing-profiles \
  -n timeoff-manager-prod \
  -g timeoff-manager-rg-prod \
  --xml > prod-publish-profile.xml

# 2. Dodaj jako GitHub Secrets
# Settings → Secrets → Actions → New repository secret
# AZURE_WEBAPP_PUBLISH_PROFILE_DEV = <zawartość dev-publish-profile.xml>
# AZURE_WEBAPP_PUBLISH_PROFILE_PROD = <zawartość prod-publish-profile.xml>

# 3. Push do GitHub → automatyczny deployment!
```

#### Opcja B: Manualne wdrożenie

```bash
# Development
cd /home/radek/timeoff-manager
zip -r deploy.zip . -x "*.git*" -x "*__pycache__*" -x "venv/*" -x ".env"

az webapp deployment source config-zip \
  -g timeoff-manager-rg-dev \
  -n timeoff-manager-dev \
  --src deploy.zip

# Production
az webapp deployment source config-zip \
  -g timeoff-manager-rg-prod \
  -n timeoff-manager-prod \
  --src deploy.zip
```

---

## 🔄 Proces DEV → PROD

### 1. Development & Testing

```bash
# Developer lokalnie
git checkout -b feature/nowa-funkcja
# ... kodowanie ...
git commit -m "feat: nowa funkcja"
git push origin feature/nowa-funkcja

# Create Pull Request → develop branch
# Merge → automatyczny deploy do DEV
```

### 2. Testowanie w DEV

```bash
# DEV URL
https://timeoff-manager-dev.azurewebsites.net

# Testy:
# - Funkcjonalne
# - Regresyjne
# - Integracyjne

# Jeśli OK → Merge do master
```

### 3. Release do PRODUCTION

```bash
# Merge develop → master
git checkout master
git merge develop
git tag -a v1.2.0 -m "Release 1.2.0"
git push origin master --tags

# GitHub Actions → automatyczny deploy do PROD
```

---

## 💰 Zarządzanie kosztami

### Zatrzymywanie DEV po godzinach

```bash
# Stop DEV (wieczorem)
az webapp stop -n timeoff-manager-dev -g timeoff-manager-rg-dev
az postgres flexible-server stop -n timeoff-manager-db-dev -g timeoff-manager-rg-dev

# Start DEV (rano)
az webapp start -n timeoff-manager-dev -g timeoff-manager-rg-dev
az postgres flexible-server start -n timeoff-manager-db-dev -g timeoff-manager-rg-dev
```

**Skrypt automatyczny** (`scripts/dev-schedule.sh`):
```bash
#!/bin/bash
# Zatrzymaj DEV o 18:00, uruchom o 8:00

HOUR=$(date +%H)

if [ $HOUR -ge 18 ] || [ $HOUR -lt 8 ]; then
    echo "Stopping DEV..."
    az webapp stop -n timeoff-manager-dev -g timeoff-manager-rg-dev
    az postgres flexible-server stop -n timeoff-manager-db-dev -g timeoff-manager-rg-dev
else
    echo "Starting DEV..."
    az webapp start -n timeoff-manager-dev -g timeoff-manager-rg-dev
    az postgres flexible-server start -n timeoff-manager-db-dev -g timeoff-manager-rg-dev
fi
```

**Oszczędność:** ~50% kosztów DEV (~$20/m zamiast $40/m)

---

## 🔧 Aktualizacja infrastruktury

### Skalowanie App Service

```hcl
# environments/prod/main.tf
module "app_service" {
  sku_name = "P2v2"  # Zmień z P1v2 na P2v2
}
```

```bash
terraform plan
terraform apply
```

### Zwiększenie storage bazy

```hcl
module "database" {
  storage_mb = 262144  # 256 GB (było 128 GB)
}
```

---

## 🗑️ Usuwanie środowisk

### Usuń Development

```bash
cd terraform/environments/dev
terraform destroy
# Potwierdź: yes
```

### Usuń Production (OSTROŻNIE!)

```bash
cd terraform/environments/prod
terraform destroy
# Potwierdź: yes
```

**UWAGA:** To usunie WSZYSTKIE zasoby i DANE!

---

## 📊 Monitorowanie

### Application Insights (PROD)

```bash
# Pobierz Instrumentation Key
cd terraform/environments/prod
terraform output -raw application_insights_key

# Dodaj do App Service
az webapp config appsettings set \
  -g timeoff-manager-rg-prod \
  -n timeoff-manager-prod \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="<key>"
```

### Logi aplikacji

```bash
# DEV
az webapp log tail -n timeoff-manager-dev -g timeoff-manager-rg-dev

# PROD
az webapp log tail -n timeoff-manager-prod -g timeoff-manager-rg-prod
```

---

## 🔐 Remote State (zalecane dla zespołów)

### Konfiguracja

```bash
# 1. Utwórz Storage Account dla Terraform state
az group create -n terraform-state-rg -l westeurope

az storage account create \
  -n tfstate$RANDOM \
  -g terraform-state-rg \
  -l westeurope \
  --sku Standard_LRS

az storage container create \
  -n tfstate \
  --account-name <nazwa-z-poprzedniego-kroku>

# 2. Odkomentuj backend w main.tf
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfstate..."
    container_name       = "tfstate"
    key                  = "timeoff-manager-prod.tfstate"
  }
}

# 3. Migruj stan
terraform init -migrate-state
```

---

## 🆘 Troubleshooting

### Problem: "Resource already exists"

```bash
# Import istniejącego zasobu
terraform import azurerm_resource_group.main /subscriptions/.../resourceGroups/nazwa
```

### Problem: Błąd połączenia z bazą

```bash
# Sprawdź firewall rules
az postgres flexible-server firewall-rule list \
  -g timeoff-manager-rg-dev \
  -n timeoff-manager-db-dev

# Dodaj swoje IP
az postgres flexible-server firewall-rule create \
  -g timeoff-manager-rg-dev \
  -n timeoff-manager-db-dev \
  -r AllowMyIP \
  --start-ip-address <twoje-ip> \
  --end-ip-address <twoje-ip>
```

### Problem: App Service nie działa

```bash
# Sprawdź logi
az webapp log tail -n <app-name> -g <rg-name>

# Restart
az webapp restart -n <app-name> -g <rg-name>

# Sprawdź zmienne środowiskowe
az webapp config appsettings list -n <app-name> -g <rg-name>
```

---

## 📚 Dodatkowa dokumentacja

- [DEPLOYMENT-GUIDE.md](../DEPLOYMENT-GUIDE.md) - Przewodnik wdrożenia aplikacji
- [PRODUCTION-DEPLOYMENT-GUIDE.md](../PRODUCTION-DEPLOYMENT-GUIDE.md) - Przygotowanie do produkcji
- [TECHNICAL-DOCS.md](../TECHNICAL-DOCS.md) - Dokumentacja techniczna

---

## 💡 Tips & Best Practices

1. **Zawsze testuj w DEV przed PROD**
2. **Używaj tagów Git dla release** (v1.0.0, v1.1.0)
3. **Backup produkcyjnej bazy przed update**
4. **Monitoruj koszty** (Azure Cost Management)
5. **Zatrzymuj DEV po godzinach**
6. **Używaj Remote State dla zespołów**
7. **Dokumentuj każdą zmianę infrastruktury**

---

**Ostatnia aktualizacja:** 2025-10-05
**Wersja:** 2.0 (2 środowiska)
