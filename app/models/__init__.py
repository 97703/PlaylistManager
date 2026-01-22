"""
Pakiet `models` zawiera definicje wszystkich modeli ORM wykorzystywanych
w aplikacji. Modele te reprezentują struktury tabel w bazie danych oraz
definiują relacje pomiędzy encjami, takie jak relacje one‑to‑many oraz
many‑to‑many.

Struktura pakietu:
- user.py          — model użytkownika oraz enum UserRole
- artist.py        — model artysty
- album.py         — model albumu muzycznego
- track.py         — model utworu muzycznego
- playlist.py      — model playlisty
- associations.py  — tabele asocjacyjne dla relacji many‑to‑many

Eksportowane elementy:
Plik `__init__.py` udostępnia wszystkie modele oraz tabele asocjacyjne
w jednym miejscu, umożliwiając wygodny import:
    from app.models import User, Track, Playlist

Dzięki temu warstwa modeli jest uporządkowana, modularna i łatwa w użyciu
w pozostałych częściach aplikacji.
"""
from .user import User, UserRole
from .artist import Artist
from .album import Album
from .track import Track
from .playlist import Playlist
from .associations import playlist_track, track_artist
