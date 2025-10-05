# 🧪 Kompleksowy Plan Testów - TimeOff Manager

**Data utworzenia:** 2025-10-05
**Wersja aplikacji:** develop (55b094a)
**URL DEV:** https://timeoff-manager-dev.azurewebsites.net
**Autor:** Plan testów wygenerowany automatycznie

---

## 📋 Spis treści

1. [Informacje ogólne](#informacje-ogólne)
2. [Konta testowe](#konta-testowe)
3. [Testy funkcjonalne - Pracownik](#testy-funkcjonalne---pracownik)
4. [Testy funkcjonalne - Manager](#testy-funkcjonalne---manager)
5. [Testy funkcjonalne - Administrator](#testy-funkcjonalne---administrator)
6. [Testy bezpieczeństwa](#testy-bezpieczeństwa)
7. [Testy UI/UX](#testy-uiux)
8. [Testy integracyjne](#testy-integracyjne)
9. [Edge cases i scenariusze graniczne](#edge-cases-i-scenariusze-graniczne)
10. [Checklist wykonania](#checklist-wykonania)

---

## Informacje ogólne

### Cel testów
Kompleksowa weryfikacja wszystkich funkcjonalności systemu TimeOff Manager, włączając:
- Wszystkie role użytkowników (Pracownik, Manager, Administrator)
- Pełny flow zarządzania wnioskami
- Zarządzanie użytkownikami
- Bezpieczeństwo i autoryzację
- UI/UX i responsywność
- Edge cases i błędne dane

### Metodologia
- **Rodzaj:** Manualne testy funkcjonalne E2E
- **Przeglądarka:** Chrome/Firefox (desktop + mobile view)
- **Środowisko:** DEV (timeoff-manager-dev.azurewebsites.net)
- **Status:** ⬜ Do wykonania | ✅ Przeszedł | ❌ Niepowodzenie | ⚠️ Częściowo

---

## Konta testowe

| Rola | Email | Hasło | Przełożony |
|------|-------|-------|------------|
| **Administrator** | admin@firma.pl | admin123 | - |
| **Manager** | manager@firma.pl | manager123 | Admin |
| **Pracownik** | jan@firma.pl | jan123 | Manager |

**Uwaga:** Przed testami upewnij się, że baza jest w stanie początkowym (użyj `init_db.py` jeśli potrzeba).

---

## Testy funkcjonalne - Pracownik

### TC-P-001: Logowanie Pracownika
**Priorytet:** Krytyczny
**Opis:** Weryfikacja logowania użytkownika z rolą Pracownik

**Kroki:**
1. Otwórz aplikację https://timeoff-manager-dev.azurewebsites.net
2. Wprowadź email: `jan@firma.pl`
3. Wprowadź hasło: `jan123`
4. Kliknij "Zaloguj się"

**Oczekiwany rezultat:**
- ✅ Użytkownik zostaje zalogowany
- ✅ Dashboard wyświetla "Witaj, Jan!"
- ✅ Widoczne menu: Dashboard, Nowy wniosek, Moje wnioski
- ✅ Brak menu: Oczekujące, Użytkownicy, Ustawienia, Audit Log
- ✅ Stopka wyświetla commit, datę, branch

**Status:** ⬜

---

### TC-P-002: Dashboard Pracownika - Statystyki
**Priorytet:** Wysoki
**Opis:** Weryfikacja wyświetlania statystyk wniosków na dashboardzie

**Pre-warunki:** Zalogowany jako jan@firma.pl

**Kroki:**
1. Sprawdź kartę "Wszystkie"
2. Sprawdź kartę "Oczekujące"
3. Sprawdź kartę "Zaakceptowane"
4. Sprawdź kartę "Odrzucone"

**Oczekiwany rezultat:**
- ✅ Karty wyświetlają poprawną liczbę wniosków
- ✅ Liczby są zgodne z rzeczywistym stanem w bazie
- ✅ Ikony są wyświetlane poprawnie
- ✅ Karty są klikalne (opcjonalnie)

**Status:** ⬜

---

### TC-P-003: Tworzenie nowego wniosku - Poprawne dane
**Priorytet:** Krytyczny
**Opis:** Pracownik tworzy nowy wniosek o wyjście służbowe

**Pre-warunki:** Zalogowany jako jan@firma.pl

**Kroki:**
1. Kliknij "Nowy wniosek"
2. Wybierz datę: jutrzejsza data
3. Wprowadź godzinę wyjścia: 10:00
4. Wprowadź godzinę powrotu: 14:00
5. Wprowadź powód: "Wizyta u lekarza specjalisty - badania kontrolne"
6. Kliknij "Wyślij wniosek"

**Oczekiwany rezultat:**
- ✅ Wyświetla się toast "Wniosek został utworzony"
- ✅ Przekierowanie do "Moje wnioski"
- ✅ Nowy wniosek jest widoczny na liście
- ✅ Status wniosku: "oczekujący"
- ✅ Wyświetla się przełożony: "Manager Testowy"
- ✅ Data utworzenia jest dzisiejsza

**Status:** ⬜

---

### TC-P-004: Walidacja formularza - Godzina powrotu wcześniejsza niż wyjście
**Priorytet:** Wysoki
**Opis:** System powinien walidować kolejność godzin

**Pre-warunki:** Zalogowany jako jan@firma.pl

**Kroki:**
1. Kliknij "Nowy wniosek"
2. Wybierz datę: jutrzejsza data
3. Wprowadź godzinę wyjścia: 14:00
4. Wprowadź godzinę powrotu: 10:00 (wcześniej niż wyjście!)
5. Wprowadź powód: "Test walidacji"
6. Kliknij "Wyślij wniosek"

**Oczekiwany rezultat:**
- ✅ Wyświetla się błąd: "Godzina powrotu musi być późniejsza niż wyjście!"
- ✅ Wniosek NIE zostaje utworzony
- ✅ Użytkownik pozostaje na formularzu

**Status:** ⬜

---

### TC-P-005: Walidacja formularza - Zbyt krótki powód
**Priorytet:** Średni
**Opis:** Powód musi mieć minimum 10 znaków

**Pre-warunki:** Zalogowany jako jan@firma.pl

**Kroki:**
1. Kliknij "Nowy wniosek"
2. Wybierz datę: jutrzejsza data
3. Wprowadź godzinę wyjścia: 10:00
4. Wprowadź godzinę powrotu: 14:00
5. Wprowadź powód: "Test" (tylko 4 znaki)
6. Kliknij "Wyślij wniosek"

**Oczekiwany rezultat:**
- ✅ Wyświetla się błąd: "Powód musi mieć minimum 10 znaków"
- ✅ Wniosek NIE zostaje utworzony

**Status:** ⬜

---

### TC-P-006: Moje wnioski - Lista wniosków
**Priorytet:** Wysoki
**Opis:** Pracownik widzi wszystkie swoje wnioski z pełnymi danymi

**Pre-warunki:**
- Zalogowany jako jan@firma.pl
- Istnieje minimum 1 wniosek zaakceptowany z wcześniejszych testów

**Kroki:**
1. Kliknij "Moje wnioski"
2. Sprawdź listę wniosków
3. Sprawdź filtr "Wszystkie"
4. Sprawdź filtr "Zaakceptowane"
5. Sprawdź filtr "Oczekujące"

**Oczekiwany rezultat:**
- ✅ Wyświetlają się wszystkie wnioski pracownika
- ✅ Dla każdego wniosku widoczne:
  - Status (OCZEKUJĄCY/ZAAKCEPTOWANY/ODRZUCONY)
  - Numer ID
  - Data wyjścia
  - Godziny (wyjście - powrót)
  - Przełożony
  - Data utworzenia
  - **Data decyzji** (jeśli wniosek rozpatrzony)
  - Powód
  - Komentarz managera (jeśli odrzucony)
- ✅ Filtry działają poprawnie
- ✅ Dla oczekujących widoczny przycisk "Anuluj"

**Status:** ⬜

---

### TC-P-007: Anulowanie wniosku oczekującego
**Priorytet:** Wysoki
**Opis:** Pracownik może anulować swój wniosek o ile ma status "oczekujący"

**Pre-warunki:**
- Zalogowany jako jan@firma.pl
- Istnieje wniosek ze statusem "oczekujący"

**Kroki:**
1. Kliknij "Moje wnioski"
2. Znajdź wniosek ze statusem "oczekujący"
3. Kliknij przycisk "Anuluj"

**Oczekiwany rezultat:**
- ✅ Wyświetla się toast "Wniosek został anulowany"
- ✅ Status wniosku zmienia się na "anulowany"
- ✅ Przycisk "Anuluj" znika
- ✅ Wniosek pozostaje na liście (soft delete)

**Status:** ⬜

---

### TC-P-008: Próba anulowania zaakceptowanego wniosku
**Priorytet:** Średni
**Opis:** Pracownik NIE MOŻE anulować wniosku, który został już rozpatrzony

**Pre-warunki:**
- Zalogowany jako jan@firma.pl
- Istnieje wniosek ze statusem "zaakceptowany" lub "odrzucony"

**Kroki:**
1. Kliknij "Moje wnioski"
2. Znajdź wniosek ze statusem "zaakceptowany" lub "odrzucony"
3. Sprawdź czy widoczny przycisk "Anuluj"

**Oczekiwany rezultat:**
- ✅ Przycisk "Anuluj" NIE JEST widoczny
- ✅ Niemożliwa jest modyfikacja wniosku

**Status:** ⬜

---

### TC-P-009: Próba dostępu do panel Admina
**Priorytet:** Krytyczny (bezpieczeństwo)
**Opis:** Pracownik NIE MOŻE uzyskać dostępu do panelu administracyjnego

**Pre-warunki:** Zalogowany jako jan@firma.pl

**Kroki:**
1. Sprawdź menu boczne
2. Spróbuj ręcznie przejść do URL:
   - `/api/users` (API)
   - Kliknij w konsoli przeglądarki: `window.location.hash = '#users'`

**Oczekiwany rezultat:**
- ✅ Menu NIE wyświetla opcji: "Oczekujące", "Użytkownicy", "Ustawienia", "Audit Log"
- ✅ Próba dostępu do API zwraca 403 Forbidden
- ✅ Frontend nie pozwala na zmianę widoku

**Status:** ⬜

---

### TC-P-010: Wylogowanie Pracownika
**Priorytet:** Wysoki
**Opis:** Poprawne wylogowanie z systemu

**Pre-warunki:** Zalogowany jako jan@firma.pl

**Kroki:**
1. Kliknij "Wyloguj się"
2. Sprawdź czy nastąpiło przekierowanie
3. Spróbuj wcisnąć przycisk "Wstecz" w przeglądarce

**Oczekiwany rezultat:**
- ✅ Przekierowanie do strony logowania
- ✅ Toast: "Zostałeś wylogowany"
- ✅ Token JWT został usunięty (localStorage)
- ✅ Przycisk "Wstecz" NIE pozwala wrócić do dashboardu (wymaga ponownego logowania)

**Status:** ⬜

---

## Testy funkcjonalne - Manager

### TC-M-001: Logowanie Managera
**Priorytet:** Krytyczny
**Opis:** Weryfikacja logowania użytkownika z rolą Manager

**Kroki:**
1. Otwórz aplikację
2. Wprowadź email: `manager@firma.pl`
3. Wprowadź hasło: `manager123`
4. Kliknij "Zaloguj się"

**Oczekiwany rezultat:**
- ✅ Dashboard wyświetla "Witaj, Manager!"
- ✅ Widoczne menu: Dashboard, Nowy wniosek, Moje wnioski, **Oczekujące**
- ✅ Brak menu: Użytkownicy, Ustawienia, Audit Log
- ✅ Stopka wyświetla wersję

**Status:** ⬜

---

### TC-M-002: Dashboard Managera - Statystyki zespołu
**Priorytet:** Wysoki
**Opis:** Manager widzi statystyki swoich wniosków (nie zespołu)

**Pre-warunki:** Zalogowany jako manager@firma.pl

**Kroki:**
1. Sprawdź karty na dashboardzie
2. Porównaj z rzeczywistym stanem wniosków

**Oczekiwany rezultat:**
- ✅ Karty pokazują wnioski MANAGERA (nie zespołu)
- ✅ Dashboard działa identycznie jak dla Pracownika (Manager też może składać wnioski)

**Status:** ⬜

---

### TC-M-003: Lista oczekujących wniosków
**Priorytet:** Krytyczny
**Opis:** Manager widzi wszystkie oczekujące wnioski swojego zespołu

**Pre-warunki:**
- Zalogowany jako manager@firma.pl
- Pracownik Jan ma wniosek ze statusem "oczekujący"

**Kroki:**
1. Kliknij "Oczekujące"
2. Sprawdź listę wniosków

**Oczekiwany rezultat:**
- ✅ Wyświetlają się tylko wnioski ze statusem "oczekujący"
- ✅ Wyświetlają się wnioski, gdzie manager_id = ID managera
- ✅ Dla każdego wniosku widoczne:
  - Imię i nazwisko pracownika
  - Email pracownika
  - Data wyjścia
  - Godziny (wyjście - powrót)
  - Data złożenia
  - **Data decyzji** (pole puste dla oczekujących)
  - Powód
  - Przyciski: "Zaakceptuj" i "Odrzuć"

**Status:** ⬜

---

### TC-M-004: Akceptacja wniosku
**Priorytet:** Krytyczny
**Opis:** Manager akceptuje wniosek pracownika

**Pre-warunki:**
- Zalogowany jako manager@firma.pl
- Istnieje wniosek oczekujący od Jana

**Kroki:**
1. Kliknij "Oczekujące"
2. Znajdź wniosek od Jana
3. Kliknij "✅ Zaakceptuj"

**Oczekiwany rezultat:**
- ✅ Wyświetla się toast "Wniosek został zaakceptowany"
- ✅ Wniosek znika z listy oczekujących
- ✅ W bazie danych:
  - `status` = 'zaakceptowany'
  - `decision_date` = dzisiejsza data
  - `manager_comment` = NULL lub pusty
- ✅ Pracownik Jan widzi zaktualizowany status w "Moje wnioski"
- ✅ **Data decyzji** jest wypełniona w widoku pracownika

**Status:** ⬜

---

### TC-M-005: Odrzucenie wniosku z komentarzem
**Priorytet:** Krytyczny
**Opis:** Manager odrzuca wniosek z uzasadnieniem

**Pre-warunki:**
- Zalogowany jako manager@firma.pl
- Istnieje wniosek oczekujący od Jana

**Kroki:**
1. Kliknij "Oczekujące"
2. Znajdź wniosek od Jana
3. Kliknij "❌ Odrzuć"
4. W modalu wprowadź komentarz: "Zbyt dużo nieobecności w tym miesiącu"
5. Kliknij "Odrzuć"

**Oczekiwany rezultat:**
- ✅ Wyświetla się modal z polem tekstowym na komentarz
- ✅ Po kliknięciu "Odrzuć":
  - Toast: "Wniosek został odrzucony"
  - Wniosek znika z listy
- ✅ W bazie danych:
  - `status` = 'odrzucony'
  - `decision_date` = dzisiejsza data
  - `manager_comment` = wprowadzony komentarz
- ✅ Pracownik Jan widzi:
  - Status "odrzucony"
  - **Data decyzji**
  - Czerwone pole z komentarzem managera

**Status:** ⬜

---

### TC-M-006: Odrzucenie wniosku bez komentarza
**Priorytet:** Średni
**Opis:** Manager może odrzucić wniosek bez podawania powodu (komentarz opcjonalny)

**Pre-warunki:**
- Zalogowany jako manager@firma.pl
- Istnieje wniosek oczekujący

**Kroki:**
1. Kliknij "Oczekujące"
2. Kliknij "❌ Odrzuć"
3. Zostaw pole komentarza puste
4. Kliknij "Odrzuć"

**Oczekiwany rezultat:**
- ✅ Wniosek zostaje odrzucony
- ✅ `manager_comment` = NULL lub pusty
- ✅ Pracownik NIE widzi czerwonego pola z komentarzem

**Status:** ⬜

---

### TC-M-007: Anulowanie odrzucenia (modal)
**Priorytet:** Niski
**Opis:** Manager może zamknąć modal odrzucenia bez podejmowania akcji

**Pre-warunki:**
- Zalogowany jako manager@firma.pl
- Istnieje wniosek oczekujący

**Kroki:**
1. Kliknij "Oczekujące"
2. Kliknij "❌ Odrzuć"
3. Wprowadź komentarz
4. Kliknij "Anuluj" (zamiast "Odrzuć")

**Oczekiwany rezultat:**
- ✅ Modal zamyka się
- ✅ Wniosek pozostaje na liście oczekujących
- ✅ Status się NIE zmienia

**Status:** ⬜

---

### TC-M-008: Manager tworzy własny wniosek
**Priorytet:** Średni
**Opis:** Manager również może składać wnioski o wyjście (ma przełożonego - Admina)

**Pre-warunki:** Zalogowany jako manager@firma.pl

**Kroki:**
1. Kliknij "Nowy wniosek"
2. Wypełnij formularz:
   - Data: jutrzejsza
   - Godzina wyjścia: 09:00
   - Godzina powrotu: 12:00
   - Powód: "Szkolenie zewnętrzne z zarządzania zespołem"
3. Kliknij "Wyślij wniosek"

**Oczekiwany rezultat:**
- ✅ Wniosek zostaje utworzony
- ✅ W bazie: `manager_id` = ID Admina (przełożony Managera)
- ✅ Manager widzi swój wniosek w "Moje wnioski"
- ✅ Admin widzi wniosek w "Oczekujące"
- ✅ Manager NIE WIDZI swojego wniosku w "Oczekujące" (nie może sam sobie zatwierdzić)

**Status:** ⬜

---

### TC-M-009: Próba dostępu do panelu Użytkowników
**Priorytet:** Krytyczny (bezpieczeństwo)
**Opis:** Manager NIE MOŻE zarządzać użytkownikami

**Pre-warunki:** Zalogowany jako manager@firma.pl

**Kroki:**
1. Sprawdź menu boczne
2. Spróbuj dostępu do API: `GET /api/users` (bez filtra `?role=manager`)

**Oczekiwany rezultat:**
- ✅ Menu NIE wyświetla "Użytkownicy", "Ustawienia", "Audit Log"
- ✅ API `/api/users` zwraca tylko listę managerów i adminów (nie pełna lista)
- ✅ Próba `POST /api/users` (tworzenie użytkownika) zwraca 403

**Status:** ⬜

---

### TC-M-010: Wylogowanie Managera
**Priorytet:** Wysoki
**Opis:** Poprawne wylogowanie

**Pre-warunki:** Zalogowany jako manager@firma.pl

**Kroki:**
1. Kliknij "Wyloguj się"

**Oczekiwany rezultat:**
- ✅ Przekierowanie do strony logowania
- ✅ Token JWT usunięty
- ✅ Wstecz nie działa

**Status:** ⬜

---

## Testy funkcjonalne - Administrator

### TC-A-001: Logowanie Administratora
**Priorytet:** Krytyczny
**Opis:** Weryfikacja logowania użytkownika z rolą Admin

**Kroki:**
1. Otwórz aplikację
2. Wprowadź email: `admin@firma.pl`
3. Wprowadź hasło: `admin123`
4. Kliknij "Zaloguj się"

**Oczekiwany rezultat:**
- ✅ Dashboard wyświetla "Witaj, Admin!"
- ✅ Widoczne WSZYSTKIE menu: Dashboard, Nowy wniosek, Moje wnioski, Oczekujące, **Użytkownicy**, **Ustawienia**, **Audit Log**
- ✅ Stopka wyświetla wersję

**Status:** ⬜

---

### TC-A-002: Lista użytkowników - Wyświetlanie
**Priorytet:** Wysoki
**Opis:** Admin widzi pełną listę użytkowników z wszystkimi danymi

**Pre-warunki:** Zalogowany jako admin@firma.pl

**Kroki:**
1. Kliknij "Użytkownicy"
2. Sprawdź tabelę/listę użytkowników

**Oczekiwany rezultat:**
- ✅ Wyświetlają się WSZYSCY użytkownicy (pracownicy, managerowie, admini)
- ✅ Dla każdego użytkownika widoczne:
  - Imię i nazwisko
  - Email
  - Rola (badge z kolorem)
  - Przełożony (lub "-" jeśli brak)
  - Status (Aktywny/Nieaktywny)
  - Przyciski: Edytuj, Deaktywuj/Aktywuj, Usuń
- ✅ Lista jest sortowana (np. po dacie utworzenia)

**Status:** ⬜

---

### TC-A-003: Tworzenie nowego użytkownika - Pracownik
**Priorytet:** Krytyczny
**Opis:** Admin tworzy nowego pracownika z przełożonym

**Pre-warunki:** Zalogowany jako admin@firma.pl

**Kroki:**
1. Kliknij "Użytkownicy"
2. Kliknij "+ Dodaj użytkownika"
3. Wypełnij formularz:
   - Imię: "Anna"
   - Nazwisko: "Kowalska"
   - Email: "anna.kowalska@firma.pl"
   - Hasło: "TestoweHaslo123!"
   - Rola: "pracownik"
   - Przełożony: "Manager Testowy"
4. Kliknij "Dodaj"

**Oczekiwany rezultat:**
- ✅ Toast: "Użytkownik został dodany"
- ✅ Nowy użytkownik pojawia się na liście
- ✅ Dane w bazie:
  - `first_name` = "Anna"
  - `last_name` = "Kowalska"
  - `email` = "anna.kowalska@firma.pl"
  - `password_hash` = hash hasła (bcrypt)
  - `role` = "pracownik"
  - `supervisor_id` = ID managera
  - `is_active` = true
- ✅ Można zalogować się na nowe konto

**Status:** ⬜

---

### TC-A-004: Walidacja tworzenia użytkownika - Email już istnieje
**Priorytet:** Wysoki
**Opis:** System NIE pozwala na duplikację emaili

**Pre-warunki:** Zalogowany jako admin@firma.pl

**Kroki:**
1. Kliknij "Użytkownicy"
2. Kliknij "+ Dodaj użytkownika"
3. Wprowadź email który już istnieje: "jan@firma.pl"
4. Wypełnij pozostałe pola
5. Kliknij "Dodaj"

**Oczekiwany rezultat:**
- ✅ Wyświetla się błąd: "Użytkownik z tym emailem już istnieje" lub podobny
- ✅ Użytkownik NIE zostaje dodany
- ✅ Modal pozostaje otwarty

**Status:** ⬜

---

### TC-A-005: Walidacja hasła - Zbyt słabe hasło
**Priorytet:** Krytyczny (bezpieczeństwo)
**Opis:** System wymaga silnych haseł (12+ znaków, wielkie, małe, cyfry, znaki specjalne)

**Pre-warunki:** Zalogowany jako admin@firma.pl

**Kroki:**
1. Kliknij "Użytkownicy" → "+ Dodaj użytkownika"
2. Wypełnij formularz z hasłem: "test123" (za krótkie, brak wielkich i znaków specjalnych)
3. Kliknij "Dodaj"

**Oczekiwany rezultat:**
- ✅ Błąd: "Hasło musi mieć minimum 12 znaków"
- ✅ Użytkownik NIE zostaje dodany

**Status:** ⬜

---

### TC-A-006: Walidacja hasła - Wszystkie wymagania
**Priorytet:** Wysoki (bezpieczeństwo)
**Opis:** Testowanie wszystkich wymogów hasła

**Pre-warunki:** Zalogowany jako admin@firma.pl

**Test cases:**

| Hasło | Oczekiwany błąd |
|-------|-----------------|
| `short` | Hasło musi mieć minimum 12 znaków |
| `lowercaseonly12chars` | Hasło musi zawierać przynajmniej jedną wielką literę |
| `UPPERCASEONLY12CHARS` | Hasło musi zawierać przynajmniej jedną małą literę |
| `NoDigitsHere!` | Hasło musi zawierać przynajmniej jedną cyfrę |
| `NoSpecialChar123` | Hasło musi zawierać przynajmniej jeden znak specjalny |
| `ValidPassword123!` | ✅ Hasło poprawne |

**Kroki:** Dla każdego hasła:
1. Kliknij "Użytkownicy" → "+ Dodaj użytkownika"
2. Wprowadź testowe hasło
3. Kliknij "Dodaj"
4. Sprawdź komunikat

**Status:** ⬜

---

### TC-A-007: Edycja użytkownika - Zmiana danych podstawowych
**Priorytet:** Wysoki
**Opis:** Admin edytuje dane użytkownika

**Pre-warunki:**
- Zalogowany jako admin@firma.pl
- Istnieje użytkownik Anna Kowalska

**Kroki:**
1. Kliknij "Użytkownicy"
2. Znajdź "Anna Kowalska"
3. Kliknij "Edytuj"
4. Zmień:
   - Imię: "Anna Maria"
   - Email: "anna.maria.kowalska@firma.pl"
5. Kliknij "Zapisz"

**Oczekiwany rezultat:**
- ✅ Toast: "Użytkownik został zaktualizowany"
- ✅ Dane są zaktualizowane w liście
- ✅ Dane w bazie są zmienione
- ✅ Użytkownik może zalogować się nowym emailem

**Status:** ⬜

---

### TC-A-008: Edycja użytkownika - Zmiana hasła
**Priorytet:** Krytyczny (bezpieczeństwo)
**Opis:** Admin zmienia hasło użytkownika, wszystkie tokeny są unieważniane

**Pre-warunki:**
- Zalogowany jako admin@firma.pl w przeglądarce A
- Zalogowany jako anna.kowalska@firma.pl w przeglądarce B (incognito)

**Kroki:**
1. **Przeglądarka B:** Zaloguj jako Anna, pozostaw otwartą sesję
2. **Przeglądarka A:** Admin → "Użytkownicy" → Edytuj Annę
3. Zmień hasło na: "NoweHaslo2025!@#"
4. Kliknij "Zapisz"
5. **Przeglądarka B:** Spróbuj wykonać akcję (np. utworzyć wniosek)
6. **Nowa karta:** Spróbuj zalogować się jako Anna ze starym hasłem
7. **Nowa karta:** Spróbuj zalogować się jako Anna z nowym hasłem

**Oczekiwany rezultat:**
- ✅ Toast w przeglądarce A: "Użytkownik został zaktualizowany"
- ✅ **Przeglądarka B:** Sesja Anny jest unieważniona (błąd 401 przy akcjach)
- ✅ Anna jest automatycznie wylogowana (token nieważny)
- ✅ Logowanie starym hasłem NIE DZIAŁA
- ✅ Logowanie nowym hasłem DZIAŁA
- ✅ W bazie: `token_version` został zwiększony o 1

**Status:** ⬜

---

### TC-A-009: Edycja użytkownika - Zmiana roli
**Priorytet:** Wysoki
**Opis:** Admin zmienia rolę użytkownika (Pracownik → Manager)

**Pre-warunki:**
- Zalogowany jako admin@firma.pl
- Użytkownik Anna ma rolę "pracownik"

**Kroki:**
1. Kliknij "Użytkownicy" → Edytuj Annę
2. Zmień rolę z "pracownik" na "manager"
3. Kliknij "Zapisz"
4. Wyloguj się z konta admina
5. Zaloguj jako anna.maria.kowalska@firma.pl

**Oczekiwany rezultat:**
- ✅ Rola zmieniona w bazie
- ✅ Po zalogowaniu Anna widzi menu "Oczekujące"
- ✅ Anna może zatwierdzać wnioski swoich podwładnych
- ✅ Token został unieważniony (wymaga ponownego logowania)

**Status:** ⬜

---

### TC-A-010: Edycja użytkownika - Zmiana przełożonego
**Priorytet:** Średni
**Opis:** Admin zmienia przełożonego pracownika

**Pre-warunki:**
- Zalogowany jako admin@firma.pl
- Jan ma przełożonego: Manager
- Istnieje drugi manager (np. Anna po awansie)

**Kroki:**
1. Kliknij "Użytkownicy" → Edytuj Jana
2. Zmień przełożonego z "Manager Testowy" na "Anna Maria Kowalska"
3. Kliknij "Zapisz"
4. Jan tworzy nowy wniosek

**Oczekiwany rezultat:**
- ✅ `supervisor_id` Jana = ID Anny
- ✅ Nowy wniosek Jana ma `manager_id` = ID Anny
- ✅ Anna widzi wniosek Jana w "Oczekujące"
- ✅ Poprzedni manager (Manager Testowy) NIE WIDZI nowego wniosku

**Status:** ⬜

---

### TC-A-011: Dezaktywacja użytkownika
**Priorytet:** Wysoki
**Opis:** Admin dezaktywuje użytkownika (soft delete)

**Pre-warunki:**
- Zalogowany jako admin@firma.pl w przeglądarce A
- Zalogowany jako anna.maria.kowalska@firma.pl w przeglądarce B

**Kroki:**
1. **Przeglądarka A:** Kliknij "Użytkownicy"
2. Znajdź Annę (status: Aktywny)
3. Kliknij "Deaktywuj"
4. **Przeglądarka B:** Spróbuj wykonać akcję jako Anna
5. Wyloguj Annę i spróbuj zalogować ponownie

**Oczekiwany rezultat:**
- ✅ Toast: "Użytkownik został dezaktywowany"
- ✅ Status Anny: "Nieaktywny" (czerwony badge)
- ✅ Przycisk zmienia się na "Aktywuj"
- ✅ W bazie: `is_active` = false
- ✅ **Przeglądarka B:** Sesja Anny jest unieważniona
- ✅ Logowanie zwraca błąd: "Konto zostało dezaktywowane"
- ✅ Anna NIE MOŻE się zalogować
- ✅ Wnioski Anny pozostają w systemie (visible)

**Status:** ⬜

---

### TC-A-012: Reaktywacja użytkownika
**Priorytet:** Średni
**Opis:** Admin reaktywuje zdezaktywowanego użytkownika

**Pre-warunki:**
- Zalogowany jako admin@firma.pl
- Anna jest zdezaktywowana

**Kroki:**
1. Kliknij "Użytkownicy"
2. Znajdź Annę (status: Nieaktywny)
3. Kliknij "Aktywuj"
4. Spróbuj zalogować się jako Anna

**Oczekiwany rezultat:**
- ✅ Toast: "Użytkownik został aktywowany"
- ✅ Status: "Aktywny" (zielony badge)
- ✅ `is_active` = true
- ✅ Anna MOŻE ponownie się zalogować
- ✅ Wszystkie dane/wnioski zachowane

**Status:** ⬜

---

### TC-A-013: Usuwanie użytkownika - Bez wniosków
**Priorytet:** Wysoki
**Opis:** Admin może usunąć użytkownika, który nie ma żadnych wniosków

**Pre-warunki:**
- Zalogowany jako admin@firma.pl
- Nowo utworzony użytkownik bez wniosków (np. "Test User")

**Kroki:**
1. Utwórz nowego użytkownika testowego
2. Kliknij "Użytkownicy"
3. Znajdź użytkownika testowego
4. Kliknij "Usuń"
5. Potwierdź usunięcie

**Oczekiwany rezultat:**
- ✅ Pojawia się potwierdzenie: "Czy na pewno chcesz usunąć użytkownika?"
- ✅ Po potwierdzeniu: Toast "Użytkownik został usunięty"
- ✅ Użytkownik znika z listy
- ✅ Użytkownik jest faktycznie usunięty z bazy (DELETE)

**Status:** ⬜

---

### TC-A-014: Usuwanie użytkownika - Z wnioskami (ochrona)
**Priorytet:** Krytyczny
**Opis:** System NIE POZWALA usunąć użytkownika z wnioskami (zachowanie integralności danych)

**Pre-warunki:**
- Zalogowany jako admin@firma.pl
- Jan ma istniejące wnioski

**Kroki:**
1. Kliknij "Użytkownicy"
2. Znajdź Jana Nowaka (ma wnioski)
3. Kliknij "Usuń"

**Oczekiwany rezultat:**
- ✅ Błąd: "Nie można usunąć użytkownika, który ma powiązane wnioski"
- ✅ Jan pozostaje w systemie
- ✅ Tooltip/hint na przycisku "Usuń": "Usuwa tylko użytkowników bez wniosków"

**Alternatywa:** Zamiast usuwania → użyj dezaktywacji

**Status:** ⬜

---

### TC-A-015: Przepisanie podwładnych (Reassign)
**Priorytet:** Średni
**Opis:** Admin przepisuje wszystkich podwładnych od jednego managera do drugiego

**Pre-warunki:**
- Zalogowany jako admin@firma.pl
- Manager1 ma 2 pracowników: Jan, Anna
- Istnieje Manager2

**Kroki:**
1. Kliknij "Użytkownicy" → Edytuj Manager1
2. Jeśli dostępne: Kliknij "Przepisz podwładnych"
3. Wybierz nowego przełożonego: Manager2
4. Kliknij "Przepisz"
5. Sprawdź listę użytkowników

**Oczekiwany rezultat:**
- ✅ Wszyscy podwładni Manager1 (Jan, Anna) mają teraz `supervisor_id` = ID Manager2
- ✅ Manager2 widzi wnioski Jana i Anny w "Oczekujące"
- ✅ Manager1 NIE WIDZI już tych wniosków

**Uwaga:** Ta funkcja może być niedostępna w UI - wtedy test N/A

**Status:** ⬜

---

### TC-A-016: Konfiguracja SMTP
**Priorytet:** Średni
**Opis:** Admin konfiguruje ustawienia SMTP dla wysyłki emaili

**Pre-warunki:** Zalogowany jako admin@firma.pl

**Kroki:**
1. Kliknij "Ustawienia"
2. Sprawdź sekcję "Konfiguracja SMTP"
3. Wprowadź dane:
   - SMTP Host: smtp.gmail.com
   - SMTP Port: 587
   - Username: test@gmail.com
   - Password: testpassword
   - From Email: noreply@firma.pl
   - From Name: TimeOff System
4. Kliknij "Test połączenia"
5. Kliknij "Zapisz"

**Oczekiwany rezultat:**
- ✅ Formularz wyświetla wszystkie pola
- ✅ "Test połączenia" zwraca status (success/error)
- ✅ Po zapisaniu: Toast "Konfiguracja SMTP zapisana"
- ✅ Dane zapisane w bazie (tabela `smtp_config`)
- ✅ Hasło jest zaszyfrowane (Fernet)

**Status:** ⬜

---

### TC-A-017: Audit Log - Wyświetlanie
**Priorytet:** Średni
**Opis:** Admin przegląda historię akcji w systemie

**Pre-warunki:**
- Zalogowany jako admin@firma.pl
- Wykonano kilka akcji (logowanie, tworzenie wniosku, edycja użytkownika)

**Kroki:**
1. Kliknij "Audit Log"
2. Sprawdź listę wpisów

**Oczekiwany rezultat:**
- ✅ Wyświetla się lista akcji audytowych
- ✅ Dla każdego wpisu widoczne:
  - Data i czas
  - Użytkownik (imię, email)
  - Akcja (USER_LOGIN, REQUEST_CREATED, USER_UPDATED, etc.)
  - Szczegóły (JSON)
- ✅ Lista jest sortowana od najnowszych
- ✅ Możliwość filtrowania/wyszukiwania (jeśli dostępne)

**Status:** ⬜

---

### TC-A-018: Audit Log - Weryfikacja logów po akcjach
**Priorytet:** Wysoki (bezpieczeństwo)
**Opis:** Sprawdzenie czy wszystkie krytyczne akcje są logowane

**Pre-warunki:** Zalogowany jako admin@firma.pl

**Kroki:**
1. Wykonaj akcje:
   - Zaloguj się
   - Utwórz użytkownika
   - Edytuj użytkownika
   - Dezaktywuj użytkownika
   - Usuń użytkownika (bez wniosków)
2. Kliknij "Audit Log"
3. Sprawdź czy każda akcja jest zarejestrowana

**Oczekiwany rezultat:**
- ✅ Każda akcja ma wpis w audit log:
  - USER_LOGIN
  - USER_CREATED
  - USER_UPDATED
  - USER_DEACTIVATED
  - USER_DELETED
- ✅ Szczegóły zawierają pełne informacje (ID użytkownika, co zostało zmienione)

**Status:** ⬜

---

### TC-A-019: Admin tworzy wniosek o wyjście
**Priorytet:** Niski
**Opis:** Admin również może składać wnioski (choć nie ma przełożonego)

**Pre-warunki:** Zalogowany jako admin@firma.pl

**Kroki:**
1. Kliknij "Nowy wniosek"
2. Wypełnij formularz i wyślij

**Oczekiwany rezultat:**
- ✅ Wniosek zostaje utworzony
- ✅ `manager_id` = NULL lub ID samego admina (do weryfikacji w implementacji)
- ✅ Admin widzi wniosek w "Moje wnioski"
- ✅ Nikt nie widzi tego wniosku w "Oczekujące" (brak managera)

**Uwaga:** To edge case - Admin nie powinien mieć przełożonego

**Status:** ⬜

---

### TC-A-020: Wylogowanie Administratora
**Priorytet:** Wysoki
**Opis:** Poprawne wylogowanie

**Pre-warunki:** Zalogowany jako admin@firma.pl

**Kroki:**
1. Kliknij "Wyloguj się"

**Oczekiwany rezultat:**
- ✅ Przekierowanie do strony logowania
- ✅ Token JWT usunięty z localStorage
- ✅ Przycisk "Wstecz" wymaga ponownego logowania

**Status:** ⬜

---

## Testy bezpieczeństwa

### TC-S-001: Rate limiting - Login
**Priorytet:** Krytyczny
**Opis:** Ochrona przed brute-force attack na endpoint logowania

**Kroki:**
1. Wyloguj się (jeśli zalogowany)
2. Wykonaj 6 błędnych prób logowania:
   - Email: jan@firma.pl
   - Hasło: wrongpassword
3. Spróbuj 6. razę

**Oczekiwany rezultat:**
- ✅ Po 5 nieudanych próbach: Błąd "Too many requests" lub podobny
- ✅ Status HTTP: 429 (Too Many Requests)
- ✅ Blokada trwa co najmniej 5 minut
- ✅ Po czasie oczekiwania można ponownie próbować

**Status:** ⬜

---

### TC-S-002: Rate limiting - Tworzenie wniosków
**Priorytet:** Średni
**Opis:** Ochrona przed spamowaniem wniosków

**Pre-warunki:** Zalogowany jako jan@firma.pl

**Kroki:**
1. Utwórz szybko 11 wniosków (skrypt lub szybkie klikanie)

**Oczekiwany rezultat:**
- ✅ Po 10 wnioskach: Błąd rate limiting
- ✅ Status HTTP: 429
- ✅ Wnioski 1-10 zostały utworzone
- ✅ Wniosek 11 został zablokowany

**Status:** ⬜

---

### TC-S-003: JWT Token - Expire po czasie
**Priorytet:** Wysoki
**Opis:** Token wygasa po 8 godzinach

**Pre-warunki:** Zalogowany jako jan@firma.pl

**Kroki:**
1. Zaloguj się i skopiuj token JWT z localStorage
2. Zdekoduj token (jwt.io) i sprawdź `exp` (czas wygaśnięcia)
3. **Symulacja:** Zmień czas systemowy na +9 godzin (lub poczekaj 8h)
4. Spróbuj wykonać akcję (np. utworzyć wniosek)

**Oczekiwany rezultat:**
- ✅ Token ma `exp` = teraz + 8 godzin
- ✅ Po 8 godzinach: błąd 401 Unauthorized
- ✅ Użytkownik jest przekierowywany do logowania

**Status:** ⬜

---

### TC-S-004: JWT Token Blacklist - Wylogowanie
**Priorytet:** Wysoki
**Opis:** Token jest dodawany do blacklisty przy wylogowaniu

**Pre-warunki:**
- Zalogowany jako jan@firma.pl w przeglądarce A
- Skopiuj token JWT przed wylogowaniem

**Kroki:**
1. **Przeglądarka A:** Wyloguj się
2. **Nowa karta/Postman:** Spróbuj użyć starego tokenu do wykonania akcji
   - Request: `GET /api/requests`
   - Header: `Authorization: Bearer <stary_token>`

**Oczekiwany rezultat:**
- ✅ Wylogowanie usuwa token z localStorage
- ✅ Próba użycia starego tokenu zwraca: 401 + "Token has been revoked"
- ✅ Token został dodany do blacklisty (Redis lub in-memory)

**Status:** ⬜

---

### TC-S-005: HTTPS Enforcement
**Priorytet:** Krytyczny (production)
**Opis:** Aplikacja wymusza HTTPS w środowisku produkcyjnym

**Pre-warunki:** Deployment na PROD

**Kroki:**
1. Spróbuj otworzyć: `http://timeoff-manager-20251004.azurewebsites.net`

**Oczekiwany rezultat:**
- ✅ Przekierowanie 301/302 na `https://...`
- ✅ Połączenie jest szyfrowane (SSL/TLS)
- ✅ Brak możliwości połączenia przez HTTP

**Status:** ⬜

---

### TC-S-006: Content Security Policy (CSP)
**Priorytet:** Średni
**Opis:** Aplikacja ma odpowiednie CSP headery

**Kroki:**
1. Otwórz aplikację w Chrome
2. Otwórz DevTools → Network → wybierz dokument HTML
3. Sprawdź Response Headers → `Content-Security-Policy`

**Oczekiwany rezultat:**
- ✅ Header `Content-Security-Policy` jest obecny
- ✅ NIE zawiera `unsafe-eval`
- ✅ Zawiera polityki:
  - `default-src 'self'`
  - `script-src` pozwala tylko na CDN (tailwind, react, babel)
  - `style-src` pozwala tylko na CDN

**Status:** ⬜

---

### TC-S-007: XSS Protection - Powód wniosku
**Priorytet:** Krytyczny
**Opis:** System nie pozwala na wykonanie XSS przez pole tekstowe

**Pre-warunki:** Zalogowany jako jan@firma.pl

**Kroki:**
1. Kliknij "Nowy wniosek"
2. Wprowadź powód: `<script>alert('XSS')</script>`
3. Wyślij wniosek
4. Przejdź do "Moje wnioski" i sprawdź wyświetlanie

**Oczekiwany rezultat:**
- ✅ Wniosek zostaje utworzony
- ✅ Powód jest wyświetlany jako zwykły tekst (escaped)
- ✅ Skrypt NIE JEST wykonywany
- ✅ W HTML widoczne: `&lt;script&gt;alert('XSS')&lt;/script&gt;`

**Status:** ⬜

---

### TC-S-008: SQL Injection Protection - Email
**Priorytet:** Krytyczny
**Opis:** Ochrona przed SQL injection w logowaniu

**Kroki:**
1. Spróbuj zalogować się z payload:
   - Email: `' OR '1'='1`
   - Hasło: `password`

**Oczekiwany rezultat:**
- ✅ Logowanie NIE DZIAŁA
- ✅ Błąd: "Nieprawidłowy email lub hasło"
- ✅ Brak błędów SQL w logach
- ✅ SQLAlchemy używa parametryzowanych zapytań (ORM)

**Status:** ⬜

---

### TC-S-009: Autoryzacja - Próba dostępu do cudzych danych
**Priorytet:** Krytyczny
**Opis:** Pracownik nie może podejrzeć/zmodyfikować cudzych wniosków

**Pre-warunki:**
- Zalogowany jako jan@firma.pl
- Istnieje wniosek Anny (ID=5)

**Kroki:**
1. **API call (Postman/DevTools):** `PUT /api/requests/5/cancel`
   - Header: Authorization token Jana
2. Sprawdź czy wniosek został anulowany

**Oczekiwany rezultat:**
- ✅ Błąd: 403 Forbidden lub "Nie masz uprawnień"
- ✅ Wniosek Anny NIE został zmodyfikowany
- ✅ Backend sprawdza czy `employee_id` = ID zalogowanego użytkownika

**Status:** ⬜

---

### TC-S-010: Timing Attack Protection - Login
**Priorytet:** Średni
**Opis:** Czas odpowiedzi logowania jest stały (constant-time)

**Kroki:**
1. Zmierz czas odpowiedzi dla istniejącego użytkownika:
   - Email: jan@firma.pl
   - Hasło: wrongpassword
   - Repeat 10x, średnia czasu T1
2. Zmierz czas dla nieistniejącego użytkownika:
   - Email: notexist@firma.pl
   - Hasło: wrongpassword
   - Repeat 10x, średnia czasu T2

**Oczekiwany rezultat:**
- ✅ Różnica |T1 - T2| < 50ms
- ✅ Czas odpowiedzi jest konstant (minimum 200ms)
- ✅ Atakujący nie może wywnioskować czy email istnieje

**Status:** ⬜

---

## Testy UI/UX

### TC-UI-001: Responsywność - Mobile (375px)
**Priorytet:** Wysoki
**Opis:** Aplikacja działa poprawnie na małych ekranach

**Kroki:**
1. Otwórz DevTools → Toggle device toolbar
2. Ustaw: iPhone SE (375x667)
3. Zaloguj się jako jan@firma.pl
4. Przetestuj wszystkie widoki

**Oczekiwany rezultat:**
- ✅ Menu boczne jest ukryte
- ✅ Dolna nawigacja mobile jest widoczna
- ✅ Wszystkie przyciski są klikalne
- ✅ Formularze są czytelne
- ✅ Tabele/listy są przewijalne
- ✅ **Scrolling działa do końca strony** (padding-bottom: 120px)
- ✅ Stopka nie zasłania treści

**Status:** ⬜

---

### TC-UI-002: Responsywność - Tablet (768px)
**Priorytet:** Średni
**Opis:** Aplikacja działa na tabletach

**Kroki:**
1. DevTools → iPad (768x1024)
2. Zaloguj się i przetestuj widoki

**Oczekiwany rezultat:**
- ✅ Layout przełącza się między mobile a desktop
- ✅ Wszystkie funkcje dostępne
- ✅ Czytelność zachowana

**Status:** ⬜

---

### TC-UI-003: Dark Mode (przyszłość)
**Priorytet:** Niski
**Opis:** Sprawdzenie czy istnieje dark mode

**Kroki:**
1. Sprawdź w ustawieniach systemowych dark mode
2. Załaduj aplikację

**Oczekiwany rezultat:**
- ⚠️ Dark mode NIE jest obecnie zaimplementowany (przyszła feature)

**Status:** N/A

---

### TC-UI-004: Ładowanie - Spinnery
**Priorytet:** Niski
**Opis:** Podczas ładowania danych wyświetlane są wskaźniki

**Kroki:**
1. Zaloguj się
2. Kliknij "Moje wnioski" z wolnym połączeniem (DevTools → Network → Slow 3G)

**Oczekiwany rezultat:**
- ✅ Wyświetla się spinner/loading indicator
- ✅ Po załadowaniu danych spinner znika
- ✅ Brak "flash of unstyled content"

**Status:** ⬜

---

### TC-UI-005: Toast Notifications
**Priorytet:** Średni
**Opis:** Powiadomienia są czytelne i znikają automatycznie

**Pre-warunki:** Zalogowany jako jan@firma.pl

**Kroki:**
1. Utwórz nowy wniosek (sukces)
2. Spróbuj utworzyć wniosek z błędnymi danymi (error)
3. Wyloguj się (info)

**Oczekiwany rezultat:**
- ✅ Toast pojawia się w prawym górnym rogu
- ✅ Różne kolory dla success/error/info
- ✅ Toast znika automatycznie po 3-5 sekundach
- ✅ Możliwość ręcznego zamknięcia (X)
- ✅ Animacja wejścia/wyjścia

**Status:** ⬜

---

### TC-UI-006: Stopka - Informacje o wersji
**Priorytet:** Niski
**Opis:** Stopka wyświetla commit, datę, branch

**Pre-warunki:** Zalogowany

**Kroki:**
1. Przewiń do dołu strony
2. Sprawdź stopkę

**Oczekiwany rezultat:**
- ✅ Widoczny commit hash (np. "55b094a")
- ✅ Widoczna data (np. "2025-10-05")
- ✅ Widoczny branch (np. "develop" lub "master")
- ✅ Badge branch ma odpowiedni kolor (niebieski dla develop, zielony dla master)
- ✅ Copyright: "© 2025 PowerBIIT"

**Status:** ⬜

---

### TC-UI-007: Ikony i grafika
**Priorytet:** Niski
**Opis:** Wszystkie ikony są wyświetlane poprawnie

**Pre-warunki:** Zalogowany

**Kroki:**
1. Sprawdź ikony w menu
2. Sprawdź ikony na dashboardzie (karty statystyk)
3. Sprawdź przyciski (Zaakceptuj/Odrzuć)

**Oczekiwany rezultat:**
- ✅ Wszystkie ikony SVG są widoczne
- ✅ Brak broken images
- ✅ Kolory ikon pasują do UI

**Status:** ⬜

---

## Testy integracyjne

### TC-INT-001: Pełny flow - Pracownik → Manager → Admin
**Priorytet:** Krytyczny
**Opis:** End-to-end test pełnego cyklu życia wniosku

**Kroki:**
1. **Jan (Pracownik):**
   - Zaloguj jako jan@firma.pl
   - Utwórz wniosek: Data: jutro, 10:00-14:00, Powód: "Wizyta u lekarza"
   - Sprawdź "Moje wnioski" - status "oczekujący"
   - Wyloguj

2. **Manager:**
   - Zaloguj jako manager@firma.pl
   - Sprawdź "Oczekujące" - wniosek Jana jest widoczny
   - Kliknij "Zaakceptuj"
   - Wyloguj

3. **Jan (Pracownik):**
   - Zaloguj jako jan@firma.pl
   - Sprawdź "Moje wnioski"
   - Status: "zaakceptowany"
   - **Data decyzji** jest wypełniona (dzisiejsza)
   - Wyloguj

4. **Admin:**
   - Zaloguj jako admin@firma.pl
   - Sprawdź "Audit Log"
   - Powinny być wpisy: REQUEST_CREATED, REQUEST_ACCEPTED

**Oczekiwany rezultat:**
- ✅ Wszystkie kroki działają poprawnie
- ✅ Dane są spójne między rolami
- ✅ Audit log zawiera wszystkie akcje

**Status:** ⬜

---

### TC-INT-002: Flow odrzucenia z komentarzem
**Priorytet:** Wysoki
**Opis:** Manager odrzuca wniosek, pracownik widzi komentarz

**Kroki:**
1. **Jan:** Utwórz wniosek
2. **Manager:** Odrzuć z komentarzem: "Zbyt krótki okres wyprzedzenia"
3. **Jan:** Sprawdź "Moje wnioski"

**Oczekiwany rezultat:**
- ✅ Status: "odrzucony"
- ✅ Komentarz managera jest widoczny (czerwone pole)
- ✅ **Data decyzji** jest wypełniona

**Status:** ⬜

---

### TC-INT-003: Zmiana przełożonego - Transfer wniosków
**Priorytet:** Średni
**Opis:** Po zmianie przełożonego, nowe wnioski trafiają do nowego managera

**Kroki:**
1. **Admin:** Zmień przełożonego Jana z Manager na Admin
2. **Jan:** Utwórz nowy wniosek
3. **Manager:** Sprawdź "Oczekujące" - wniosku Jana NIE MA
4. **Admin:** Sprawdź "Oczekujące" - wniosek Jana JEST

**Oczekiwany rezultat:**
- ✅ Nowy wniosek ma `manager_id` = ID Admina
- ✅ Stare wnioski Jana (jeśli były) mają nadal `manager_id` = ID Managera

**Status:** ⬜

---

### TC-INT-004: SMTP - Wysyłka emaili (jeśli skonfigurowane)
**Priorytet:** Niski
**Opis:** System wysyła emaile po akceptacji/odrzuceniu

**Pre-warunki:**
- SMTP skonfigurowane w Settings
- Prawdziwe konto email (lub mailtrap.io)

**Kroki:**
1. **Admin:** Skonfiguruj SMTP
2. **Jan:** Utwórz wniosek
3. Sprawdź skrzynkę mailową Managera
4. **Manager:** Zaakceptuj wniosek
5. Sprawdź skrzynkę mailową Jana

**Oczekiwany rezultat:**
- ✅ Manager otrzymuje email: "Nowy wniosek od Jan Nowak"
- ✅ Jan otrzymuje email: "Twój wniosek został zaakceptowany"
- ✅ Emaile zawierają szczegóły wniosku

**Uwaga:** Jeśli SMTP nie skonfigurowane - test N/A

**Status:** ⬜

---

## Edge cases i scenariusze graniczne

### TC-EDGE-001: Długi tekst w powodzie
**Priorytet:** Niski
**Opis:** System radzi sobie z bardzo długim tekstem

**Pre-warunki:** Zalogowany jako jan@firma.pl

**Kroki:**
1. Utwórz wniosek z powodem 1000+ znaków (Lorem ipsum...)
2. Wyślij
3. Sprawdź wyświetlanie w "Moje wnioski"

**Oczekiwany rezultat:**
- ✅ Wniosek zostaje utworzony
- ✅ Tekst jest wyświetlany w całości lub z "read more"
- ✅ Layout nie jest zepsuty
- ✅ Scrolling działa

**Status:** ⬜

---

### TC-EDGE-002: Znaki specjalne w danych użytkownika
**Priorytet:** Średni
**Opis:** System akceptuje znaki Unicode

**Pre-warunki:** Zalogowany jako admin@firma.pl

**Kroki:**
1. Utwórz użytkownika:
   - Imię: "Łukasz"
   - Nazwisko: "Żółć-Świętochowski"
   - Email: "lukasz.zolc@firma.pl"
2. Zaloguj się jako ten użytkownik
3. Utwórz wniosek

**Oczekiwany rezultat:**
- ✅ Użytkownik zostaje utworzony
- ✅ Polskie znaki są poprawnie wyświetlane
- ✅ Logowanie działa
- ✅ Imię wyświetla się poprawnie w całej aplikacji

**Status:** ⬜

---

### TC-EDGE-003: Brak internetu - Graceful degradation
**Priorytet:** Niski
**Opis:** Aplikacja wyświetla błąd gdy brak połączenia

**Pre-warunki:** Zalogowany jako jan@firma.pl

**Kroki:**
1. DevTools → Network → Offline
2. Spróbuj utworzyć wniosek
3. Włącz połączenie
4. Odśwież stronę

**Oczekiwany rezultat:**
- ✅ Wyświetla się błąd: "Brak połączenia z serwerem"
- ✅ Użytkownik pozostaje na formularzu
- ✅ Po przywróceniu połączenia i odświeżeniu - aplikacja działa

**Status:** ⬜

---

### TC-EDGE-004: Równoczesne logowanie na dwóch urządzeniach
**Priorytet:** Średni
**Opis:** Ten sam użytkownik zalogowany w dwóch przeglądarkach

**Kroki:**
1. Zaloguj jako jan@firma.pl w Chrome
2. Zaloguj jako jan@firma.pl w Firefox
3. W Chrome utwórz wniosek
4. W Firefox sprawdź "Moje wnioski"

**Oczekiwany rezultat:**
- ✅ Oba logowania działają (każdy ma swój token JWT)
- ✅ Wniosek utworzony w Chrome jest widoczny w Firefox po odświeżeniu
- ✅ Brak konfliktów

**Status:** ⬜

---

### TC-EDGE-005: LocalStorage pełne/zablokowane
**Priorytet:** Niski
**Opis:** Aplikacja działa gdy localStorage jest niedostępne

**Kroki:**
1. Wyłącz cookies i storage w przeglądarce
2. Spróbuj zalogować

**Oczekiwany rezultat:**
- ⚠️ Logowanie może nie działać (token nie może być zapisany)
- ✅ Wyświetla się błąd: "Włącz obsługę localStorage"

**Status:** ⬜

---

### TC-EDGE-006: Bardzo stara data wniosku
**Priorytet:** Niski
**Opis:** Walidacja daty - nie można wybrać przeszłości?

**Pre-warunki:** Zalogowany jako jan@firma.pl

**Kroki:**
1. Kliknij "Nowy wniosek"
2. Wybierz datę: wczoraj lub tydzień temu
3. Wypełnij resztę formularza
4. Wyślij

**Oczekiwany rezultat:**
- ⚠️ **Do sprawdzenia:** Czy aplikacja blokuje daty przeszłe?
- Jeśli TAK: Błąd "Data nie może być w przeszłości"
- Jeśli NIE: Wniosek zostaje utworzony (może być celowe - wniosek post-factum)

**Status:** ⬜

---

### TC-EDGE-007: Duplikowane wnioski (ten sam dzień)
**Priorytet:** Niski
**Opis:** Czy można utworzyć 2 wnioski na ten sam dzień?

**Pre-warunki:** Zalogowany jako jan@firma.pl

**Kroki:**
1. Utwórz wniosek: jutro, 10:00-12:00
2. Utwórz drugi wniosek: jutro, 14:00-16:00

**Oczekiwany rezultat:**
- ⚠️ **Do sprawdzenia:** Czy aplikacja pozwala na duplikaty?
- Jeśli TAK: Oba wnioski utworzone (może być celowe - 2 wyjścia tego samego dnia)
- Jeśli NIE: Błąd "Wniosek na ten dzień już istnieje"

**Status:** ⬜

---

### TC-EDGE-008: Usunięcie przełożonego pracownika
**Priorytet:** Średni
**Opis:** Co się dzieje gdy przełożony zostanie usunięty/dezaktywowany?

**Pre-warunki:**
- Jan ma przełożonego: Manager
- Jan ma wniosek "oczekujący"

**Kroki:**
1. **Admin:** Dezaktywuj Managera
2. Sprawdź wniosek Jana - jaki status?
3. Spróbuj zalogować jako Manager

**Oczekiwany rezultat:**
- ✅ Manager jest zdezaktywowany
- ✅ Wniosek Jana pozostaje "oczekujący" (nie można go rozpatrzyć)
- ⚠️ **Rekomendacja:** Admin powinien przepisać podwładnych Managera do innego managera PRZED dezaktywacją

**Status:** ⬜

---

## Checklist wykonania

### Przed testami
- [ ] Środowisko DEV jest dostępne
- [ ] Baza danych jest w stanie początkowym (init_db.py)
- [ ] Konta testowe działają
- [ ] Przeglądarki: Chrome + Firefox gotowe
- [ ] DevTools otwarte (Network, Console)

### Po testach
- [ ] Wszystkie test cases oznaczone (✅/❌/⚠️)
- [ ] Znalezione błędy zgłoszone jako Issues
- [ ] Screenshots/video z błędów zachowane
- [ ] Raport podsumowujący utworzony

### Metryki
- **Łączna liczba test cases:** 97
- **Priorytet krytyczny:** 25
- **Priorytet wysoki:** 32
- **Priorytet średni:** 23
- **Priorytet niski:** 17

---

## Legenda statusów

- ⬜ **Do wykonania** - Test nie został jeszcze uruchomiony
- ✅ **PASS** - Test przeszedł pomyślnie
- ❌ **FAIL** - Test nie przeszedł, znaleziono błąd
- ⚠️ **PARTIAL** - Test częściowo przeszedł, wymaga uwagi
- 🔄 **RETEST** - Test wymaga ponownej weryfikacji
- N/A **Nie dotyczy** - Test nie jest aplikowalny (np. funkcja nie zaimplementowana)

---

## Uwagi końcowe

1. **Kolejność wykonania:** Zaleca się wykonywanie testów w kolejności: Pracownik → Manager → Admin → Bezpieczeństwo → UI/UX → Integracyjne → Edge cases

2. **Dokumentacja błędów:** Każdy FAIL powinien zawierać:
   - Screenshot/video
   - Kroki do reprodukcji
   - Oczekiwany vs rzeczywisty rezultat
   - Logi z konsoli (jeśli dostępne)

3. **Środowisko DEV:** Testy wykonywane na DEV. Przed deploymentem do PROD - wykonać pełną regresję.

4. **Automatyzacja:** W przyszłości warto rozważyć Playwright/Cypress dla testów E2E.

---

**Koniec planu testów**
