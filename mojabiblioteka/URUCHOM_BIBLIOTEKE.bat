@echo off
cd /d "%~dp0"
title Serwer BiblioTech - STATUS: URUCHAMIANIE
color 0B

echo ======================================================
echo           SYSTEM BIBLIOTECZNY BIBLIOTECH
echo ======================================================
echo.

:: 1. Szukanie manage.py (potwierdzenie, ze jestesmy w dobrym miejscu)
if not exist manage.py (
    color 0C
    echo [!] BLAD: Nie znaleziono pliku manage.py w tym folderze.
    echo Obecna sciezka: %cd%
    pause
    exit
)

:: 2. Szukanie venv (najpierw tutaj, potem folder wyzej)
echo [1/3] Szukanie srodowiska venv...
set VENV_PATH=none

if exist venv\Scripts\activate (
    set VENV_PATH=venv\Scripts\activate
) else if exist ..\venv\Scripts\activate (
    set VENV_PATH=..\venv\Scripts\activate
)

if "%VENV_PATH%"=="none" (
    color 0C
    echo [!] BLAD: Nie znaleziono folderu venv ani tutaj, ani w folderze wyzej!
    echo Upewnij sie, ze folder venv istnieje.
    pause
    exit
)

:: 3. Aktywacja i otwarcie przegladarki
echo [+] Znaleziono venv: %VENV_PATH%
call %VENV_PATH%
echo [2/3] Otwieranie aplikacji...
start "" http://127.0.0.1:8000/

:: 4. Start serwera
echo [3/3] Start serwera Django...
title Serwer BiblioTech - STATUS: DZIALA
python manage.py runserver

if %errorlevel% neq 0 (
    color 0C
    pause
)