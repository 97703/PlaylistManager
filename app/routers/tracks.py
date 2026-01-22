"""
Router odpowiedzialny za operacje CRUD związane z utworami muzycznymi (tracks).

Udostępnia następujące funkcjonalności:
- tworzenie nowego utworu (tylko administrator),
- pobieranie listy wszystkich utworów,
- pobieranie pojedynczego utworu po ID,
- aktualizację danych utworu,
- usuwanie utworu.

Router korzysta z warstwy CRUD, modeli SQLAlchemy oraz schematów Pydantic.
Tworzenie i modyfikacja utworów wymaga uprawnień administratora.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from app.schemas import TrackOut
from app.dependencies import admin_required
from app.models import User

router = APIRouter(prefix="/tracks", tags=["Tracks"])

@router.post("", response_model=TrackOut)
def create_track(
    track: schemas.TrackCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(admin_required)
):
    """
        Tworzy nowy utwór muzyczny.
        Mechanizm:
        - endpoint dostępny wyłącznie dla administratorów,
        - dane wejściowe walidowane są przez schemat TrackCreate,
        - wywoływana jest funkcja CRUD odpowiedzialna za utworzenie utworu,
        - zwracany jest obiekt TrackOut zawierający listę ID artystów.
        Parametry:
            track: Dane nowego utworu (tytuł, czas trwania, album, artyści).
            db: Sesja bazy danych SQLAlchemy.
            _current_user: Użytkownik zweryfikowany jako administrator.
        Zwraca:
            Obiekt TrackOut reprezentujący nowo utworzony utwór.
        Wyjątki:
            HTTPException 400: jeśli plik o podanej nazwie nie istnieje w static/tracks.
    """
    try:
        db_track = crud.create_track(db, track)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return TrackOut(
        id=db_track.id,
        title=db_track.title,
        duration=db_track.duration,
        album_id=db_track.album_id,
        artist_ids=[a.id for a in db_track.artists],
        file_path=db_track.file_path
    )

@router.get("")
def get_tracks(db: Session = Depends(get_db)):
    """
        Zwraca listę wszystkich utworów zapisanych w bazie danych.
        Parametry:
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Lista obiektów Track.
    """
    return crud.get_tracks(db)

@router.get("/{track_id}")
def get_track(track_id: int, db: Session = Depends(get_db)):
    """
        Pobiera pojedynczy utwór na podstawie jego identyfikatora.
        Parametry:
            track_id: Identyfikator utworu.
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Obiekt Track, jeśli istnieje.
        Wyjątki:
            HTTPException 404: jeśli utwór o podanym ID nie istnieje.
    """
    track = crud.get_track(db, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track

@router.patch("/{track_id}")
def update_track(track_id: int, data: schemas.TrackUpdate,
                 db: Session = Depends(get_db),
                 _current_user: User = Depends(admin_required)):
    """
        Aktualizuje dane istniejącego utworu.
        Mechanizm:
        - endpoint dostępny wyłącznie dla administratorów,
        - pobiera utwór z bazy,
        - jeśli nie istnieje - błąd 404,
        - zapisuje ścieżkę do pliku,
        - jeśli plik nie istnieje - błąd 400,
        - aktualizuje tylko pola przekazane w żądaniu (exclude_unset=True),
        - zapisuje zmiany i odświeża obiekt.
        Parametry:
            track_id: Identyfikator utworu do aktualizacji.
            data: Dane aktualizacyjne utworu.
            db: Sesja bazy danych SQLAlchemy.
            _current_user: Użytkownik zweryfikowany jako administrator.
        Zwraca:
            Zaktualizowany obiekt Track.
        Wyjątki:
            HTTPException 400: jeśli plik o podanej nazwie nie istnieje w static/tracks.
            HTTPException 404: jeśli utwór nie istnieje.
    """
    try:
        updated = crud.update_track(db, track_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not updated:
        raise HTTPException(status_code=404, detail="Track not found")

    return TrackOut(
        id=updated.id,
        title=updated.title,
        duration=updated.duration,
        album_id=updated.album_id,
        artist_ids=[a.id for a in updated.artists],
        file_path=updated.file_path
    )

@router.delete("/{track_id}")
def delete_track(track_id: int, db: Session = Depends(get_db),
                 _current_user: User = Depends(admin_required)):
    """
        Usuwa utwór z bazy danych.
        Mechanizm:
        - endpoint dostępny wyłącznie dla administratorów,
        - wywołuje funkcję CRUD usuwającą utwór,
        - jeśli utwór nie istnieje - błąd 404.
        Parametry:
            track_id: Identyfikator utworu do usunięcia.
            db: Sesja bazy danych SQLAlchemy.
            _current_user: Użytkownik zweryfikowany jako administrator.
        Zwraca:
            Słownik z komunikatem o pomyślnym usunięciu utworu.
        Wyjątki:
            HTTPException 404: jeśli utwór nie istnieje.
    """
    if not crud.delete_track(db, track_id):
        raise HTTPException(status_code=404, detail="Track not found")
    return {"message": "Track deleted successfully"}
