# BiblioTech - System Zarządzania Biblioteką

Projekt dyplomowy nowoczesnego systemu do obsługi biblioteki opartego na frameworku **Django**.

## Kluczowe funkcjonalności
* **Katalog Książek:** Zaawansowana wyszukiwarka z filtrowaniem według kategorii i parametrów tekstowych.
* **System Wypożyczeń:** Automatyczne obliczanie terminów zwrotu, zmiana statusów egzemplarzy oraz obsługa transakcyjna.
* **Panel Pracownika:** Kompleksowe zarządzanie zasobami (CRUD), edycja książek i monitorowanie historii egzemplarzy.
* **Powiadomienia:** System powiadomień e-mail oraz systemowych o dostępności zarezerwowanych pozycji.
* **Historia Akcji:** Pełny log działań użytkowników i bibliotekarzy (audyt).

## Technologia
* **Backend:** Python 3.12, Django 6.0
* **Frontend:** Bootstrap 5, HTMX (dynamiczne odświeżanie tabel)
* **Baza danych:** SQLite (środowisko deweloperskie)
* **Kontrola wersji:** Git / GitHub

## Instrukcja uruchomienia
1. Sklonuj repozytorium.
2. Stwórz środowisko wirtualne: `python -m venv venv`.
3. Aktywuj środowisko i zainstaluj zależności: `pip install -r requirements.txt`.
4. Wykonaj migracje: `python manage.py migrate`.
5. (Opcjonalnie) Załaduj dane testowe: `python manage.py seed_data`.
6. Uruchom serwer: `python manage.py runserver`.

---
*Autor: Ernest*
