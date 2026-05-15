from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime

# ==========================================================
# 1. PODSTAWOWE MODELE (GATUNEK, AUTOR, KSIĄŻKA)
# ==========================================================

class Gatunek(models.Model):
    nazwa = models.CharField(max_length=100, unique=True, verbose_name="Nazwa gatunku")
    class Meta:
        verbose_name_plural = "Gatunki"
    def __str__(self):
        return self.nazwa

class Autor(models.Model):
    imie_nazwisko = models.CharField(max_length=200, verbose_name="Imię i Nazwisko")
    zdjecie = models.ImageField(upload_to='autorzy/', blank=True, null=True, verbose_name="Zdjęcie autora")
    class Meta:
        verbose_name_plural = "Autorzy"
    def __str__(self):
        return self.imie_nazwisko

class Ksiazka(models.Model):
    tytul = models.CharField(max_length=255, verbose_name="Tytuł")
    opis = models.TextField(verbose_name="Opis fabuły")
    rok_wydania = models.PositiveIntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(datetime.date.today().year)],
        verbose_name="Rok wydania",
        default=2026
    )
    okladka = models.ImageField(upload_to='okladki/', blank=True, null=True, verbose_name="Okładka")
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name="ksiazki")
    gatunek = models.ForeignKey(Gatunek, on_delete=models.SET_NULL, null=True, related_name="ksiazki")
    class Meta:
        verbose_name_plural = "Książki"
    def __str__(self):
        return self.tytul

# ==========================================================
# 2. ZASOBY I REZERWACJE
# ==========================================================

class Egzemplarz(models.Model):
    STATUS_CHOICES = [('D', 'Dostępny'), ('W', 'Wypożyczony'), ('R', 'Zarezerwowany')]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    ksiazka = models.ForeignKey(Ksiazka, on_delete=models.CASCADE, related_name="egzemplarze")
    kod_kreskowy = models.CharField(max_length=50, unique=True)
    termin_zwrotu = models.DateField(null=True, blank=True, verbose_name="Termin oddania")
    aktualny_czytelnik = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="wypozyczone_egzemplarze")
    class Meta:
        verbose_name_plural = "Egzemplarze"
    def __str__(self):
        return f"{self.ksiazka.tytul} - {self.kod_kreskowy}"

class Rezerwacja(models.Model):
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)
    egzemplarz = models.ForeignKey(Egzemplarz, on_delete=models.CASCADE)
    data_rezerwacji = models.DateTimeField(auto_now_add=True)
    data_waznosci = models.DateTimeField()
    def save(self, *args, **kwargs):
        if not self.id:
            self.data_waznosci = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)
    class Meta:
        verbose_name_plural = "Rezerwacje"

    
    @property
    def czy_aktualna(self):
        return self.data_waznosci > timezone.now()    

# ==========================================================
# 3. SYSTEM POWIADOMIEŃ I LOGI
# ==========================================================

class ZapisNaPowiadomienie(models.Model):
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE)
    ksiazka = models.ForeignKey(Ksiazka, on_delete=models.CASCADE)
    data_zapisu = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('uzytkownik', 'ksiazka')

class Powiadomienie(models.Model):
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE, related_name='powiadomienia')
    # Dodajemy default="", żeby migracja przeszła bez pytań
    tytul = models.CharField(max_length=200, default="Powiadomienie")
    tresc = models.TextField(default="")
    ksiazka = models.ForeignKey(Ksiazka, on_delete=models.SET_NULL, null=True, blank=True)
    czy_przeczytane = models.BooleanField(default=False)
    data_stworzenia = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "Powiadomienia"
    def __str__(self):
        return f"{self.tytul} dla {self.uzytkownik.username}"

class LogAkcji(models.Model):
    AKCJE = [('R', 'Rezerwacja'), ('W', 'Wypożyczenie'), ('Z', 'Zwrot'), ('A', 'Anulowanie rezerwacji')]
    egzemplarz = models.ForeignKey(Egzemplarz, on_delete=models.CASCADE, related_name="historia")
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Czytelnik")
    akcja = models.CharField(max_length=1, choices=AKCJE)
    data = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "Historia Akcji"
        ordering = ['-data']