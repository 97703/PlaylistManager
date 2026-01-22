"""
Pakiet `crud` zawiera warstwę logiki dostępu do danych (CRUD) dla wszystkich
głównych modeli aplikacji: użytkowników, artystów, albumów, utworów oraz playlist.

Struktura pakietu:
- user.py      — operacje CRUD dla modelu User
- artist.py    — operacje CRUD dla modelu Artist
- album.py     — operacje CRUD dla modelu Album
- track.py     — operacje CRUD dla modelu Track
- playlist.py  — operacje CRUD dla modelu Playlist

Każdy moduł odpowiada za:
- tworzenie nowych rekordów (Create),
- pobieranie danych (Read),
- aktualizację istniejących rekordów (Update),
- usuwanie rekordów (Delete).

Plik `__init__.py` udostępnia wszystkie funkcje CRUD w jednym miejscu,
umożliwiając wygodny import:
    from app.crud import create_user, get_tracks, update_playlist

Dzięki temu warstwa logiki bazodanowej jest uporządkowana, modularna
i łatwa w utrzymaniu.
"""
from .user import (
    register_user,
    authenticate_user,
    get_users,
    get_user,
    update_user,
    delete_user,
)

from .artist import (
    create_artist,
    get_artists,
    get_artist,
    update_artist,
    delete_artist,
)

from .album import (
    create_album,
    get_albums,
    get_album,
    update_album,
    delete_album,
)

from .track import (
    create_track,
    get_tracks,
    get_track,
    update_track,
    delete_track,
)

from .playlist import (
    create_playlist,
    get_playlists,
    get_playlist,
    update_playlist,
    delete_playlist,
    add_track_to_playlist,
    get_playlist_tracks,
    remove_track_from_playlist,
)
