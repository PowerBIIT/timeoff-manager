#!/bin/bash
# Konfiguracja monitoringu bezczynności
# Automatyczne zatrzymanie po 30 minutach bez requestów

set -e

echo "💤 Konfiguracja monitoringu bezczynności..."
echo "============================================="
echo ""

PROJECT_PATH="/home/radek/timeoff-manager"
SCRIPT_PATH="$PROJECT_PATH/scripts/auto-stop-on-idle.sh"

# Sprawdź czy skrypt istnieje
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Skrypt nie znaleziony: $SCRIPT_PATH"
    exit 1
fi

# Nadaj uprawnienia wykonywania
chmod +x "$SCRIPT_PATH"
echo "✅ Nadano uprawnienia: $SCRIPT_PATH"
echo ""

# Usuń stary harmonogram czasowy (jeśli jest)
echo "🔧 Konfiguracja crontab..."
if crontab -l 2>/dev/null | grep -q "auto-stop-both.sh"; then
    echo "⚠️  Wykryto stary harmonogram czasowy (auto-stop-both.sh)"
    echo "   Czy chcesz go usunąć i zastąpić monitoringiem bezczynności? (t/n)"
    read -r response
    if [[ "$response" =~ ^([tT]|[yY]es)$ ]]; then
        crontab -l 2>/dev/null | grep -v "auto-stop-both.sh" | crontab -
        echo "   ✅ Stary harmonogram usunięty"
    fi
fi

# Dodaj idle monitoring
if crontab -l 2>/dev/null | grep -q "auto-stop-on-idle.sh"; then
    echo "⚠️  Idle monitoring już skonfigurowany. Pomijam..."
else
    echo "📝 Dodawanie idle monitoring do crontab..."
    (crontab -l 2>/dev/null; echo "") | crontab -
    (crontab -l 2>/dev/null; echo "# Auto-stop DEV + PROD po 30 min bezczynności (sprawdzanie co 5 min)") | crontab -
    (crontab -l 2>/dev/null; echo "*/5 * * * * $SCRIPT_PATH >> /var/log/idle-monitor.log 2>&1") | crontab -
    echo "✅ Dodano do crontab!"
fi

echo ""
echo "📋 Aktualny crontab:"
crontab -l | grep -E "(auto-stop|idle)" || echo "Brak wpisów"
echo ""

# Test wykonania
echo "🧪 Test pierwszego wykonania..."
echo ""
bash "$SCRIPT_PATH"

echo ""
echo "✅ Konfiguracja zakończona!"
echo "============================================="
echo ""
echo "💤 Automatyczne zatrzymanie:"
echo "   - Monitoring: co 5 minut"
echo "   - Próg bezczynności: 30 minut"
echo "   - Po 30 min bez requestów → STOP"
echo "   - Przy pierwszym requeście → START (~2 min)"
echo ""
echo "💰 Oszczędność:"
echo "   - Maksymalna: ~$300/m (jeśli środowiska rzadko używane)"
echo "   - Realna: zależy od wzorca użycia"
echo ""
echo "📝 Logi: /var/log/idle-monitor.log"
echo "   tail -f /var/log/idle-monitor.log"
echo ""
echo "⚙️  Zmiana progu bezczynności:"
echo "   Edytuj: $SCRIPT_PATH"
echo "   Zmień: IDLE_THRESHOLD=30  (na inną wartość w minutach)"
echo ""
