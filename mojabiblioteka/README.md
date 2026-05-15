System Zarządzania Biblioteką - BiblioTech

Witaj w projekcie BiblioTech! Jest to kompletna aplikacja webowa zbudowana w oparciu o framework Django, służąca do zarządzania zasobami bibliotecznymi, rezerwacjami oraz bazą czytelników.
 Instrukcja Szybkiego Startu

Postępuj zgodnie z poniższymi krokami, aby uruchomić czystą wersję aplikacji na swoim komputerze.
1. Przygotowanie środowiska (Izolacja)

Stwórz wirtualne środowisko, aby biblioteki projektu nie kolidowały z Twoim systemem:


python -m venv venv

Aktywuj środowisko:

    Windows: venv\Scripts\activate

    macOS/Linux: source venv/bin/activate

2. Instalacja wymaganych komponentów

Zainstaluj silnik Django oraz bibliotekę do obsługi obrazów (okładek):


pip install django pillow

3. Budowa struktury bazy danych

Stwórz tabele w lokalnej bazie danych SQLite:


python manage.py makemigrations
python manage.py migrate

4. Tworzenie konta Administratora (Bibliotekarza)

Stwórz pierwsze konto z pełnymi uprawnieniami (podaj login, email i hasło):


python manage.py createsuperuser

5. Generowanie danych testowych (Seed)

Aby nie musieć wpisywać wszystkiego ręcznie, wypełnij bazę przykładowymi książkami i autorami:


python manage.py seed_data

6. Uruchomienie aplikacji

Odpal serwer deweloperski:


python manage.py runserver

Aplikacja jest teraz dostępna pod adresem: http://127.0.0.1:8000/

Przez Panel Administratora nadajemy uprawnienia dla bibliotekarza(pracownika biblioteki)
Jeśli masz już stworzone konto Superużytkownika (tego z komendy createsuperuser), możesz nadawać uprawnienia innym osobom.
1.	Zaloguj się na: http://127.0.0.1:8000/admin/.
2.	Wejdź w sekcję Użytkownicy (Users).
3.	Kliknij w nazwę użytkownika, który ma zostać bibliotekarzem.
4.	Zjedź do sekcji Uprawnienia (Permissions).
5.	Zaznacz okienko Status personelu (Staff status).
Ważne: Nie musisz zaznaczać "Status superużytkownika". Bibliotekarz potrzebuje tylko statusu personelu, aby kod go wpuścił do panelu.
6.	Kliknij Zapisz na dole strony.


Wszystkie widoki dla pracowników są zabezpieczone dekoratorami @staff_member_required. Aby przetestować funkcje bibliotekarza, należy zalogować się na konto stworzone w punkcie 4 (Superuser).