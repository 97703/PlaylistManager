"""
Router odpowiedzialny za operacje CRUD związane z albumami muzycznymi.

Udostępnia następujące funkcjonalności:
- tworzenie nowego albumu (tylko administrator),
- pobieranie listy wszystkich albumów,
- pobieranie pojedynczego albumu po ID,
- aktualizację danych albumu,
- usuwanie albumu.

Router korzysta z warstwy CRUD, modeli SQLAlchemy oraz schematów Pydantic.
Operacje tworzenia i modyfikacji albumów są zabezpieczone wymogiem posiadania
uprawnień administratora.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.dependencies import admin_required
from app.models import User

router = APIRouter(prefix="/albums", tags=["Albums"])

@router.post("")
def create_album(
    album: schemas.AlbumCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(admin_required)
):
    """
        Tworzy nowy album muzyczny.
        Mechanizm:
        - endpoint dostępny wyłącznie dla administratorów,
        - dane wejściowe są walidowane przez schemat AlbumCreate,
        - wywoływana jest funkcja CRUD odpowiedzialna za utworzenie albumu.
        Parametry:
            album: Dane nowego albumu (tytuł, data wydania, ID artysty).
            db: Sesja bazy danych SQLAlchemy.
            _current_user: Użytkownik zweryfikowany jako administrator.
        Zwraca:
            Obiekt Album utworzony w bazie danych.
    """
    return crud.create_album(db, album)

@router.get("")
def get_albums(db: Session = Depends(get_db)):
    """
        Zwraca listę wszystkich albumów zapisanych w bazie danych.
        Parametry:
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Lista obiektów Album.
    """
    return db.query(models.Album).all()

@router.get("/{album_id}")
def get_album(album_id: int, db: Session = Depends(get_db)):
    """
        Pobiera pojedynczy album na podstawie jego identyfikatora.
        Parametry:
            album_id: Identyfikator albumu.
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Obiekt Album, jeśli istnieje.
        Wyjątki:
            HTTPException 404: jeśli album o podanym ID nie istnieje.
    """
    album = db.query(models.Album).get(album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album

@router.patch("/{album_id}")
def update_album(album_id: int, data: schemas.AlbumCreate,
                 db: Session = Depends(get_db),
                 _current_user: User = Depends(admin_required)):
    """
        Aktualizuje dane istniejącego albumu.
        Mechanizm:
        - endpoint dostępny wyłącznie dla administratorów,
        - pobiera album z bazy,
        - jeśli nie istnieje - zwraca błąd 404,
        - aktualizuje tylko pola przekazane w żądaniu (exclude_unset=True),
        - zapisuje zmiany i odświeża obiekt.
        Parametry:
            album_id: Identyfikator albumu do aktualizacji.
            data: Dane aktualizacyjne albumu.
            db: Sesja bazy danych SQLAlchemy.
            _current_user: Użytkownik zweryfikowany jako administrator.
        Zwraca:
            Zaktualizowany obiekt Album.
        Wyjątki:
            HTTPException 404: jeśli album nie istnieje.
    """
    album = db.query(models.Album).get(album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(album, key, value)

    db.commit()
    db.refresh(album)
    return album

@router.delete("/{album_id}")
def delete_album(album_id: int, db: Session = Depends(get_db),
                 _current_user: User = Depends(admin_required)):
    """
        Usuwa album z bazy danych.
        Mechanizm:
        - endpoint dostępny wyłącznie dla administratorów,
        - pobiera album z bazy,
        - jeśli nie istnieje - zwraca błąd 404,
        - usuwa album i zapisuje zmiany.
        Parametry:
            album_id: Identyfikator albumu do usunięcia.
            db: Sesja bazy danych SQLAlchemy.
            _current_user: Użytkownik zweryfikowany jako administrator.
        Zwraca:
            Słownik z komunikatem o pomyślnym usunięciu albumu.
        Wyjątki:
            HTTPException 404: jeśli album nie istnieje.
    """
    album = db.query(models.Album).get(album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    db.delete(album)
    db.commit()
    return {"message": "Album deleted successfully"}