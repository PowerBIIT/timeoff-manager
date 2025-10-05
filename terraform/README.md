# TimeOff Manager - Infrastructure as Code (Terraform)

Pełna infrastruktura Azure dla trzech środowisk: Development, Staging, Production.

---

## 📁 Struktura projektu

```
terraform/
├── main.tf                      # Główna konfiguracja Terraform
├── variables.tf                 # Zmienne globalne
├── modules/                     # Moduły reużywalne
│   ├── app-service/            # Azure App Service + Plan
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── database/               # PostgreSQL Flexible Server
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── environments/               # Konfiguracje per środowisko
    ├── dev/                   # Development
    │   ├── main.tf
    │   ├── variables.tf
    │   ├── outputs.tf
    │   └── terraform.tfvars.example
    ├── staging/               # Staging/Pre-production
    │   ├── main.tf
    │   ├── variables.tf
    │   ├── outputs.tf
    │   └── terraform.tfvars.example
    └── prod/                  # Production
        ├── main.tf
        ├── variables.tf
        ├── outputs.tf
        └── terraform.tfvars.example
```

---

## 🌍 Środowiska

### Development
- **App Service**: B1 (Basic tier)
- **Database**: B_Standard_B1ms (Burstable, 1 vCore, 2GB RAM)
- **Storage**: 32 GB
- **Backup**: 7 dni, bez geo-redundancji
- **HA**: Wyłączone
- **Koszt**: ~$50-70/miesiąc

### Staging
- **App Service**: S1 (Standard tier)
- **Database**: GP_Standard_D2s_v3 (2 vCores, 8GB RAM)
- **Storage**: 64 GB
- **Backup**: 14 dni, z geo-redundancją
- **HA**: Wyłączone
- **Koszt**: ~$200-250/miesiąc

### Production
- **App Service**: P1v2 (Premium tier)
- **Database**: GP_Standard_D4s_v3 (4 vCores, 16GB RAM)
- **Storage**: 128 GB
- **Backup**: 35 dni, z geo-redundancją
- **HA**: Włączone (Zone-redundant)
- **Monitoring**: Application Insights
- **Security**: Azure Key Vault
- **Deployment**: Blue-green (staging slot)
- **Koszt**: ~$600-800/miesiąc

---

## 🚀 Instalacja i użycie

### Wymagania

```bash
# Terraform
terraform --version  # >= 1.0

# Azure CLI
az --version        # >= 2.0
az login
```

### Krok 1: Przygotowanie zmiennych

```bash
# Wybierz środowisko (dev/staging/prod)
cd terraform/environments/dev

# Skopiuj przykładowy plik
cp terraform.tfvars.example terraform.tfvars

# Edytuj wartości
nano terraform.tfvars
```

**Ważne zmienne:**
```hcl
db_admin_password = "SilneHaslo123!"        # Min 16 znaków dla prod
secret_key        = "generuj-openssl-rand"   # Min 32 znaki dla prod
```

**Generowanie bezpiecznych wartości:**
```bash
# SECRET_KEY (hex, 32 znaki)
openssl rand -hex 32

# DB Password (base64, ~24 znaki)
openssl rand -base64 24
```

### Krok 2: Inicjalizacja Terraform

```bash
# Wewnątrz environments/dev (lub staging/prod)
terraform init
```

### Krok 3: Plan zmian

```bash
terraform plan
```

Sprawdź co zostanie utworzone:
- Resource Group
- PostgreSQL Flexible Server
- PostgreSQL Database
- App Service Plan
- App Service (Web App)
- Firewall rules
- (prod) Application Insights
- (prod) Key Vault

### Krok 4: Wdrożenie

```bash
terraform apply

# Potwierdź: yes
```

### Krok 5: Pobierz dane wyjściowe

```bash
# URL aplikacji
terraform output app_service_url

# Connection string (sensitive)
terraform output -raw connection_string

# Wszystkie outputy
terraform output
```

---

## 📊 Zarządzanie wieloma środowiskami

### Wdrożenie wszystkich środowisk

```bash
# Development
cd terraform/environments/dev
terraform init
terraform apply

# Staging
cd ../staging
terraform init
terraform apply

# Production
cd ../prod
terraform init
terraform apply
```

### Praca z konkretnym środowiskiem

```bash
# Zawsze pracuj z katalogu środowiska
cd terraform/environments/prod

# Zobacz stan
terraform state list

# Zaktualizuj infrastrukturę
terraform apply

# Usuń środowisko (OSTROŻNIE!)
terraform destroy
```

---

## 🔐 Bezpieczeństwo

### Wrażliwe pliki (dodane do .gitignore)

```
terraform.tfvars         # Sekrety per środowisko
*.tfstate               # Stan Terraform
*.tfstate.backup
.terraform/             # Provider plugins
```

### Remote State (zalecane dla produkcji)

```bash
# 1. Utwórz Storage Account dla state
az group create -n terraform-state-rg -l westeurope
az storage account create -n tfstate$RANDOM -g terraform-state-rg -l westeurope --sku Standard_LRS
az storage container create -n tfstate --account-name <nazwa>

# 2. Odkomentuj backend w prod/main.tf
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

## 📝 Typowe operacje

### Skalowanie App Service

```hcl
# W environments/prod/main.tf
module "app_service" {
  sku_name = "P2v2"  # Zmień z P1v2 na P2v2
}
```

```bash
terraform apply
```

### Zwiększenie storage bazy danych

```hcl
# W environments/prod/main.tf
module "database" {
  storage_mb = 262144  # 256 GB (było 128 GB)
}
```

### Dodanie IP do firewall

```hcl
# W environments/dev/main.tf
module "database" {
  allowed_ip_addresses = ["1.2.3.4", "5.6.7.8"]
}
```

---

## 🔄 CI/CD Integration

### GitHub Actions z Terraform

```yaml
# .github/workflows/terraform.yml
name: Terraform Production Deploy

on:
  push:
    branches: [main]
    paths: ['terraform/**']

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: hashicorp/setup-terraform@v2

      - name: Terraform Init
        run: terraform init
        working-directory: terraform/environments/prod

      - name: Terraform Plan
        run: terraform plan
        env:
          TF_VAR_db_admin_password: ${{ secrets.DB_PASSWORD }}
          TF_VAR_secret_key: ${{ secrets.SECRET_KEY }}

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main'
        run: terraform apply -auto-approve
```

---

## 🛠️ Troubleshooting

### Problem: "Resource already exists"

```bash
# Import istniejącego zasobu
terraform import azurerm_resource_group.main /subscriptions/.../resourceGroups/nazwa
```

### Problem: "Backend initialization failed"

```bash
# Usuń lokalny state i ponów init
rm -rf .terraform
terraform init
```

### Problem: "Invalid credentials"

```bash
# Zaloguj ponownie do Azure
az login
az account set --subscription "nazwa-subskrypcji"
```

---

## 💰 Szacunkowe koszty (miesięcznie)

| Środowisko | App Service | Database | Storage | Backup | **Total** |
|-----------|------------|----------|---------|--------|-----------|
| Dev       | $13        | $25      | $2      | -      | **~$40**  |
| Staging   | $73        | $140     | $5      | $10    | **~$230** |
| Production| $170       | $360     | $10     | $25    | **~$565** |

*Ceny orientacyjne (West Europe, 2025)*

### Optymalizacja kosztów

1. **Dev**: Zatrzymuj po godzinach
```bash
az webapp stop -n timeoff-manager-dev -g timeoff-manager-rg-dev
az postgres flexible-server stop -n timeoff-manager-db-dev -g timeoff-manager-rg-dev
```

2. **Staging**: Używaj tylko przed release
3. **Production**: Reserved instances (-30%)

---

## 📚 Dokumentacja

- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure App Service Pricing](https://azure.microsoft.com/pricing/details/app-service/)
- [Azure PostgreSQL Pricing](https://azure.microsoft.com/pricing/details/postgresql/)
- [Best Practices](https://learn.microsoft.com/azure/well-architected/)

---

## 🆘 Wsparcie

Issues: https://github.com/PowerBIIT/timeoff-manager/issues
Docs: ../TECHNICAL-DOCS.md

**Ostatnia aktualizacja:** 2025-10-05
