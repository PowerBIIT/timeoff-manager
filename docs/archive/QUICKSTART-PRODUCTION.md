# 🚀 Quick Start - Production Deployment

## Wdrożenie produkcyjne w 15 minut

### ✅ Przed rozpoczęciem

**Wymagania:**
- Azure CLI zainstalowane (`az --version`)
- Konto Azure z aktywną subskrypcją
- 15 minut czasu

---

## 📝 Krok 1: Przygotowanie (2 min)

```bash
# Zaloguj się do Azure
az login

# Sklonuj repozytorium
git clone <repository-url>
cd timeoff-manager

# Ustaw zmienne środowiskowe
export DB_PASSWORD="TwojeBardzoBezpieczneHaslo123!@#"
export RESOURCE_GROUP="timeoff-production"
export APP_NAME="timeoff-manager-prod"
export LOCATION="westeurope"
```

**⚠️ WAŻNE:** Użyj silnego hasła (min. 16 znaków, litery, cyfry, znaki specjalne)

---

## 🚀 Krok 2: Deployment (10 min)

```bash
# Uruchom skrypt deploymentu
chmod +x azure-deploy.sh
./azure-deploy.sh
```

Skrypt automatycznie:
1. Utworzy Resource Group
2. Wdroży PostgreSQL (z SSL)
3. Utworzy bazę danych
4. Wdroży Web App
5. Skonfiguruje zmienne środowiskowe
6. Wymusi HTTPS
7. Uruchomi aplikację

**Poczekaj ~10 minut na zakończenie deploymentu.**

---

## 🔐 Krok 3: Pierwsza konfiguracja (3 min)

### 3.1 Otwórz aplikację

```
https://[APP_NAME].azurewebsites.net
```

### 3.2 Zaloguj się jako admin

**Email:** `admin@firma.pl`
**Hasło:** `admin123`

### 3.3 **NATYCHMIAST zmień hasło!**

1. Przejdź do **Użytkownicy**
2. Kliknij **Edytuj** przy koncie admin
3. Ustaw nowe, silne hasło
4. Zapisz

### 3.4 Usuń lub zmień konta testowe

- `manager@firma.pl` → Zmień hasło lub usuń
- `jan@firma.pl` → Zmień hasło lub usuń

---

## 📧 Krok 4: Konfiguracja SMTP (opcjonalnie, 2 min)

### Dla Gmail:

1. Zaloguj się jako admin
2. Przejdź do **Ustawienia**
3. Wypełnij formularz SMTP:
   - **Server:** `smtp.gmail.com`
   - **Port:** `587`
   - **Use SSL:** `true`
   - **Login:** `your-email@gmail.com`
   - **Password:** `[App Password]` ← **NIE** hasło do Gmail!
   - **Email From:** `system@firma.pl`
4. Kliknij **Zapisz**

**Jak utworzyć App Password:**
https://myaccount.google.com/apppasswords

---

## 👥 Krok 5: Dodaj użytkowników (2 min)

1. Przejdź do **Użytkownicy**
2. Kliknij **Dodaj użytkownika**
3. Wypełnij dane:
   - Email
   - Hasło (min. 8 znaków)
   - Imię i nazwisko
   - Rola (pracownik/manager/admin)
   - Manager (dla pracowników)
4. Zapisz

---

## ✅ Krok 6: Test funkcjonalności (3 min)

### Test scenariusz:

**Jako Pracownik:**
1. Zaloguj się kontem pracownika
2. Przejdź do **Nowy wniosek**
3. Wypełnij formularz (data, godziny, powód)
4. Złóż wniosek

**Jako Manager:**
1. Wyloguj się
2. Zaloguj jako manager
3. Przejdź do **Oczekujące wnioski**
4. Zobacz wniosek od pracownika
5. Zaakceptuj lub odrzuć

**Sprawdź email** - pracownik powinien dostać powiadomienie!

---

## 📊 Monitorowanie

### Sprawdź logi:
```bash
az webapp log tail \
  --resource-group timeoff-production \
  --name timeoff-manager-prod
```

### Health check:
```bash
curl https://timeoff-manager-prod.azurewebsites.net/health
```

Odpowiedź:
```json
{"status": "healthy", "app": "TimeOff Manager"}
```

---

## 🔒 Security Checklist

Po deploymencie upewnij się, że:

- [x] Zmieniono hasło admina
- [x] Usunięto/zmieniono konta testowe
- [x] HTTPS wymuszony (automatycznie przez skrypt)
- [x] Firewall PostgreSQL skonfigurowany (automatycznie)
- [x] SSL dla bazy danych włączony (automatycznie)

**Dodatkowe (opcjonalne):**
- [ ] Własna domena skonfigurowana
- [ ] Azure Key Vault dla sekretów
- [ ] Application Insights (monitoring)
- [ ] Alerty ustawione

---

## 🐛 Troubleshooting

### Aplikacja nie działa?

```bash
# Sprawdź logi
az webapp log tail --resource-group timeoff-production --name timeoff-manager-prod

# Zrestartuj aplikację
az webapp restart --resource-group timeoff-production --name timeoff-manager-prod
```

### Email nie działa?

1. Sprawdź App Password (Gmail) - czy poprawny?
2. Czy 2FA włączone w Gmail?
3. Sprawdź logi: `az webapp log tail ... | grep -i email`

### Błąd połączenia z bazą?

```bash
# Sprawdź firewall
az postgres flexible-server firewall-rule list \
  --resource-group timeoff-production \
  --name timeoff-db-prod
```

---

## 📚 Więcej informacji

- **Pełna dokumentacja:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Production checklist:** [PRODUCTION-CHECKLIST.md](PRODUCTION-CHECKLIST.md)
- **README:** [README.md](README.md)

---

## 🗑️ Jak usunąć zasoby

```bash
# Usuń całą grupę zasobów (NIE DA SIĘ COFNĄĆ!)
az group delete --name timeoff-production --yes
```

---

## ✅ Gotowe!

**Aplikacja TimeOff Manager działa w produkcji!** 🎉

**URL:** `https://[APP_NAME].azurewebsites.net`

**Następne kroki:**
1. Dodaj więcej użytkowników
2. Skonfiguruj własną domenę (opcjonalnie)
3. Ustaw monitoring i alerty
4. Przeczytaj [PRODUCTION-CHECKLIST.md](PRODUCTION-CHECKLIST.md)

---

**Potrzebujesz pomocy?** Sprawdź [DEPLOYMENT.md](DEPLOYMENT.md) lub otwórz issue w repozytorium.
