# FastAPI Playlist Manager z WebSocket Player

**Autor:** Paweł Pieczykolan s97703, Politechnika Lubelska

Backendowa aplikacja do zarządzania biblioteką muzyczną, playlistami, albumami, artystami oraz odtwarzaczem audio działającym w czasie rzeczywistym poprzez WebSocket.
Projekt został zbudowany w oparciu o **FastAPI**, **SQLAlchemy**, **Pydantic**, **WebSocket**, z zestawem testów jednostkowych i integracyjnych.

**Wymagania:** Python 3.13.5, pakiety z pliku **requirements.txt**

---

## Funkcjonalności

### Odtwarzacz WebSocket

- Kolejka utworów  

- Odtwarzanie, pauza, skip  

- Pętla utworu i playlisty  

- Obsługa playlist i albumów  

- Tick czasu w czasie rzeczywistym  

- Automatyczne przełączanie utworów  

- Pełne testy integracyjne symulujące działanie klienta

### Zarządzanie muzyką

CRUD dla:

- Utworów

- Albumów

- Artystów

- Playlist

- Użytkowników

Relacje:

- Album → utwory  

- Artysta → utwory  

- Playlista → utwory  

- Użytkownik → playlisty  

### Autoryzacja i role

- Sesja (5 minut po zalogowaniu lub wykonaniu akcji)

- Logowanie i rejestracja  

- Role:

&nbsp; - `admin` — pełny dostęp  

&nbsp; - `user` — ograniczenia (np. max 10 playlist)  

- Kontrola dostępu w endpointach (owner/admin)

---

## Testy

Projekt posiada zestaw testów obejmujących:

- Modele: `User`, `Track`, `Album`, `Artist`, `Playlist`  

- Logikę odtwarzacza (tick, kolejka, pętle)  

- WebSocket `/ws`  

- CRUD dla wszystkich zasobów  

- Autoryzację i sesje  

- Limity użytkownika (max 10 playlist)  

- Relacje (track w playliście, albumie itd.)  

---

## Uruchamianie

### Windows

```bash
cd PlaylistManager

python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```
Przygotowany został skrypt <code>seed.py</code>, który pozwala na utworzenie testowych rekordów w bazie danych.
Aby go uruchomić wystarczy wpisać **python seed.py**.

## Po uruchomieniu:  

Dla testowania Endpointów

**Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

Dla testowania Playera

Aby połączyć się z WebSocketem można skorzystać z darmowej wtyczki do przeglądarki [Pie Host WebSocket Tester](https://piehost.com/websocket-tester).

**WebSocket Player:** ws://localhost:8000/ws

**Wybrane komendy WebSocket Player:**

- Dodanie utworu do kolejki, o ile utwór o takim id istnieje w bazie danych.
```json
{"command": "queue_add", "payload": {"track": 1}}
```
- Zapauzowanie utworu, o ile utwór jest aktualnie odtwarzany.
```json
{"command": "pause"}
```
- Wznowienie utworu, o ile utwór jest zapauzowany.
```json
{"command": "play"}
```
- Pominięcie utworu, o ile jakikolwiek utwór jest odtwarzany.
```json
{"command": "skip"}
```
- Zapętlenie utworu, o ile jakikolwiek utwór jest odtwarzany.
```json
{"command": "loop_track", "payload": true}
```






