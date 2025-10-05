# 💤 Idle Monitoring - Auto-stop po bezczynności

**Data:** 2025-10-05

---

## 🎯 Co to jest?

System automatycznego monitoringu bezczynności, który **zatrzymuje środowiska Azure (DEV + PROD) po 30 minutach braku requestów HTTP**.

### Różnica vs. harmonogram czasowy:

| Funkcja | Harmonogram czasowy | Idle Monitoring |
|---------|---------------------|-----------------|
| **Zatrzymanie** | O określonych godzinach (18:00-08:00) | Po 30 min bez requestów |
| **Oszczędność** | ~$300/m (50%) | Zależy od użycia, max ~$300/m |
| **Reakcja na ruch** | Nie | Tak - auto start przy requeście |
| **Najlepsze dla** | Przewidywalny harmonogram | Sporadyczne użycie |

---

## 🚀 Instalacja

### Metoda 1: Automatyczna

```bash
cd /home/radek/timeoff-manager
./scripts/setup-idle-monitor.sh
```

**Skrypt:**
1. Nadaje uprawnienia
2. Pyta czy usunąć stary harmonogram (auto-stop-both.sh)
3. Dodaje do crontab monitoring co 5 minut
4. Testuje pierwsze wykonanie

### Metoda 2: Manualna

```bash
# Nadaj uprawnienia
chmod +x /home/radek/timeoff-manager/scripts/auto-stop-on-idle.sh

# Edytuj crontab
crontab -e

# Dodaj linię (sprawdza co 5 minut):
*/5 * * * * /home/radek/timeoff-manager/scripts/auto-stop-on-idle.sh >> /var/log/idle-monitor.log 2>&1
```

---

## ⚙️ Konfiguracja

### Zmiana progu bezczynności (domyślnie 30 minut)

Edytuj skrypt:

```bash
nano /home/radek/timeoff-manager/scripts/auto-stop-on-idle.sh
```

Zmień wartość:

```bash
# Czas bezczynności (w minutach)
IDLE_THRESHOLD=30  # Zmień na 15, 60, etc.
```

Przykłady:
- `IDLE_THRESHOLD=15` - zatrzymanie po 15 minutach
- `IDLE_THRESHOLD=60` - zatrzymanie po 1 godzinie
- `IDLE_THRESHOLD=120` - zatrzymanie po 2 godzinach

### Zmiana częstotliwości sprawdzania (domyślnie co 5 minut)

```bash
crontab -e

# Zmień na co 10 minut:
*/10 * * * * /home/radek/timeoff-manager/scripts/auto-stop-on-idle.sh >> /var/log/idle-monitor.log 2>&1

# Lub co 1 minutę (większa dokładność, więcej wywołań az CLI):
*/1 * * * * /home/radek/timeoff-manager/scripts/auto-stop-on-idle.sh >> /var/log/idle-monitor.log 2>&1
```

---

## 🔍 Jak to działa?

### 1. Monitoring (co 5 minut)

Skrypt:
1. Sprawdza czy App Service jest uruchomiony
2. Jeśli TAK → pobiera ostatnie logi Azure (ostatnie 100 linii)
3. Szuka HTTP requestów (200, 404, 500, etc.)
4. Zapisuje timestamp ostatniego requestu

### 2. Licznik bezczynności

```
Request wykryty → reset licznika
Brak requestu → licznik++

Jeśli licznik >= 30 minut → STOP
```

### 3. Auto-start

**UWAGA:** Skrypt **NIE startuje automatycznie** środowisk!

Musisz uruchomić ręcznie:

```bash
# DEV
az webapp start -n timeoff-manager-dev -g timeoff-manager-rg-dev
az postgres flexible-server start -n timeoff-db-dev -g timeoff-manager-rg-dev

# PROD
az webapp start -n timeoff-manager-20251004 -g timeoff-rg-prod
az postgres flexible-server start -n timeoff-db-20251004 -g timeoff-rg-prod
```

**Alternatywa:** Można dodać Azure Application Gateway z health probe który auto-startuje, ale to dodatkowy koszt.

---

## 📊 Przykładowy scenariusz

### Dzień 1:

```
08:00 - Start ręczny DEV
08:15 - Developer loguje się → requesty HTTP
10:00 - Przerwa kawowa (30 min)
10:35 - DEV STOP (30 min bezczynności) 💰
11:00 - Start ręczny DEV
12:00 - Lunch break
12:35 - DEV STOP 💰
13:00 - Start ręczny DEV
17:00 - Koniec pracy
17:35 - DEV STOP 💰
```

**Oszczędność:** ~6h działania zamiast 24h = 75% oszczędności tego dnia!

---

## 📝 Monitorowanie

### Sprawdź logi:

```bash
# Tail live
tail -f /var/log/idle-monitor.log

# Ostatnie 50 linii
tail -50 /var/log/idle-monitor.log

# Szukaj zatrzymań
grep "Zatrzymywanie" /var/log/idle-monitor.log
```

### Przykładowy log:

```
2025-10-05 10:05:00 - Checking idle status...

🔍 DEV Environment:
  DEV: Aktywny (ostatni request: teraz)

🔍 PROD Environment:
  PROD: Bezczynny przez 25 minut

2025-10-05 10:05:15 - Check complete!
---

2025-10-05 10:10:00 - Checking idle status...

🔍 DEV Environment:
  DEV: Bezczynny przez 5 minut

🔍 PROD Environment:
  PROD: Bezczynny przez 30 minut
  🌙 Zatrzymywanie PROD (brak aktywności > 30min)...
    ✅ App zatrzymany
    ✅ DB zatrzymany
    💰 Oszczędzanie rozpoczęte!

2025-10-05 10:10:45 - Check complete!
---
```

### Sprawdź status środowisk:

```bash
# DEV
az webapp show -n timeoff-manager-dev -g timeoff-manager-rg-dev --query state -o tsv

# PROD
az webapp show -n timeoff-manager-20251004 -g timeoff-rg-prod --query state -o tsv

# Powinno być: "Running" lub "Stopped"
```

---

## 🛠️ Troubleshooting

### Problem: Środowiska zatrzymują się zbyt często

**Rozwiązanie:**
- Zwiększ `IDLE_THRESHOLD` z 30 do 60 minut
- Zmniejsz częstotliwość sprawdzania z `*/5` na `*/10`

### Problem: Środowiska nie zatrzymują się wcale

**Sprawdź:**

```bash
# Czy cron działa?
crontab -l | grep idle

# Czy są logi?
ls -lh /var/log/idle-monitor.log

# Czy są błędy?
tail -100 /var/log/idle-monitor.log | grep -i error
```

### Problem: "az: command not found" w logach

**Rozwiązanie:**

Dodaj pełną ścieżkę do az w crontab:

```bash
crontab -e

# Zmień na:
*/5 * * * * /usr/bin/az --version > /dev/null && /home/radek/timeoff-manager/scripts/auto-stop-on-idle.sh >> /var/log/idle-monitor.log 2>&1
```

### Problem: Nie wykrywa requestów

**Debug:**

```bash
# Test ręczny
cd /home/radek/timeoff-manager
bash -x scripts/auto-stop-on-idle.sh

# Sprawdź czy az CLI działa
az webapp log tail -n timeoff-manager-dev -g timeoff-manager-rg-dev --lines 10
```

---

## 🔄 Przełączanie między trybami

### Harmonogram czasowy → Idle Monitoring

```bash
# 1. Usuń stary cron
crontab -e
# Usuń linię: 0 * * * * .../auto-stop-both.sh

# 2. Dodaj idle monitoring
./scripts/setup-idle-monitor.sh
```

### Idle Monitoring → Harmonogram czasowy

```bash
# 1. Usuń idle monitoring
crontab -e
# Usuń linię: */5 * * * * .../auto-stop-on-idle.sh

# 2. Dodaj harmonogram
./scripts/setup-auto-stop.sh
```

### Oba jednocześnie (hybrydowy)

```bash
crontab -e

# Harmonogram: STOP po godzinach
0 18 * * * /home/radek/timeoff-manager/scripts/auto-stop-both.sh

# Idle: STOP po bezczynności w ciągu dnia
*/5 8-17 * * 1-5 /home/radek/timeoff-manager/scripts/auto-stop-on-idle.sh >> /var/log/idle-monitor.log 2>&1
```

**Efekt:**
- W nocy i weekendy: automatyczne STOP o 18:00
- W ciągu dnia (8-17, pon-pt): STOP po 30 min bezczynności

---

## 💰 Oszczędności

### Scenariusz 1: Środowiska używane 2h dziennie

```
DEV:  ~$40/m → ~$3/m (92% oszczędność!)
PROD: ~$565/m → ~$47/m (92% oszczędność!)
TOTAL: ~$50/m vs $605/m = ~$555/m oszczędności!
```

### Scenariusz 2: Środowiska używane 8h dziennie (harmonogram pracy)

```
DEV:  ~$40/m → ~$13/m (67% oszczędność)
PROD: ~$565/m → ~$188/m (67% oszczędność)
TOTAL: ~$201/m vs $605/m = ~$404/m oszczędności!
```

### Scenariusz 3: Harmonogram czasowy (18:00-08:00 + weekend)

```
DEV:  ~$40/m → ~$20/m (50% oszczędność)
PROD: ~$565/m → ~$285/m (50% oszczędność)
TOTAL: ~$305/m vs $605/m = ~$300/m oszczędności!
```

**Wniosek:** Idle monitoring daje **większe oszczędności** jeśli środowiska są używane sporadycznie!

---

## 📚 Pliki

- `scripts/auto-stop-on-idle.sh` - główny skrypt monitoringu
- `scripts/setup-idle-monitor.sh` - instalator
- `/var/log/idle-monitor.log` - logi monitoringu
- `/var/tmp/azure-idle-monitor/dev-last-request` - timestamp ostatniego requestu DEV
- `/var/tmp/azure-idle-monitor/prod-last-request` - timestamp ostatniego requestu PROD

---

## ✅ Checklist

Po instalacji sprawdź:

- [ ] Skrypt ma uprawnienia wykonywania: `ls -l scripts/auto-stop-on-idle.sh`
- [ ] Crontab skonfigurowany: `crontab -l | grep idle`
- [ ] Pierwszy test wykonany: `bash scripts/auto-stop-on-idle.sh`
- [ ] Logi są tworzone: `ls -lh /var/log/idle-monitor.log`
- [ ] State directory istnieje: `ls -la /var/tmp/azure-idle-monitor/`

---

**Data utworzenia:** 2025-10-05
**Wersja:** 1.0
**Próg bezczynności:** 30 minut
**Częstotliwość sprawdzania:** 5 minut
