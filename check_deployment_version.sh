#!/bin/bash
# Sprawdza czy wdrożenie ma najnowszy commit

set -e

# Kolory
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parametry
ENVIRONMENT=${1:-dev}
if [ "$ENVIRONMENT" = "dev" ]; then
    APP_URL="https://timeoff-manager-dev.azurewebsites.net"
    BRANCH="develop"
elif [ "$ENVIRONMENT" = "prod" ]; then
    APP_URL="https://timeoff-manager-20251004.azurewebsites.net"
    BRANCH="master"
else
    echo -e "${RED}❌ Nieprawidłowe środowisko. Użyj: dev lub prod${NC}"
    exit 1
fi

echo "🔍 Sprawdzanie wersji wdrożenia: $ENVIRONMENT"
echo "🌐 URL: $APP_URL"
echo "🌿 Branch: $BRANCH"
echo ""

# Pobierz lokalny commit hash
LOCAL_COMMIT=$(git rev-parse --short HEAD)
echo -e "💻 Lokalny commit (HEAD): ${GREEN}$LOCAL_COMMIT${NC}"

# Pobierz commit z brancha
BRANCH_COMMIT=$(git rev-parse --short origin/$BRANCH)
echo -e "🌿 Branch commit ($BRANCH): ${GREEN}$BRANCH_COMMIT${NC}"

# Pobierz wersję z wdrożenia
echo "🌐 Pobieranie wersji z $APP_URL/api/version ..."
DEPLOYED_VERSION=$(curl -s "$APP_URL/api/version" || echo "{}")
DEPLOYED_COMMIT=$(echo "$DEPLOYED_VERSION" | grep -o '"commit":"[^"]*"' | cut -d'"' -f4)
DEPLOYED_DATE=$(echo "$DEPLOYED_VERSION" | grep -o '"date":"[^"]*"' | cut -d'"' -f4)
DEPLOYED_BRANCH=$(echo "$DEPLOYED_VERSION" | grep -o '"branch":"[^"]*"' | cut -d'"' -f4)

if [ -z "$DEPLOYED_COMMIT" ] || [ "$DEPLOYED_COMMIT" = "unknown" ]; then
    echo -e "${RED}❌ Nie można pobrać wersji z wdrożenia!${NC}"
    exit 1
fi

echo -e "🚀 Wdrożony commit: ${YELLOW}$DEPLOYED_COMMIT${NC} (branch: $DEPLOYED_BRANCH, data: $DEPLOYED_DATE)"
echo ""

# Porównanie
if [ "$DEPLOYED_COMMIT" = "$BRANCH_COMMIT" ]; then
    echo -e "${GREEN}✅ Wdrożenie jest AKTUALNE!${NC}"
    echo -e "${GREEN}   Wdrożony commit: $DEPLOYED_COMMIT${NC}"
    echo -e "${GREEN}   Branch commit:   $BRANCH_COMMIT${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Wdrożenie jest NIEAKTUALNE!${NC}"
    echo -e "${YELLOW}   Wdrożony commit: $DEPLOYED_COMMIT${NC}"
    echo -e "${YELLOW}   Branch commit:   $BRANCH_COMMIT${NC}"
    echo ""
    echo "💡 Aby zaktualizować, poczekaj na GitHub Actions deployment lub uruchom ręcznie:"
    echo "   git push origin $BRANCH"
    exit 1
fi
