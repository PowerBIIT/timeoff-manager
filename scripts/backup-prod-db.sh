#!/bin/bash
# Backup bazy PROD przed migracją
# Użycie: ./scripts/backup-prod-db.sh

set -e

PROD_DB="timeoff-db-20251004"
PROD_RG="timeoff-rg-prod"
BACKUP_NAME="manual-backup-$(date +%Y%m%d-%H%M%S)"

echo "💾 BACKUP BAZY PROD"
echo "==================="
echo ""
echo "Database: $PROD_DB"
echo "Backup name: $BACKUP_NAME"
echo ""

# Sprawdź czy baza działa
DB_STATE=$(az postgres flexible-server show -n $PROD_DB -g $PROD_RG --query state -o tsv 2>/dev/null || echo "NotFound")

if [ "$DB_STATE" != "Ready" ]; then
    echo "❌ Baza nie jest gotowa (status: $DB_STATE)"
    echo "   Uruchom najpierw: ./scripts/production-mode.sh"
    exit 1
fi

echo "🔄 Tworzenie backupu..."
echo ""

# Azure automatic backup
az postgres flexible-server backup create \
    --resource-group $PROD_RG \
    --name $PROD_DB \
    --backup-name $BACKUP_NAME

echo ""
echo "✅ Backup utworzony: $BACKUP_NAME"
echo ""
echo "📋 Lista backupów:"
az postgres flexible-server backup list \
    --resource-group $PROD_RG \
    --server-name $PROD_DB \
    --query "[].{Name:name, CreatedAt:completedTime}" \
    -o table

echo ""
echo "💡 Restore z backupu (jeśli potrzeba):"
echo "   az postgres flexible-server restore \\"
echo "     --resource-group $PROD_RG \\"
echo "     --name timeoff-db-restored \\"
echo "     --source-server $PROD_DB \\"
echo "     --restore-time \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""
echo ""
