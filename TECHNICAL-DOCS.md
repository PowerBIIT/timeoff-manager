# TimeOff Manager - Dokumentacja Techniczna

## Spis Treści

1. [Architektura Systemu](#architektura-systemu)
2. [Schemat Bazy Danych](#schemat-bazy-danych)
3. [API Endpoints](#api-endpoints)
4. [Autentykacja i Autoryzacja](#autentykacja-i-autoryzacja)
5. [Implementacja Hierarchii Przełożonych](#implementacja-hierarchii-przełożonych)
6. [Deployment](#deployment)
7. [Konfiguracja](#konfiguracja)
8. [Bezpieczeństwo](#bezpieczeństwo)

---

## 1. Architektura Systemu

### Stack Technologiczny

**Backend:**
- **Framework:** Flask 3.1.0 (Python)
- **ORM:** Flask-SQLAlchemy 3.1.1
- **Baza danych:** SQLite (development), PostgreSQL (production)
- **Autentykacja:** Flask-Login 0.6.3
- **CORS:** Flask-CORS 5.0.0
- **Hasła:** Werkzeug password hashing (PBKDF2-SHA256)

**Frontend:**
- **Framework:** React 18.x (via CDN)
- **HTTP Client:** Axios 1.6.7
- **Styling:** Tailwind CSS 3.4.1
- **Ikony:** Lucide React

**Deployment:**
- **Platform:** Azure Web App
- **Reverse Proxy:** Gunicorn
- **CI/CD:** Bash script (`azure-deploy.sh`)

### Architektura Warstwowa

```
┌─────────────────────────────────────┐
│   Frontend (React SPA)              │
│   - User Management UI              │
│   - Request Management UI           │
│   - Dashboard                       │
└─────────────┬───────────────────────┘
              │ HTTP/AJAX (Axios)
              │
┌─────────────▼───────────────────────┐
│   Flask Backend (REST API)          │
│   - /api/users                      │
│   - /api/requests                   │
│   - /api/login, /api/logout         │
└─────────────┬───────────────────────┘
              │ SQLAlchemy ORM
              │
┌─────────────▼───────────────────────┐
│   Database Layer                    │
│   - SQLite (dev)                    │
│   - PostgreSQL (prod)               │
│   - Tables: users, time_off_requests│
└─────────────────────────────────────┘
```

### Przepływ Danych

1. **Logowanie:**
   ```
   User → Login Form → POST /api/login → Validate → Flask-Login Session → Redirect
   ```

2. **Tworzenie Wniosku:**
   ```
   User → Request Form → POST /api/requests → Assign supervisor → Save → Notify
   ```

3. **Akceptacja Wniosku:**
   ```
   Manager → Click Approve → PATCH /api/requests/:id → Update status → Save
   ```

---

## 2. Schemat Bazy Danych

### Tabela: `users`

| Kolumna         | Typ           | Opis                                      | Constraints                    |
|-----------------|---------------|-------------------------------------------|--------------------------------|
| `id`            | INTEGER       | Klucz główny                              | PRIMARY KEY, AUTOINCREMENT     |
| `username`      | VARCHAR(80)   | Nazwa użytkownika (login)                 | UNIQUE, NOT NULL               |
| `password_hash` | VARCHAR(255)  | Hash hasła (PBKDF2-SHA256)                | NOT NULL                       |
| `first_name`    | VARCHAR(100)  | Imię                                      | NOT NULL                       |
| `last_name`     | VARCHAR(100)  | Nazwisko                                  | NOT NULL                       |
| `role`          | VARCHAR(20)   | Rola: `admin`, `manager`, `pracownik`     | NOT NULL                       |
| `supervisor_id` | INTEGER       | FK do `users.id` (przełożony)             | FOREIGN KEY, NULLABLE          |

**Relacje:**
- **Self-referential:** `supervisor_id` → `users.id`
- Jeden użytkownik może mieć wielu podwładnych
- Jeden użytkownik może mieć jednego przełożonego (lub NULL)

**Przykładowe Dane:**
```sql
INSERT INTO users (username, password_hash, first_name, last_name, role, supervisor_id) VALUES
('admin', 'pbkdf2:sha256:...', 'Admin', 'System', 'admin', NULL),
('manager1', 'pbkdf2:sha256:...', 'Anna', 'Kowalska', 'manager', 1),
('emp1', 'pbkdf2:sha256:...', 'Jan', 'Nowak', 'pracownik', 2);
```

### Tabela: `time_off_requests`

| Kolumna       | Typ          | Opis                                      | Constraints                    |
|---------------|--------------|-------------------------------------------|--------------------------------|
| `id`          | INTEGER      | Klucz główny                              | PRIMARY KEY, AUTOINCREMENT     |
| `user_id`     | INTEGER      | FK do `users.id` (wnioskodawca)           | FOREIGN KEY, NOT NULL          |
| `type`        | VARCHAR(50)  | Typ: `urlop`, `L4`, `okolicznościowy`     | NOT NULL                       |
| `start_date`  | DATE         | Data rozpoczęcia                          | NOT NULL                       |
| `end_date`    | DATE         | Data zakończenia                          | NOT NULL                       |
| `reason`      | TEXT         | Powód (opcjonalny)                        | NULLABLE                       |
| `status`      | VARCHAR(20)  | Status: `pending`, `approved`, `rejected` | NOT NULL, DEFAULT='pending'    |
| `supervisor_id` | INTEGER    | FK do `users.id` (akceptujący)            | FOREIGN KEY, NULLABLE          |
| `created_at`  | TIMESTAMP    | Data utworzenia                           | DEFAULT=CURRENT_TIMESTAMP      |

**Relacje:**
- `user_id` → `users.id` (wnioskodawca)
- `supervisor_id` → `users.id` (przełożony akceptujący)

**Indeksy:**
```sql
CREATE INDEX idx_requests_user_id ON time_off_requests(user_id);
CREATE INDEX idx_requests_supervisor_id ON time_off_requests(supervisor_id);
CREATE INDEX idx_requests_status ON time_off_requests(status);
```

### Diagram ER

```
┌─────────────────────────┐
│       users             │
├─────────────────────────┤
│ id (PK)                 │
│ username                │◄────┐
│ password_hash           │     │
│ first_name              │     │
│ last_name               │     │
│ role                    │     │
│ supervisor_id (FK) ─────┼─────┘ (self-reference)
└──────────┬──────────────┘
           │
           │ 1:N (user → requests)
           │
┌──────────▼──────────────┐
│  time_off_requests      │
├─────────────────────────┤
│ id (PK)                 │
│ user_id (FK)            │
│ type                    │
│ start_date              │
│ end_date                │
│ reason                  │
│ status                  │
│ supervisor_id (FK)      │
│ created_at              │
└─────────────────────────┘
```

---

## 3. API Endpoints

### Autentykacja

#### `POST /api/login`

**Opis:** Logowanie użytkownika

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "admin",
  "first_name": "Admin",
  "last_name": "System",
  "role": "admin",
  "supervisor_id": null
}
```

**Response (401 Unauthorized):**
```json
{
  "error": "Invalid credentials"
}
```

#### `POST /api/logout`

**Opis:** Wylogowanie użytkownika

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

#### `GET /api/current-user`

**Opis:** Pobranie danych zalogowanego użytkownika

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "admin",
  "first_name": "Admin",
  "last_name": "System",
  "role": "admin",
  "supervisor_id": null
}
```

**Response (401 Unauthorized):**
```json
{
  "error": "Not authenticated"
}
```

---

### Użytkownicy

#### `GET /api/users`

**Opis:** Pobranie listy wszystkich użytkowników

**Query Parameters:**
- `role` (optional): Filtrowanie po roli (`admin`, `manager`, `pracownik`)

**Przykład:**
```
GET /api/users
GET /api/users?role=manager
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "username": "admin",
    "first_name": "Admin",
    "last_name": "System",
    "role": "admin",
    "supervisor_id": null
  },
  {
    "id": 2,
    "username": "manager1",
    "first_name": "Anna",
    "last_name": "Kowalska",
    "role": "manager",
    "supervisor_id": 1
  }
]
```

**Wymagane uprawnienia:** Zalogowany użytkownik

#### `POST /api/users`

**Opis:** Utworzenie nowego użytkownika

**Request Body:**
```json
{
  "username": "emp1",
  "password": "emp123",
  "first_name": "Jan",
  "last_name": "Nowak",
  "role": "pracownik",
  "supervisor_id": 2
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "username": "emp1",
  "first_name": "Jan",
  "last_name": "Nowak",
  "role": "pracownik",
  "supervisor_id": 2
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Username already exists"
}
```

**Wymagane uprawnienia:** Admin

#### `PATCH /api/users/<id>`

**Opis:** Aktualizacja danych użytkownika

**Request Body (partial update):**
```json
{
  "first_name": "Jan",
  "last_name": "Kowalski",
  "role": "manager",
  "supervisor_id": 1,
  "password": "newpassword123" // opcjonalne
}
```

**Response (200 OK):**
```json
{
  "id": 3,
  "username": "emp1",
  "first_name": "Jan",
  "last_name": "Kowalski",
  "role": "manager",
  "supervisor_id": 1
}
```

**Wymagane uprawnienia:** Admin

#### `DELETE /api/users/<id>`

**Opis:** Usunięcie użytkownika

**Response (200 OK):**
```json
{
  "message": "User deleted successfully"
}
```

**Response (404 Not Found):**
```json
{
  "error": "User not found"
}
```

**Wymagane uprawnienia:** Admin

---

### Wnioski Urlopowe

#### `GET /api/requests`

**Opis:** Pobranie listy wniosków (filtrowanych zależnie od roli)

**Logika Filtrowania:**
- **Admin:** Wszystkie wnioski
- **Manager:** Wnioski własne + wnioski podwładnych (gdzie `supervisor_id = current_user.id`)
- **Pracownik:** Tylko własne wnioski

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 3,
    "user_name": "Jan Nowak",
    "type": "urlop",
    "start_date": "2025-11-01",
    "end_date": "2025-11-05",
    "reason": "Wakacje rodzinne",
    "status": "pending",
    "supervisor_id": 2,
    "supervisor_name": "Anna Kowalska",
    "created_at": "2025-10-01T10:30:00"
  }
]
```

**Wymagane uprawnienia:** Zalogowany użytkownik

#### `POST /api/requests`

**Opis:** Utworzenie nowego wniosku urlopowego

**Request Body:**
```json
{
  "type": "urlop",
  "start_date": "2025-11-01",
  "end_date": "2025-11-05",
  "reason": "Wakacje rodzinne"
}
```

**Backend Logic:**
1. Pobiera `current_user` z sesji Flask-Login
2. Automatycznie przypisuje `supervisor_id` z `current_user.supervisor_id`
3. Ustawia `status = 'pending'`
4. Tworzy rekord w bazie danych

**Response (201 Created):**
```json
{
  "id": 5,
  "user_id": 3,
  "type": "urlop",
  "start_date": "2025-11-01",
  "end_date": "2025-11-05",
  "reason": "Wakacje rodzinne",
  "status": "pending",
  "supervisor_id": 2,
  "created_at": "2025-10-04T12:00:00"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Missing required fields"
}
```

**Wymagane uprawnienia:** Zalogowany użytkownik

#### `PATCH /api/requests/<id>`

**Opis:** Aktualizacja statusu wniosku (approve/reject)

**Request Body:**
```json
{
  "status": "approved"
}
```

**Dozwolone wartości:** `approved`, `rejected`

**Backend Logic:**
1. Sprawdza czy `current_user` ma uprawnienia (admin LUB supervisor dla tego wniosku)
2. Aktualizuje `status`

**Response (200 OK):**
```json
{
  "id": 5,
  "status": "approved"
}
```

**Response (403 Forbidden):**
```json
{
  "error": "You are not authorized to approve/reject this request"
}
```

**Wymagane uprawnienia:** Admin LUB supervisor dla danego wniosku

#### `DELETE /api/requests/<id>`

**Opis:** Usunięcie wniosku

**Logika Uprawnień:**
- **Własny wniosek:** Użytkownik może usunąć własny wniosek
- **Admin:** Może usunąć dowolny wniosek

**Response (200 OK):**
```json
{
  "message": "Request deleted successfully"
}
```

**Response (403 Forbidden):**
```json
{
  "error": "You can only delete your own requests"
}
```

**Wymagane uprawnienia:** Admin LUB właściciel wniosku

---

## 4. Autentykacja i Autoryzacja

### Flask-Login

**Konfiguracja (app.py):**
```python
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

**User Model:**
```python
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # ... inne pola
```

### Hashowanie Haseł

**Metoda:** PBKDF2-SHA256 (via Werkzeug)

**Tworzenie hasła:**
```python
from werkzeug.security import generate_password_hash

password_hash = generate_password_hash('plaintext_password')
# Wynik: pbkdf2:sha256:600000$<salt>$<hash>
```

**Weryfikacja hasła:**
```python
from werkzeug.security import check_password_hash

is_valid = check_password_hash(user.password_hash, 'plaintext_password')
```

### Session Management

**Backend (Flask):**
- Session cookie: `session` (HTTP-only, secure in prod)
- Login: `login_user(user)`
- Logout: `logout_user()`
- Check: `@login_required` decorator

**Frontend (React):**
- Axios automatically sends cookies with requests
- State management via React hooks (`currentUser`, `setCurrentUser`)

### Role-Based Access Control (RBAC)

**Role Hierarchy:**
```
admin > manager > pracownik
```

**Permissions Matrix:**

| Feature                      | Admin | Manager | Pracownik |
|------------------------------|-------|---------|-----------|
| View own requests            | ✅     | ✅       | ✅         |
| Create request               | ✅     | ✅       | ✅         |
| Delete own request           | ✅     | ✅       | ✅         |
| View subordinate requests    | ✅     | ✅       | ❌         |
| Approve/reject requests      | ✅     | ✅*      | ❌         |
| View all users               | ✅     | ✅       | ✅         |
| Create user                  | ✅     | ❌       | ❌         |
| Edit user                    | ✅     | ❌       | ❌         |
| Delete user                  | ✅     | ❌       | ❌         |
| View all requests            | ✅     | ❌       | ❌         |

*Manager może akceptować tylko wnioski, gdzie `supervisor_id = manager.id`

**Implementation Example (app.py):**
```python
@app.route('/api/requests/<int:id>', methods=['PATCH'])
@login_required
def update_request(id):
    req = TimeOffRequest.query.get_or_404(id)

    # Authorization check
    if current_user.role != 'admin' and req.supervisor_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # ... update logic
```

---

## 5. Implementacja Hierarchii Przełożonych

### Koncepcja

System wykorzystuje **self-referential relationship** w tabeli `users`:

```sql
supervisor_id INTEGER REFERENCES users(id)
```

**Kluczowe cechy:**
- ✅ Każdy użytkownik może mieć przełożonego (lub NULL)
- ✅ Przełożonym może być DOWOLNY użytkownik (niezależnie od roli)
- ✅ Brak ograniczeń hierarchicznych (np. Manager może mieć Pracownika jako przełożonego)
- ✅ Automatyczne przypisanie supervisora do wniosków

### Algorytm Przypisania Przełożonego

**Kod (app.py:153-166):**
```python
@app.route('/api/requests', methods=['POST'])
@login_required
def create_request():
    data = request.json

    # Automatyczne przypisanie supervisor_id
    supervisor_id = current_user.supervisor_id

    new_request = TimeOffRequest(
        user_id=current_user.id,
        type=data['type'],
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
        reason=data.get('reason', ''),
        status='pending',
        supervisor_id=supervisor_id  # ← Automatyczne przypisanie
    )

    db.session.add(new_request)
    db.session.commit()
    return jsonify(new_request.to_dict()), 201
```

### Frontend: Dropdown dla Przełożonych

**Kod (static/index.html:793-800):**
```javascript
const loadManagers = async () => {
    try {
        // Pobieranie WSZYSTKICH użytkowników (nie tylko managerów)
        const res = await axios.get('/api/users');
        setManagers(res.data);
    } catch (err) {
        console.error('Error loading managers:', err);
    }
};
```

**Dropdown w formularzu (static/index.html:983-992):**
```jsx
<select
    value={newUser.supervisor_id || ''}
    onChange={(e) => setNewUser({...newUser, supervisor_id: e.target.value ? parseInt(e.target.value) : null})}
    className="w-full px-4 py-2 border rounded-lg"
>
    <option value="">Brak przełożonego</option>
    {managers.map(m => (
        <option key={m.id} value={m.id}>
            {m.first_name} {m.last_name} ({m.role})
        </option>
    ))}
</select>
```

**Filtrowanie w edycji (static/index.html:1080):**
```jsx
{managers.filter(m => m.id !== editModal.id).map(m => (
    <option key={m.id} value={m.id}>
        {m.first_name} {m.last_name} ({m.role})
    </option>
))}
```

### Przykładowa Hierarchia

```
Admin System (admin) [supervisor: NULL]
    ├── Anna Kowalska (manager) [supervisor: Admin]
    │       ├── Jan Nowak (pracownik) [supervisor: Anna]
    │       └── Maria Wiśniewska (pracownik) [supervisor: Anna]
    └── Piotr Zieliński (manager) [supervisor: Admin]
            └── Krzysztof Lewandowski (pracownik) [supervisor: Piotr]
```

**Elastyczny przykład (dowolna hierarchia):**
```
Board Member (pracownik) [supervisor: NULL]
    └── CEO (admin) [supervisor: Board Member]  ← Admin ma przełożonego!
            ├── CTO (manager) [supervisor: CEO]
            │       └── Senior Dev (pracownik) [supervisor: CTO]
            └── CFO (manager) [supervisor: CEO]
```

---

## 6. Deployment

### Środowisko Produkcyjne: Azure Web App

**Platforma:** Azure App Service (Linux)

**Stack:**
- Python 3.11+
- Gunicorn WSGI server
- PostgreSQL 14+

### Skrypt Deployment: `azure-deploy.sh`

**Plik:** `/home/radek/azure-deploy.sh`

**Funkcje:**
1. Walidacja zmiennych środowiskowych
2. Budowanie backendu
3. Tworzenie Dockerfile
4. Build obrazu Docker
5. Deployment do Azure Container Registry
6. Deployment do Azure Web App

**Wymagane zmienne środowiskowe:**
```bash
export DB_PASSWORD="YourStrongPasswordHere"
```

**Uruchomienie:**
```bash
chmod +x azure-deploy.sh
./azure-deploy.sh
```

**Proces deployment:**

1. **Walidacja:**
   ```bash
   if [ -z "$DB_PASSWORD" ]; then
       echo "❌ BŁĄD: Brak hasła do bazy danych!"
       exit 1
   fi
   ```

2. **Build backend:**
   ```bash
   python build_backend.py
   ```

3. **Docker build:**
   ```bash
   docker build -t timeoff-manager:latest .
   ```

4. **Push do Azure:**
   ```bash
   az acr login --name timeoffregistry
   docker tag timeoff-manager:latest timeoffregistry.azurecr.io/timeoff-manager:latest
   docker push timeoffregistry.azurecr.io/timeoff-manager:latest
   ```

5. **Deploy do Web App:**
   ```bash
   az webapp config container set \
       --name timeoff-manager \
       --resource-group TimeOffRG \
       --docker-custom-image-name timeoffregistry.azurecr.io/timeoff-manager:latest
   ```

### Konfiguracja Azure

**App Settings (Environment Variables):**
```bash
az webapp config appsettings set \
    --name timeoff-manager \
    --resource-group TimeOffRG \
    --settings \
        FLASK_ENV=production \
        SECRET_KEY="your-secret-key-here" \
        DATABASE_URL="postgresql://user:$DB_PASSWORD@server/db" \
        PYTHONUNBUFFERED=1
```

### Dockerfile

**Przykład:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
```

### Database Migration (prod)

**PostgreSQL Setup:**
```sql
CREATE DATABASE timeoff_db;
CREATE USER timeoff_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE timeoff_db TO timeoff_user;
```

**Migration (app.py):**
```python
with app.app_context():
    db.create_all()  # Tworzy tabele jeśli nie istnieją
```

---

## 7. Konfiguracja

### Zmienne Środowiskowe

**Development (.env):**
```bash
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///timeoff.db
```

**Production (Azure App Settings):**
```bash
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://<user>:<password>@<host>/<database>
PYTHONUNBUFFERED=1
```

### app.py Configuration

**Kod (app.py:17-30):**
```python
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///timeoff.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS configuration
CORS(app, supports_credentials=True, origins=['http://localhost:5000', 'https://timeoff-manager.azurewebsites.net'])
```

### Baza Danych

**SQLite (Development):**
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timeoff.db'
```

**PostgreSQL (Production):**
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@host:5432/database'
```

### CORS Policy

**Dozwolone originy:**
- `http://localhost:5000` (development)
- `https://timeoff-manager.azurewebsites.net` (production)

**Credentials:** Enabled (wymaga wysyłania cookies dla autentykacji)

---

## 8. Bezpieczeństwo

### Ochrona Haseł

✅ **PBKDF2-SHA256** hashing (Werkzeug)
✅ **600,000 iterations** (domyślne w Werkzeug)
✅ **Unique salt** per password
✅ Hasła **nigdy** nie są przechowywane w plaintext

**Przykład hash:**
```
pbkdf2:sha256:600000$8zJnwXkR$5eb7d6e4a6f9b3c2d1a0e9f8g7h6i5j4k3l2m1n0o9p8q7r6s5t4u3v2w1x0y9z
```

### Session Security

✅ **HTTP-only cookies** (brak dostępu z JS)
✅ **Secure flag** w produkcji (HTTPS only)
✅ **SameSite=Lax** (ochrona CSRF)
✅ Session timeout (domyślnie 31 dni w Flask-Login)

**Konfiguracja:**
```python
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # w produkcji
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

### SQL Injection Protection

✅ **SQLAlchemy ORM** (parametryzowane zapytania)
✅ Brak raw SQL queries
✅ Input validation via ORM constraints

**Bezpieczne (ORM):**
```python
user = User.query.filter_by(username=username).first()
```

**Niebezpieczne (raw SQL):**
```python
# NIGDY NIE ROBIMY TAK!
cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

### XSS Protection

✅ React **automatycznie escapuje** wartości w JSX
✅ Brak użycia `dangerouslySetInnerHTML`
✅ Content-Security-Policy headers (do dodania w produkcji)

**Bezpieczne (React):**
```jsx
<p>{user.first_name}</p>  {/* Automatycznie escapowane */}
```

### CSRF Protection

⚠️ **Brak dedykowanego CSRF tokena** (aplikacja SPA)
✅ **SameSite cookies** jako ochrona podstawowa
✅ **Origin checking** przez CORS policy

**Rekomendacja dla produkcji:**
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
app.config['WTF_CSRF_ENABLED'] = True
```

### Authorization Checks

✅ **@login_required** decorator na wszystkich endpoints
✅ **Role-based access** w logice biznesowej
✅ **Ownership checks** przed modyfikacją danych

**Przykład (app.py:200-207):**
```python
@app.route('/api/requests/<int:id>', methods=['DELETE'])
@login_required
def delete_request(id):
    req = TimeOffRequest.query.get_or_404(id)

    # Authorization check
    if req.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(req)
    db.session.commit()
    return jsonify({'message': 'Request deleted successfully'}), 200
```

### Rate Limiting

⚠️ **Brak implementacji** (rekomendowane dla produkcji)

**Rekomendacja:**
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: current_user.id if current_user.is_authenticated else request.remote_addr)

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # ...
```

### Environment Variables

✅ **SECRET_KEY** z environment variables
✅ **DB_PASSWORD** nie jest hardcoded
⚠️ Brak `.env` w repo (użyj `.gitignore`)

**`.gitignore`:**
```
.env
*.db
__pycache__/
*.pyc
```

### HTTPS Enforcement

✅ Azure Web App automatycznie przekierowuje HTTP → HTTPS
✅ Secure cookies enabled w produkcji

### Logging & Monitoring

⚠️ **Brak implementacji**

**Rekomendacja:**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/login', methods=['POST'])
def login():
    logger.info(f"Login attempt for user: {request.json.get('username')}")
    # ...
```

---

## 9. Build Process

### `build_backend.py`

**Funkcje:**
1. Minifikacja `static/index.html`
2. Inlining CSS i JavaScript
3. Optymalizacja rozmiaru

**Uruchomienie:**
```bash
python build_backend.py
```

**Output:**
- `static/index.html` (zminifikowany)

---

## 10. Testing

### Testy Backend (Pytest)

**Plik:** `test_app.py`

**Uruchomienie:**
```bash
pytest test_app.py -v
```

**Coverage:**
- ✅ Logowanie (poprawne credentials, błędne credentials)
- ✅ Tworzenie użytkownika (admin)
- ✅ Pobieranie listy użytkowników
- ✅ Tworzenie wniosku urlopowego
- ✅ Akceptacja wniosku przez supervisora
- ✅ Odrzucenie wniosku
- ✅ Autoryzacja (403 dla nieuprawnionego użytkownika)

### Testy UI (Playwright)

**Plik:** `test_ui.py`

**Uruchomienie:**
```bash
pytest test_ui.py -v
```

**Coverage:**
- ✅ Logowanie i nawigacja
- ✅ Tworzenie użytkownika (Admin panel)
- ✅ Tworzenie wniosku urlopowego
- ✅ Akceptacja wniosku (Manager view)

---

## 11. Troubleshooting

### Problem: "Not authenticated" error

**Przyczyna:** Brak ważnej sesji Flask-Login

**Rozwiązanie:**
1. Sprawdź czy użytkownik jest zalogowany: `GET /api/current-user`
2. Zaloguj się ponownie: `POST /api/login`

### Problem: "Unauthorized" (403) przy akceptacji wniosku

**Przyczyna:** Użytkownik nie jest supervisorem dla danego wniosku

**Rozwiązanie:**
- Admin może akceptować wszystkie wnioski
- Manager może akceptować tylko wnioski gdzie `supervisor_id = manager.id`

### Problem: SQLite locked database

**Przyczyna:** Równoczesny dostęp do SQLite (single-writer limitation)

**Rozwiązanie:** Użyj PostgreSQL w produkcji

### Problem: CORS errors w przeglądarce

**Przyczyna:** Nieprawidłowe originy w konfiguracji CORS

**Rozwiązanie:**
```python
CORS(app, supports_credentials=True, origins=['http://localhost:5000', 'https://your-domain.com'])
```

### Problem: Azure deployment failed

**Przyczyna:** Brak `DB_PASSWORD` environment variable

**Rozwiązanie:**
```bash
export DB_PASSWORD="YourStrongPassword"
./azure-deploy.sh
```

---

## 12. Kontakt i Support

**Repozytorium:** https://github.com/PowerBIIT/timeoff-manager

**Zgłaszanie błędów:** GitHub Issues

**Dokumentacja użytkownika:** `USER-GUIDE.md`

**Plan testów:** `TEST-PLAN-DETAILED.md`

---

## 13. Changelog

### v1.0.0 (2025-10-04)

**Features:**
- ✅ Hierarchia przełożonych (self-referential supervisor_id)
- ✅ Automatyczne przypisanie supervisora do wniosków
- ✅ Role-based access control (Admin, Manager, Pracownik)
- ✅ Akceptacja/odrzucenie wniosków przez przełożonych
- ✅ Pełny CRUD dla użytkowników (Admin)
- ✅ Flask-Login authentication
- ✅ React SPA frontend
- ✅ Azure deployment script

**Fixes:**
- ✅ Dropdown przełożonych pokazuje wszystkich użytkowników (nie tylko managerów)
- ✅ Dodano labele ról w dropdownie przełożonych
- ✅ Zabezpieczenie przed wyborem siebie jako przełożonego (edit form)

---

**Koniec Dokumentacji Technicznej**
