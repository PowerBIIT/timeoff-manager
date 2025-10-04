# TimeOff Manager - Szczegółowy Plan Testów

## Spis Treści

1. [Wprowadzenie](#wprowadzenie)
2. [Scope Testów](#scope-testów)
3. [Środowisko Testowe](#środowisko-testowe)
4. [Typy Testów](#typy-testów)
5. [Testy Funkcjonalne](#testy-funkcjonalne)
6. [Testy Backend API](#testy-backend-api)
7. [Testy UI/Frontend](#testy-uifrontend)
8. [Testy Bezpieczeństwa](#testy-bezpieczeństwa)
9. [Testy Wydajnościowe](#testy-wydajnościowe)
10. [Testy Regresyjne](#testy-regresyjne)
11. [Acceptance Criteria](#acceptance-criteria)
12. [Bug Tracking](#bug-tracking)

---

## 1. Wprowadzenie

### Cel Dokumentu

Dokument definiuje szczegółowy plan testów dla aplikacji **TimeOff Manager**, obejmujący testy funkcjonalne, bezpieczeństwa, wydajnościowe oraz regresyjne.

### Zakres Aplikacji

**Funkcjonalności do przetestowania:**
- Autentykacja i autoryzacja użytkowników
- Zarządzanie użytkownikami (CRUD)
- Hierarchia przełożonych (supervisor_id)
- Tworzenie i zarządzanie wnioskami urlopowymi
- Akceptacja/odrzucenie wniosków przez przełożonych
- Role-based access control (Admin, Manager, Pracownik)

---

## 2. Scope Testów

### In Scope ✅

- Testy jednostkowe (Backend API)
- Testy integracyjne (Backend + Database)
- Testy UI/E2E (Playwright)
- Testy bezpieczeństwa (autentykacja, autoryzacja, SQL injection, XSS)
- Testy wydajnościowe (load testing)
- Testy regresyjne (po każdej zmianie w kodzie)

### Out of Scope ❌

- Testy mobilne (aplikacja desktop-only)
- Testy kompatybilności z przeglądarkami (tylko Chrome)
- Performance testing powyżej 100 concurrent users

---

## 3. Środowisko Testowe

### Hardware

- **CPU:** 4 cores minimum
- **RAM:** 8 GB minimum
- **Disk:** 20 GB free space

### Software

- **OS:** Ubuntu 22.04 / Windows 11 / macOS 14+
- **Python:** 3.11+
- **Node.js:** 18+ (dla Playwright)
- **Browser:** Chrome 120+
- **Database:** SQLite (dev), PostgreSQL 14+ (prod)

### Test Tools

| Tool         | Version | Purpose                  |
|--------------|---------|--------------------------|
| Pytest       | 8.3+    | Backend unit tests       |
| Playwright   | 1.49+   | UI/E2E tests             |
| Locust       | 2.15+   | Load testing             |
| OWASP ZAP    | 2.14+   | Security testing         |

### Test Data

**Test Users:**

| Username  | Password  | Role       | Supervisor       |
|-----------|-----------|------------|------------------|
| admin     | admin123  | admin      | NULL             |
| manager1  | mgr123    | manager    | admin            |
| manager2  | mgr456    | manager    | admin            |
| emp1      | emp123    | pracownik  | manager1         |
| emp2      | emp456    | pracownik  | manager1         |
| emp3      | emp789    | pracownik  | manager2         |

**Test Requests:**

| ID | User  | Type             | Start Date | End Date   | Status   | Supervisor |
|----|-------|------------------|------------|------------|----------|------------|
| 1  | emp1  | urlop            | 2025-11-01 | 2025-11-05 | pending  | manager1   |
| 2  | emp2  | L4               | 2025-10-15 | 2025-10-20 | approved | manager1   |
| 3  | emp3  | okolicznościowy  | 2025-12-01 | 2025-12-01 | rejected | manager2   |

---

## 4. Typy Testów

### 4.1 Testy Jednostkowe (Unit Tests)

**Cel:** Testowanie pojedynczych funkcji/metod w izolacji

**Tools:** Pytest

**Coverage target:** 80%+

**Przykład:**
```python
def test_user_password_hashing():
    user = User(username='test', password='test123')
    assert user.password_hash != 'test123'
    assert user.check_password('test123') == True
```

### 4.2 Testy Integracyjne (Integration Tests)

**Cel:** Testowanie interakcji między komponentami (API + Database)

**Tools:** Pytest + Flask test client

**Przykład:**
```python
def test_create_request_integration():
    # Login
    client.post('/api/login', json={'username': 'emp1', 'password': 'emp123'})

    # Create request
    response = client.post('/api/requests', json={
        'type': 'urlop',
        'start_date': '2025-11-01',
        'end_date': '2025-11-05'
    })

    assert response.status_code == 201
    assert response.json['supervisor_id'] == 2  # manager1's ID
```

### 4.3 Testy UI/E2E (End-to-End Tests)

**Cel:** Testowanie pełnych user flows w przeglądarce

**Tools:** Playwright (Python)

**Przykład:**
```python
def test_employee_create_request_flow(page):
    # Login
    page.goto('http://localhost:5000')
    page.fill('input[name="username"]', 'emp1')
    page.fill('input[name="password"]', 'emp123')
    page.click('button[type="submit"]')

    # Create request
    page.click('text=Nowy Wniosek')
    page.select_option('select[name="type"]', 'urlop')
    page.fill('input[name="start_date"]', '2025-11-01')
    page.fill('input[name="end_date"]', '2025-11-05')
    page.click('button:has-text("Złóż wniosek")')

    # Verify
    expect(page.locator('text=Wniosek został złożony')).to_be_visible()
```

### 4.4 Testy Bezpieczeństwa (Security Tests)

**Cel:** Weryfikacja zabezpieczeń (autentykacja, autoryzacja, injection attacks)

**Tools:** OWASP ZAP, manual testing

### 4.5 Testy Wydajnościowe (Performance Tests)

**Cel:** Sprawdzenie zachowania systemu pod obciążeniem

**Tools:** Locust

**Target metrics:**
- Response time < 200ms (95th percentile)
- Support 50 concurrent users
- 0% error rate under normal load

---

## 5. Testy Funkcjonalne

### 5.1 Moduł Autentykacji

#### TC-AUTH-001: Logowanie z poprawnymi danymi

**Priorytet:** Krytyczny

**Warunki wstępne:**
- Użytkownik `admin` istnieje w bazie danych
- Hasło: `admin123`

**Kroki:**
1. Otwórz aplikację (`http://localhost:5000`)
2. Wprowadź username: `admin`
3. Wprowadź hasło: `admin123`
4. Kliknij "Zaloguj się"

**Oczekiwany rezultat:**
- ✅ Przekierowanie do dashboard
- ✅ Wyświetlenie komunikatu: "Witaj, Admin System"
- ✅ Widoczne menu z opcjami (Wnioski, Użytkownicy)

**Actual result:** [Do uzupełnienia przez testera]

**Status:** [ ] Pass / [ ] Fail

---

#### TC-AUTH-002: Logowanie z błędnymi danymi

**Priorytet:** Krytyczny

**Kroki:**
1. Otwórz aplikację
2. Wprowadź username: `admin`
3. Wprowadź hasło: `wrongpassword`
4. Kliknij "Zaloguj się"

**Oczekiwany rezultat:**
- ✅ Brak przekierowania
- ✅ Komunikat błędu: "Nieprawidłowe dane logowania"
- ✅ Pola formularza pozostają wypełnione (username)

**Status:** [ ] Pass / [ ] Fail

---

#### TC-AUTH-003: Wylogowanie

**Priorytet:** Wysoki

**Warunki wstępne:**
- Użytkownik zalogowany jako `admin`

**Kroki:**
1. Kliknij ikonę użytkownika w prawym górnym rogu
2. Kliknij "Wyloguj się"

**Oczekiwany rezultat:**
- ✅ Przekierowanie do strony logowania
- ✅ Brak możliwości powrotu do dashboard (wymaga ponownego logowania)

**Status:** [ ] Pass / [ ] Fail

---

#### TC-AUTH-004: Dostęp do chronionej strony bez logowania

**Priorytet:** Krytyczny

**Kroki:**
1. Otwórz URL: `http://localhost:5000/api/users` (bez logowania)

**Oczekiwany rezultat:**
- ✅ Status 401 Unauthorized
- ✅ Odpowiedź JSON: `{"error": "Not authenticated"}`

**Status:** [ ] Pass / [ ] Fail

---

### 5.2 Moduł Zarządzania Użytkownikami

#### TC-USER-001: Utworzenie nowego użytkownika (Admin)

**Priorytet:** Krytyczny

**Warunki wstępne:**
- Zalogowany jako `admin`
- Username `newuser` nie istnieje w bazie

**Kroki:**
1. Kliknij zakładkę "Użytkownicy"
2. Kliknij "Dodaj użytkownika"
3. Wypełnij formularz:
   - Username: `newuser`
   - Hasło: `pass123`
   - Imię: `Jan`
   - Nazwisko: `Testowy`
   - Rola: `pracownik`
   - Przełożony: `Anna Kowalska (manager)`
4. Kliknij "Dodaj użytkownika"

**Oczekiwany rezultat:**
- ✅ Komunikat: "Użytkownik został dodany"
- ✅ Nowy użytkownik widoczny w tabeli
- ✅ Dane użytkownika poprawne (imię, nazwisko, rola, przełożony)

**Status:** [ ] Pass / [ ] Fail

---

#### TC-USER-002: Utworzenie użytkownika z istniejącą nazwą

**Priorytet:** Wysoki

**Warunki wstępne:**
- Zalogowany jako `admin`
- Username `admin` już istnieje

**Kroki:**
1. Spróbuj utworzyć użytkownika z username: `admin`

**Oczekiwany rezultat:**
- ✅ Błąd: "Nazwa użytkownika już istnieje"
- ✅ Użytkownik NIE został utworzony

**Status:** [ ] Pass / [ ] Fail

---

#### TC-USER-003: Edycja użytkownika (zmiana przełożonego)

**Priorytet:** Wysoki

**Warunki wstępne:**
- Zalogowany jako `admin`
- Użytkownik `emp1` istnieje z przełożonym `manager1`

**Kroki:**
1. Kliknij "Edytuj" przy użytkowniku `emp1`
2. Zmień przełożonego na `manager2`
3. Kliknij "Zapisz"

**Oczekiwany rezultat:**
- ✅ Komunikat: "Użytkownik został zaktualizowany"
- ✅ Przełożony zmieniony na `manager2`

**Status:** [ ] Pass / [ ] Fail

---

#### TC-USER-004: Usunięcie użytkownika

**Priorytet:** Wysoki

**Warunki wstępne:**
- Zalogowany jako `admin`
- Użytkownik `testuser` istnieje

**Kroki:**
1. Kliknij "Usuń" przy użytkowniku `testuser`
2. Potwierdź usunięcie

**Oczekiwany rezultat:**
- ✅ Komunikat: "Użytkownik został usunięty"
- ✅ Użytkownik zniknął z listy

**Status:** [ ] Pass / [ ] Fail

---

#### TC-USER-005: Dropdown przełożonych pokazuje wszystkich użytkowników

**Priorytet:** Krytyczny

**Warunki wstępne:**
- Zalogowany jako `admin`
- W systemie są użytkownicy z różnymi rolami (admin, manager, pracownik)

**Kroki:**
1. Kliknij "Dodaj użytkownika"
2. Sprawdź opcje w dropdownie "Przełożony"

**Oczekiwany rezultat:**
- ✅ Dropdown zawiera WSZYSTKICH użytkowników (niezależnie od roli)
- ✅ Każdy użytkownik ma label z rolą (np. "Jan Nowak (pracownik)")
- ✅ Dostępna opcja "Brak przełożonego"

**Status:** [ ] Pass / [ ] Fail

---

#### TC-USER-006: Niemożność wyboru siebie jako przełożonego

**Priorytet:** Wysoki

**Warunki wstępne:**
- Zalogowany jako `admin`
- Edycja użytkownika `emp1` (ID=3)

**Kroki:**
1. Kliknij "Edytuj" przy użytkowniku `emp1`
2. Sprawdź opcje w dropdownie "Przełożony"

**Oczekiwany rezultat:**
- ✅ Dropdown NIE zawiera użytkownika `emp1` (samego siebie)
- ✅ Wszystkie inne użytkowniki są dostępne

**Status:** [ ] Pass / [ ] Fail

---

#### TC-USER-007: Pracownik nie może zarządzać użytkownikami

**Priorytet:** Wysoki

**Warunki wstępne:**
- Zalogowany jako `emp1` (pracownik)

**Kroki:**
1. Spróbuj otworzyć zakładkę "Użytkownicy"

**Oczekiwany rezultat:**
- ✅ Zakładka "Użytkownicy" NIE jest widoczna
- ✅ Bezpośredni dostęp do `/api/users` (POST) zwraca 403 Forbidden

**Status:** [ ] Pass / [ ] Fail

---

### 5.3 Moduł Wniosków Urlopowych

#### TC-REQ-001: Utworzenie wniosku urlopowego (Pracownik)

**Priorytet:** Krytyczny

**Warunki wstępne:**
- Zalogowany jako `emp1`
- `emp1` ma przełożonego `manager1`

**Kroki:**
1. Kliknij "Nowy Wniosek"
2. Wypełnij formularz:
   - Typ: `Urlop wypoczynkowy`
   - Data rozpoczęcia: `2025-11-01`
   - Data zakończenia: `2025-11-05`
   - Powód: `Wakacje rodzinne`
3. Kliknij "Złóż wniosek"

**Oczekiwany rezultat:**
- ✅ Komunikat: "Wniosek został złożony"
- ✅ Wniosek widoczny w tabeli z statusem `Oczekuje`
- ✅ Automatycznie przypisany supervisor: `Anna Kowalska (manager1)`
- ✅ NIE było ręcznego wyboru przełożonego w formularzu

**Status:** [ ] Pass / [ ] Fail

---

#### TC-REQ-002: Utworzenie wniosku przez użytkownika bez przełożonego

**Priorytet:** Wysoki

**Warunki wstępne:**
- Zalogowany jako `admin` (brak przełożonego, supervisor_id = NULL)

**Kroki:**
1. Utwórz wniosek urlopowy

**Oczekiwany rezultat:**
- ✅ Wniosek utworzony pomyślnie
- ✅ `supervisor_id` = NULL
- ✅ Status: `Oczekuje`
- ✅ Brak błędów

**Status:** [ ] Pass / [ ] Fail

---

#### TC-REQ-003: Akceptacja wniosku przez przełożonego

**Priorytet:** Krytyczny

**Warunki wstępne:**
- Zalogowany jako `manager1`
- Wniosek od `emp1` z `supervisor_id = manager1.id` i status `pending`

**Kroki:**
1. Kliknij zakładkę "Wnioski do zaakceptowania"
2. Znajdź wniosek od `emp1`
3. Kliknij "Akceptuj"

**Oczekiwany rezultat:**
- ✅ Komunikat: "Wniosek został zaakceptowany"
- ✅ Status wniosku zmieniony na `Zaakceptowany`
- ✅ Wniosek zniknął z listy "Wnioski do zaakceptowania"

**Status:** [ ] Pass / [ ] Fail

---

#### TC-REQ-004: Odrzucenie wniosku przez przełożonego

**Priorytet:** Krytyczny

**Kroki:**
1. Zalogowany jako `manager1`
2. Znajdź wniosek od `emp1` (status `pending`)
3. Kliknij "Odrzuć"

**Oczekiwany rezultat:**
- ✅ Status zmieniony na `Odrzucony`
- ✅ Wniosek NIE zniknął z historii

**Status:** [ ] Pass / [ ] Fail

---

#### TC-REQ-005: Manager nie może akceptować cudzych wniosków

**Priorytet:** Krytyczny

**Warunki wstępne:**
- Zalogowany jako `manager1`
- Wniosek od `emp3` z `supervisor_id = manager2.id`

**Kroki:**
1. Spróbuj zaakceptować wniosek od `emp3` (via API lub UI)

**Oczekiwany rezultat:**
- ✅ UI: Brak przycisku "Akceptuj" dla tego wniosku
- ✅ API: 403 Forbidden

**Status:** [ ] Pass / [ ] Fail

---

#### TC-REQ-006: Admin może akceptować wszystkie wnioski

**Priorytet:** Wysoki

**Warunki wstępne:**
- Zalogowany jako `admin`
- Wnioski od różnych użytkowników z różnymi supervisorami

**Kroki:**
1. Spróbuj zaakceptować dowolny wniosek

**Oczekiwany rezultat:**
- ✅ Admin może zaakceptować KAŻDY wniosek (niezależnie od supervisor_id)

**Status:** [ ] Pass / [ ] Fail

---

#### TC-REQ-007: Usunięcie własnego wniosku

**Priorytet:** Średni

**Warunki wstępne:**
- Zalogowany jako `emp1`
- Wniosek utworzony przez `emp1`

**Kroki:**
1. Kliknij "Usuń" przy własnym wniosku

**Oczekiwany rezultat:**
- ✅ Wniosek usunięty
- ✅ Komunikat: "Wniosek został usunięty"

**Status:** [ ] Pass / [ ] Fail

---

#### TC-REQ-008: Niemożność usunięcia cudzego wniosku (Pracownik)

**Priorytet:** Wysoki

**Warunki wstępne:**
- Zalogowany jako `emp1`
- Wniosek utworzony przez `emp2`

**Kroki:**
1. Spróbuj usunąć wniosek `emp2` (via API)

**Oczekiwany rezultat:**
- ✅ UI: Brak przycisku "Usuń"
- ✅ API: 403 Forbidden

**Status:** [ ] Pass / [ ] Fail

---

#### TC-REQ-009: Filtrowanie wniosków (Pracownik widzi tylko swoje)

**Priorytet:** Wysoki

**Warunki wstępne:**
- Zalogowany jako `emp1`
- W systemie są wnioski od `emp1`, `emp2`, `emp3`

**Kroki:**
1. Sprawdź listę wniosków

**Oczekiwany rezultat:**
- ✅ Widoczne TYLKO wnioski utworzone przez `emp1`

**Status:** [ ] Pass / [ ] Fail

---

#### TC-REQ-010: Filtrowanie wniosków (Manager widzi swoje + podwładnych)

**Priorytet:** Wysoki

**Warunki wstępne:**
- Zalogowany jako `manager1`
- `emp1` i `emp2` mają `supervisor_id = manager1.id`
- `emp3` ma `supervisor_id = manager2.id`

**Kroki:**
1. Sprawdź listę wniosków

**Oczekiwany rezultat:**
- ✅ Widoczne wnioski od: `manager1`, `emp1`, `emp2`
- ✅ NIE widoczne wnioski od: `emp3`

**Status:** [ ] Pass / [ ] Fail

---

### 5.4 Hierarchia Przełożonych

#### TC-HIER-001: Manager może mieć Managera jako przełożonego

**Priorytet:** Krytyczny

**Warunki wstępne:**
- Zalogowany jako `admin`
- Użytkownik `manager1` (rola: manager)
- Użytkownik `manager2` (rola: manager)

**Kroki:**
1. Edytuj użytkownika `manager1`
2. Ustaw przełożonego jako `manager2`
3. Zapisz

**Oczekiwany rezultat:**
- ✅ Zapis się udał
- ✅ `manager1.supervisor_id = manager2.id`

**Status:** [ ] Pass / [ ] Fail

---

#### TC-HIER-002: Admin może mieć przełożonego

**Priorytet:** Wysoki

**Kroki:**
1. Edytuj użytkownika `admin`
2. Ustaw przełożonego jako `manager1`
3. Zapisz

**Oczekiwany rezultat:**
- ✅ Zapis się udał
- ✅ `admin.supervisor_id = manager1.id`

**Status:** [ ] Pass / [ ] Fail

---

#### TC-HIER-003: Pracownik może mieć Pracownika jako przełożonego

**Priorytet:** Wysoki

**Kroki:**
1. Edytuj użytkownika `emp1` (pracownik)
2. Ustaw przełożonego jako `emp2` (pracownik)
3. Zapisz

**Oczekiwany rezultat:**
- ✅ Zapis się udał
- ✅ Hierarchia jest elastyczna (role nie determinują hierarchii)

**Status:** [ ] Pass / [ ] Fail

---

## 6. Testy Backend API

### 6.1 Test Suite: Authentication

**Plik:** `test_app.py`

```python
import pytest
from app import app, db, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Seed test data
            admin = User(username='admin', password='admin123',
                         first_name='Admin', last_name='System', role='admin')
            db.session.add(admin)
            db.session.commit()
        yield client

def test_login_success(client):
    """TC-API-001: Login with correct credentials"""
    response = client.post('/api/login', json={
        'username': 'admin',
        'password': 'admin123'
    })

    assert response.status_code == 200
    data = response.json
    assert data['username'] == 'admin'
    assert data['role'] == 'admin'

def test_login_invalid_password(client):
    """TC-API-002: Login with incorrect password"""
    response = client.post('/api/login', json={
        'username': 'admin',
        'password': 'wrongpassword'
    })

    assert response.status_code == 401
    assert 'error' in response.json

def test_login_missing_fields(client):
    """TC-API-003: Login with missing fields"""
    response = client.post('/api/login', json={
        'username': 'admin'
    })

    assert response.status_code == 400

def test_logout(client):
    """TC-API-004: Logout"""
    # Login first
    client.post('/api/login', json={'username': 'admin', 'password': 'admin123'})

    # Logout
    response = client.post('/api/logout')
    assert response.status_code == 200

    # Verify session cleared
    response = client.get('/api/current-user')
    assert response.status_code == 401

def test_current_user_authenticated(client):
    """TC-API-005: Get current user (authenticated)"""
    client.post('/api/login', json={'username': 'admin', 'password': 'admin123'})

    response = client.get('/api/current-user')
    assert response.status_code == 200
    assert response.json['username'] == 'admin'

def test_current_user_unauthenticated(client):
    """TC-API-006: Get current user (not authenticated)"""
    response = client.get('/api/current-user')
    assert response.status_code == 401
```

### 6.2 Test Suite: User Management

```python
def test_get_users(client):
    """TC-API-007: Get all users"""
    client.post('/api/login', json={'username': 'admin', 'password': 'admin123'})

    response = client.get('/api/users')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 1

def test_create_user(client):
    """TC-API-008: Create new user"""
    client.post('/api/login', json={'username': 'admin', 'password': 'admin123'})

    response = client.post('/api/users', json={
        'username': 'newuser',
        'password': 'pass123',
        'first_name': 'Jan',
        'last_name': 'Testowy',
        'role': 'pracownik',
        'supervisor_id': 1
    })

    assert response.status_code == 201
    assert response.json['username'] == 'newuser'
    assert response.json['supervisor_id'] == 1

def test_create_user_duplicate_username(client):
    """TC-API-009: Create user with existing username"""
    client.post('/api/login', json={'username': 'admin', 'password': 'admin123'})

    response = client.post('/api/users', json={
        'username': 'admin',  # Already exists
        'password': 'pass123',
        'first_name': 'Jan',
        'last_name': 'Testowy',
        'role': 'pracownik'
    })

    assert response.status_code == 400

def test_update_user(client):
    """TC-API-010: Update user"""
    client.post('/api/login', json={'username': 'admin', 'password': 'admin123'})

    # Create user first
    create_response = client.post('/api/users', json={
        'username': 'updatetest',
        'password': 'pass123',
        'first_name': 'Jan',
        'last_name': 'Przed',
        'role': 'pracownik'
    })
    user_id = create_response.json['id']

    # Update
    response = client.patch(f'/api/users/{user_id}', json={
        'last_name': 'Po',
        'role': 'manager'
    })

    assert response.status_code == 200
    assert response.json['last_name'] == 'Po'
    assert response.json['role'] == 'manager'

def test_delete_user(client):
    """TC-API-011: Delete user"""
    client.post('/api/login', json={'username': 'admin', 'password': 'admin123'})

    # Create user first
    create_response = client.post('/api/users', json={
        'username': 'deletetest',
        'password': 'pass123',
        'first_name': 'Jan',
        'last_name': 'Do Usunięcia',
        'role': 'pracownik'
    })
    user_id = create_response.json['id']

    # Delete
    response = client.delete(f'/api/users/{user_id}')
    assert response.status_code == 200

    # Verify deleted
    get_response = client.get(f'/api/users/{user_id}')
    assert get_response.status_code == 404
```

### 6.3 Test Suite: Time Off Requests

```python
def test_create_request(client):
    """TC-API-012: Create time off request"""
    # Login as employee
    client.post('/api/login', json={'username': 'emp1', 'password': 'emp123'})

    response = client.post('/api/requests', json={
        'type': 'urlop',
        'start_date': '2025-11-01',
        'end_date': '2025-11-05',
        'reason': 'Test vacation'
    })

    assert response.status_code == 201
    assert response.json['status'] == 'pending'
    assert response.json['supervisor_id'] == 2  # emp1's supervisor (manager1)

def test_approve_request_by_supervisor(client):
    """TC-API-013: Approve request by supervisor"""
    # Create request as emp1
    client.post('/api/login', json={'username': 'emp1', 'password': 'emp123'})
    create_response = client.post('/api/requests', json={
        'type': 'urlop',
        'start_date': '2025-11-01',
        'end_date': '2025-11-05'
    })
    request_id = create_response.json['id']

    # Logout and login as manager1
    client.post('/api/logout')
    client.post('/api/login', json={'username': 'manager1', 'password': 'mgr123'})

    # Approve
    response = client.patch(f'/api/requests/{request_id}', json={
        'status': 'approved'
    })

    assert response.status_code == 200
    assert response.json['status'] == 'approved'

def test_approve_request_unauthorized(client):
    """TC-API-014: Approve request by wrong manager (403)"""
    # Create request as emp1 (supervisor: manager1)
    client.post('/api/login', json={'username': 'emp1', 'password': 'emp123'})
    create_response = client.post('/api/requests', json={
        'type': 'urlop',
        'start_date': '2025-11-01',
        'end_date': '2025-11-05'
    })
    request_id = create_response.json['id']

    # Logout and login as manager2 (NOT emp1's supervisor)
    client.post('/api/logout')
    client.post('/api/login', json={'username': 'manager2', 'password': 'mgr456'})

    # Try to approve
    response = client.patch(f'/api/requests/{request_id}', json={
        'status': 'approved'
    })

    assert response.status_code == 403

def test_delete_own_request(client):
    """TC-API-015: Delete own request"""
    client.post('/api/login', json={'username': 'emp1', 'password': 'emp123'})

    # Create
    create_response = client.post('/api/requests', json={
        'type': 'urlop',
        'start_date': '2025-11-01',
        'end_date': '2025-11-05'
    })
    request_id = create_response.json['id']

    # Delete
    response = client.delete(f'/api/requests/{request_id}')
    assert response.status_code == 200

def test_delete_others_request(client):
    """TC-API-016: Cannot delete other's request (403)"""
    # Create as emp1
    client.post('/api/login', json={'username': 'emp1', 'password': 'emp123'})
    create_response = client.post('/api/requests', json={
        'type': 'urlop',
        'start_date': '2025-11-01',
        'end_date': '2025-11-05'
    })
    request_id = create_response.json['id']

    # Login as emp2
    client.post('/api/logout')
    client.post('/api/login', json={'username': 'emp2', 'password': 'emp456'})

    # Try to delete
    response = client.delete(f'/api/requests/{request_id}')
    assert response.status_code == 403
```

---

## 7. Testy UI/Frontend

### 7.1 Test Suite: Playwright E2E

**Plik:** `test_ui.py`

```python
import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080}
    }

def test_login_flow(page: Page):
    """TC-UI-001: Login and dashboard navigation"""
    page.goto('http://localhost:5000')

    # Login
    page.fill('input[placeholder="Nazwa użytkownika"]', 'admin')
    page.fill('input[type="password"]', 'admin123')
    page.click('button:has-text("Zaloguj się")')

    # Verify dashboard
    expect(page.locator('text=Witaj, Admin System')).to_be_visible()
    expect(page.locator('text=Wnioski')).to_be_visible()
    expect(page.locator('text=Użytkownicy')).to_be_visible()

def test_create_user_flow(page: Page):
    """TC-UI-002: Create new user (Admin)"""
    # Login as admin
    page.goto('http://localhost:5000')
    page.fill('input[placeholder="Nazwa użytkownika"]', 'admin')
    page.fill('input[type="password"]', 'admin123')
    page.click('button:has-text("Zaloguj się")')

    # Navigate to Users
    page.click('text=Użytkownicy')

    # Click Add User
    page.click('button:has-text("Dodaj użytkownika")')

    # Fill form
    page.fill('input[placeholder="Nazwa użytkownika"]', 'uitest')
    page.fill('input[placeholder="Hasło"]', 'test123')
    page.fill('input[placeholder="Imię"]', 'Jan')
    page.fill('input[placeholder="Nazwisko"]', 'UITest')
    page.select_option('select', 'pracownik')
    page.select_option('select[name="supervisor"]', '2')  # manager1

    # Submit
    page.click('button:has-text("Dodaj użytkownika")')

    # Verify
    expect(page.locator('text=Jan UITest')).to_be_visible()

def test_create_request_flow(page: Page):
    """TC-UI-003: Create time off request (Employee)"""
    # Login as emp1
    page.goto('http://localhost:5000')
    page.fill('input[placeholder="Nazwa użytkownika"]', 'emp1')
    page.fill('input[type="password"]', 'emp123')
    page.click('button:has-text("Zaloguj się")')

    # Click New Request
    page.click('button:has-text("Nowy Wniosek")')

    # Fill form
    page.select_option('select[name="type"]', 'urlop')
    page.fill('input[name="start_date"]', '2025-11-01')
    page.fill('input[name="end_date"]', '2025-11-05')
    page.fill('textarea[name="reason"]', 'UI test vacation')

    # Submit
    page.click('button:has-text("Złóż wniosek")')

    # Verify
    expect(page.locator('text=Oczekuje')).to_be_visible()

def test_approve_request_flow(page: Page):
    """TC-UI-004: Approve request (Manager)"""
    # Login as manager1
    page.goto('http://localhost:5000')
    page.fill('input[placeholder="Nazwa użytkownika"]', 'manager1')
    page.fill('input[type="password"]', 'mgr123')
    page.click('button:has-text("Zaloguj się")')

    # Navigate to pending requests
    page.click('text=Wnioski do zaakceptowania')

    # Find and approve first request
    page.click('button:has-text("Akceptuj")').first()

    # Verify status changed
    expect(page.locator('text=Zaakceptowany')).to_be_visible()

def test_supervisor_dropdown_shows_all_users(page: Page):
    """TC-UI-005: Supervisor dropdown shows all users with roles"""
    # Login as admin
    page.goto('http://localhost:5000')
    page.fill('input[placeholder="Nazwa użytkownika"]', 'admin')
    page.fill('input[type="password"]', 'admin123')
    page.click('button:has-text("Zaloguj się")')

    # Navigate to Users and click Add
    page.click('text=Użytkownicy')
    page.click('button:has-text("Dodaj użytkownika")')

    # Check supervisor dropdown options
    supervisor_select = page.locator('select').nth(1)  # Second select (supervisor)
    options = supervisor_select.locator('option').all_text_contents()

    # Verify
    assert 'Brak przełożonego' in options
    assert any('(admin)' in opt for opt in options)
    assert any('(manager)' in opt for opt in options)
    assert any('(pracownik)' in opt for opt in options)

def test_edit_user_cannot_select_self(page: Page):
    """TC-UI-006: Cannot select self as supervisor in edit form"""
    # Login as admin
    page.goto('http://localhost:5000')
    page.fill('input[placeholder="Nazwa użytkownika"]', 'admin')
    page.fill('input[type="password"]', 'admin123')
    page.click('button:has-text("Zaloguj się")')

    # Navigate to Users
    page.click('text=Użytkownicy')

    # Edit first user (emp1, ID=3)
    page.click('button:has-text("Edytuj")').first()

    # Check supervisor dropdown does NOT contain emp1 itself
    supervisor_options = page.locator('select[name="supervisor"] option').all_text_contents()

    # Get current user's name from form
    current_name = page.locator('input[placeholder="Imię"]').input_value()

    # Verify user cannot select themselves
    assert not any(current_name in opt for opt in supervisor_options if opt != 'Brak przełożonego')
```

### 7.2 Visual Regression Tests

```python
def test_login_page_screenshot(page: Page):
    """TC-UI-VIS-001: Login page visual regression"""
    page.goto('http://localhost:5000')
    page.screenshot(path='screenshots/login_page.png')

    # Compare with baseline (manual verification first time)

def test_dashboard_screenshot(page: Page):
    """TC-UI-VIS-002: Dashboard visual regression"""
    # Login
    page.goto('http://localhost:5000')
    page.fill('input[placeholder="Nazwa użytkownika"]', 'admin')
    page.fill('input[type="password"]', 'admin123')
    page.click('button:has-text("Zaloguj się")')

    # Screenshot
    page.screenshot(path='screenshots/dashboard.png')
```

---

## 8. Testy Bezpieczeństwa

### 8.1 Authentication & Authorization

#### TC-SEC-001: SQL Injection - Login Form

**Priorytet:** Krytyczny

**Kroki:**
1. Wprowadź w pole username: `admin' OR '1'='1`
2. Wprowadź hasło: `password`
3. Kliknij "Zaloguj się"

**Oczekiwany rezultat:**
- ✅ Logowanie NIE powiodło się
- ✅ Błąd: "Invalid credentials"
- ✅ Brak dostępu do systemu

**Status:** [ ] Pass / [ ] Fail

---

#### TC-SEC-002: XSS - User First Name

**Priorytet:** Wysoki

**Kroki:**
1. Zaloguj jako admin
2. Utwórz użytkownika z imieniem: `<script>alert('XSS')</script>`
3. Sprawdź wyświetlanie na liście użytkowników

**Oczekiwany rezultat:**
- ✅ Script NIE został wykonany
- ✅ Imię wyświetlone jako plain text: `<script>alert('XSS')</script>`

**Status:** [ ] Pass / [ ] Fail

---

#### TC-SEC-003: Password Hashing

**Priorytet:** Krytyczny

**Kroki:**
1. Utwórz użytkownika z hasłem: `test123`
2. Sprawdź bazę danych (SQLite)

**Oczekiwany rezultat:**
- ✅ Hasło w bazie NIE jest w plaintext
- ✅ Format: `pbkdf2:sha256:600000$<salt>$<hash>`

**Status:** [ ] Pass / [ ] Fail

---

#### TC-SEC-004: Session Hijacking Prevention

**Priorytet:** Wysoki

**Kroki:**
1. Zaloguj się jako `admin`
2. Skopiuj cookie `session` z DevTools
3. Otwórz incognito window
4. Spróbuj użyć skopiowanego cookie

**Oczekiwany rezultat:**
- ✅ Cookie powinien być HTTP-only (brak dostępu z JS)
- ✅ Cookie powinien być Secure w produkcji (HTTPS only)

**Status:** [ ] Pass / [ ] Fail

---

#### TC-SEC-005: CSRF Protection

**Priorytet:** Średni

**Kroki:**
1. Utwórz external page z formularzem POST do `/api/users`
2. Spróbuj submit z zalogowanej sesji

**Oczekiwany rezultat:**
- ✅ Request odrzucony (SameSite cookies)
- ✅ Lub CSRF token validation failure

**Status:** [ ] Pass / [ ] Fail

---

#### TC-SEC-006: Authorization Bypass - Direct API Access

**Priorytet:** Krytyczny

**Kroki:**
1. Zaloguj jako `emp1` (pracownik)
2. Wyślij request: `POST /api/users` (create user)

**Oczekiwany rezultat:**
- ✅ 403 Forbidden (brak uprawnień)

**Status:** [ ] Pass / [ ] Fail

---

#### TC-SEC-007: Insecure Direct Object Reference (IDOR)

**Priorytet:** Krytyczny

**Kroki:**
1. Zaloguj jako `emp1`
2. Utwórz wniosek (otrzymasz request ID=5)
3. Spróbuj usunąć wniosek: `DELETE /api/requests/3` (cudzy wniosek)

**Oczekiwany rezultat:**
- ✅ 403 Forbidden
- ✅ Można usunąć tylko własne wnioski

**Status:** [ ] Pass / [ ] Fail

---

### 8.2 OWASP ZAP Automated Scan

**Narzędzie:** OWASP ZAP

**Kroki:**
1. Uruchom aplikację na `http://localhost:5000`
2. Uruchom OWASP ZAP
3. Skonfiguruj authenticated scan (login as admin)
4. Run automated scan

**Sprawdzane vulnerabilities:**
- SQL Injection
- XSS (Reflected, Stored, DOM-based)
- CSRF
- Insecure Headers
- SSL/TLS issues
- Cookie security

**Acceptance criteria:**
- ✅ Brak HIGH severity issues
- ✅ Max 3 MEDIUM severity issues

---

## 9. Testy Wydajnościowe

### 9.1 Load Testing - Locust

**Plik:** `locustfile.py`

```python
from locust import HttpUser, task, between

class TimeOffUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login before starting tasks"""
        self.client.post('/api/login', json={
            'username': 'emp1',
            'password': 'emp123'
        })

    @task(3)
    def view_requests(self):
        """View own requests (weight: 3)"""
        self.client.get('/api/requests')

    @task(1)
    def create_request(self):
        """Create new request (weight: 1)"""
        self.client.post('/api/requests', json={
            'type': 'urlop',
            'start_date': '2025-11-01',
            'end_date': '2025-11-05',
            'reason': 'Load test'
        })

    @task(2)
    def view_users(self):
        """View users list (weight: 2)"""
        self.client.get('/api/users')

class ManagerUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.client.post('/api/login', json={
            'username': 'manager1',
            'password': 'mgr123'
        })

    @task(5)
    def view_pending_requests(self):
        """View pending requests"""
        self.client.get('/api/requests')

    @task(1)
    def approve_request(self):
        """Approve first pending request"""
        # Get requests
        response = self.client.get('/api/requests')
        requests = response.json()

        # Approve first pending
        pending = [r for r in requests if r['status'] == 'pending']
        if pending:
            request_id = pending[0]['id']
            self.client.patch(f'/api/requests/{request_id}', json={
                'status': 'approved'
            })
```

**Uruchomienie:**
```bash
locust -f locustfile.py --host http://localhost:5000
```

**Test Scenarios:**

#### TC-PERF-001: Normal Load (10 users)

**Konfiguracja:**
- Users: 10
- Spawn rate: 1 user/sec
- Duration: 5 min

**Acceptance Criteria:**
- ✅ Avg response time < 100ms
- ✅ 95th percentile < 200ms
- ✅ Error rate < 0.1%

**Status:** [ ] Pass / [ ] Fail

---

#### TC-PERF-002: Peak Load (50 users)

**Konfiguracja:**
- Users: 50
- Spawn rate: 5 users/sec
- Duration: 10 min

**Acceptance Criteria:**
- ✅ Avg response time < 200ms
- ✅ 95th percentile < 500ms
- ✅ Error rate < 1%

**Status:** [ ] Pass / [ ] Fail

---

#### TC-PERF-003: Stress Test (100 users)

**Konfiguracja:**
- Users: 100
- Spawn rate: 10 users/sec
- Duration: 5 min

**Cel:** Znaleźć breaking point aplikacji

**Zbierane metryki:**
- Response times
- Error rate
- Throughput (RPS)
- CPU usage
- Memory usage

**Status:** [ ] Pass / [ ] Fail

---

### 9.2 Database Query Performance

#### TC-PERF-004: Get Requests Query Time

**Cel:** Sprawdzić czas wykonania `GET /api/requests` z dużą ilością danych

**Setup:**
- 1000 użytkowników
- 10,000 wniosków

**Kroki:**
1. Seed database z test data
2. Login as manager
3. GET /api/requests
4. Measure response time

**Acceptance Criteria:**
- ✅ Response time < 500ms

**Status:** [ ] Pass / [ ] Fail

---

## 10. Testy Regresyjne

### 10.1 Smoke Tests (po każdym deploy)

**Czas wykonania:** ~5 minut

**Checklist:**

- [ ] TC-AUTH-001: Login działa
- [ ] TC-USER-001: Tworzenie użytkownika działa
- [ ] TC-REQ-001: Tworzenie wniosku działa
- [ ] TC-REQ-003: Akceptacja wniosku działa
- [ ] TC-USER-005: Dropdown przełożonych pokazuje wszystkich

**Status:** [ ] Pass / [ ] Fail

---

### 10.2 Full Regression Suite

**Czas wykonania:** ~30 minut

**Scope:** Wszystkie testy funkcjonalne (sekcja 5)

**Trigger:** Przed release do produkcji

**Checklist:**
- [ ] Sekcja 5.1: Autentykacja (4 testy)
- [ ] Sekcja 5.2: Zarządzanie użytkownikami (7 testów)
- [ ] Sekcja 5.3: Wnioski (10 testów)
- [ ] Sekcja 5.4: Hierarchia (3 testy)

**Status:** [ ] Pass / [ ] Fail

---

### 10.3 Critical Path Tests

**Wykonywane:** Po każdej zmianie w kodzie

**User Flow 1: Employee Request Workflow**
1. Login as employee
2. Create request
3. Verify request visible with status "pending"
4. Logout
5. Login as manager (employee's supervisor)
6. Approve request
7. Verify status changed to "approved"

**User Flow 2: Admin User Management**
1. Login as admin
2. Create new user with supervisor
3. Edit user (change supervisor)
4. Verify supervisor changed
5. Delete user

**Status:** [ ] Pass / [ ] Fail

---

## 11. Acceptance Criteria

### Definition of Done

Feature jest uznana za zakończoną gdy:

✅ Wszystkie testy funkcjonalne (sekcja 5) przechodzą
✅ Code coverage backend >= 80%
✅ Wszystkie testy bezpieczeństwa (sekcja 8.1) przechodzą
✅ OWASP ZAP scan: brak HIGH severity issues
✅ Performance tests (normal load): response time < 200ms
✅ Smoke tests przechodzą
✅ Code review zatwierdzony
✅ Dokumentacja zaktualizowana (USER-GUIDE.md, TECHNICAL-DOCS.md)

---

## 12. Bug Tracking

### Bug Report Template

```markdown
## Bug ID: BUG-XXX

**Tytuł:** [Krótki opis problemu]

**Priorytet:** [Critical / High / Medium / Low]

**Środowisko:**
- Browser: Chrome 120
- OS: Ubuntu 22.04
- App version: v1.0.0

**Kroki do reprodukcji:**
1. [Krok 1]
2. [Krok 2]
3. [Krok 3]

**Oczekiwany rezultat:**
[Co powinno się stać]

**Aktualny rezultat:**
[Co faktycznie się dzieje]

**Screenshots/Logs:**
[Załącz screenshoty lub logi]

**Severity:**
- [ ] Blocker (aplikacja nie działa)
- [ ] Critical (główna funkcjonalność nie działa)
- [ ] Major (ważna funkcjonalność działa nieprawidłowo)
- [ ] Minor (drobny błąd)

**Assigned to:** [Imię]

**Status:** [New / In Progress / Fixed / Closed]
```

### Bug Severity Levels

**P0 - Blocker:**
- Aplikacja się nie uruchamia
- Brak możliwości logowania
- Critical security vulnerability

**P1 - Critical:**
- Nie można utworzyć wniosku
- Nie można zaakceptować wniosku
- Brak autoryzacji (każdy może wszystko)

**P2 - Major:**
- Dropdown przełożonych pokazuje tylko managerów (fixed)
- Można wybrać siebie jako przełożonego w edit form (fixed)

**P3 - Minor:**
- Literówki w UI
- Nieprawidłowe kolory
- Drobne UX issues

---

## 13. Test Execution Summary

### Test Metrics

**Planowana coverage:**
- Backend unit tests: 80%+
- Integration tests: 100% API endpoints
- UI tests: Critical user flows (login, create request, approve)
- Security tests: OWASP Top 10
- Performance tests: Normal + peak load

**Execution Schedule:**

| Test Type        | Frequency         | Duration | Responsible |
|------------------|-------------------|----------|-------------|
| Unit tests       | On every commit   | 2 min    | Developer   |
| Integration      | On every commit   | 5 min    | CI/CD       |
| UI/E2E           | Daily             | 10 min   | QA          |
| Security         | Weekly            | 30 min   | Security    |
| Performance      | Before release    | 1 hour   | QA          |
| Regression (full)| Before release    | 30 min   | QA          |

---

## 14. Appendix

### A. Test Data Seeds

**Plik:** `seed_test_data.py`

```python
from app import app, db, User, TimeOffRequest
from datetime import datetime, timedelta

def seed_test_data():
    with app.app_context():
        # Clear existing data
        TimeOffRequest.query.delete()
        User.query.delete()
        db.session.commit()

        # Create users
        admin = User(username='admin', password='admin123',
                     first_name='Admin', last_name='System', role='admin')
        manager1 = User(username='manager1', password='mgr123',
                        first_name='Anna', last_name='Kowalska',
                        role='manager', supervisor_id=None)
        manager2 = User(username='manager2', password='mgr456',
                        first_name='Piotr', last_name='Zieliński',
                        role='manager', supervisor_id=None)

        db.session.add_all([admin, manager1, manager2])
        db.session.commit()

        # Set supervisors (after commit to get IDs)
        manager1.supervisor_id = admin.id
        manager2.supervisor_id = admin.id

        emp1 = User(username='emp1', password='emp123',
                    first_name='Jan', last_name='Nowak',
                    role='pracownik', supervisor_id=manager1.id)
        emp2 = User(username='emp2', password='emp456',
                    first_name='Maria', last_name='Wiśniewska',
                    role='pracownik', supervisor_id=manager1.id)
        emp3 = User(username='emp3', password='emp789',
                    first_name='Krzysztof', last_name='Lewandowski',
                    role='pracownik', supervisor_id=manager2.id)

        db.session.add_all([emp1, emp2, emp3])
        db.session.commit()

        # Create test requests
        req1 = TimeOffRequest(
            user_id=emp1.id,
            type='urlop',
            start_date=(datetime.now() + timedelta(days=30)).date(),
            end_date=(datetime.now() + timedelta(days=34)).date(),
            reason='Test vacation',
            status='pending',
            supervisor_id=manager1.id
        )

        req2 = TimeOffRequest(
            user_id=emp2.id,
            type='L4',
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=5)).date(),
            reason='Medical leave',
            status='approved',
            supervisor_id=manager1.id
        )

        db.session.add_all([req1, req2])
        db.session.commit()

        print("✅ Test data seeded successfully!")

if __name__ == '__main__':
    seed_test_data()
```

### B. CI/CD Integration

**GitHub Actions Workflow:** `.github/workflows/test.yml`

```yaml
name: Run Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run backend tests
      run: |
        pytest test_app.py -v --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml

    - name: Install Playwright
      run: |
        pip install playwright pytest-playwright
        playwright install

    - name: Run UI tests
      run: |
        python app.py &
        sleep 5
        pytest test_ui.py -v
```

---

**Koniec Szczegółowego Planu Testów**
