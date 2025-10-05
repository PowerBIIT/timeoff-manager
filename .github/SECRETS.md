# GitHub Secrets Configuration

Ten dokument opisuje wymagane sekrety dla GitHub Actions CI/CD.

## Wymagane Secrets

### 1. AZURE_CREDENTIALS
**Opis:** Azure Service Principal credentials dla Azure CLI
**Format:** JSON
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

**Jak uzyskać:**
```bash
az ad sp create-for-rbac \
  --name "github-actions-timeoff" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/timeoff-rg-prod \
  --sdk-auth
```

### 2. AZURE_WEBAPP_PUBLISH_PROFILE
**Opis:** Publish profile dla PRODUCTION environment
**Jak uzyskać:**
```bash
az webapp deployment list-publishing-profiles \
  --resource-group timeoff-rg-prod \
  --name timeoff-manager-20251004 \
  --xml
```

### 3. AZURE_WEBAPP_PUBLISH_PROFILE_DEV
**Opis:** Publish profile dla DEV environment
**Jak uzyskać:**
```bash
az webapp deployment list-publishing-profiles \
  --resource-group timeoff-manager-rg-dev \
  --name timeoff-manager-dev \
  --xml
```

## Konfiguracja w GitHub

1. Przejdź do: `Settings` → `Secrets and variables` → `Actions`
2. Kliknij `New repository secret`
3. Dodaj każdy secret z nazwą i wartością

## Environments

### Development
- **Name:** `development`
- **URL:** https://timeoff-manager-dev.azurewebsites.net
- **Branch protection:** `develop`

### Production
- **Name:** `production`
- **URL:** https://timeoff-manager-20251004.azurewebsites.net
- **Branch protection:** `master`
- **Required reviewers:** 1 (opcjonalnie)

## Workflow Improvements

### Restart App After Deployment
Workflows automatycznie restartują aplikację po deployment aby:
- Wyczyścić cache statycznych plików
- Załadować nowy kod bez opóźnień
- Zapewnić spójność między kodem a wyświetlaną stroną

### Version.json Generation
Każdy deployment automatycznie generuje `version.json`:
```json
{
  "commit": "d026987",
  "date": "2025-10-05",
  "branch": "develop"
}
```
Wyświetlany w stopce aplikacji.

## Troubleshooting

### Problem: 401 Unauthorized podczas restartu
**Rozwiązanie:** Upewnij się że `AZURE_CREDENTIALS` ma rolę `contributor` na resource group

### Problem: Cache nie jest czyszczony
**Rozwiązanie:** Workflow automatycznie restartuje app - jeśli problem persystuje, sprawdź czy restart się wykonał

### Problem: Version.json nie pojawia się w aplikacji
**Rozwiązanie:** Sprawdź czy plik jest w package (`deploy.zip`) i czy restart się wykonał
