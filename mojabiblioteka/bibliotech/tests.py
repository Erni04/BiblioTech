from django.test import TestCase
from .models import Gatunek, Autor, Ksiazka

class BibliotekaTest(TestCase):
    
    def setUp(self):
        """Przygotowanie danych do testów (uruchamiane przed każdym testem)"""
        self.gatunek = Gatunek.objects.create(nazwa="Dramat")
        self.autor = Autor.objects.create(imie_nazwisko="Jan Kowalski")
        self.ksiazka = Ksiazka.objects.create(
            tytul="Testowa Książka",
            autor=self.autor,
            gatunek=self.gatunek,
            rok_wydania="2024"
        )

    def test_czy_ksiazka_ma_poprawny_tytul(self):
        """Sprawdza, czy model poprawnie zapisuje i zwraca tytuł"""
        ksiazka = Ksiazka.objects.get(id=self.ksiazka.id)
        self.assertEqual(ksiazka.tytul, "Testowa Książka")

    def test_str_method(self):
        """Sprawdza, czy obiekty poprawnie wyświetlają swoje nazwy w panelu Admina"""
        self.assertEqual(str(self.gatunek), "Dramat")
        self.assertEqual(str(self.ksiazka), "Testowa Książka")