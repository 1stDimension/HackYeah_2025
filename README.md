# Automatyzacja Procesu Rekrutacyjnego z AI

## Opis

Ten projekt to zautomatyzowany system do tworzenia i zarządzania formularzami rekrutacyjnymi, stworzony w ramach hackathonu HackYeah 2025. System wykorzystuje interfejsy API Google Forms i Google Calendar do generowania formularzy aplikacyjnych oraz powiązanych z nimi wydarzeń w kalendarzu. Dodatkowo, projekt zawiera mechanizmy do monitorowania odpowiedzi, przetwarzania danych oraz integracji z modelami sztucznej inteligencji (Gemini).

## Funkcjonalności

-   **Automatyczne tworzenie formularzy**: Generowanie różnorodnych formularzy Google dla ofert pracy, staży, wolontariatu itp.
-   **Integracja z Kalendarzem Google**: Automatyczne tworzenie wydarzeń w kalendarzu dla każdego formularza.
-   **Monitorowanie odpowiedzi**: Skrypt cyklicznie sprawdza nowe odpowiedzi w formularzach.
-   **Przetwarzanie danych**: Zbieranie i przetwarzanie odpowiedzi z formularzy do ustrukturyzowanego formatu JSON.
-   **Generowanie danych syntetycznych**: Użycie biblioteki `Faker` do generowania realistycznych danych testowych.
-   **Przygotowanie pod AI**: Szkielet kodu do integracji z Gemini API w celu dalszej analizy danych.

## Struktura projektu

-   `create_google_form.py`: Główny skrypt do tworzenia formularzy i wydarzeń w kalendarzu.
-   `form_watcher.py`: Skrypt do monitorowania i pobierania odpowiedzi z formularzy.
-   `combine_data.py`: Skrypt do łączenia danych z wielu plików JSON w jeden plik JSONL.
-   `ai.py`: Moduł do interakcji z Gemini API.
-   `forms.jsonl`: Plik przechowujący metadane utworzonych formularzy.
-   `syntetic_data.jsonl`: Plik wynikowy z połączonymi odpowiedziami z formularzy.
-   `data/`: Katalog, w którym przechowywane są odpowiedzi z poszczególnych formularzy w formacie JSON.

## Instalacja

1.  **Klonowanie repozytorium:**
    ```bash
    git clone <adres-repozytorium>
    cd <nazwa-katalogu>
    ```

2.  **Instalacja zależności:**
    Projekt używa `uv` do zarządzania zależnościami. Zainstaluj zależności z pliku `pyproject.toml`.
    ```bash
    uv pip install .
    ```

3.  **Konfiguracja Google API:**
    -   Utwórz projekt w [Google Cloud Console](https://console.cloud.google.com/).
    -   Włącz API: **Google Forms API** i **Google Calendar API**.
    -   Skonfiguruj ekran zgody OAuth.
    -   Utwórz dane logowania typu "Identyfikator klienta OAuth" dla aplikacji komputerowej.
    -   Pobierz plik JSON z danymi logowania i zmień jego nazwę na `client_secret.apps.googleusercontent.com.json`.
    -   Umieść plik `client_secret.apps.googleusercontent.com.json` w katalogu nadrzędnym projektu.
    -   Przy pierwszym uruchomieniu skryptu, który wymaga autoryzacji, zostaniesz poproszony o zalogowanie się na swoje konto Google w przeglądarce i udzielenie zgody. Plik `token.json` zostanie automatycznie utworzony do przechowywania poświadczeń.

## Użycie

1.  **Tworzenie formularzy i wydarzeń:**
    Uruchom skrypt, aby wygenerować nowe formularze i wydarzenia w kalendarzu.
    ```bash
    python create_google_form.py
    ```

2.  **Monitorowanie odpowiedzi:**
    Uruchom skrypt, aby zacząć monitorować formularze w poszukiwaniu nowych odpowiedzi. Skrypt działa w pętli i sprawdza odpowiedzi co 10 minut.
    ```bash
    python form_watcher.py
    ```

3.  **Łączenie danych:**
    Po zebraniu odpowiedzi w katalogu `data/`, użyj tego skryptu, aby połączyć je w jeden plik `syntetic_data.jsonl`.
    ```bash
    python combine_data.py
    ```

## Konfiguracja

-   **ID Kalendarza**: Domyślnie skrypt używa kalendarza "primary". Możesz to zmienić, ustawiając zmienną środowiskową `CALENDAR_ID`.
    ```bash
    export CALENDAR_ID="twoj_identyfikator_kalendarza@group.calendar.google.com"
    ```

## Wymagania

-   Python 3.10+
-   Biblioteki: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, `Faker`, `pytz`, `jsonl` (wszystkie zależności są zdefiniowane w `pyproject.toml`).
