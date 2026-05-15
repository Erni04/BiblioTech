import random
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker

# Import modeli
from bibliotech.models import Autor, Gatunek, Ksiazka, Egzemplarz, LogAkcji

# Inicjalizacja Fakera w języku polskim
fake = Faker('pl_PL')

class Command(BaseCommand):
    help = 'Wypełnia bazę danych losowymi danymi testowymi za pomocą Fakera'

    def handle(self, *args, **kwargs):
        self.stdout.write("Generowanie danych... Proszę czekać.")
        
        # 1. Tworzenie Gatunków
        self.stdout.write("Tworzę gatunki...")
        gatunki_nazwy = ['Kryminał', 'Fantasy', 'Sci-Fi', 'Biografia', 'Romans', 'Historyczna', 'Reportaż']
        gatunki_obiekty = []
        for nazwa in gatunki_nazwy:
            g, created = Gatunek.objects.get_or_create(nazwa=nazwa)
            gatunki_obiekty.append(g)

        # 2. Tworzenie Czytelników (Użytkowników)
        self.stdout.write("Generuję czytelników...")
        for i in range(15):  #15 dla lepszych testów
            username = f"czytelnik_{i+1}"
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    password='haslo123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.email()
                )
        
        # POBIERAMY WSZYSTKICH CZYTELNIKÓW DO LISTY
        czytelnicy_obj = list(User.objects.filter(is_staff=False))

        # 3. Tworzenie Autorów
        self.stdout.write("Tworzę autorów...")
        autorzy_obj = []
        for _ in range(12):
            a = Autor.objects.create(imie_nazwisko=fake.name())
            autorzy_obj.append(a)

        # 4. Tworzenie Książek i Egzemplarzy
        self.stdout.write("Tworzę książki i fizyczne egzemplarze...")
        wszystkie_egzemplarze = []
        for _ in range(25):
            k = Ksiazka.objects.create(
                tytul=fake.sentence(nb_words=3).replace(".", "").title(),
                opis=fake.paragraph(nb_sentences=5),                
                rok_wydania=random.randint(1990, 2026),
                autor=random.choice(autorzy_obj),
                gatunek=random.choice(gatunki_obiekty)
            )

            # Dla każdej książki tworzymy od 1 do 3 fizycznych egzemplarzy
            for _ in range(random.randint(1, 3)):
                egz = Egzemplarz.objects.create(
                    ksiazka=k,
                    kod_kreskowy=fake.ean8(),
                    status='D'
                )
                wszystkie_egzemplarze.append(egz)

        # 5. Generowanie aktywnych wypożyczeń
        if czytelnicy_obj and wszystkie_egzemplarze:
            self.stdout.write("Generuję aktywne wypożyczenia i historię...")
            # Losujemy 10 egzemplarzy, które będą wypożyczone
            do_wypozyczenia = random.sample(wszystkie_egzemplarze, min(10, len(wszystkie_egzemplarze)))
            
            for egz in do_wypozyczenia:
                random_user = random.choice(czytelnicy_obj)
                egz.status = 'W'
                egz.aktualny_czytelnik = random_user
                # Ustawiamy termin zwrotu (od 5 dni temu do 14 dni w przód)
                egz.termin_zwrotu = timezone.now().date() + timedelta(days=random.randint(-5, 14))
                egz.save()
                
                # Dodajemy wpis do logów, żeby system nie był pusty
                LogAkcji.objects.create(
                    egzemplarz=egz,
                    uzytkownik=random_user,
                    akcja='W',
                    data=timezone.now()
                )

        self.stdout.write(self.style.SUCCESS('Sukces! Baza danych została nakarmiona soczystymi danymi.'))