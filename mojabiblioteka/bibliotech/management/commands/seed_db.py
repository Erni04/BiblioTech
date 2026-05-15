import random
from django.core.management.base import BaseCommand
from faker import Faker
from bibliotech.models import Autor, Gatunek, Ksiazka, Egzemplarz

# Inicjalizacja Fakera w języku polskim
fake = Faker('pl_PL')

class Command(BaseCommand):
    help = 'Wypełnia bazę danych losowymi danymi testowymi'

    def handle(self, *args, **kwargs):
        self.stdout.write("Generowanie danych... Proszę czekać.")

        # 1. Tworzymy Gatunki
        gatunki_nazwy = ['Kryminał', 'Fantasy', 'Sci-Fi', 'Biografia', 'Romans', 'Historyczna']
        gatunki_obiekty = []
        for nazwa in gatunki_nazwy:
            g, created = Gatunek.objects.get_or_create(nazwa=nazwa)
            gatunki_obiekty.append(g)

        # 2. Tworzymy Autorów
        autorzy = []
        for _ in range(10):
            a = Autor.objects.create(
                imie_nazwisko=fake.name()
            )
            autorzy.append(a)

        # 3. Tworzymy Książki
        for _ in range(20):
            k = Ksiazka.objects.create(
                tytul=fake.sentence(nb_words=3).replace(".", ""),
                opis=fake.paragraph(nb_sentences=5),
                rok_wydania=fake.date_between(start_date='-20y', end_date='today'),
                autor=random.choice(autorzy),
                gatunek=random.choice(gatunki_obiekty)
            )

            # 4. Dla każdej książki tworzymy od 1 do 3 fizycznych egzemplarzy
            for _ in range(random.randint(1, 3)):
                Egzemplarz.objects.create(
                    ksiazka=k,
                    kod_kreskowy=fake.ean8(), # Losowy kod kreskowy
                    status='D' # Domyślnie wszystkie dostępne
                )

        self.stdout.write(self.style.SUCCESS('Sukces! Baza danych została nakarmiona.'))