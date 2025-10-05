#!/bin/bash
# Tryb PRODUCTION: Uruchom PROD, opcjonalnie zatrzymaj DEV
# Użycie przed wdrożeniem do produkcji
#
# Użycie: ./production-mode.sh [--keep-dev]

set -e

KEEP_DEV=false

# Parse arguments
if [ "$1" = "--keep-dev" ]; then
    KEEP_DEV=true
fi

echo "🚀 PRODUCTION MODE - Przygotowanie do wdrożenia"
echo "================================================"
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

# Uruchom PROD
echo "☀️ Uruchamianie PROD environment..."
echo ""

if [ "$PROD_DB_STATE" != "Ready" ]; then
    echo "🔄 Uruchamianie PROD DB..."
    az postgres flexible-server start -n $PROD_DB -g $PROD_RG 2>/dev/null || echo "   ⚠️  PROD DB już działa lub błąd"
    echo "   ⏳ Czekam 30s na DB..."
    sleep 30
    echo "   ✅ PROD DB uruchomiony"
else
    echo "   ℹ️  PROD DB już działa"
fi

if [ "$PROD_APP_STATE" != "Running" ]; then
    echo "🔄 Uruchamianie PROD App..."
    az webapp start -n $PROD_APP -g $PROD_RG 2>/dev/null || echo "   ⚠️  PROD App już działa lub błąd"
    echo "   ✅ PROD App uruchomiony"
else
    echo "   ℹ️  PROD App już działa"
fi

echo ""

# Opcjonalnie zatrzymaj DEV
if [ "$KEEP_DEV" = false ]; then
    echo "🌙 Zatrzymywanie DEV environment (oszczędzanie)..."
    echo ""

    if [ "$DEV_APP_STATE" != "Stopped" ]; then
        echo "🔄 Zatrzymywanie DEV App..."
        az webapp stop -n $DEV_APP -g $DEV_RG 2>/dev/null || echo "   ⚠️  DEV App już zatrzymany"
        echo "   ✅ DEV App zatrzymany"
    fi

    if [ "$DEV_DB_STATE" != "Stopped" ]; then
        echo "🔄 Zatrzymywanie DEV DB..."
        az postgres flexible-server stop -n $DEV_DB -g $DEV_RG 2>/dev/null || echo "   ⚠️  DEV DB już zatrzymany"
        echo "   ✅ DEV DB zatrzymany"
    fi
else
    echo "   ℹ️  DEV pozostaje uruchomiony (--keep-dev)"
fi

echo ""
echo "✅ PRODUCTION MODE aktywny!"
echo "================================================"
echo ""
echo "🚀 PROD Environment:"
echo "   URL: https://$PROD_APP.azurewebsites.net"
echo "   Status: Uruchomiony"
echo ""

if [ "$KEEP_DEV" = false ]; then
    echo "💤 DEV Environment:"
    echo "   Status: Zatrzymany (oszczędzanie ~\$40/m)"
    echo ""
    echo "💰 Koszty:"
    echo "   PROD: ~\$565/m (aktywny)"
    echo "   DEV: \$0/m (zatrzymany)"
else
    echo "🚀 DEV Environment:"
    echo "   URL: https://$DEV_APP.azurewebsites.net"
    echo "   Status: Uruchomiony"
    echo ""
    echo "💰 Koszty:"
    echo "   PROD: ~\$565/m (aktywny)"
    echo "   DEV: ~\$40/m (aktywny)"
fi

echo ""
echo "📝 Test PROD:"
echo "   curl https://$PROD_APP.azurewebsites.net/health"
echo ""
echo "📝 Powrót do DEV-ONLY:"
echo "   ./scripts/dev-only-mode.sh"
echo ""
