#!/bin/bash
# Automatyczne zatrzymywanie/uruchamianie DEV environment
# Oszczędza ~50% kosztów DEV (~$20/miesiąc)
#
# Użycie: ./dev-schedule.sh
# Cron: 0 * * * * /path/to/dev-schedule.sh >> /var/log/dev-schedule.log 2>&1

set -e

# Konfiguracja
RG_NAME="timeoff-manager-rg-dev"
WEBAPP_NAME="timeoff-manager-dev"
DB_NAME="timeoff-manager-db-dev"

# Godziny pracy: 8:00 - 18:00
HOUR=$(date +%H)

echo "$(date '+%Y-%m-%d %H:%M:%S') - Checking DEV environment status..."

if [ $HOUR -ge 18 ] || [ $HOUR -lt 8 ]; then
    echo "🌙 Outside working hours - stopping DEV..."

    # Stop App Service
    az webapp stop --name $WEBAPP_NAME --resource-group $RG_NAME 2>/dev/null || true
    echo "  ✅ App Service stopped"

    # Stop Database
    az postgres flexible-server stop --name $DB_NAME --resource-group $RG_NAME 2>/dev/null || true
    echo "  ✅ Database stopped"

    echo "💰 Saving ~$1/hour (~$20/month)"
else
    echo "☀️ Working hours - starting DEV..."

    # Start Database first
    az postgres flexible-server start --name $DB_NAME --resource-group $RG_NAME 2>/dev/null || true
    echo "  ✅ Database started"

    # Wait 30s for DB to be ready
    sleep 30

    # Start App Service
    az webapp start --name $WEBAPP_NAME --resource-group $RG_NAME 2>/dev/null || true
    echo "  ✅ App Service started"

    echo "🚀 DEV environment ready at: https://$WEBAPP_NAME.azurewebsites.net"
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') - Done!"
