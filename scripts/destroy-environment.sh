#!/bin/bash
# Usuwa kompletne środowisko Azure za pomocą Terraform
#
# UWAGA: To usunie WSZYSTKIE zasoby i DANE!
# Użycie: ./destroy-environment.sh [dev|prod]

set -e

ENV=${1:-}

if [ -z "$ENV" ]; then
    echo "❌ Błąd: Podaj środowisko do usunięcia"
    echo "Użycie: ./destroy-environment.sh [dev|prod]"
    exit 1
fi

if [ "$ENV" != "dev" ] && [ "$ENV" != "prod" ]; then
    echo "❌ Błąd: Nieprawidłowe środowisko: $ENV"
    echo "Dozwolone: dev lub prod"
    exit 1
fi

echo "⚠️  ⚠️  ⚠️  OSTRZEŻENIE ⚠️  ⚠️  ⚠️"
echo "=================================================="
echo "To usunie KOMPLETNE środowisko: $ENV"
echo ""
echo "Zostaną usunięte:"
echo "  - Resource Group: timeoff-manager-rg-$ENV"
echo "  - App Service: timeoff-manager-$ENV"
echo "  - PostgreSQL Database: timeoff-manager-db-$ENV"
if [ "$ENV" == "prod" ]; then
    echo "  - Application Insights"
    echo "  - Azure Key Vault"
fi
echo ""
echo "❌ WSZYSTKIE DANE ZOSTANĄ UTRACONE!"
echo "❌ OPERACJA NIEODWRACALNA!"
echo ""
echo "=================================================="
echo ""

# Triple confirmation dla PROD
if [ "$ENV" == "prod" ]; then
    read -p "Czy NA PEWNO usunąć PRODUCTION? Wpisz 'DESTROY PRODUCTION': " CONFIRM1
    if [ "$CONFIRM1" != "DESTROY PRODUCTION" ]; then
        echo "❌ Anulowano"
        exit 0
    fi

    read -p "Ostatnia szansa! Wpisz nazwę środowiska ($ENV): " CONFIRM2
    if [ "$CONFIRM2" != "$ENV" ]; then
        echo "❌ Anulowano"
        exit 0
    fi
fi

# Single confirmation dla DEV
if [ "$ENV" == "dev" ]; then
    read -p "Czy usunąć DEV environment? Wpisz 'yes': " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo "❌ Anulowano"
        exit 0
    fi
fi

echo ""
echo "🗑️  Usuwanie środowiska $ENV..."
echo ""

cd terraform/environments/$ENV

# Terraform Destroy
terraform destroy -auto-approve

echo ""
echo "✅ Środowisko $ENV zostało usunięte"
echo ""
echo "Opcjonalnie: Usuń pliki konfiguracyjne:"
echo "  rm -f terraform.tfvars"
echo "  rm -f ${ENV}-outputs.txt"
echo "  rm -f ${ENV}-db-connection.txt"
echo "  rm -f .terraform.lock.hcl"
echo "  rm -rf .terraform/"
echo ""
