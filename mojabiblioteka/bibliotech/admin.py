from django.contrib import admin
from .models import Gatunek, Autor, Ksiazka, Egzemplarz, Rezerwacja

# Inline pozwala edytować Egzemplarze bezpośrednio w widoku Książki
class EgzemplarzInline(admin.TabularInline):
    model = Egzemplarz
    extra = 1 # Ile pustych pól wyświetlić na starcie

@admin.register(Ksiazka)
class KsiazkaAdmin(admin.ModelAdmin):
    # Co widać na liście książek
    list_display = ('tytul', 'autor', 'gatunek', 'liczba_egzemplarzy')
    # Po czym można wyszukiwać
    search_fields = ('tytul', 'autor__imie_nazwisko')
    # Filtry po boku
    list_filter = ('gatunek', 'autor')
    # Podpięcie Inline
    inlines = [EgzemplarzInline]

    # Własna metoda wyświetlająca dynamiczne dane
    def liczba_egzemplarzy(self, obj):
        return obj.egzemplarze.count()
    liczba_egzemplarzy.short_description = "Ilość sztuk"

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('imie_nazwisko', 'pokaz_zdjecie')

    def pokaz_zdjecie(self, obj):
        if obj.zdjecie:
            return "Jest zdjęcie"
        return "Brak"

# Rejestrujemy resztę standardowo
admin.site.register(Gatunek)
admin.site.register(Egzemplarz)
admin.site.register(Rezerwacja)