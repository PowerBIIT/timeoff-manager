#!/bin/bash

# TimeOff Manager - Azure Deployment Script
# Automatyczny deployment aplikacji na Azure

# Kolory dla output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   TimeOff Manager - Azure Deployment        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
echo

# Konfiguracja - EDYTUJ TE WARTOŚCI PRZED DEPLOYMENTEM!
RESOURCE_GROUP="${RESOURCE_GROUP:-timeoff-rg-prod}"
LOCATION="${LOCATION:-westeurope}"
APP_NAME="${APP_NAME:-timeoff-manager-$(date +%Y%m%d)}"
DB_SERVER="${DB_SERVER:-timeoff-db-$(date +%Y%m%d)}"
DB_NAME="${DB_NAME:-timeoffdb}"
DB_ADMIN="${DB_ADMIN:-dbadmin}"

# WAŻNE: Ustaw silne hasło do bazy danych!
# Możesz przekazać przez zmienną środowiskową: export DB_PASSWORD="YourStrongPassword"
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}❌ BŁĄD: Brak hasła do bazy danych!${NC}"
    echo -e "${YELLOW}Ustaw zmienną: export DB_PASSWORD=\"YourStrongPassword\"${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  UWAGA: Sprawdź konfigurację przed deploymentem!${NC}"
echo -e "Resource Group: ${GREEN}$RESOURCE_GROUP${NC}"
echo -e "Location: ${GREEN}$LOCATION${NC}"
echo -e "App Name: ${GREEN}$APP_NAME${NC}"
echo -e "DB Server: ${GREEN}$DB_SERVER${NC}"
echo
read -p "Kontynuować deployment? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo -e "${RED}Deployment anulowany${NC}"
    exit 1
fi

# Check if Azure CLI is installed
if ! command -v az &> /dev/null
then
    echo -e "${RED}❌ Azure CLI nie jest zainstalowane!${NC}"
    echo "Zainstaluj: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login check
echo -e "${GREEN}1. Sprawdzanie logowania do Azure...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Nie jesteś zalogowany. Logowanie...${NC}"
    az login
fi

# Create Resource Group
echo -e "${GREEN}2. Tworzenie Resource Group...${NC}"
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION \
  --output table

# Create PostgreSQL Server
echo -e "${GREEN}3. Tworzenie PostgreSQL Flexible Server...${NC}"
echo -e "${YELLOW}   To może potrwać kilka minut...${NC}"
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER \
  --location $LOCATION \
  --admin-user $DB_ADMIN \
  --admin-password $DB_PASSWORD \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 14 \
  --storage-size 32 \
  --public-access 0.0.0.0 \
  --output table

# Create database
echo -e "${GREEN}4. Tworzenie bazy danych...${NC}"
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_SERVER \
  --database-name $DB_NAME \
  --output table

# Configure firewall
echo -e "${GREEN}5. Konfiguracja firewall PostgreSQL...${NC}"
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0 \
  --output table

# Generate SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)

# Build DATABASE_URL
DATABASE_URL="postgresql://$DB_ADMIN:$DB_PASSWORD@$DB_SERVER.postgres.database.azure.com/$DB_NAME?sslmode=require"

# Deploy Web App
echo -e "${GREEN}6. Deployowanie Web App...${NC}"
az webapp up \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --runtime "PYTHON:3.11" \
  --sku B1 \
  --location $LOCATION \
  --output table

# Configure environment variables
echo -e "${GREEN}7. Konfiguracja zmiennych środowiskowych...${NC}"
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
    DATABASE_URL="$DATABASE_URL" \
    SECRET_KEY="$SECRET_KEY" \
    FLASK_ENV="production" \
    APP_NAME="$APP_NAME" \
  --output table

# Configure startup command
echo -e "${GREEN}8. Konfiguracja startup command...${NC}"
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --startup-file "startup.sh" \
  --output table

# Enable application logs
echo -e "${GREEN}9. Włączanie logów aplikacji...${NC}"
az webapp log config \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --application-logging filesystem \
  --detailed-error-messages true \
  --failed-request-tracing true \
  --web-server-logging filesystem \
  --output table

# Enable HTTPS only
echo -e "${GREEN}10. Wymuszanie HTTPS...${NC}"
az webapp update \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --https-only true \
  --output table

# Configure custom domain (optional - can be done later)
echo -e "${GREEN}11. Konfiguracja domeny...${NC}"
echo -e "${YELLOW}   Możesz dodać własną domenę później przez Azure Portal${NC}"

# Restart app to apply changes
echo -e "${GREEN}12. Restart aplikacji...${NC}"
az webapp restart \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --output table

echo
echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║            DEPLOYMENT COMPLETE!              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
echo
echo -e "${GREEN}✅ Aplikacja wdrożona pomyślnie!${NC}"
echo
echo -e "${GREEN}📋 Informacje o deploymencie:${NC}"
echo -e "   URL aplikacji: ${BLUE}https://$APP_NAME.azurewebsites.net${NC}"
echo -e "   Resource Group: ${BLUE}$RESOURCE_GROUP${NC}"
echo -e "   Database Server: ${BLUE}$DB_SERVER.postgres.database.azure.com${NC}"
echo
echo -e "${GREEN}👤 Domyślne konta testowe:${NC}"
echo -e "   Admin:     ${YELLOW}admin@firma.pl${NC} / ${YELLOW}admin123${NC}"
echo -e "   Manager:   ${YELLOW}manager@firma.pl${NC} / ${YELLOW}manager123${NC}"
echo -e "   Employee:  ${YELLOW}jan@firma.pl${NC} / ${YELLOW}jan123${NC}"
echo
echo -e "${GREEN}📝 Następne kroki:${NC}"
echo "   1. Otwórz aplikację w przeglądarce"
echo "   2. Zaloguj się jako admin"
echo "   3. Zmień hasło admina"
echo "   4. Skonfiguruj SMTP w ustawieniach (dla powiadomień email)"
echo "   5. Dodaj użytkowników"
echo
echo -e "${YELLOW}📊 Sprawdź logi:${NC}"
echo "   az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"
echo
echo -e "${YELLOW}🗑️  Usuń zasoby (jeśli potrzeba):${NC}"
echo "   az group delete --name $RESOURCE_GROUP --yes"
echo
