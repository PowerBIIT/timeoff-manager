# 🚀 Production Deployment Guide

## Przewodnik wdrożenia produkcyjnego TimeOff Manager

---

## 📋 Checklist przed uruchomieniem produkcji

### 1. ✅ Weryfikacja kodu
- [x] Brak hardcoded localhost
- [x] Debug mode wyłączony w production
- [x] Security headers skonfigurowane
- [x] CORS ograniczony do production domain
- [x] Encryption dla SMTP passwords
- [x] Rate limiting aktywny

### 2. 🗄️ Czyszczenie bazy danych

**WAŻNE:** Przed uruchomieniem produkcji usuń wszystkie testowe dane!

#### Sposób 1: Przez skrypt (ZALECANE)

```bash
# Na Azure App Service (przez SSH/Kudu Console)
cd /home/site/wwwroot
python3 clear_prod_data.py
```

Skrypt:
- Wymaga potwierdzenia przez wpisanie 'TAK'
- Usuwa wszystkich użytkowników
- Usuwa wszystkie wnioski
- Usuwa logi audytowe
- Usuwa konfigurację SMTP
- Pokazuje podsumowanie

#### Sposób 2: Manualnie przez PostgreSQL

```bash
# Połącz się z Azure PostgreSQL
az postgres flexible-server connect \
  --name timeoff-db-20251004 \
  --admin-user dbadmin \
  --database timeoffdb

# Usuń dane (zachowaj strukturę tabel)
DELETE FROM requests;
DELETE FROM audit_logs;
DELETE FROM smtp_config;
DELETE FROM users;
```

### 3. 👤 Utworzenie pierwszego użytkownika Admin

Po wyczyszczeniu bazy **nie będzie żadnych użytkowników**.

#### Opcja A: Przez init_db.py (tworzy testowe konta)

```bash
python3 init_db.py
```

Utworzy:
- admin@firma.pl / admin123
- manager@firma.pl / manager123
- jan@firma.pl / jan123

**⚠️ Zmień email i hasło admina po pierwszym logowaniu!**

#### Opcja B: Przez API (zalecane dla produkcji)

```bash
# Curl request (zamień dane)
curl -X POST https://timeoff-manager-20251004.azurewebsites.net/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@twojafirma.pl",
    "password": "BezpieczneHaslo123!",
    "first_name": "Admin",
    "last_name": "System",
    "role": "admin",
    "supervisor_id": null
  }'
```

**Uwaga:** Ten endpoint może wymagać tokenu admin - w takim przypadku użyj Opcji A lub dodaj tymczasowe obejście w kodzie.

#### Opcja C: Bezpośrednio w bazie danych

```sql
-- Generuj hash hasła lokalnie
python3 -c "import bcrypt; print(bcrypt.hashpw('TwojeHaslo123!'.encode(), bcrypt.gensalt()).decode())"

-- Wstaw do bazy
INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, created_at)
VALUES (
  'admin@twojafirma.pl',
  '$2b$12$...', -- hash z poprzedniego kroku
  'Admin',
  'System',
  'admin',
  true,
  NOW()
);
```

### 4. ⚙️ Konfiguracja SMTP

Po zalogowaniu jako admin:

1. Przejdź do **Settings** → **SMTP Configuration**
2. Wypełnij dane:
   - SMTP Server: `smtp.gmail.com` (lub inny)
   - Port: `587`
   - Use SSL: ✅
   - Login: `twoj-email@gmail.com`
   - Password: hasło aplikacji Gmail
   - Email From: `system@twojafirma.pl`
3. Kliknij **Test Connection**
4. Zapisz konfigurację

### 5. 👥 Dodawanie użytkowników

1. Zaloguj się jako admin
2. Przejdź do **Users** → **Add User**
3. Utwórz hierarchię organizacyjną:
   - Najpierw CEO/dyrektor (supervisor: brak)
   - Potem managerów (supervisor: CEO)
   - Na końcu pracowników (supervisor: manager)

### 6. 🔐 Zmiana domyślnych haseł

Jeśli używałeś `init_db.py`:

1. Zaloguj się jako każdy użytkownik testowy
2. Przez Settings → User Profile → Change Password
3. Lub usuń konta testowe i utwórz nowe

---

## 🛡️ Security Best Practices

### Hasła

- Minimum 8 znaków
- Wielka i mała litera
- Przynajmniej jedna cyfra
- Dla adminów: zalecane 12+ znaków z symbolami

### SMTP

- Używaj hasła aplikacji (nie głównego hasła email)
- Gmail: https://support.google.com/accounts/answer/185833
- Hasło jest szyfrowane w bazie przez Fernet

### Baza danych

- Regularne backupy (Azure robi automatycznie)
- SSL required (już skonfigurowane)
- Silne hasło administratora

### Azure App Service

```bash
# Sprawdź czy FLASK_ENV=production
az webapp config appsettings list \
  --name timeoff-manager-20251004 \
  --resource-group timeoff-rg-prod \
  --query "[?name=='FLASK_ENV'].value" -o tsv

# Jeśli nie, ustaw:
az webapp config appsettings set \
  --name timeoff-manager-20251004 \
  --resource-group timeoff-rg-prod \
  --settings FLASK_ENV=production
```

---

## 📊 Monitoring i Logi

### Application Logs

```bash
# Pobierz ostatnie logi
az webapp log tail \
  --name timeoff-manager-20251004 \
  --resource-group timeoff-rg-prod

# Włącz logowanie
az webapp log config \
  --name timeoff-manager-20251004 \
  --resource-group timeoff-rg-prod \
  --application-logging filesystem \
  --level information
```

### Audit Logs

W aplikacji: **Settings** → **Audit Logs**
- Wszystkie akcje użytkowników
- Login/logout
- Tworzenie/edycja/usuwanie
- Decyzje na wnioskach

---

## 🚨 Troubleshooting

### Problem: Nie można się zalogować po wyczyszczeniu bazy

**Rozwiązanie:** Utwórz użytkownika admin przez `init_db.py` lub bezpośrednio w bazie.

### Problem: Emaile nie wysyłają się

**Rozwiązanie:**
1. Sprawdź konfigurację SMTP w Settings
2. Użyj Test Connection
3. Sprawdź logi: `az webapp log tail`

### Problem: 500 Internal Server Error

**Rozwiązanie:**
1. Sprawdź logi aplikacji
2. Zweryfikuj zmienne środowiskowe (DATABASE_URL, SECRET_KEY)
3. Sprawdź czy baza jest dostępna

---

## 📞 Wsparcie

- GitHub Issues: https://github.com/PowerBIIT/timeoff-manager/issues
- Dokumentacja: README.md, TECHNICAL-DOCS.md
- Test Plan: TEST-PLAN-DETAILED.md

---

**Data ostatniej aktualizacji:** 2025-10-05
**Wersja:** 1.0 Production Ready
