# TimeOff Manager - Instrukcja Użytkownika

## Spis treści
1. [Wprowadzenie](#wprowadzenie)
2. [Logowanie](#logowanie)
3. [Role użytkowników](#role-użytkowników)
4. [Hierarchia przełożonych](#hierarchia-przełożonych)
5. [Tworzenie wniosku](#tworzenie-wniosku)
6. [Zarządzanie wnioskami](#zarządzanie-wnioskami)
7. [Administracja użytkownikami](#administracja-użytkownikami)
8. [FAQ](#faq)

---

## Wprowadzenie

TimeOff Manager to system do zarządzania wnioskami o wyjścia służbowe z automatycznym routingiem do przełożonych.

**Główne funkcje:**
- ✅ Automatyczne przypisywanie wniosków do przełożonego
- ✅ Hierarchia organizacyjna (każdy może mieć przełożonego)
- ✅ Akceptacja/odrzucanie wniosków
- ✅ Historia wniosków
- ✅ Powiadomienia email
- ✅ Audit log

---

## Logowanie

### Konta testowe:
```
Admin:      admin@firma.pl    / admin123
Manager:    manager@firma.pl  / manager123
Pracownik:  jan@firma.pl      / jan123
```

### Proces logowania:
1. Otwórz aplikację w przeglądarce
2. Wpisz email i hasło
3. Kliknij "Zaloguj się"

---

## Role użytkowników

### Administrator
**Uprawnienia:**
- ✅ Zarządzanie użytkownikami (dodawanie, edycja, usuwanie)
- ✅ Przeglądanie wszystkich wniosków
- ✅ Akceptacja/odrzucanie wniosków
- ✅ Dostęp do audit log
- ✅ Zarządzanie ustawieniami

**Dashboard:**
- Statystyki wszystkich wniosków w systemie
- Oczekujące wnioski przypisane do niego

### Manager
**Uprawnienia:**
- ✅ Tworzenie własnych wniosków (do swojego przełożonego)
- ✅ Akceptacja/odrzucanie wniosków podwładnych
- ✅ Przeglądanie wniosków zespołu

**Dashboard:**
- Statystyki własnych wniosków + wniosków podwładnych
- Oczekujące wnioski od podwładnych

### Pracownik
**Uprawnienia:**
- ✅ Tworzenie wniosków (do swojego przełożonego)
- ✅ Przeglądanie własnych wniosków
- ✅ Anulowanie oczekujących wniosków

**Dashboard:**
- Statystyki własnych wniosków

---

## Hierarchia przełożonych

### Jak działa hierarchia?

Każdy użytkownik może mieć **przełożonego** (supervisor):
- **Pracownik** → Przełożony: Manager
- **Manager** → Przełożony: Starszy Manager / Admin
- **Admin** → Przełożony: Brak (lub Board of Directors)

### Przykładowa hierarchia:

```
Admin (CEO)
├─ Manager Anna
│  ├─ Pracownik Jan
│  └─ Manager Piotr
│     └─ Pracownik Maria
└─ Manager Tomasz
   └─ Pracownik Ewa
```

### Kto może być przełożonym?

**Każdy użytkownik** może być przełożonym innej osoby, niezależnie od roli!

**Przykłady:**
- Manager może mieć innego Managera jako przełożonego ✅
- Admin może mieć przełożonego (np. Board) ✅
- Pracownik może mieć Admina jako przełożonego ✅

### Użytkownicy bez przełożonego

Użytkownicy bez przełożonego (np. CEO):
- ❌ **NIE mogą** tworzyć wniosków (brak komu zatwierdzić)
- ✅ Mogą akceptować wnioski innych

---

## Tworzenie wniosku

### Krok po kroku:

1. **Kliknij "➕ Nowy wniosek"** w menu

2. **Wypełnij formularz:**
   - **Data** - dzień wyjścia (nie może być w przeszłości)
   - **Wyjście** - godzina wyjścia (HH:MM)
   - **Powrót** - godzina powrotu (HH:MM)
   - **Powód** - minimum 10 znaków

3. **Kliknij "Złóż wniosek"**

### Automatyczne przypisanie

⚠️ **UWAGA:** Pole "Manager" zostało **usunięte** z formularza!

Wniosek jest **automatycznie** wysyłany do Twojego przełożonego (supervisor).

**Komunikat w formularzu:**
> "Wniosek zostanie automatycznie wysłany do Twojego przełożonego"

### Walidacja

**Formularz sprawdza:**
- ❌ Data nie może być w przeszłości
- ❌ Godzina powrotu musi być po godzinie wyjścia
- ❌ Powód musi mieć minimum 10 znaków
- ❌ Użytkownik musi mieć przypisanego przełożonego

**Błędy:**
```
"You must have a supervisor assigned to create requests"
→ Skontaktuj się z adminem aby przypisał Ci przełożonego
```

---

## Zarządzanie wnioskami

### Widok "Moje wnioski"

**Filtry:**
- Wszystkie
- Oczekujące
- Zaakceptowane
- Odrzucone
- Anulowane

**Informacje o wniosku:**
- Data i godziny (wyjście - powrót)
- Przełożony (kto zatwierdza)
- Status
- Data utworzenia
- Powód

**Akcje:**
- **Anuluj** - tylko dla wniosków oczekujących

### Widok "Oczekujące" (Manager/Admin)

**Kto widzi:**
- Manager widzi wnioski **przypisane do niego** (od podwładnych)
- Admin widzi **wszystkie** oczekujące wnioski

**Akcje:**
- **✅ Zaakceptuj** - zatwierdź wniosek
- **❌ Odrzuć** - odrzuć z opcjonalnym komentarzem

### Statusy wniosków

| Status | Opis | Kolor |
|--------|------|-------|
| **Oczekujący** | Czeka na decyzję przełożonego | 🟡 Żółty |
| **Zaakceptowany** | Zatwierdzony przez przełożonego | 🟢 Zielony |
| **Odrzucony** | Odrzucony przez przełożonego | 🔴 Czerwony |
| **Anulowany** | Anulowany przez pracownika | ⚫ Szary |

---

## Administracja użytkownikami

### Dodawanie użytkownika (Admin)

1. **Przejdź do "👥 Użytkownicy"**
2. **Kliknij "➕ Dodaj użytkownika"**
3. **Wypełnij formularz:**
   - Email *
   - Hasło * (min. 8 znaków)
   - Imię *
   - Nazwisko *
   - Rola * (Pracownik / Manager / Administrator)
   - **Przełożony** - wybierz z listy lub "Brak przełożonego"

4. **Kliknij "Dodaj"**

### Lista przełożonych

Lista "Przełożony" zawiera **wszystkich użytkowników**:

```
Brak przełożonego
Maria Kowalska (pracownik)
Piotr Nowak (manager)
Jan Nowak (pracownik)
Anna Kowalska (manager)
Admin System (admin)
```

**Uwagi:**
- ✅ Pole dostępne dla **wszystkich ról**
- ✅ Przy edycji: nie można wybrać samego siebie
- ✅ Widoczna rola przy każdym użytkowniku

### Edycja użytkownika

1. **Kliknij "Edytuj" przy użytkowniku**
2. **Zmień dane** (email, imię, nazwisko, rola, przełożony, hasło)
3. **Kliknij "Zapisz"**

### Usuwanie użytkownika

⚠️ **Ograniczenia:**
- ❌ Nie można usunąć własnego konta
- ❌ Nie można usunąć użytkownika z wnioskami (deaktywuj zamiast tego)

**Alternatywa:** Zmień `is_active` na `false`

---

## FAQ

### Pytanie 1: Dlaczego nie widzę pola "Manager" w formularzu wniosku?

**Odpowiedź:** Pole zostało usunięte! Wniosek jest **automatycznie** wysyłany do Twojego przełożonego (supervisor).

---

### Pytanie 2: Kto może być moim przełożonym?

**Odpowiedź:** Dowolny użytkownik w systemie, niezależnie od roli. Admin może ustawić to w panelu "Użytkownicy".

---

### Pytanie 3: Czy Manager może mieć Managera jako przełożonego?

**Odpowiedź:** Tak! Każdy może mieć dowolnego użytkownika jako przełożonego.

---

### Pytanie 4: Co jeśli nie mam przełożonego?

**Odpowiedź:** Nie możesz tworzyć wniosków. Skontaktuj się z adminem aby przypisał Ci przełożonego.

---

### Pytanie 5: Czy mogę anulować zaakceptowany wniosek?

**Odpowiedź:** Nie. Możesz anulować tylko wnioski ze statusem "oczekujący".

---

### Pytanie 6: Czy otrzymam powiadomienie email?

**Odpowiedź:** Tak, jeśli SMTP jest skonfigurowany:
- Przełożony dostaje email gdy powstaje nowy wniosek
- Pracownik dostaje email gdy wniosek zostaje zaakceptowany/odrzucony

---

### Pytanie 7: Gdzie mogę zobaczyć historię zmian?

**Odpowiedź:** Admin ma dostęp do "📜 Audit Log" gdzie widać wszystkie akcje w systemie.

---

## Kontakt

W razie problemów skontaktuj się z administratorem systemu.
