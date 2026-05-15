from django import forms
from .models import Ksiazka, Egzemplarz

class KsiazkaZAutoEgzemplarzamiForm(forms.ModelForm):
    liczba_egzemplarzy = forms.IntegerField(
        min_value=1, initial=1, label="Ile sztuk dodajesz?"
    )
    kod_manualny = forms.CharField(
        required=False, 
        label="Podaj kod (jeśli dodajesz 1 sztukę)",
        help_text="Zostaw puste, jeśli system ma wygenerować kod."
    )
    auto_generuj = forms.BooleanField(
        required=False, 
        initial=True, 
        label="Generuj kody automatycznie?"
    )

    class Meta:
        model = Ksiazka
        fields = ['tytul', 'autor', 'gatunek', 'opis', 'rok_wydania', 'okladka']