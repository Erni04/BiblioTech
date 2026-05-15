import uuid
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q 
from django.utils import timezone
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.core.mail import send_mail
from django.conf import settings

# Import Twoich modeli i formularzy
from .models import Ksiazka, Egzemplarz, Rezerwacja, Gatunek, Powiadomienie, LogAkcji, ZapisNaPowiadomienie
from .forms import KsiazkaZAutoEgzemplarzamiForm

# ==========================================================
# 1. ZABEZPIECZENIA I REJESTRACJA
# ==========================================================

class BibliotekarzRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Adres e-mail jest wymagany do powiadomień.")
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class Rejestracja(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'bibliotech/rejestracja.html'

# ==========================================================
# 2. WIDOKI CZYTELNIKA
# ==========================================================

def lista_ksiazek(request):
    query = request.GET.get('q', '') # Dobrze jest dodać domyślny pusty ciąg
    gatunek_id = request.GET.get('gatunek', '')
    
    # Rozpoczynamy od wszystkich książek
    ksiazki = Ksiazka.objects.all()

    # Filtrowanie po tekście
    if query:
        ksiazki = ksiazki.filter(
            Q(tytul__icontains=query) | Q(autor__imie_nazwisko__icontains=query)
        ).distinct()

    # Filtrowanie po kategorii (gatunku)
    if gatunek_id:
        ksiazki = ksiazki.filter(gatunek_id=gatunek_id)

    # Przygotowanie pełnego kontekstu
    context = {
        'ksiazki': ksiazki,
        'query': query,
        'gatunki': Gatunek.objects.all(),
        'wybrany_gatunek': gatunek_id
    }
    
    # POPRAWKA: Przekazujemy cały słownik 'context'
    return render(request, 'bibliotech/lista_ksiazek.html', context)


def ksiazka_detale(request, pk):
    ksiazka = get_object_or_404(Ksiazka, pk=pk)
    return render(request, 'bibliotech/ksiazka_detale.html', {'ksiazka': ksiazka})

@login_required
def profil_uzytkownika(request):
    # --- AUTOMATYCZNE SPRZĄTANIE PRZETERMINOWANYCH REZERWACJI ---
    teraz = timezone.now()
    stare_rezerwacje = Rezerwacja.objects.filter(data_waznosci__lt=teraz)
    
    for rez in stare_rezerwacje:
        with transaction.atomic():
            egz = rez.egzemplarz
            egz.status = 'D'  # Przywracamy książkę na półkę
            egz.save()
            rez.delete()      # Usuwamy wygasłą rezerwację
            LogAkcji.objects.create(egzemplarz=egz, uzytkownik=rez.uzytkownik, akcja='A')
    # -----------------------------------------------------------

    wypozyczone = Egzemplarz.objects.filter(aktualny_czytelnik=request.user)
    rezerwacje = Rezerwacja.objects.filter(uzytkownik=request.user)
    historia = LogAkcji.objects.filter(uzytkownik=request.user).order_by('-data')[:10]
    
    return render(request, 'bibliotech/moje_konto.html', {
        'wypozyczone': wypozyczone,
        'rezerwacje': rezerwacje,
        'historia': historia,
        'dzisiaj': timezone.now().date()
    })

@login_required
def edytuj_profil(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, "Twoje dane zostały zaktualizowane!")
        return redirect('profil_uzytkownika')
    return render(request, 'bibliotech/edytuj_profil.html')

# ==========================================================
# 3. POWIADOMIENIA I REZERWACJE
# ==========================================================

@login_required
def powiadom_o_dostepnosci(request, ksiazka_id):
    ksiazka = get_object_or_404(Ksiazka, id=ksiazka_id)
    ZapisNaPowiadomienie.objects.get_or_create(uzytkownik=request.user, ksiazka=ksiazka)
    messages.info(request, f"Będziemy Cię informować o dostępności: {ksiazka.tytul}")
    return redirect('ksiazka_detale', pk=ksiazka.id)

@login_required
def oznacz_przeczytane(request, p_id):
    powiadomienie = get_object_or_404(Powiadomienie, id=p_id, uzytkownik=request.user)
    powiadomienie.czy_przeczytane = True
    powiadomienie.save()
    
    # Pobieramy cel z adresu URL (parametr ?next=)
    cel = request.GET.get('next')
    
    if cel:
        return redirect(cel)
    return redirect('lista_ksiazek')

@login_required
def rezerwuj_ksiazke(request, egzemplarz_id):
    egzemplarz = get_object_or_404(Egzemplarz, id=egzemplarz_id)
    with transaction.atomic():
        if egzemplarz.status == 'D':
            Rezerwacja.objects.create(uzytkownik=request.user, egzemplarz=egzemplarz)
            egzemplarz.status = 'R'
            egzemplarz.save()
            LogAkcji.objects.create(egzemplarz=egzemplarz, uzytkownik=request.user, akcja='R')
            messages.success(request, f"Zarezerwowano: {egzemplarz.ksiazka.tytul}!")
        else:
            messages.error(request, "Ten egzemplarz przestał być dostępny.")
    return redirect('ksiazka_detale', pk=egzemplarz.ksiazka.id)

@login_required
def anuluj_rezerwacje(request, rezerwacja_id):
    rezerwacja = get_object_or_404(Rezerwacja, id=rezerwacja_id, uzytkownik=request.user)
    with transaction.atomic():
        egzemplarz = rezerwacja.egzemplarz
        egzemplarz.status = 'D'
        egzemplarz.save()
        rezerwacja.delete()
        messages.info(request, "Rezerwacja anulowana.")
    return redirect('profil_uzytkownika')

# ==========================================================
# 4. PANEL BIBLIOTEKARZA
# ==========================================================

@staff_member_required
def panel_bibliotekarza(request):
    # 1. NAJPIERW POBIERAMY DANE (Definiujemy zmienne)
    ksiazki_bez_egz = Ksiazka.objects.filter(egzemplarze__isnull=True)
    query = request.GET.get('q', '')
    gatunek_id = request.GET.get('gatunek', '')
    
    # Pobieramy bazowy QuerySet
    egzemplarze = Egzemplarz.objects.all().select_related(
        'ksiazka', 'ksiazka__autor', 'ksiazka__gatunek', 'aktualny_czytelnik'
    ).prefetch_related('rezerwacja_set__uzytkownik').order_by('ksiazka__tytul')
    

    # 2. FILTRUJEMY (Jeśli trzeba)
    if query:
        egzemplarze = egzemplarze.filter(
            Q(ksiazka__tytul__icontains=query) | 
            Q(kod_kreskowy__icontains=query) |
            Q(aktualny_czytelnik__username__icontains=query)
        )

    if gatunek_id:
        egzemplarze = egzemplarze.filter(ksiazka__gatunek_id=gatunek_id)

    # 3. TWORZYMY KONTEKST (Pakujemy dane)
    context = {
        'egzemplarze': egzemplarze,
        'ksiazki_bez_egz': ksiazki_bez_egz,
        'query': query,
        'gatunki': Gatunek.objects.all(),
        'wybrany_gatunek': gatunek_id,
    }

    # 4. DECYDUJEMY O FORMIE WYSYŁKI
    # Jeśli zapytanie przyszło od HTMX (automatyczne odświeżanie)
    if request.headers.get('HX-Request'):
        return render(request, 'bibliotech/partials/tabela_egzemplarzy.html', context)
    
    # Jeśli to normalne wejście na stronę
    return render(request, 'bibliotech/panel_pracownika.html', context)


@staff_member_required
def zmien_status_egzemplarza(request, egz_id, nowy_status):
    egzemplarz = get_object_or_404(Egzemplarz, id=egz_id)
    ksiazka = egzemplarz.ksiazka
    with transaction.atomic():
        egzemplarz.status = nowy_status
        if nowy_status == 'D': # Zwrot
            egzemplarz.aktualny_czytelnik = None
            egzemplarz.termin_zwrotu = None
            oczekujacy = ZapisNaPowiadomienie.objects.filter(ksiazka=ksiazka)
            for zapis in oczekujacy:
                Powiadomienie.objects.create(
                    uzytkownik=zapis.uzytkownik,
                    tytul="Książka dostępna!",
                    tresc=f"Książka '{ksiazka.tytul}' wróciła.",
                    ksiazka=ksiazka
                )
                send_mail('Dostępność', f'Książka {ksiazka.tytul} jest dostępna!', settings.DEFAULT_FROM_EMAIL, [zapis.uzytkownik.email], fail_silently=True)
            oczekujacy.delete()
        egzemplarz.save()
        LogAkcji.objects.create(egzemplarz=egzemplarz, uzytkownik=request.user, akcja='Z' if nowy_status == 'D' else 'I')
    return redirect('panel_bibliotekarza')

@staff_member_required
def wydaj_ksiazke(request, egz_id):
    egzemplarz = get_object_or_404(Egzemplarz, id=egz_id)
    # widok tylko czytelnicy
    # czytelnicy = User.objects.filter(is_staff=False)

    # widok wszyscy zarejestrowani w bazie
    # POPRAWKA: Pobiera wszystkich użytkowników, nie tylko tych bez is_staff
    czytelnicy = User.objects.all().order_by('last_name')

    if request.method == "POST":
        user_id = request.POST.get('czytelnik')
        dni = int(request.POST.get('dni', 30))
        with transaction.atomic():
            czytelnik = User.objects.get(id=user_id)
            egzemplarz.status = 'W'
            egzemplarz.aktualny_czytelnik = czytelnik
            egzemplarz.termin_zwrotu = timezone.now().date() + timedelta(days=dni)
            egzemplarz.save()
            Rezerwacja.objects.filter(egzemplarz=egzemplarz).delete()
            LogAkcji.objects.create(egzemplarz=egzemplarz, uzytkownik=czytelnik, akcja='W')
        messages.success(request, f"Wydano: {czytelnik.username}")
        return redirect('panel_bibliotekarza')
    return render(request, 'bibliotech/wydaj_ksiazke.html', {'egzemplarz': egzemplarz, 'czytelnicy': czytelnicy})

# ==========================================================
# 5. KLASY (CREATE / UPDATE)
# ==========================================================

class KsiazkaCreate(BibliotekarzRequiredMixin, CreateView):
    model = Ksiazka
    form_class = KsiazkaZAutoEgzemplarzamiForm
    template_name = 'bibliotech/ksiazka_form.html'
    success_url = reverse_lazy('panel_bibliotekarza')

    def form_valid(self, form):
        response = super().form_valid(form)
        ile = form.cleaned_data.get('liczba_egzemplarzy', 1)
        manualny = form.cleaned_data.get('kod_manualny')
        auto = form.cleaned_data.get('auto_generuj')
        with transaction.atomic():
            for i in range(ile):
                if not auto and manualny and ile == 1:
                    kod = manualny
                elif not auto and manualny and ile > 1:
                    kod = f"{manualny}-{i+1}"
                else:
                    kod = f"LIB-{self.object.id}-{str(uuid.uuid4())[:5]}"
                Egzemplarz.objects.create(ksiazka=self.object, kod_kreskowy=kod, status='D')
        return response

class KsiazkaUpdate(BibliotekarzRequiredMixin, UpdateView):
    model = Ksiazka
    fields = ['tytul', 'autor', 'gatunek', 'opis', 'rok_wydania', 'okladka']
    template_name = 'bibliotech/ksiazka_form.html'
    success_url = reverse_lazy('panel_bibliotekarza')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['egzemplarze'] = Egzemplarz.objects.filter(ksiazka=self.object)
        return context

class EgzemplarzCreate(BibliotekarzRequiredMixin, CreateView):
    model = Egzemplarz
    fields = ['ksiazka', 'kod_kreskowy', 'status']
    template_name = 'bibliotech/egzemplarz_form.html'
    success_url = reverse_lazy('panel_bibliotekarza')
    def get_initial(self):
        initial = super().get_initial()
        ks_id = self.request.GET.get('ksiazka_id')
        if ks_id: initial['ksiazka'] = get_object_or_404(Ksiazka, id=ks_id)
        return initial

# ==========================================================
# 6. INNE
# ==========================================================

@staff_member_required
def historia_egzemplarza(request, egz_id):
    egzemplarz = get_object_or_404(Egzemplarz, id=egz_id)
    wpisy = LogAkcji.objects.filter(egzemplarz=egzemplarz).select_related('uzytkownik')
    return render(request, 'bibliotech/historia_egzemplarza.html', {'egzemplarz': egzemplarz, 'wpisy': wpisy})

@staff_member_required
def lista_czytelnikow(request):
    query = request.GET.get('q', '')
    czytelnicy = User.objects.filter(is_staff=False).order_by('last_name')
    if query: czytelnicy = czytelnicy.filter(Q(last_name__icontains=query) | Q(username__icontains=query))
    return render(request, 'bibliotech/lista_czytelnikow.html', {'czytelnicy': czytelnicy, 'query': query})

@staff_member_required
def detale_czytelnika(request, user_id):
    czytelnik = get_object_or_404(User, id=user_id)
    return render(request, 'bibliotech/detale_czytelnika.html', {
        'czytelnik': czytelnik,
        'wypozyczone': Egzemplarz.objects.filter(aktualny_czytelnik=czytelnik),
        'rezerwacje': Rezerwacja.objects.filter(uzytkownik=czytelnik),
        'historia': LogAkcji.objects.filter(uzytkownik=czytelnik).select_related('egzemplarz__ksiazka'),
        'dzisiaj': timezone.now().date()
    })

# ==========================================================
# 🛡️ ŻELAZNE ALIASY (Zapobiegają błędom AttributeError)
# ==========================================================
moje_konto = profil_uzytkownika
zapisz_na_powiadomienie = powiadom_o_dostepnosci
przyjmij_zwrot = zmien_status_egzemplarza

@staff_member_required
def prosba_o_zwrot(request, egz_id):
    egzemplarz = get_object_or_404(Egzemplarz, id=egz_id)
    czytelnik = egzemplarz.aktualny_czytelnik
    
    if czytelnik:
        # 1. Tworzymy powiadomienie systemowe (okienko u czytelnika)
        Powiadomienie.objects.create(
            uzytkownik=czytelnik,
            tytul="PILNY ZWROT: " + egzemplarz.ksiazka.tytul,
            tresc=f"Biblioteka prosi o pilny zwrot książki '{egzemplarz.ksiazka.tytul}'. "
                  f"Inni czytelnicy czekają w kolejce!",
            ksiazka=egzemplarz.ksiazka
        )
        
        # 2. Wysyłamy e-mail
        send_mail(
            'Prośba o pilny zwrot książki',
            f'Witaj {czytelnik.first_name}! Prosimy o jak najszybszy zwrot książki "{egzemplarz.ksiazka.tytul}".',
            settings.DEFAULT_FROM_EMAIL,
            [czytelnik.email],
            fail_silently=True,
        )
        
        messages.warning(request, f"Wysłano ponaglenie do użytkownika {czytelnik.username}.")
    
    return redirect('panel_bibliotekarza')