from django.urls import path, include
from . import views # Importujemy widoki z tego samego folderu

urlpatterns = [
    # pusty cudzysłów '' oznacza stronę główną (np. 127.0.0.1:8000)
    path('', views.lista_ksiazek, name='lista_ksiazek'),
    path('rezerwuj/<int:egzemplarz_id>/', views.rezerwuj_ksiazke, name='rezerwuj'),
    path('rejestracja/', views.Rejestracja.as_view(), name='rejestracja'),
# TA LINIA JEST KLUCZOWA:
    # Ona rejestruje nazwy 'login', 'logout', 'password_reset' itp.
    path('accounts/', include('django.contrib.auth.urls')),
    path('profil/', views.profil_uzytkownika, name='profil_uzytkownika'),
    path('anuluj/<int:rezerwacja_id>/', views.anuluj_rezerwacje, name='anuluj_rezerwacje'),
    # wyciągnie liczbę z adresu i przekaże ją do widoku jako zmienną.
    path('ksiazka/<int:pk>/', views.ksiazka_detale, name='ksiazka_detale'),

    # Panel dla bibliotekarza
    path('pracownik/panel/', views.panel_bibliotekarza, name='panel_bibliotekarza'),
    
    # Akcja zmiany statusu (Wydanie/Zwrot)
    path('pracownik/status/<int:egz_id>/<str:nowy_status>/', views.zmien_status_egzemplarza, name='zmien_status'),
    
    # Akcja zapisu na listę oczekujących
    path('ksiazka/powiadom/<int:ksiazka_id>/', views.powiadom_o_dostepnosci, name='powiadom'),

    path('pracownik/dodaj/', views.KsiazkaCreate.as_view(), name='ksiazka_dodaj'),
    
   # path('pracownik/edytuj/<int:pk>/', views.KsiazkaUpdate.as_view(), name='ksiazka_edytuj'),
    path('pracownik/ksiazka/<int:pk>/edytuj/', views.KsiazkaUpdate.as_view(), name='ksiazka_edytuj'),
    
    path('ksiazka/<int:pk>/edytuj/', views.KsiazkaUpdate.as_view(), name='edytuj_ksiazke'),
    
    path('pracownik/wydaj/<int:egz_id>/', views.wydaj_ksiazke, name='wydaj_ksiazke'),
    path('pracownik/historia/<int:egz_id>/', views.historia_egzemplarza, name='historia_egzemplarza'),

    # Baza czytelników
    path('pracownik/czytelnicy/', views.lista_czytelnikow, name='lista_czytelnikow'),
    
    # Detale konkretnego czytelnika (historia, spóźnienia, rezerwacje)
    path('pracownik/czytelnik/<int:user_id>/', views.detale_czytelnika, name='detale_czytelnika'),

    path('pracownik/egzemplarz/dodaj/', views.EgzemplarzCreate.as_view(), name='egzemplarz_dodaj'),
    
    path('moje-konto/', views.moje_konto, name='moje_konto'),
    path('profil/edytuj/', views.edytuj_profil, name='edytuj_profil'),

    # Zapis na powiadomienie
    path('powiadom-mnie/<int:ksiazka_id>/', views.zapisz_na_powiadomienie, name='powiadom_mnie'),
    
    # Oznaczanie powiadomienia jako przeczytane (żeby okienko zniknęło)
    path('powiadomienie/przeczytane/<int:p_id>/', views.oznacz_przeczytane, name='oznacz_przeczytane'),

    path('pracownik/prosba-zwrot/<int:egz_id>/', views.prosba_o_zwrot, name='prosba_o_zwrot'),

]