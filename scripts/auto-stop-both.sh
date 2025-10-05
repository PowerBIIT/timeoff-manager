#!/bin/bash
# Automatyczne zatrzymywanie/uruchamianie OBUICH środowisk (DEV + PROD)
# Oszczędza koszty kiedy środowiska nie są używane
#
# Użycie: ./auto-stop-both.sh
# Cron: 0 * * * * /path/to/auto-stop-both.sh >> /var/log/auto-stop.log 2>&1

set -e

# Konfiguracja
DEV_RG="timeoff-manager-rg-dev"
DEV_APP="timeoff-manager-dev"
DEV_DB="timeoff-db-dev"

PROD_RG="timeoff-rg-prod"
PROD_APP="timeoff-manager-20251004"
PROD_DB="timeoff-db-20251004"

# Godziny działania: 8:00 - 18:00 (tylko w tygodniu roboczym)
HOUR=$(date +%H)
DAY=$(date +%u)  # 1=Poniedziałek, 7=Niedziela

echo "$(date '+%Y-%m-%d %H:%M:%S') - Checking environments..."
echo "  Hour: $HOUR, Day: $DAY (1=Mon, 7=Sun)"

# Warunek zatrzymania: po 18:00 LUB przed 8:00 LUB weekend
if [ $HOUR -ge 18 ] || [ $HOUR -lt 8 ] || [ $DAY -ge 6 ]; then
    echo "🌙 Outside working hours - STOPPING both environments..."

    # Stop DEV
    echo "  Stopping DEV..."
    az webapp stop --name $DEV_APP --resource-group $DEV_RG 2>/dev/null || echo "    DEV App already stopped or not exists"
    az postgres flexible-server stop --name $DEV_DB --resource-group $DEV_RG 2>/dev/null || echo "    DEV DB already stopped or not exists"

    # Stop PROD
    echo "  Stopping PROD..."
    az webapp stop --name $PROD_APP --resource-group $PROD_RG 2>/dev/null || echo "    PROD App already stopped"
    az postgres flexible-server stop --name $PROD_DB --resource-group $PROD_RG 2>/dev/null || echo "    PROD DB already stopped"

    echo "✅ Both environments STOPPED"
    echo "💰 Saving: ~\$1.50/hour (~\$300/month)"

else
    echo "☀️ Working hours - STARTING both environments..."

    # Start DEV Database first
    echo "  Starting DEV DB..."
    az postgres flexible-server start --name $DEV_DB --resource-group $DEV_RG 2>/dev/null || echo "    DEV DB already running or not exists"

    # Start PROD Database first
    echo "  Starting PROD DB..."
    az postgres flexible-server start --name $PROD_DB --resource-group $PROD_RG 2>/dev/null || echo "    PROD DB already running"

    # Wait for databases
    echo "  Waiting 30s for databases..."
    sleep 30

    # Start DEV App
    echo "  Starting DEV App..."
    az webapp start --name $DEV_APP --resource-group $DEV_RG 2>/dev/null || echo "    DEV App already running or not exists"

    # Start PROD App
    echo "  Starting PROD App..."
    az webapp start --name $PROD_APP --resource-group $PROD_RG 2>/dev/null || echo "    PROD App already running"

    echo "✅ Both environments RUNNING"
    echo "🚀 DEV: https://$DEV_APP.azurewebsites.net"
    echo "🚀 PROD: https://$PROD_APP.azurewebsites.net"
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') - Done!"
echo "---"
