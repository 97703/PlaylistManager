"""
Pakiet `schemas` zawiera wszystkie schematy Pydantic wykorzystywane
do walidacji danych wejściowych i wyjściowych w aplikacji.

Schematy są podzielone na moduły odpowiadające poszczególnym encjom
systemu, co zapewnia przejrzystość, modularność i łatwiejsze utrzymanie.

Dostępne schematy:
- user:
    * UserRegister — dane rejestracyjne użytkownika
    * UserLogin — dane logowania
    * UserUpdate — aktualizacja danych użytkownika
    * UserOut — dane użytkownika zwracane w odpowiedziach API
- artist:
    * ArtistCreate — tworzenie artysty
    * ArtistUpdate — aktualizacja artysty
    * ArtistOut — dane artysty zwracane w API
- album:
    * AlbumCreate — tworzenie albumu
    * AlbumUpdate — aktualizacja albumu
- track:
    * TrackCreate — tworzenie utworu
    * TrackUpdate — aktualizacja utworu
    * TrackOut — dane utworu zwracane w API
- playlist:
    * PlaylistCreate — tworzenie playlisty
    * PlaylistUpdate — aktualizacja playlisty
    * PlaylistOut — dane playlisty zwracane w API

Schematy mogą być importowane zbiorczo:
    from app.schemas import UserOut, TrackCreate, PlaylistOut
"""
from .user import UserRegister, UserOut, UserLogin, UserUpdate
from .artist import ArtistCreate, ArtistUpdate, ArtistOut
from .album import AlbumCreate, AlbumUpdate
from .track import TrackCreate, TrackUpdate, TrackOut
from .playlist import PlaylistCreate, PlaylistUpdate, PlaylistOut