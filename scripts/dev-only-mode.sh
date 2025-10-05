#!/bin/bash
# Tryb DEV-ONLY: Zatrzymaj PROD, zostaw DEV działający
# Oszczędza ~$565/m na PROD podczas developmentu
#
# Użycie: ./dev-only-mode.sh

set -e

echo "💰 DEV-ONLY MODE - Oszczędzanie na PROD"
echo "========================================"
echo ""

PROD_RG="timeoff-rg-prod"
PROD_APP="timeoff-manager-20251004"
PROD_DB="timeoff-db-20251004"

DEV_RG="timeoff-manager-rg-dev"
DEV_APP="timeoff-manager-dev"
DEV_DB="timeoff-db-dev"

echo "🔍 Sprawdzanie statusu środowisk..."
echo ""

# Status PROD
PROD_APP_STATE=$(az webapp show -n $PROD_APP -g $PROD_RG --query state -o tsv 2>/dev/null || echo "NotFound")
PROD_DB_STATE=$(az postgres flexible-server show -n $PROD_DB -g $PROD_RG --query state -o tsv 2>/dev/null || echo "NotFound")

# Status DEV
DEV_APP_STATE=$(az webapp show -n $DEV_APP -g $DEV_RG --query state -o tsv 2>/dev/null || echo "NotFound")
DEV_DB_STATE=$(az postgres flexible-server show -n $DEV_DB -g $DEV_RG --query state -o tsv 2>/dev/null || echo "NotFound")

echo "📊 Obecny status:"
echo "   PROD App: $PROD_APP_STATE"
echo "   PROD DB:  $PROD_DB_STATE"
echo "   DEV App:  $DEV_APP_STATE"
echo "   DEV DB:   $DEV_DB_STATE"
echo ""

# Zatrzymaj PROD
if [ "$PROD_APP_STATE" != "Stopped" ] && [ "$PROD_APP_STATE" != "NotFound" ]; then
    echo "🌙 Zatrzymywanie PROD App..."
    az webapp stop -n $PROD_APP -g $PROD_RG 2>/dev/null || echo "   ⚠️  Błąd zatrzymania PROD App"
    echo "   ✅ PROD App zatrzymany"
else
    echo "   ℹ️  PROD App już zatrzymany"
fi

if [ "$PROD_DB_STATE" != "Stopped" ] && [ "$PROD_DB_STATE" != "NotFound" ]; then
    echo "🌙 Zatrzymywanie PROD DB..."
    az postgres flexible-server stop -n $PROD_DB -g $PROD_RG 2>/dev/null || echo "   ⚠️  Błąd zatrzymania PROD DB"
    echo "   ✅ PROD DB zatrzymany"
else
    echo "   ℹ️  PROD DB już zatrzymany"
fi

echo ""

# Uruchom DEV jeśli zatrzymany
if [ "$DEV_DB_STATE" = "Stopped" ]; then
    echo "☀️ Uruchamianie DEV DB..."
    az postgres flexible-server start -n $DEV_DB -g $DEV_RG 2>/dev/null || echo "   ⚠️  Błąd uruchomienia DEV DB"
    echo "   ⏳ Czekam 30s na DB..."
    sleep 30
fi

if [ "$DEV_APP_STATE" = "Stopped" ]; then
    echo "☀️ Uruchamianie DEV App..."
    az webapp start -n $DEV_APP -g $DEV_RG 2>/dev/null || echo "   ⚠️  Błąd uruchomienia DEV App"
    echo "   ✅ DEV App uruchomiony"
fi

echo ""
echo "✅ DEV-ONLY MODE aktywny!"
echo "========================================"
echo ""
echo "💰 Oszczędności:"
echo "   PROD App (P1v2): ~\$90/m → \$0/m"
echo "   PROD DB (GP_Standard_D4s_v3): ~\$475/m → \$0/m"
echo "   ────────────────────────────────────"
echo "   TOTAL: ~\$565/m → \$0/m"
echo ""
echo "🚀 DEV Environment:"
echo "   URL: https://$DEV_APP.azurewebsites.net"
echo "   Status: Aktywny"
echo ""
echo "💤 PROD Environment:"
echo "   URL: https://$PROD_APP.azurewebsites.net"
echo "   Status: Zatrzymany (oszczędzanie!)"
echo ""
echo "📝 Aby wrócić do PROD:"
echo "   ./scripts/production-mode.sh"
echo ""
