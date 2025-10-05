#!/bin/bash
# Deployment do nowej subskrypcji Azure
# Wdraża kompletną infrastrukturę za pomocą Terraform
#
# Użycie: ./deploy-to-new-subscription.sh [dev|prod]

set -e

ENV=${1:-dev}

if [ "$ENV" != "dev" ] && [ "$ENV" != "prod" ]; then
    echo "❌ Błąd: Podaj środowisko: dev lub prod"
    echo "Użycie: ./deploy-to-new-subscription.sh [dev|prod]"
    exit 1
fi

echo "🚀 Deployment TimeOff Manager do środowiska: $ENV"
echo "=================================================="
echo ""

# Krok 1: Sprawdź wymagania
echo "📋 Krok 1/7: Sprawdzanie wymagań..."
command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform not installed"; exit 1; }
command -v az >/dev/null 2>&1 || { echo "❌ Azure CLI not installed"; exit 1; }
echo "✅ Terraform: $(terraform version | head -1)"
echo "✅ Azure CLI: $(az version --query '\"azure-cli\"' -o tsv)"
echo ""

# Krok 2: Login do Azure
echo "📋 Krok 2/7: Azure Login..."
az account show >/dev/null 2>&1 || az login
SUBSCRIPTION=$(az account show --query name -o tsv)
echo "✅ Zalogowany do: $SUBSCRIPTION"
echo ""

# Krok 3: Przygotowanie zmiennych
echo "📋 Krok 3/7: Przygotowanie terraform.tfvars..."
cd terraform/environments/$ENV

if [ ! -f "terraform.tfvars" ]; then
    echo "⚠️  Brak terraform.tfvars - tworzę z template..."
    cp terraform.tfvars.example terraform.tfvars

    # Generuj silne hasła
    DB_PASSWORD=$(openssl rand -base64 24)
    SECRET_KEY=$(openssl rand -hex 32)

    # Podmień w pliku
    sed -i "s/DevPassword123!/$DB_PASSWORD/" terraform.tfvars 2>/dev/null || sed -i '' "s/DevPassword123!/$DB_PASSWORD/" terraform.tfvars
    sed -i "s/dev-secret-key-change-this-32-chars-minimum/$SECRET_KEY/" terraform.tfvars 2>/dev/null || sed -i '' "s/dev-secret-key-change-this-32-chars-minimum/$SECRET_KEY/" terraform.tfvars

    echo "✅ terraform.tfvars created with generated passwords"
    echo "⚠️  ZAPISZ TE DANE BEZPIECZNIE!"
    echo ""
else
    echo "✅ terraform.tfvars already exists"
    echo ""
fi

# Krok 4: Terraform Init
echo "📋 Krok 4/7: Terraform Init..."
terraform init
echo "✅ Terraform initialized"
echo ""

# Krok 5: Terraform Plan
echo "📋 Krok 5/7: Terraform Plan..."
echo "📊 Co zostanie utworzone:"
terraform plan -out=tfplan
echo ""

# Krok 6: Potwierdzenie
echo "📋 Krok 6/7: Potwierdzenie deployment..."
echo "⚠️  To utworzy następujące zasoby Azure:"
if [ "$ENV" == "dev" ]; then
    echo "  - Resource Group: timeoff-manager-rg-dev"
    echo "  - App Service: timeoff-manager-dev (B1 tier)"
    echo "  - PostgreSQL: timeoff-manager-db-dev (B_Standard_B1ms)"
    echo "  💰 Koszt: ~\$40/miesiąc"
else
    echo "  - Resource Group: timeoff-manager-rg-prod"
    echo "  - App Service: timeoff-manager-prod (P1v2 tier)"
    echo "  - PostgreSQL: timeoff-manager-db-prod (GP_Standard_D4s_v3, HA)"
    echo "  - Application Insights"
    echo "  - Azure Key Vault"
    echo "  💰 Koszt: ~\$565/miesiąc"
fi
echo ""
read -p "Czy kontynuować? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Deployment anulowany"
    exit 0
fi

# Krok 7: Terraform Apply
echo ""
echo "📋 Krok 7/7: Terraform Apply..."
echo "⏳ To może potrwać 10-30 minut..."
terraform apply tfplan

# Zapisz outputs
terraform output > ${ENV}-outputs.txt
terraform output -raw connection_string > ${ENV}-db-connection.txt 2>/dev/null || true
terraform output -raw application_insights_key > ${ENV}-insights-key.txt 2>/dev/null || true

echo ""
echo "🎉 Deployment zakończony pomyślnie!"
echo "=================================================="
echo ""
echo "📊 Informacje o środowisku $ENV:"
cat ${ENV}-outputs.txt
echo ""
echo "📝 Następne kroki:"
echo "1. Inicjalizuj bazę danych:"
echo "   export DATABASE_URL=\$(cat ${ENV}-db-connection.txt)"
echo "   export SECRET_KEY=\$(grep secret_key terraform.tfvars | cut -d'=' -f2 | tr -d ' \"')"
if [ "$ENV" == "dev" ]; then
    echo "   python3 init_db.py"
else
    echo "   python3 clear_prod_data.py"
fi
echo ""
echo "2. Pobierz publish profile do GitHub Actions:"
echo "   az webapp deployment list-publishing-profiles -n timeoff-manager-$ENV -g timeoff-manager-rg-$ENV --xml > ${ENV}-publish-profile.xml"
echo ""
echo "3. Dodaj jako GitHub Secret:"
echo "   AZURE_WEBAPP_PUBLISH_PROFILE_$(echo $ENV | tr '[:lower:]' '[:upper:]') = <zawartość ${ENV}-publish-profile.xml>"
echo ""
echo "4. Deploy aplikacji przez Git push lub manual deployment"
echo ""
echo "✅ Gotowe!"
