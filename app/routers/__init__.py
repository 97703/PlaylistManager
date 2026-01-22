"""
Pakiet `routers` zawiera wszystkie moduły odpowiedzialne za obsługę
tras (endpointów) API w aplikacji. Każdy router odpowiada za jedną
logicznie wydzieloną część systemu, co zapewnia modularność,
czytelność i łatwiejsze utrzymanie kodu.

Dostępne routery:
- auth: operacje logowania, rejestracji i sesji użytkownika
- users: operacje CRUD na użytkownikach
- artists: operacje CRUD na artystach
- albums: operacje CRUD na albumach
- tracks: operacje CRUD na utworach
- playlists: operacje CRUD i zarządzanie playlistami
- websocket: obsługa połączeń WebSocket

Routery mogą być importowane zbiorczo w pliku `main.py`:
    from app.routers import auth, users, artists, albums, tracks, playlists, websocket
"""
from . import auth
from . import users
from . import artists
from . import albums
from . import tracks
from . import playlists
from . import websocket
