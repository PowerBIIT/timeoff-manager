# Plan Testów - Hierarchia Przełożonych

## Wykonane Zmiany

### 1. Model Danych ✅
- ✅ Zmiana `manager_id` → `supervisor_id` w modelu User
- ✅ Każdy użytkownik (pracownik, manager, admin) może mieć przełożonego
- ✅ Relacja `supervisor` / `subordinates`
- ✅ Skrypt migracji bazy danych

### 2. Backend API ✅
- ✅ `routes/user_routes.py`: Zmiana manager_id → supervisor_id
- ✅ Usunięcie walidacji "musi być manager" (każdy może być przełożonym)
- ✅ `routes/request_routes.py`: Automatyczne przypisywanie supervisor_id do wniosków
- ✅ Usunięcie pola `manager_id` z POST /api/requests (teraz automatyczne)

### 3. Inicjalizacja Danych ✅
- ✅ Admin (supervisor_id = NULL) - szczyt hierarchii
- ✅ Manager Anna (supervisor_id = Admin)
- ✅ Pracownik Jan (supervisor_id = Manager Anna)

### 4. Frontend UI ⚠️ WYMAGA NAPRAWY
- ✅ Usunięcie pola "Manager" z formularza nowego wniosku
- ⚠️ Częściowa zmiana manager_id → supervisor_id (sed global)
- ❌ **BŁĘDY SKŁADNI HTML** - wymagają ręcznej naprawy

---

## Problemy do Naprawienia

### HTML Syntax Errors (krytyczne!)
1. **Linia 451**: `<p className="text-sm text-gray-500>Przełożony<p>`
   - Powinno być: `<p className="text-sm text-gray-500">Przełożony</p>`

2. **Linia 882**: `<th className="px-6 py-4 text-left text-sm font-semibold text-gray-700>Przełożony<th>`
   - Powinno być: `<th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Przełożony</th>`

3. **Linia 977**: `<option value="manager>Przełożony<option>`
   - Powinno być: `<option value="manager">Manager</option>` (rola pozostaje "manager")

4. **Linia 983**: `<label className="block text-sm font-semibold mb-2>Przełożony<label>`
   - Powinno być: `<label className="block text-sm font-semibold mb-2">Przełożony</label>`

5. **Podobne błędy w linii 1070, 1076**

### Logiczne Zmiany UI
1. **Panel użytkowników**:
   - Zmienić nagłówek kolumny "Manager" → "Przełożony"
   - Zmienić `user.manager` → `user.supervisor` w wyświetlaniu

2. **Formularz dodawania/edycji użytkownika**:
   - Pole "Przełożony" powinno być dostępne dla WSZYSTKICH ról (nie tylko pracownik)
   - Lista przełożonych powinna pokazywać wszystkich użytkowników (nie tylko managerów)
   - Dodać możliwość wyboru "Brak przełożonego" (dla top-level users)

3. **Wyświetlanie wniosków**:
   - req.manager → req.supervisor (semantycznie)

---

## Plan Testów - Do Wykonania

### TEST 1: Hierarchia Użytkowników
**Cel**: Sprawdzić poprawność struktury hierarchii

**Kroki**:
1. Zaloguj się jako Admin
2. Przejdź do panelu Użytkownicy
3. Sprawdź:
   - Admin: Przełożony = `-` (brak)
   - Manager Anna: Przełożony = `Admin System`
   - Pracownik Jan: Przełożony = `Anna Kowalska`

**Oczekiwany wynik**: Wszyscy użytkownicy mają poprawnie przypisanych przełożonych

---

### TEST 2: Tworzenie Wniosku przez Pracownika
**Cel**: Sprawdzić automatyczne przypisanie przełożonego

**Kroki**:
1. Zaloguj się jako `jan@firma.pl`
2. Kliknij "Nowy wniosek"
3. Wypełnij formularz (NIE MA pola "Manager" - automatyczne!)
4. Złóż wniosek

**Oczekiwany wynik**:
- Wniosek zostaje złożony
- Manager wniosku = Anna Kowalska (supervisor Jana)
- Toast: "Wniosek złożony pomyślnie!"

---

### TEST 3: Tworzenie Wniosku przez Managera
**Cel**: Sprawdzić flow: Manager → Admin

**Kroki**:
1. Zaloguj się jako `manager@firma.pl`
2. Kliknij "Nowy wniosek"
3. Wypełnij formularz
4. Złóż wniosek

**Oczekiwany wynik**:
- Wniosek zostaje złożony
- Manager wniosku = Admin System (supervisor Anny)
- Wniosek pojawia się w zakładce "Oczekujące" Admina

---

### TEST 4: Zatwierdzanie przez Przełożonego
**Cel**: Sprawdzić uprawnienia przełożonego

**Kroki**:
1. Zaloguj się jako `manager@firma.pl`
2. Przejdź do "Oczekujące"
3. Powinien być widoczny wniosek od Jana
4. Zatwierdź wniosek

**Oczekiwany wynik**:
- Wniosek zatwierdzony
- Status zmieniony na "zaakceptowany"
- Toast: "Wniosek zaakceptowany"

---

### TEST 5: Dodawanie Użytkownika z Przełożonym
**Cel**: Sprawdzić nowy flow dodawania użytkowników

**Kroki**:
1. Zaloguj się jako Admin
2. Przejdź do "Użytkownicy" → "Dodaj użytkownika"
3. Wypełnij:
   - Email: `piotr@firma.pl`
   - Hasło: `piotr123`
   - Imię: Piotr
   - Nazwisko: Nowak
   - Rola: `Manager`
   - **Przełożony**: `Admin System`
4. Zapisz

**Oczekiwany wynik**:
- Użytkownik utworzony
- Piotr ma supervisor_id = 1 (Admin)
- Manager Piotr może tworzyć wnioski do Admina

---

### TEST 6: Edycja Przełożonego
**Cel**: Zmiana przełożonego użytkownika

**Kroki**:
1. Zaloguj się jako Admin
2. Edytuj użytkownika "Piotr Nowak"
3. Zmień przełożonego na `Anna Kowalska`
4. Zapisz

**Oczekiwany wynik**:
- Przełożony zmieniony
- Piotr może teraz tworzyć wnioski do Anny

---

### TEST 7: Użytkownik bez Przełożonego
**Cel**: Sprawdzić walidację braku przełożonego

**Kroki**:
1. Zaloguj się jako `piotr@firma.pl` (jeśli ma supervisor_id = NULL)
2. Spróbuj utworzyć wniosek

**Oczekiwany wynik**:
- Błąd: "You must have a supervisor assigned to create requests"
- Toast error

---

### TEST 8: Audit Log
**Cel**: Sprawdzić logowanie akcji

**Kroki**:
1. Zaloguj się jako Admin
2. Przejdź do "Audit Log"
3. Sprawdź wpisy:
   - USER_CREATED z supervisor_id
   - REQUEST_CREATED z auto-assigned manager

**Oczekiwany wynik**: Wszystkie akcje zalogowane

---

### TEST 9: RBAC - Dostęp do Przełożonych
**Cel**: Sprawdzić uprawnienia

**Kroki**:
1. Zaloguj się jako Manager
2. Przejdź do "Oczekujące"
3. Sprawdź czy widać tylko wnioski od podwładnych (Jan)
4. NIE widać wniosków od innych managerów

**Oczekiwany wynik**: Manager widzi tylko wnioski przypisane do niego

---

### TEST 10: Błąd Brakującego Przełożonego
**Cel**: Edge case

**Kroki**:
1. Admin usuwa Annę (supervisor Jana)
2. Jan próbuje utworzyć wniosek

**Oczekiwany wynik**:
- Błąd: "Your supervisor not found in system"
- Albo Jan automatycznie dostaje nowego supervisora

---

## Metryki Sukcesu

✅ **Podstawowe flow (musi działać)**:
- Pracownik → Manager → Admin (hierarchia 3-poziomowa)
- Automatyczne przypisywanie supervisora do wniosków
- Zatwierdzanie przez właściwego przełożonego

⚠️ **Ważne (powinno działać)**:
- Manager może tworzyć wnioski do Admina
- Admin może mieć supervisor_id = NULL
- Edycja przełożonego

🔧 **Nice to have**:
- Walidacja cyklicznych zależności (A→B→A)
- Wielopoziomowa hierarchia (więcej niż 3 poziomy)
- Automatyczna aktualizacja wniosków przy zmianie supervisora

---

## Status Implementacji

| Komponent | Status | Uwagi |
|-----------|--------|-------|
| Model (backend) | ✅ DONE | supervisor_id zamiast manager_id |
| API endpoints | ✅ DONE | Auto-assign supervisor |
| Migracja DB | ✅ DONE | Dane skopiowane |
| UI - Formularz wniosku | ✅ DONE | Pole Manager usunięte |
| UI - Panel użytkowników | ⚠️ PARTIAL | Wymaga naprawy HTML |
| UI - Semantyka (manager→supervisor) | ⚠️ PARTIAL | Częściowo zmienione |
| Testy | ❌ TODO | Plan gotowy |

---

## Następne Kroki

1. **KRYTYCZNE**: Naprawić błędy HTML w index.html
2. Zaktualizować UI do pełnej semantyki supervisor
3. Uruchomić aplikację i przetestować (plan powyżej)
4. Wdrożyć na Azure
5. Utworzyć dokumentację nowej hierarchii

---

## Znane Problemy

1. ❌ **HTML syntax errors** (linie 451, 882, 977, 983, 1070, 1076)
2. ⚠️ Semantyka: Niektóre miejsca nadal używają "manager" zamiast "supervisor"
3. ⚠️ UI nie pokazuje przełożonego dla Managerów/Adminów (tylko dla pracowników)
4. ⚠️ Lista przełożonych jest ograniczona do managerów (powinni być wszyscy)

---

## Flow Biznesowy (Nowy)

```
Hierarchia:
  Admin (CEO) - supervisor_id: NULL
    ├─ Manager Anna - supervisor_id: 1 (Admin)
    │   └─ Pracownik Jan - supervisor_id: 2 (Anna)
    └─ Manager Piotr - supervisor_id: 1 (Admin)
        └─ Pracownik Maria - supervisor_id: 4 (Piotr)

Wnioski:
  - Jan tworzy wniosek → automatycznie przypisany do Anny
  - Anna zatwierdza wniosek Jana
  - Anna tworzy wniosek → automatycznie przypisany do Admina
  - Admin zatwierdza wniosek Anny
  - Admin NIE może tworzyć wniosków (brak supervisora) ❌
```

**UWAGA**: Admin nie może tworzyć wniosków!
**Rozwiązanie**: Albo Admin może auto-approve, albo Admin ma supervisora (np. "Board of Directors")
