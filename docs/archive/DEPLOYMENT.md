# 🚀 TimeOff Manager - Przewodnik Wdrożenia Produkcyjnego

## ✅ LIVE PRODUCTION
**URL:** https://timeoff-manager-20251004.azurewebsites.net
**Status:** Deployed and tested ✅
**Last Updated:** 2025-10-04

## 📊 Production Test Results
- ✅ Admin login and user management
- ✅ Supervisor hierarchy (any user can be supervisor)
- ✅ Supervisor dropdown shows ALL users with roles
- ✅ Self-selection prevention
- ✅ Role-based access control
- ✅ Request validation

## 📋 Spis treści
- [Live Deployment Info](#live-deployment-info)
- [Wymagania](#wymagania)
- [Przygotowanie](#przygotowanie)
- [Deployment na Azure](#deployment-na-azure)
- [Konfiguracja po wdrożeniu](#konfiguracja-po-wdrożeniu)
- [Monitorowanie](#monitorowanie)
- [Backup i Recovery](#backup-i-recovery)
- [Troubleshooting](#troubleshooting)

---

## 🌐 Live Deployment Info

### Azure Resources
- **Resource Group:** timeoff-rg-prod
- **App Service:** timeoff-manager-20251004
- **Database Server:** timeoff-db-20251004.postgres.database.azure.com
- **Database Name:** timeoffdb
- **Location:** West Europe
- **Plan:** Basic (B1)

### Credentials
Database password stored in: `~/.azure-credentials`

### Test Accounts
| Role          | Email              | Password    | Supervisor     |
|---------------|-------------------|-------------|----------------|
| Administrator | admin@firma.pl    | admin123    | -              |
| Manager       | manager@firma.pl  | manager123  | -              |
| Employee      | jan@firma.pl      | jan123      | Anna Kowalska  |

### Quick Commands
```bash
# View logs
az webapp log tail --resource-group timeoff-rg-prod --name timeoff-manager-20251004

# Restart app
az webapp restart --resource-group timeoff-rg-prod --name timeoff-manager-20251004

# Check status
az webapp show --resource-group timeoff-rg-prod --name timeoff-manager-20251004 --query state
```

---

## 🔧 Wymagania

### Przed deploymentem upewnij się, że masz:

✅ **Azure CLI** zainstalowane i skonfigurowane
```bash
# Instalacja Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Weryfikacja
az --version

# Logowanie
az login
```

✅ **Azure Subscription** z aktywnymi zasobami

✅ **Uprawnienia** do tworzenia zasobów w Azure:
- Resource Groups
- Azure Database for PostgreSQL
- App Services
- (Opcjonalnie) Azure Key Vault

---

## 🎯 Przygotowanie

### 1. Sklonuj lub pobierz kod aplikacji
```bash
git clone <repository-url>
cd timeoff-manager
```

### 2. Ustaw zmienne środowiskowe

**Wymagane:**
```bash
export DB_PASSWORD="YourVeryStrongPassword123!@#"
```

**Opcjonalne (custom naming):**
```bash
export RESOURCE_GROUP="timeoff-production"
export APP_NAME="timeoff-manager-prod"
export DB_SERVER="timeoff-db-prod"
export LOCATION="westeurope"  # lub inna lokalizacja Azure
```

### 3. Wygeneruj silny SECRET_KEY
```bash
# Zostanie wygenerowany automatycznie podczas deploymentu
# lub ustaw własny:
export SECRET_KEY=$(openssl rand -hex 32)
```

---

## ☁️ Deployment na Azure

### Automatyczny deployment (zalecany)

```bash
# Upewnij się, że jesteś w katalogu projektu
cd timeoff-manager

# Ustaw hasło do bazy danych
export DB_PASSWORD="YourStrongPassword123!@#"

# Uruchom skrypt deploymentu
chmod +x azure-deploy.sh
./azure-deploy.sh
```

**Czas deploymentu: ~10-15 minut**

Skrypt automatycznie:
1. ✅ Utworzy Resource Group
2. ✅ Wdroży PostgreSQL Flexible Server
3. ✅ Skonfiguruje firewall i SSL
4. ✅ Utworzy bazę danych
5. ✅ Wdroży Web App (Python 3.11)
6. ✅ Ustawi zmienne środowiskowe
7. ✅ Wymusi HTTPS
8. ✅ Włączy logi aplikacji
9. ✅ Uruchomi aplikację

### Ręczny deployment (zaawansowany)

Jeśli preferujesz ręczny deployment, wykonaj kroki opisane w `azure-deploy.sh` pojedynczo.

---

## 🔐 Konfiguracja po wdrożeniu

### 1. Pierwsza konfiguracja

Po deploymencie otwórz aplikację w przeglądarce:
```
https://[APP_NAME].azurewebsites.net
```

### 2. Zaloguj się jako administrator

**Domyślne konto admin:**
- Email: `admin@firma.pl`
- Hasło: `admin123`

⚠️ **WAŻNE: Natychmiast zmień hasło!**

### 3. Zmień hasła domyślnych kont

1. Zaloguj się jako admin
2. Przejdź do **Użytkownicy**
3. Edytuj każde konto i ustaw nowe, silne hasła
4. Lub usuń konta testowe (manager, jan) i utwórz nowe

### 4. Konfiguruj SMTP (powiadomienia email)

1. Zaloguj się jako admin
2. Przejdź do **Ustawienia**
3. Skonfiguruj SMTP:

**Gmail:**
```
Server: smtp.gmail.com
Port: 587
Use SSL: true
Login: your-email@gmail.com
Password: [App Password - nie hasło do konta!]
Email From: system@firma.pl
```

**Utwórz App Password dla Gmail:**
https://myaccount.google.com/apppasswords

**Inne providery:**
- **Office 365**: smtp.office365.com:587
- **SendGrid**: smtp.sendgrid.net:587
- **AWS SES**: email-smtp.[region].amazonaws.com:587

4. Kliknij **Zapisz konfigurację**

### 5. Dodaj użytkowników

1. Przejdź do **Użytkownicy**
2. Kliknij **Dodaj użytkownika**
3. Wypełnij formularz:
   - Email
   - Hasło (min. 8 znaków)
   - Imię i nazwisko
   - Rola (pracownik/manager/admin)
   - Manager (dla pracowników)

---

## 📊 Monitorowanie

### Sprawdzanie logów

**Z terminala:**
```bash
# Stream logów na żywo
az webapp log tail \
  --resource-group timeoff-rg-prod \
  --name timeoff-manager-prod

# Pobierz ostatnie logi
az webapp log download \
  --resource-group timeoff-rg-prod \
  --name timeoff-manager-prod \
  --log-file logs.zip
```

**Z Azure Portal:**
1. Przejdź do App Service
2. Wybierz **Monitoring** → **Log stream**
3. Lub **Monitoring** → **Logs**

### Health Check

Aplikacja udostępnia endpoint health check:
```bash
curl https://[APP_NAME].azurewebsites.net/health
```

Odpowiedź:
```json
{
  "status": "healthy",
  "app": "TimeOff Manager"
}
```

### Metryki

**Azure Portal → App Service → Monitoring → Metrics:**
- HTTP requests
- Response time
- Error rate
- CPU/Memory usage

### Alerty (opcjonalne)

Skonfiguruj alerty dla:
- ❌ High error rate (>5% HTTP 5xx)
- ⏱️ Slow response time (>3s average)
- 💾 High memory usage (>80%)
- 🔥 CPU usage (>80%)

---

## 💾 Backup i Recovery

### Database Backup (automatyczny)

Azure PostgreSQL Flexible Server ma automatyczne backupy:
- **Retention**: 7 dni (domyślnie)
- **Frequency**: Codziennie
- **Point-in-time restore**: Tak

**Zwiększ retention period:**
```bash
az postgres flexible-server update \
  --resource-group timeoff-rg-prod \
  --name timeoff-db-prod \
  --backup-retention 30  # 30 dni
```

### Manual Backup

```bash
# Export bazy danych
az postgres flexible-server db export \
  --resource-group timeoff-rg-prod \
  --server-name timeoff-db-prod \
  --database-name timeoffdb \
  --output-file backup-$(date +%Y%m%d).sql
```

### Restore z backupu

**Point-in-time restore:**
```bash
az postgres flexible-server restore \
  --resource-group timeoff-rg-prod \
  --name timeoff-db-restored \
  --source-server timeoff-db-prod \
  --restore-time "2025-10-04T12:00:00Z"
```

---

## 🔒 Zabezpieczenia Produkcyjne

### ✅ Zaimplementowane zabezpieczenia

1. **HTTPS Only** - wymuszony SSL/TLS
2. **JWT Authentication** - tokeny sesji
3. **Password Hashing** - bcrypt
4. **Role-Based Access Control** - uprawnienia wg ról
5. **SQL Injection Prevention** - parametryzowane zapytania
6. **CORS** - ograniczony dostęp cross-origin
7. **Error Hiding** - w produkcji nie pokazuj szczegółów błędów
8. **PostgreSQL SSL** - szyfrowane połączenie do bazy

### 🔐 Dodatkowe zabezpieczenia (opcjonalne)

**Azure Key Vault dla sekretów:**
```bash
# Utwórz Key Vault
az keyvault create \
  --name timeoff-vault \
  --resource-group timeoff-rg-prod \
  --location westeurope

# Dodaj sekret
az keyvault secret set \
  --vault-name timeoff-vault \
  --name db-password \
  --value "$DB_PASSWORD"

# Przypisz Managed Identity do App Service
az webapp identity assign \
  --resource-group timeoff-rg-prod \
  --name timeoff-manager-prod

# Daj dostęp do Key Vault
az keyvault set-policy \
  --name timeoff-vault \
  --object-id <identity-id> \
  --secret-permissions get list
```

**Azure Front Door (WAF):**
- DDoS protection
- WAF rules
- Global load balancing

---

## 🐛 Troubleshooting

### Aplikacja nie działa

**1. Sprawdź logi:**
```bash
az webapp log tail --resource-group timeoff-rg-prod --name timeoff-manager-prod
```

**2. Sprawdź zmienne środowiskowe:**
```bash
az webapp config appsettings list \
  --resource-group timeoff-rg-prod \
  --name timeoff-manager-prod
```

**3. Zrestartuj aplikację:**
```bash
az webapp restart \
  --resource-group timeoff-rg-prod \
  --name timeoff-manager-prod
```

### Błędy połączenia z bazą danych

**1. Sprawdź firewall:**
```bash
az postgres flexible-server firewall-rule list \
  --resource-group timeoff-rg-prod \
  --name timeoff-db-prod
```

**2. Test połączenia:**
```bash
psql "postgresql://dbadmin:PASSWORD@timeoff-db-prod.postgres.database.azure.com/timeoffdb?sslmode=require"
```

### Email nie działa

**1. Sprawdź konfigurację SMTP w aplikacji:**
- Zaloguj się jako admin
- Ustawienia → SMTP Config
- Sprawdź dane logowania

**2. Test Gmail App Password:**
- Sprawdź czy App Password jest poprawny
- Czy 2FA jest włączone w Gmail

**3. Sprawdź logi:**
```bash
# Szukaj błędów email
az webapp log tail ... | grep -i "email\|smtp"
```

### 500 Internal Server Error

**1. Sprawdź logi aplikacji**
```bash
az webapp log tail --resource-group timeoff-rg-prod --name timeoff-manager-prod
```

**2. Sprawdź czy wszystkie zmienne środowiskowe są ustawione:**
- DATABASE_URL
- SECRET_KEY
- FLASK_ENV=production

---

## 🔄 Aktualizacje Aplikacji

### Deployment nowej wersji

```bash
# 1. Zaktualizuj kod
git pull

# 2. Deploy aktualizacji
az webapp up \
  --name timeoff-manager-prod \
  --resource-group timeoff-rg-prod

# 3. Zrestartuj aplikację
az webapp restart \
  --resource-group timeoff-rg-prod \
  --name timeoff-manager-prod
```

### Zero-downtime deployment (Blue-Green)

```bash
# 1. Utwórz slot stagingowy
az webapp deployment slot create \
  --name timeoff-manager-prod \
  --resource-group timeoff-rg-prod \
  --slot staging

# 2. Deploy do stagingu
az webapp deployment source config-zip \
  --resource-group timeoff-rg-prod \
  --name timeoff-manager-prod \
  --slot staging \
  --src app.zip

# 3. Test stagingu
# https://timeoff-manager-prod-staging.azurewebsites.net

# 4. Swap staging → production
az webapp deployment slot swap \
  --resource-group timeoff-rg-prod \
  --name timeoff-manager-prod \
  --slot staging
```

---

## 🗑️ Usuwanie Zasobów

**Usuń całą grupę zasobów:**
```bash
az group delete \
  --name timeoff-rg-prod \
  --yes \
  --no-wait
```

⚠️ **UWAGA**: To usunie WSZYSTKIE zasoby w grupie (baza danych, web app, etc.)

---

## 📞 Wsparcie

W przypadku problemów:

1. Sprawdź [Troubleshooting](#troubleshooting)
2. Przejrzyj logi aplikacji
3. Sprawdź dokumentację Azure
4. Otwórz issue w repozytorium projektu

---

## ✅ Production Checklist

Przed uruchomieniem produkcyjnym upewnij się, że:

- [ ] Zmieniono wszystkie domyślne hasła
- [ ] Skonfigurowano SMTP dla powiadomień email
- [ ] Włączono HTTPS only
- [ ] Skonfigurowano backup bazy danych
- [ ] Ustawiono monitoring i alerty
- [ ] Przetestowano wszystkie funkcje
- [ ] Dodano prawdziwych użytkowników
- [ ] Skonfigurowano własną domenę (opcjonalnie)
- [ ] Włączono Azure Key Vault dla sekretów (opcjonalnie)
- [ ] Skonfigurowano WAF/Front Door (opcjonalnie)

---

**Aplikacja gotowa do użycia w produkcji! 🚀**
