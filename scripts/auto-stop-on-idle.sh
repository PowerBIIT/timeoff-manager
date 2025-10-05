#!/bin/bash
# Automatyczne zatrzymywanie środowisk po 30 minutach bezczynności
# Monitoruje logi Azure App Service i zatrzymuje gdy brak requestów
#
# Użycie: ./auto-stop-on-idle.sh
# Cron: */5 * * * * /home/radek/timeoff-manager/scripts/auto-stop-on-idle.sh >> /var/log/idle-monitor.log 2>&1

set -e

# Konfiguracja
DEV_RG="timeoff-manager-rg-dev"
DEV_APP="timeoff-manager-dev"
DEV_DB="timeoff-db-dev"

PROD_RG="timeoff-rg-prod"
PROD_APP="timeoff-manager-20251004"
PROD_DB="timeoff-db-20251004"

# Czas bezczynności (w minutach)
IDLE_THRESHOLD=30

# Plik do śledzenia ostatniej aktywności
STATE_DIR="/var/tmp/azure-idle-monitor"
mkdir -p "$STATE_DIR"

DEV_LAST_REQUEST="$STATE_DIR/dev-last-request"
PROD_LAST_REQUEST="$STATE_DIR/prod-last-request"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Checking idle status..."

# Funkcja: sprawdź ostatni request w logach Azure
check_last_request() {
    local app_name=$1
    local rg_name=$2

    # Pobierz ostatnie 100 linii logów (ostatnie 5 minut)
    local logs=$(az webapp log tail --name "$app_name" --resource-group "$rg_name" --lines 100 2>/dev/null || echo "")

    # Sprawdź czy są jakiekolwiek requesty HTTP (200, 201, 404, etc.)
    if echo "$logs" | grep -qE "HTTP/[0-9\.]+\" [0-9]{3}"; then
        echo "$(date +%s)"
        return 0
    else
        return 1
    fi
}

# Funkcja: zatrzymaj środowisko
stop_environment() {
    local env_name=$1
    local app_name=$2
    local db_name=$3
    local rg_name=$4

    echo "  🌙 Zatrzymywanie $env_name (brak aktywności > ${IDLE_THRESHOLD}min)..."

    # Sprawdź czy app już jest zatrzymany
    local app_state=$(az webapp show --name "$app_name" --resource-group "$rg_name" --query state -o tsv 2>/dev/null || echo "Unknown")

    if [ "$app_state" != "Stopped" ]; then
        az webapp stop --name "$app_name" --resource-group "$rg_name" 2>/dev/null || echo "    ⚠️  App already stopped or error"
        echo "    ✅ App zatrzymany"
    else
        echo "    ℹ️  App już zatrzymany"
    fi

    # Sprawdź czy DB już jest zatrzymany
    local db_state=$(az postgres flexible-server show --name "$db_name" --resource-group "$rg_name" --query state -o tsv 2>/dev/null || echo "Unknown")

    if [ "$db_state" != "Stopped" ]; then
        az postgres flexible-server stop --name "$db_name" --resource-group "$rg_name" 2>/dev/null || echo "    ⚠️  DB already stopped or error"
        echo "    ✅ DB zatrzymany"
    else
        echo "    ℹ️  DB już zatrzymany"
    fi

    echo "    💰 Oszczędzanie rozpoczęte!"
}

# Funkcja: uruchom środowisko
start_environment() {
    local env_name=$1
    local app_name=$2
    local db_name=$3
    local rg_name=$4

    echo "  ☀️ Uruchamianie $env_name (wykryto aktywność)..."

    # Start DB first
    local db_state=$(az postgres flexible-server show --name "$db_name" --resource-group "$rg_name" --query state -o tsv 2>/dev/null || echo "Unknown")

    if [ "$db_state" = "Stopped" ]; then
        echo "    🔄 Uruchamianie DB..."
        az postgres flexible-server start --name "$db_name" --resource-group "$rg_name" 2>/dev/null || echo "    ⚠️  DB already running or error"
        sleep 20  # Czekaj na DB
    fi

    # Start App
    local app_state=$(az webapp show --name "$app_name" --resource-group "$rg_name" --query state -o tsv 2>/dev/null || echo "Unknown")

    if [ "$app_state" = "Stopped" ]; then
        echo "    🔄 Uruchamianie App..."
        az webapp start --name "$app_name" --resource-group "$rg_name" 2>/dev/null || echo "    ⚠️  App already running or error"
    fi

    echo "    ✅ Środowisko uruchomione!"
}

# Funkcja: sprawdź bezczynność środowiska
check_idle() {
    local env_name=$1
    local app_name=$2
    local db_name=$3
    local rg_name=$4
    local last_request_file=$5

    # Sprawdź czy app jest uruchomiony
    local app_state=$(az webapp show --name "$app_name" --resource-group "$rg_name" --query state -o tsv 2>/dev/null || echo "Unknown")

    if [ "$app_state" = "Stopped" ]; then
        echo "  $env_name: Zatrzymany (OK)"
        return
    fi

    # App działa - sprawdź ostatni request
    if check_last_request "$app_name" "$rg_name"; then
        # Są nowe requesty - zapisz timestamp
        local new_timestamp=$?
        echo "$new_timestamp" > "$last_request_file"
        echo "  $env_name: Aktywny (ostatni request: teraz)"
        return
    fi

    # Brak nowych requestów - sprawdź kiedy był ostatni
    if [ -f "$last_request_file" ]; then
        local last_timestamp=$(cat "$last_request_file")
        local now=$(date +%s)
        local idle_minutes=$(( (now - last_timestamp) / 60 ))

        echo "  $env_name: Bezczynny przez ${idle_minutes} minut"

        if [ $idle_minutes -ge $IDLE_THRESHOLD ]; then
            stop_environment "$env_name" "$app_name" "$db_name" "$rg_name"
            # Usuń plik - zaczynamy od nowa przy następnym starcie
            rm -f "$last_request_file"
        fi
    else
        # Pierwszy check - zapisz aktualny czas
        echo "$(date +%s)" > "$last_request_file"
        echo "  $env_name: Monitoring started"
    fi
}

# === GŁÓWNA LOGIKA ===

echo ""
echo "🔍 DEV Environment:"
check_idle "DEV" "$DEV_APP" "$DEV_DB" "$DEV_RG" "$DEV_LAST_REQUEST"

echo ""
echo "🔍 PROD Environment:"
check_idle "PROD" "$PROD_APP" "$PROD_DB" "$PROD_RG" "$PROD_LAST_REQUEST"

echo ""
echo "$(date '+%Y-%m-%d %H:%M:%S') - Check complete!"
echo "---"
