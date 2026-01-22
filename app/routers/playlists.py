"""
Router odpowiedzialny za operacje CRUD oraz zarządzanie zawartością playlist.

Udostępnia następujące funkcjonalności:
- tworzenie playlist (z limitem dla zwykłych użytkowników),
- dodawanie i usuwanie utworów z playlist,
- pobieranie listy utworów z playlisty,
- pobieranie wszystkich playlist lub pojedynczej playlisty,
- aktualizację danych playlisty,
- usuwanie playlist.

Dostęp do niektórych operacji jest ograniczony:
- zwykły użytkownik może posiadać maksymalnie 10 playlist,
- modyfikować playlistę może tylko jej właściciel lub administrator.

Router korzysta z warstwy CRUD, modeli SQLAlchemy oraz schematów Pydantic.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/playlists", tags=["Playlists"])

@router.post("", response_model=schemas.PlaylistOut)
def create_playlist(
    playlist: schemas.PlaylistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
        Tworzy nową playlistę.
        Mechanizm:
        - jeśli użytkownik nie jest administratorem, sprawdzany jest limit 10 playlist,
        - dane wejściowe walidowane są przez schemat PlaylistCreate,
        - wywoływana jest funkcja CRUD odpowiedzialna za utworzenie playlisty,
        - zwracany jest obiekt PlaylistOut z listą ID utworów.
        Parametry:
            playlist: Dane nowej playlisty (nazwa, właściciel).
            db: Sesja bazy danych SQLAlchemy.
            current_user: Aktualnie zalogowany użytkownik.
        Zwraca:
            Obiekt PlaylistOut.
        Wyjątki:
            HTTPException 400: jeśli ownerid nie istnieje w bazie danych.
            HTTPException 403: jeśli użytkownik przekroczył limit playlist.
    """
    if current_user.role != "admin":
        count = db.query(models.Playlist).filter_by(owner_id=current_user.id).count()
        if count >= 10:
            raise HTTPException(status_code=403, detail="You cannot have more than 10 playlists")
        playlist.owner_id = current_user.id

    else:
        if playlist.owner_id is None:
            playlist.owner_id = current_user.id
        else:
            owner = db.query(models.User).filter_by(id=playlist.owner_id).first()
            if not owner:
                raise HTTPException(status_code=400, detail="Owner with given ID does not exist")

    db_playlist = crud.create_playlist(db, playlist)

    return schemas.PlaylistOut(
        id=db_playlist.id,
        name=db_playlist.name,
        owner_id=db_playlist.owner_id,
        track_ids=[t.id for t in db_playlist.tracks]
    )

@router.post("/{playlist_id}/tracks/{track_id}")
def add_track(
    playlist_id: int,
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
        Dodaje utwór do playlisty.
        Mechanizm:
        - pobiera playlistę i utwór z bazy,
        - jeśli któryś nie istnieje - błąd 404,
        - jeśli użytkownik nie jest administratorem ani właścicielem playlisty - błąd 403,
        - wywołuje funkcję CRUD dodającą utwór do playlisty.
        Parametry:
            playlist_id: Identyfikator playlisty.
            track_id: Identyfikator utworu.
            db: Sesja bazy danych SQLAlchemy.
            current_user: Aktualnie zalogowany użytkownik.
        Zwraca:
            Słownik {"status": "ok"} po pomyślnym dodaniu.
    """
    playlist = crud.get_playlist(db, playlist_id)
    track = crud.get_track(db, track_id)

    if not playlist or not track:
        raise HTTPException(status_code=404, detail="Playlist or track not found")

    if current_user.role != "admin" and playlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only modify your own playlists")

    crud.add_track_to_playlist(db, playlist_id, track_id)
    return {"status": "ok"}

@router.delete("/{playlist_id}/tracks/{track_id}")
def remove_track_from_playlist(
    playlist_id: int,
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Usuwa utwór z playlisty.
    Mechanizm:
    - pobiera playlistę,
    - jeśli nie istnieje → błąd 404,
    - sprawdza, czy użytkownik jest właścicielem lub administratorem,
    - usuwa powiązanie utworu z playlistą.
    Parametry:
        playlist_id: Identyfikator playlisty.
        track_id: Identyfikator utworu.
        db: Sesja bazy danych SQLAlchemy.
        current_user: Aktualnie zalogowany użytkownik.
    Zwraca:
        Słownik z komunikatem o pomyślnym usunięciu utworu.
    Wyjątki:
        HTTPException 403: jeśli użytkownik nie ma uprawnień.
    """
    playlist = crud.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    if playlist.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not allowed to modify this playlist")

    if not crud.remove_track_from_playlist(db, playlist_id, track_id):
        raise HTTPException(status_code=404, detail="Track not found in playlist")

    return {"message": "Track removed from playlist successfully"}

@router.get("/{playlist_id}/tracks")
def get_tracks_from_playlist(playlist_id: int, db: Session = Depends(get_db)):
    """
        Pobiera listę utworów znajdujących się w danej playliście.
        Parametry:
            playlist_id: Identyfikator playlisty.
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Lista obiektów Track.
        Wyjątki:
            HTTPException 404: jeśli playlista nie istnieje.
    """
    tracks = crud.get_playlist_tracks(db, playlist_id)
    if tracks is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return tracks

@router.get("")
def get_playlists(db: Session = Depends(get_db)):
    """
        Zwraca listę wszystkich playlist w systemie.
        Parametry:
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Lista obiektów Playlist.
    """
    return crud.get_playlists(db)

@router.get("/{playlist_id}")
def get_playlist(playlist_id: int, db: Session = Depends(get_db)):
    """
        Pobiera pojedynczą playlistę na podstawie jej identyfikatora.
        Parametry:
            playlist_id: Identyfikator playlisty.
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Obiekt Playlist.
        Wyjątki:
            HTTPException 404: jeśli playlista nie istnieje.
    """
    playlist = crud.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlist

@router.patch("/{playlist_id}", response_model=schemas.PlaylistOut)
def update_playlist(
    playlist_id: int,
    data: schemas.PlaylistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aktualizuje dane istniejącej playlisty.
    Mechanizm:
    - pobiera playlistę z bazy,
    - jeśli nie istnieje → błąd 404,
    - sprawdza, czy użytkownik jest właścicielem lub administratorem,
    - aktualizuje tylko pola przekazane w żądaniu (exclude_unset=True),
    - zapisuje zmiany i odświeża obiekt.
    Parametry:
        playlist_id: Identyfikator playlisty.
        data: Dane aktualizacyjne playlisty.
        db: Sesja bazy danych SQLAlchemy.
        current_user: Aktualnie zalogowany użytkownik.
    Zwraca:
        Zaktualizowany obiekt PlaylistOut.
    Wyjątki:
        HTTPException 403: jeśli użytkownik nie ma uprawnień.
        HTTPException 404: jeśli nie znaleziono playlisty.
    """
    playlist = crud.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    if playlist.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not allowed to modify this playlist")

    update_data = data.model_dump(exclude_unset=True)

    if current_user.role != "admin" and "owner_id" in update_data:
        if update_data["owner_id"] != playlist.owner_id:
            raise HTTPException(status_code=403, detail="You cannot change playlist owner")

    for key, value in update_data.items():
        setattr(playlist, key, value)

    db.commit()
    db.refresh(playlist)

    return schemas.PlaylistOut(
        id=playlist.id,
        name=playlist.name,
        owner_id=playlist.owner_id,
        track_ids=[t.id for t in playlist.tracks]
    )

@router.delete("/{playlist_id}")
def delete_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Usuwa playlistę z bazy danych.
    Mechanizm:
    - pobiera playlistę,
    - jeśli nie istnieje → błąd 404,
    - sprawdza, czy użytkownik jest właścicielem lub administratorem,
    - usuwa playlistę.
    Parametry:
        playlist_id: Identyfikator playlisty.
        db: Sesja bazy danych SQLAlchemy.
        current_user: Aktualnie zalogowany użytkownik.
    Zwraca:
        Słownik z komunikatem o pomyślnym usunięciu playlisty.
    Wyjątki:
        HTTPException 403: jeśli użytkownik nie ma uprawnień.
    """
    playlist = crud.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    if playlist.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not allowed to delete this playlist")

    crud.delete_playlist(db, playlist_id)
    return {"message": "Playlist deleted successfully"}