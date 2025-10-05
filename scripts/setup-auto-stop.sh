#!/bin/bash
# Automatyczna konfiguracja crontab dla auto-stop obu środowisk
# Użycie: ./setup-auto-stop.sh

set -e

echo "💰 Konfiguracja automatycznego oszczędzania kosztów..."
echo "=================================================="
echo ""

PROJECT_PATH="/home/radek/timeoff-manager"
SCRIPT_PATH="$PROJECT_PATH/scripts/auto-stop-both.sh"

# Sprawdź czy skrypt istnieje
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Skrypt nie znaleziony: $SCRIPT_PATH"
    exit 1
fi

# Nadaj uprawnienia wykonywania
chmod +x "$SCRIPT_PATH"
echo "✅ Nadano uprawnienia wykonywania: $SCRIPT_PATH"
echo ""

# Sprawdź czy wpis już istnieje w crontab
if crontab -l 2>/dev/null | grep -q "auto-stop-both.sh"; then
    echo "⚠️  Wpis już istnieje w crontab. Pomijam..."
else
    # Dodaj do crontab
    echo "📝 Dodawanie do crontab..."
    (crontab -l 2>/dev/null; echo "") | crontab -
    (crontab -l 2>/dev/null; echo "# Auto-stop DEV + PROD environments (saves ~\$300/month)") | crontab -
    (crontab -l 2>/dev/null; echo "0 * * * * $SCRIPT_PATH >> /var/log/auto-stop.log 2>&1") | crontab -
    echo "✅ Dodano do crontab!"
fi

echo ""
echo "📋 Aktualny crontab:"
crontab -l | grep -A1 "Auto-stop"
echo ""

# Test wykonania
echo "🧪 Test pierwszego wykonania..."
echo ""
bash "$SCRIPT_PATH"

echo ""
echo "✅ Konfiguracja zakończona!"
echo "=================================================="
echo ""
echo "💰 Automatyczne oszczędzanie:"
echo "   - STOP: 18:00 - 08:00 + weekendy"
echo "   - START: 08:00 - 18:00 (pon-pt)"
echo ""
echo "💵 Oszczędność: ~\$300/miesiąc (50%)"
echo ""
echo "📊 Koszty:"
echo "   - BEZ auto-stop: ~\$605/m"
echo "   - Z auto-stop: ~\$305/m"
echo ""
echo "📝 Logi: /var/log/auto-stop.log"
echo "   tail -f /var/log/auto-stop.log"
echo ""
