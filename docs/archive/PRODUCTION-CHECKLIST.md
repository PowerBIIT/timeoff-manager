# ✅ Production Deployment Checklist

## 🔐 Bezpieczeństwo

### Przed deploymentem:
- [ ] Wygenerowano silny `SECRET_KEY` (min. 32 znaki hex)
- [ ] Ustawiono silne hasło do bazy danych PostgreSQL (min. 16 znaków, litery, cyfry, znaki specjalne)
- [ ] Sprawdzono, że plik `.env` jest w `.gitignore` (nie commituj sekretów!)
- [ ] Ustawiono `FLASK_ENV=production` w zmiennych środowiskowych

### Po deploymencie:
- [ ] Zmieniono hasło domyślnego konta admin (`admin@firma.pl`)
- [ ] Zmieniono lub usunięto konta testowe (`manager@firma.pl`, `jan@firma.pl`)
- [ ] Wymuszono HTTPS only w Azure App Service
- [ ] Sprawdzono konfigurację CORS (tylko dozwolone domeny)
- [ ] (Opcjonalnie) Skonfigurowano Azure Key Vault dla sekretów

---

## 🗄️ Baza Danych

- [ ] PostgreSQL Flexible Server wdrożony na Azure
- [ ] SSL/TLS wymuszony dla połączeń (`sslmode=require`)
- [ ] Firewall skonfigurowany (tylko Azure services + trusted IPs)
- [ ] Automatyczne backupy włączone (min. 7 dni retention)
- [ ] Baza danych zainicjalizowana (`python init_db.py` przez startup.sh)
- [ ] Sprawdzono połączenie z aplikacją

---

## 📧 Powiadomienia Email

- [ ] SMTP skonfigurowane w admin panelu lub przez zmienne środowiskowe
- [ ] Test wysłania emaila (Ustawienia → Test SMTP)
- [ ] Sprawdzono, że emaile trafiają do inbox (nie spam)
- [ ] Skonfigurowano SPF/DKIM dla domeny (jeśli wysyłasz z własnej domeny)

**Provider SMTP:**
- [ ] Gmail App Password utworzony (jeśli Gmail)
- [ ] Office 365 / SendGrid / AWS SES skonfigurowany (jeśli inne)

---

## 🌐 Azure App Service

### Konfiguracja:
- [ ] Web App wdrożony (Python 3.11)
- [ ] Startup command: `startup.sh`
- [ ] Zmienne środowiskowe ustawione:
  - [ ] `DATABASE_URL`
  - [ ] `SECRET_KEY`
  - [ ] `FLASK_ENV=production`
  - [ ] `APP_NAME`
- [ ] HTTPS wymuszony
- [ ] Logi aplikacji włączone (filesystem + blob storage opcjonalnie)

### Monitoring:
- [ ] Health check endpoint działa (`/health`)
- [ ] Application Insights skonfigurowany (opcjonalnie)
- [ ] Alerty ustawione dla:
  - [ ] High error rate (>5% HTTP 5xx)
  - [ ] Slow response time (>3s)
  - [ ] High CPU/Memory usage (>80%)

---

## 👥 Użytkownicy

- [ ] Domyślne konta testowe usunięte lub hasła zmienione
- [ ] Pierwsi prawdziwi użytkownicy dodani (admin, managerowie, pracownicy)
- [ ] Struktura organizacyjna skonfigurowana (pracownicy przypisani do managerów)
- [ ] Uprawnienia sprawdzone (każda rola widzi tylko to co powinna)

---

## 🧪 Testowanie

### Testy funkcjonalne:
- [ ] **Logowanie** - wszystkie role mogą się zalogować
- [ ] **Pracownik**:
  - [ ] Może złożyć wniosek
  - [ ] Widzi tylko swoje wnioski
  - [ ] Może anulować wniosek (status: oczekujący)
  - [ ] Otrzymuje email po decyzji managera
- [ ] **Manager**:
  - [ ] Widzi oczekujące wnioski swojego zespołu
  - [ ] Może zaakceptować wniosek
  - [ ] Może odrzucić wniosek (z komentarzem)
  - [ ] Otrzymuje email o nowym wniosku
- [ ] **Admin**:
  - [ ] Może dodać użytkownika
  - [ ] Może edytować użytkownika
  - [ ] Może usunąć użytkownika (walidacja: brak wniosków)
  - [ ] Może skonfigurować SMTP
  - [ ] Widzi audit log

### Testy bezpieczeństwa:
- [ ] Nie można zalogować bez tokenu
- [ ] Nie można wykonać akcji bez odpowiedniej roli
- [ ] Manager nie widzi wniosków innego zespołu
- [ ] Pracownik nie może anulować wniosku innego pracownika
- [ ] Szczegóły błędów nie są widoczne w produkcji

### Testy wydajności (opcjonalnie):
- [ ] Aplikacja odpowiada szybko (<1s średnio)
- [ ] Baza danych obsługuje concurrent requests
- [ ] Frontend działa na mobile

---

## 📊 Backup & Recovery

- [ ] Automatyczne backupy bazy danych włączone
- [ ] Backup retention period ustawiony (min. 7 dni, zalecane 30)
- [ ] Point-in-time restore przetestowany (na staging)
- [ ] Procedura recovery udokumentowana
- [ ] Manual backup wykonany przed go-live

---

## 🌍 Domena & SSL

- [ ] Własna domena skonfigurowana (opcjonalnie)
- [ ] SSL certificate zainstalowany (Azure managed lub custom)
- [ ] DNS records zaktualizowane
- [ ] Subdomain dla staging/UAT (opcjonalnie)

---

## 📝 Dokumentacja

- [ ] README.md zaktualizowany (URL produkcji, konta, etc.)
- [ ] DEPLOYMENT.md przeczytany i zrozumiany przez zespół
- [ ] Procedury operacyjne udokumentowane:
  - [ ] Jak dodać użytkownika
  - [ ] Jak skonfigurować SMTP
  - [ ] Jak sprawdzić logi
  - [ ] Jak wykonać backup/restore
- [ ] Kontakty do wsparcia technicznego ustalone

---

## 🚀 Go-Live

### Dzień przed uruchomieniem:
- [ ] Wszystkie punkty z checklisty sprawdzone ✅
- [ ] Smoke tests wykonane na staging
- [ ] Zespół powiadomiony o uruchomieniu
- [ ] Plan rollback przygotowany (co jeśli coś pójdzie nie tak?)

### W dniu uruchomienia:
- [ ] Deploy wykonany w oknie maintenance
- [ ] Testy smoke po deploymencie
- [ ] Monitoring sprawdzony (logi, metryki, alerty)
- [ ] Użytkownicy finalni powiadomieni
- [ ] Support team w gotowości (pierwsze 24h)

### Po uruchomieniu:
- [ ] Monitorowanie przez pierwsze 48h
- [ ] Feedback od użytkowników zebrany
- [ ] Ewentualne hotfixy wdrożone
- [ ] Post-mortem meeting zaplanowany (co poszło dobrze/źle)

---

## 🔄 Maintenance

### Codziennie:
- [ ] Sprawdzenie logów pod kątem błędów
- [ ] Monitoring metryk (CPU, memory, response time)

### Co tydzień:
- [ ] Sprawdzenie audit log
- [ ] Analiza użycia aplikacji

### Co miesiąc:
- [ ] Aktualizacja zależności (security patches)
- [ ] Review backupów
- [ ] Sprawdzenie przestrzeni dyskowej

### Co kwartał:
- [ ] Security audit
- [ ] Performance review
- [ ] User feedback review

---

## 📞 Kontakty

**W razie problemów:**

1. **Support L1** (podstawowe problemy): ___________
2. **Support L2** (techniczne problemy): ___________
3. **Azure Support**: https://portal.azure.com (Support + help)
4. **Emergency contact**: ___________

**Eskalacja:**
- Severity 1 (Critical - app down): → Natychmiastowa eskalacja
- Severity 2 (High - major feature broken): → Do 2h
- Severity 3 (Medium - minor issue): → Do 24h
- Severity 4 (Low - cosmetic): → Next sprint

---

## ✅ Sign-off

**Przed przejściem do produkcji, następujące osoby muszą zatwierdzić:**

- [ ] **Tech Lead**: _____________ (Data: ________)
- [ ] **DevOps Engineer**: _____________ (Data: ________)
- [ ] **Security Officer**: _____________ (Data: ________)
- [ ] **Product Owner**: _____________ (Data: ________)

---

**🎉 Aplikacja gotowa do produkcji!**

Data uruchomienia: ______________
