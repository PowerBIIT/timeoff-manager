#!/bin/bash
# Wdrożenie DEV environment na obecnej subskrypcji
# Szybkie wdrożenie bez Terraform

set -e

echo "🚀 Wdrażanie DEV environment..."
echo "================================"
echo ""

# Zmienne
RG_NAME="timeoff-manager-rg-dev"
LOCATION="westeurope"
APP_NAME="timeoff-manager-dev"
DB_NAME="timeoff-db-dev"
DB_ADMIN="dbadmin"
DB_PASSWORD="Vcte9IKmHO+80QvRS3HFIg=="
SECRET_KEY="106e600452304fd169651b2451eca236f7e04ad728f419040738a57bc03b3d47"

# Krok 1: Resource Group
echo "📦 Krok 1/5: Tworzenie Resource Group..."
az group create \
  --name $RG_NAME \
  --location $LOCATION \
  --tags Environment=Development Project=TimeOffManager ManagedBy=AzureCLI
echo "✅ Resource Group created"
echo ""

# Krok 2: PostgreSQL Database
echo "🗄️  Krok 2/5: Tworzenie PostgreSQL Database (B_Standard_B1ms)..."
echo "   ⏳ To może potrwać 5-10 minut..."
az postgres flexible-server create \
  --resource-group $RG_NAME \
  --name $DB_NAME \
  --location $LOCATION \
  --admin-user $DB_ADMIN \
  --admin-password "$DB_PASSWORD" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 13 \
  --storage-size 32 \
  --backup-retention 7 \
  --yes

# Firewall rule - Azure services
az postgres flexible-server firewall-rule create \
  --resource-group $RG_NAME \
  --name $DB_NAME \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Create database
az postgres flexible-server db create \
  --resource-group $RG_NAME \
  --server-name $DB_NAME \
  --database-name timeoffdb

echo "✅ PostgreSQL Database created"
echo ""

# Krok 3: App Service Plan
echo "📱 Krok 3/5: Tworzenie App Service Plan (B1)..."
az appservice plan create \
  --resource-group $RG_NAME \
  --name ${APP_NAME}-plan \
  --location $LOCATION \
  --sku B1 \
  --is-linux

echo "✅ App Service Plan created"
echo ""

# Krok 4: Web App
echo "🌐 Krok 4/5: Tworzenie Web App..."
az webapp create \
  --resource-group $RG_NAME \
  --plan ${APP_NAME}-plan \
  --name $APP_NAME \
  --runtime "PYTHON:3.9"

# Configure App Settings
DB_HOST="${DB_NAME}.postgres.database.azure.com"
CONNECTION_STRING="postgresql://${DB_ADMIN}:${DB_PASSWORD}@${DB_HOST}:5432/timeoffdb?sslmode=require"

az webapp config appsettings set \
  --resource-group $RG_NAME \
  --name $APP_NAME \
  --settings \
    FLASK_ENV=development \
    DATABASE_URL="$CONNECTION_STRING" \
    SECRET_KEY="$SECRET_KEY" \
    APP_NAME="$APP_NAME" \
    PYTHON_VERSION=3.9 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true

echo "✅ Web App created and configured"
echo ""

# Krok 5: Outputs
echo "📊 Krok 5/5: Podsumowanie..."
echo ""
echo "✅ DEV Environment utworzony pomyślnie!"
echo "================================"
echo ""
echo "📋 Informacje:"
echo "   Resource Group: $RG_NAME"
echo "   App Service: $APP_NAME"
echo "   PostgreSQL: $DB_NAME"
echo ""
echo "🔗 URL: https://${APP_NAME}.azurewebsites.net"
echo ""
echo "🗄️  Database:"
echo "   Host: $DB_HOST"
echo "   Database: timeoffdb"
echo "   User: $DB_ADMIN"
echo ""
echo "📝 Następne kroki:"
echo "1. Pobierz publish profile:"
echo "   az webapp deployment list-publishing-profiles -n $APP_NAME -g $RG_NAME --xml > dev-publish-profile.xml"
echo ""
echo "2. Dodaj jako GitHub Secret: AZURE_WEBAPP_PUBLISH_PROFILE_DEV"
echo ""
echo "3. Utwórz branch develop i push → auto-deploy!"
echo ""
echo "💰 Koszt: ~\$40/m (lub \$20/m z auto-stop)"
echo ""
