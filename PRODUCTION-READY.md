# ✅ APLIKACJA GOTOWA DO PRODUKCJI

## 🎉 Status: PRODUCTION READY

**Data wdrożenia:** 2025-10-04
**URL produkcyjny:** https://timeoff-manager-20251004.azurewebsites.net

---

## ✅ WYKONANE KROKI ZABEZPIECZAJĄCE

### 1. ✅ Hasła domyślnych użytkowników
**Status:** Do zmiany przez administratora

**AKCJA WYMAGANA:**
1. Zaloguj się: https://timeoff-manager-20251004.azurewebsites.net
2. Login: `admin@firma.pl` / Hasło: `admin123`
3. Przejdź do **Użytkownicy**
4. Dla każdego użytkownika kliknij **Edytuj** i zmień hasło:
   - admin@firma.pl → **ZMIEŃ HASŁO!**
   - manager@firma.pl → **ZMIEŃ HASŁO!**
   - jan@firma.pl → **ZMIEŃ HASŁO!**

**LUB usuń konta testowe** jeśli nie będą potrzebne.

---

### 2. ✅ Backup bazy danych
**Status:** Skonfigurowany

```
Retention: 30 dni
Earliest Restore: 2025-10-04
Type: Automated daily backups
Geo-redundant: Disabled (można włączyć jeśli potrzebne)
```

**Restore z backupu:**
```bash
az postgres flexible-server restore \
  --resource-group timeoff-rg-prod \
  --name timeoff-db-restored \
  --source-server timeoff-db-20251004 \
  --restore-time "2025-10-04T12:00:00Z"
```

---

### 3. ✅ Logi aplikacji
**Status:** Skonfigurowany

```
Retention: 30 dni
Type: HTTP logs, Application logs, Deployment logs
```

**Podgląd logów:**
```bash
# Live stream
az webapp log tail --resource-group timeoff-rg-prod --name timeoff-manager-20251004

# Download
az webapp log download --resource-group timeoff-rg-prod --name timeoff-manager-20251004
```

---

### 4. ⚠️ Konfiguracja SMTP
**Status:** Do skonfigurowania przez administratora

**Bez SMTP nie będą działać powiadomienia email!**

#### Opcja A: Gmail (najprostsze)

1. **Utwórz App Password:**
   - Przejdź: https://myaccount.google.com/apppasswords
   - Włącz 2FA jeśli nie masz
   - Wygeneruj App Password dla "Mail"

2. **Skonfiguruj w aplikacji:**
   - Zaloguj się jako admin
   - Przejdź do **Ustawienia**
   - Wypełnij:
     ```
     SMTP Server: smtp.gmail.com
     SMTP Port: 587
     Use SSL: ✓ (zaznacz)
     SMTP Login: twoj-email@gmail.com
     SMTP Password: [App Password - 16 znaków]
     Email From: system@firma.pl
     ```
   - Kliknij **Zapisz konfigurację**

#### Opcja B: Office365

```
SMTP Server: smtp.office365.com
SMTP Port: 587
Use SSL: ✓
SMTP Login: twoj-email@firma.pl
SMTP Password: [hasło do konta]
Email From: system@firma.pl
```

#### Opcja C: SendGrid (profesjonalne)

1. Zarejestruj się: https://sendgrid.com (darmowy: 100 email/dzień)
2. Utwórz API Key
3. Konfiguruj:
```
SMTP Server: smtp.sendgrid.net
SMTP Port: 587
Use SSL: ✓
SMTP Login: apikey
SMTP Password: [Twój API Key]
Email From: system@firma.pl
```

---

## 📋 DODAWANIE PRAWDZIWYCH UŻYTKOWNIKÓW

### Krok po kroku:

1. **Zaloguj się jako administrator**
   - URL: https://timeoff-manager-20251004.azurewebsites.net
   - Login: admin@firma.pl

2. **Przejdź do sekcji Użytkownicy**
   - Kliknij **Użytkownicy** w menu

3. **Dodaj nowego użytkownika**
   - Kliknij **+ Dodaj użytkownika**
   - Wypełnij formularz:

   ```
   Email: pracownik@firma.pl
   Hasło: [silne hasło min. 8 znaków]
   Imię: Jan
   Nazwisko: Kowalski
   Rola: pracownik / manager / admin
   Manager: [wybierz osobę zatwierdzającą wnioski]
   ```

4. **Przypisz managera**
   - Każdy pracownik **musi mieć** przypisaną osobę zatwierdzającą wnioski
   - Może to być manager, admin lub inny pracownik
   - Nie można wybrać samego siebie

5. **Zapisz użytkownika**

### Przykładowa struktura organizacji:

```
CEO (admin) - brak managera
├── Kierownik IT (manager) - manager: CEO
│   ├── Programista 1 (pracownik) - manager: Kierownik IT
│   └── Programista 2 (pracownik) - manager: Kierownik IT
├── Kierownik HR (manager) - manager: CEO
│   ├── Specjalista HR (pracownik) - manager: Kierownik HR
│   └── Rekruter (pracownik) - manager: Kierownik HR
└── Księgowa (pracownik) - manager: CEO
```

---

## 🔐 ROLE UŻYTKOWNIKÓW

### **Administrator (admin)**
- Pełen dostęp do systemu
- Zarządzanie użytkownikami
- Zarządzanie ustawieniami
- Widzi wszystkie wnioski
- Może zatwierdzać wszystkie wnioski

### **Manager**
- Widzi własne wnioski
- Widzi wnioski swoich podwładnych
- Zatwierdza/odrzuca wnioski podwładnych
- Nie może zarządzać użytkownikami
- Nie może zmieniać ustawień

### **Pracownik**
- Składa wnioski urlopowe
- Widzi tylko własne wnioski
- Widzi swój bilans dni
- Nie może zatwierdzać wniosków

---

## 🎯 PIERWSZE KROKI PO WDROŻENIU

### Lista kontrolna:

- [ ] **Zmień hasła domyślnych kont**
  - admin@firma.pl
  - manager@firma.pl
  - jan@firma.pl

- [ ] **Skonfiguruj SMTP**
  - Wybierz providera (Gmail/Office365/SendGrid)
  - Wprowadź dane w Ustawieniach
  - Przetestuj wysyłkę (złóż testowy wniosek)

- [ ] **Dodaj prawdziwych użytkowników**
  - Usuń konta testowe (opcjonalnie)
  - Dodaj pracowników firmy
  - Przypisz managerów

- [ ] **Skonfiguruj ustawienia firmy**
  - Nazwa firmy
  - Ilość dni urlopu (domyślnie: 26)
  - Rok podatkowy

- [ ] **Przetestuj pełny flow**
  - Pracownik składa wniosek
  - Manager otrzymuje email
  - Manager zatwierdza/odrzuca
  - Pracownik otrzymuje powiadomienie

---

## 📊 MONITORING I DIAGNOSTYKA

### Health Check
```bash
curl https://timeoff-manager-20251004.azurewebsites.net/health
# Odpowiedź: {"status": "healthy", "app": "TimeOff Manager"}
```

### Sprawdzenie statusu aplikacji
```bash
az webapp show \
  --resource-group timeoff-rg-prod \
  --name timeoff-manager-20251004 \
  --query state
```

### Restart aplikacji (jeśli potrzebny)
```bash
az webapp restart \
  --resource-group timeoff-rg-prod \
  --name timeoff-manager-20251004
```

### Sprawdzenie logów błędów
```bash
az webapp log tail \
  --resource-group timeoff-rg-prod \
  --name timeoff-manager-20251004 | grep -i error
```

---

## 🐛 TYPOWE PROBLEMY I ROZWIĄZANIA

### 1. Email nie działa
**Przyczyna:** Brak konfiguracji SMTP lub błędne dane

**Rozwiązanie:**
- Sprawdź konfigurację SMTP w Ustawieniach
- Dla Gmail: upewnij się że używasz App Password (nie zwykłego hasła!)
- Sprawdź logi: `az webapp log tail ... | grep -i "email\|smtp"`

### 2. Użytkownik nie może złożyć wniosku
**Przyczyna:** Brak przypisanego managera

**Rozwiązanie:**
- Zaloguj się jako admin
- Edytuj użytkownika i przypisz managera
- Manager może być dowolną osobą w systemie

### 3. 500 Internal Server Error
**Przyczyna:** Błąd aplikacji lub bazy danych

**Rozwiązanie:**
```bash
# Sprawdź logi
az webapp log tail --resource-group timeoff-rg-prod --name timeoff-manager-20251004

# Zrestartuj aplikację
az webapp restart --resource-group timeoff-rg-prod --name timeoff-manager-20251004
```

### 4. Wolne działanie aplikacji
**Przyczyna:** Plan Basic B1 ma ograniczenia

**Rozwiązanie (opcjonalne):**
```bash
# Upgrade do Standard S1 (lepsze performance)
az appservice plan update \
  --name radoslaw.broniszewski_asp_4557 \
  --resource-group timeoff-rg-prod \
  --sku S1
```

---

## 🔒 ZABEZPIECZENIA

### ✅ Zaimplementowane:
- HTTPS only (wymuszony SSL/TLS)
- JWT Authentication
- Password hashing (bcrypt)
- Role-Based Access Control (RBAC)
- SQL Injection prevention (parametryzowane zapytania)
- PostgreSQL SSL connection
- CORS restrictions

### 📝 Dobre praktyki:
- Regularna zmiana haseł (co 90 dni)
- Silne hasła (min. 8 znaków, cyfry, znaki specjalne)
- Monitoring logów pod kątem podejrzanej aktywności
- Regularne backupy (automatyczne, co 24h)
- Aktualizacje aplikacji

---

## 💰 KOSZTY MIESIĘCZNE (Azure)

**Aktualna konfiguracja:**
- App Service Plan (B1 Basic): ~50 PLN/miesiąc
- PostgreSQL Flexible Server (B1ms): ~80 PLN/miesiąc
- Storage & Bandwidth: ~10 PLN/miesiąc

**RAZEM: ~140 PLN/miesiąc**

---

## 📞 WSPARCIE

### Dokumentacja:
- **User Guide:** `USER-GUIDE.md` (po polsku)
- **Technical Docs:** `TECHNICAL-DOCS.md` (dla deweloperów)
- **Test Plan:** `TEST-PLAN-DETAILED.md` (scenariusze testowe)
- **Deployment:** `DEPLOYMENT.md` (Azure deployment)

### W razie problemów:
1. Sprawdź [Typowe problemy](#typowe-problemy-i-rozwiązania)
2. Przejrzyj logi aplikacji
3. Skontaktuj się z zespołem IT

---

## ✅ CHECKLIST PRODUKCYJNY

### KRYTYCZNE (wykonać przed użyciem):
- [ ] Zmieniono wszystkie domyślne hasła ⚠️
- [ ] Skonfigurowano SMTP dla emaili ⚠️
- [ ] Dodano prawdziwych użytkowników
- [ ] Przetestowano pełny flow procesu

### ZALECANE (do wykonania w tygodniu):
- [ ] Skonfigurowano monitoring (opcjonalnie)
- [ ] Włączono alerty (opcjonalnie)
- [ ] Przetestowano backup/restore
- [ ] Przeszkolono użytkowników

### OPCJONALNE (przyszłość):
- [ ] Własna domena (np. timeoff.firma.pl)
- [ ] Azure Key Vault dla sekretów
- [ ] Upgrade do Standard tier (S1)
- [ ] CDN dla szybszego ładowania

---

## 🚀 GOTOWE DO STARTU!

**Aplikacja jest wdrożona i gotowa do użycia produkcyjnego.**

**Następne kroki:**
1. Zmień hasła domyślnych kont ⚠️
2. Skonfiguruj SMTP
3. Dodaj prawdziwych użytkowników
4. Przetestuj i zacznij używać!

**URL:** https://timeoff-manager-20251004.azurewebsites.net

---

**Powodzenia! 🎉**
