"""
Moduł zawiera operacje CRUD (Create, Read, Update, Delete) dla modelu Playlist.
Funkcje umożliwiają:
- tworzenie nowych playlist,
- pobieranie listy playlist,
- pobieranie pojedynczej playlisty po ID,
- aktualizację danych playlisty,
- usuwanie playlist,
- dodawanie utworów do playlisty,
- usuwanie utworów z playlisty,
- pobieranie listy utworów należących do playlisty.
Wszystkie operacje wykorzystują SQLAlchemy ORM i działają w kontekście
sesji przekazanej jako argument `db`.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Playlist, Track
from app.schemas import PlaylistCreate, PlaylistUpdate

def create_playlist(db: Session, playlist: PlaylistCreate) -> Playlist:
    """
        Tworzy nową playlistę na podstawie danych wejściowych z Pydantic schema.
        Parametry:
            db: Sesja SQLAlchemy.
            playlist: Obiekt PlaylistCreate zawierający dane nowej playlisty.
        Zwraca:
            Obiekt Playlist zapisany w bazie danych.
    """
    db_playlist = Playlist(
        name=playlist.name,
        owner_id=playlist.owner_id
    )
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist

def get_playlists(db: Session) -> list[type[Playlist]]:
    """
        Zwraca listę wszystkich playlist zapisanych w bazie danych.
        Parametry:
            db: Sesja SQLAlchemy.
        Zwraca:
            Lista obiektów Playlist.
    """
    return db.query(Playlist).all()

def get_playlist(db: Session, playlist_id: int) -> Optional[Playlist]:
    """
    Pobiera pojedynczą playlistę na podstawie jej ID.
    Parametry:
        db: Sesja SQLAlchemy.
        playlist_id: Identyfikator playlisty.
    Zwraca:
        Obiekt Playlist, jeśli istnieje, w przeciwnym razie None.
    """
    return db.query(Playlist).get(playlist_id)

def update_playlist(db: Session, playlist_id: int, data: PlaylistUpdate) -> Optional[Playlist]:
    """
        Aktualizuje dane istniejącej playlisty.
        Mechanizm:
        - pobiera playlistę z bazy,
        - jeśli nie istnieje - zwraca None,
        - aktualizuje tylko pola przekazane w `data` (exclude_unset=True),
        - zapisuje zmiany i odświeża obiekt.
        Parametry:
            db: Sesja SQLAlchemy.
            playlist_id: Identyfikator playlisty do aktualizacji.
            data: Obiekt PlaylistUpdate zawierający zmieniane pola.
        Zwraca:
            Zaktualizowany obiekt Playlist lub None, jeśli playlisty nie znaleziono.
    """
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(playlist, key, value)

    db.commit()
    db.refresh(playlist)
    return playlist

def delete_playlist(db: Session, playlist_id: int) -> bool:
    """
        Usuwa playlistę z bazy danych.
        Parametry:
            db: Sesja SQLAlchemy.
            playlist_id: Identyfikator playlisty do usunięcia.
        Zwraca:
            True jeśli playlista została usunięta,
            False jeśli playlista o podanym ID nie istnieje.
    """
    playlist = db.get(Playlist, playlist_id)
    if not playlist:
        return False
    db.delete(playlist)
    db.commit()
    return True

def add_track_to_playlist(db: Session, playlist_id: int, track_id: int) -> bool:
    """
        Dodaje utwór do playlisty.
        Parametry:
            db: Sesja SQLAlchemy.
            playlist_id: Identyfikator playlisty.
            track_id: Identyfikator utworu.
        Zwraca:
            True jeśli operacja się powiodła,
            False jeśli playlista lub utwór nie istnieją.
    """
    playlist = get_playlist(db, playlist_id)
    track = db.query(Track).get(track_id)

    if not playlist or not track:
        return False

    playlist.tracks.append(track)
    db.commit()
    return True

def get_playlist_tracks(db: Session, playlist_id: int) -> Optional[list[Track]]:
    """
        Pobiera listę utworów należących do playlisty.
        Parametry:
            db: Sesja SQLAlchemy.
            playlist_id: Identyfikator playlisty.
        Zwraca:
            Lista obiektów Track lub None, jeśli playlista nie istnieje.
    """
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        return None
    return playlist.tracks

def remove_track_from_playlist(db: Session, playlist_id: int, track_id: int) -> bool:
    """
        Usuwa utwór z playlisty.
        Mechanizm:
        - sprawdza, czy playlista i utwór istnieją,
        - sprawdza, czy utwór faktycznie znajduje się na playliście,
        - usuwa utwór i zapisuje zmiany.
        Parametry:
            db: Sesja SQLAlchemy.
            playlist_id: Identyfikator playlisty.
            track_id: Identyfikator utworu.
        Zwraca:
            True jeśli utwór został usunięty,
            False jeśli playlista/utwór nie istnieją lub utwór nie był na playliście.
    """
    playlist = get_playlist(db, playlist_id)
    track = db.query(Track).get(track_id)

    if not playlist or not track:
        return False

    if track not in playlist.tracks:
        return False

    playlist.tracks.remove(track)
    db.commit()
    return True