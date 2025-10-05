# 🔄 Database Migrations - Instrukcja

## Proces aktualizacji bazy danych PROD

### ⚠️ WAŻNE: CI/CD NIE aktualizuje bazy automatycznie!

Deployment przez `git push origin master`:
- ✅ Aktualizuje KOD aplikacji
- ❌ **NIE** dotyka bazy danych
- ❌ **NIE** usuwa użytkowników
- ❌ **NIE** uruchamia migracji

**Baza danych jest aktualizowana TYLKO ręcznie i kontrolowanie!**

---

## 🛠️ Jak zaktualizować bazę PROD?

### Krok 1: Utwórz migrację lokalnie

```bash
# Zainstaluj Alembic (jeśli nie masz)
pip install alembic

# Wygeneruj automatyczną migrację z modeli
alembic revision --autogenerate -m "Dodanie kolumny email_verified"

# LUB utwórz ręczną migrację
alembic revision -m "Dodanie indeksu na email"
```

To utworzy plik w `migrations/versions/YYYYMMDD_HHMM_xxxxx_opis.py`

### Krok 2: Edytuj migrację (jeśli trzeba)

```python
# migrations/versions/20251005_1200_xxxxx_dodanie_kolumny.py

def upgrade() -> None:
    # Dodaj kolumnę
    op.add_column('users',
        sa.Column('email_verified', sa.Boolean(), nullable=True)
    )
    # Ustaw domyślną wartość dla istniejących
    op.execute("UPDATE users SET email_verified = false")
    # Zmień na NOT NULL
    op.alter_column('users', 'email_verified', nullable=False)

def downgrade() -> None:
    # Rollback
    op.drop_column('users', 'email_verified')
```

### Krok 3: Testuj lokalnie

```bash
# Test upgrade
alembic upgrade head

# Test downgrade (rollback)
alembic downgrade -1

# Przywróć
alembic upgrade head
```

### Krok 4: Deploy kodu (z migracją)

```bash
git add migrations/
git commit -m "feat: Dodanie email_verified do User model + migracja"
git push origin master
```

### Krok 5: Uruchom migrację na PROD

**Opcja A: SSH do Azure (zalecane)**
```bash
# Zaloguj się do PROD
az webapp ssh -n timeoff-manager-20251004 -g timeoff-rg-prod

# Sprawdź obecną wersję
alembic current

# Pokaż zaplanowane migracje
alembic history

# Uruchom migrację
alembic upgrade head

# Sprawdź czy OK
alembic current
```

**Opcja B: Azure CLI (lokalne wykonanie)**
```bash
# Backup bazy przed migracją (ZAWSZE!)
./scripts/backup-prod-db.sh

# Uruchom migrację przez SSH command
az webapp ssh -n timeoff-manager-20251004 -g timeoff-rg-prod \
  --command "cd /home/site/wwwroot && alembic upgrade head"
```

---

## 🔒 Bezpieczeństwo

### Przed każdą migracją PROD:

1. ✅ **Backup bazy danych**
   ```bash
   az postgres flexible-server backup create \
     --name timeoff-db-20251004 \
     --resource-group timeoff-rg-prod \
     --backup-name "before-migration-$(date +%Y%m%d-%H%M)"
   ```

2. ✅ **Testuj na DEV**
   ```bash
   # Uruchom DEV
   ./scripts/dev-only-mode.sh

   # SSH do DEV
   az webapp ssh -n timeoff-manager-dev -g timeoff-manager-rg-dev

   # Test migracji
   alembic upgrade head
   ```

3. ✅ **Plan rollback**
   - Każda migracja MUSI mieć `downgrade()`
   - Test rollback lokalnie: `alembic downgrade -1`

### Rollback w PROD (jeśli coś pójdzie nie tak):

```bash
# SSH do PROD
az webapp ssh -n timeoff-manager-20251004 -g timeoff-rg-prod

# Rollback o 1 wersję
alembic downgrade -1

# LUB rollback do konkretnej wersji
alembic downgrade abc123def456

# LUB restore z backup
az postgres flexible-server restore \
  --resource-group timeoff-rg-prod \
  --name timeoff-db-20251004-restored \
  --source-server timeoff-db-20251004 \
  --restore-time "2025-10-05T10:00:00Z"
```

---

## 📋 Przykładowe migracje

### Dodanie kolumny
```python
def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

def downgrade():
    op.drop_column('users', 'phone')
```

### Zmiana typu kolumny
```python
def upgrade():
    op.alter_column('requests', 'status',
        type_=sa.String(50),
        existing_type=sa.String(20)
    )

def downgrade():
    op.alter_column('requests', 'status',
        type_=sa.String(20),
        existing_type=sa.String(50)
    )
```

### Dodanie indeksu
```python
def upgrade():
    op.create_index('idx_user_email', 'users', ['email'], unique=True)

def downgrade():
    op.drop_index('idx_user_email', 'users')
```

### Migracja danych
```python
def upgrade():
    # Dodaj kolumnę
    op.add_column('users', sa.Column('full_name', sa.String(200)))

    # Migruj dane
    connection = op.get_bind()
    connection.execute(
        "UPDATE users SET full_name = first_name || ' ' || last_name"
    )

def downgrade():
    op.drop_column('users', 'full_name')
```

---

## 🚨 Błędy i troubleshooting

### "Migration already applied"
```bash
# Sprawdź obecną wersję
alembic current

# Zobacz historię
alembic history

# Oznacz jako wykonane (jeśli ręcznie zmieniłeś DB)
alembic stamp head
```

### "Can't locate revision"
```bash
# Usuń stare wersje z bazy
alembic downgrade base
alembic upgrade head
```

### "Database locked"
```bash
# Zatrzymaj aplikację
az webapp stop -n timeoff-manager-20251004 -g timeoff-rg-prod

# Uruchom migrację
alembic upgrade head

# Uruchom aplikację
az webapp start -n timeoff-manager-20251004 -g timeoff-rg-prod
```

---

## 📊 Monitoring migracji

### Sprawdź wersję bazy
```bash
alembic current
```

### Historia migracji
```bash
alembic history --verbose
```

### Pokaż SQL bez wykonania
```bash
alembic upgrade head --sql
```

---

## ✅ Checklist: Migracja PROD

- [ ] Utwórz migrację lokalnie
- [ ] Testuj upgrade/downgrade lokalnie
- [ ] Testuj na DEV environment
- [ ] Backup bazy PROD
- [ ] Deploy kodu (git push)
- [ ] Zatrzymaj PROD app (opcjonalnie, dla dużych zmian)
- [ ] SSH do PROD
- [ ] `alembic upgrade head`
- [ ] Sprawdź `alembic current`
- [ ] Uruchom PROD app
- [ ] Test aplikacji
- [ ] Monitoruj logi

---

**Aktualizacja:** 2025-10-05
**Autor:** PowerBIIT + Claude Code
