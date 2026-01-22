"""
Moduł zawiera operacje CRUD (Create, Read, Update, Delete) dla modelu Track.
Funkcje umożliwiają:
- tworzenie nowych utworów wraz z powiązaniem z artystami,
- pobieranie listy wszystkich utworów,
- pobieranie pojedynczego utworu po ID,
- aktualizację danych utworu (w tym zmianę artystów),
- usuwanie utworów z bazy danych.
Wszystkie operacje wykorzystują SQLAlchemy ORM i działają w kontekście
sesji przekazanej jako argument `db`.
"""
import os
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Track, Artist
from app.schemas import TrackCreate, TrackUpdate

TRACK_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "tracks")
TRACK_DIR = os.path.abspath(TRACK_DIR)

def _normalize_filename(filename: str) -> str:
    """
    Normalizuje nazwę pliku:
    - jeśli użytkownik poda "1" - zwróci "1.mp3"
    - jeśli poda "1.mp3" - zostaje bez zmian
    """
    if not filename.lower().endswith(".mp3"):
        return filename + ".mp3"
    return filename

def _validate_filename(filename: Optional[str]):
    """
    Sprawdza, czy użytkownik podał nazwę pliku MP3.
    Jeśli filename=None - brak walidacji.
    Jeśli podano - sprawdza, czy plik istnieje w static/tracks/.
    """
    if filename is None:
        return

    normalized = _normalize_filename(filename)
    full_path = os.path.join(TRACK_DIR, normalized)

    if not os.path.isfile(full_path):
        raise ValueError(f"File '{normalized}' not found in {TRACK_DIR}")

def create_track(db: Session, track: TrackCreate) -> Track:
    """
        Tworzy nowy utwór na podstawie danych wejściowych z Pydantic schema.
        Mechanizm:
        - tworzy obiekt Track z tytułem, czasem trwania i opcjonalnym albumem,
        - zapisuje go w bazie,
        - jeśli podano listę artist_ids:
            * pobiera artystów z bazy,
            * przypisuje ich do utworu (relacja many-to-many),
            * ponownie zapisuje zmiany.
        - jeśli podano nazwę pliku w `file_path`:
            * zapisuje lokalną ścieżkę do pliku,
        Parametry:
            db: Sesja SQLAlchemy.
            track: Obiekt TrackCreate zawierający dane nowego utworu.
        Zwraca:
            Obiekt Track zapisany w bazie danych.
    """
    _validate_filename(track.file_path)

    db_track = Track(
        title=track.title,
        duration=track.duration,
        album_id=track.album_id
    )

    if track.file_path:
        normalized = _normalize_filename(track.file_path)
        db_track.file_path = f"{TRACK_DIR}/{normalized}"

    db.add(db_track)
    db.commit()
    db.refresh(db_track)

    if track.artist_ids:
        artists = db.query(Artist).filter(Artist.id.in_(track.artist_ids)).all()
        db_track.artists.extend(artists)
        db.commit()

    return db_track

def get_tracks(db: Session) -> list[type[Track]]:
    """
        Zwraca listę wszystkich utworów zapisanych w bazie danych.
        Parametry:
            db: Sesja SQLAlchemy.
        Zwraca:
            Lista obiektów Track.
    """
    return db.query(Track).all()

def get_track(db: Session, track_id: int) -> Optional[Track]:
    """
        Pobiera pojedynczy utwór na podstawie jego ID.
        Parametry:
            db: Sesja SQLAlchemy.
            track_id: Identyfikator utworu.
        Zwraca:
            Obiekt Track, jeśli istnieje, w przeciwnym razie None.
    """
    return db.query(Track).get(track_id)

def update_track(db: Session, track_id: int, data: TrackUpdate) -> Optional[Track]:
    """
        Aktualizuje dane istniejącego utworu.
        Mechanizm:
        - pobiera utwór z bazy,
        - jeśli nie istnieje - zwraca None,
        - aktualizuje wszystkie pola oprócz `artist_ids`,
        - jeśli podano `artist_ids`:
            * pobiera artystów z bazy,
            * nadpisuje relację track.artists,
        - jeśli podano nazwę pliku w `file_path`:
            * aktualizuje ścieżkę do pliku,
        - zapisuje zmiany i odświeża obiekt.
        Parametry:
            db: Sesja SQLAlchemy.
            track_id: Identyfikator utworu do aktualizacji.
            data: Obiekt TrackUpdate zawierający zmieniane pola.
        Zwraca:
            Zaktualizowany obiekt Track lub None, jeśli utwór nie istnieje.
    """
    track = get_track(db, track_id)
    if not track:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if "file_path" in update_data:
        _validate_filename(update_data["file_path"])
        normalized = _normalize_filename(update_data["file_path"])
        track.file_path = f"{TRACK_DIR}/{normalized}"

    for key, value in update_data.items():
        if key not in ("artist_ids", "file_path"):
            setattr(track, key, value)

    if data.artist_ids:
        artists = db.query(Artist).filter(Artist.id.in_(data.artist_ids)).all()
        track.artists = artists

    db.commit()
    db.refresh(track)
    return track

def delete_track(db: Session, track_id: int) -> bool:
    """
        Usuwa utwór z bazy danych.
        Parametry:
            db: Sesja SQLAlchemy.
            track_id: Identyfikator utworu do usunięcia.
        Zwraca:
            True jeśli utwór został usunięty,
            False jeśli utwór o podanym ID nie istnieje.
    """
    track = db.get(Track, track_id)
    if not track:
        return False
    db.delete(track)
    db.commit()
    return True
