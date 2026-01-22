"""
Router odpowiedzialny za operacje CRUD związane z artystami muzycznymi.

Udostępnia następujące funkcjonalności:
- tworzenie nowego artysty (tylko administrator),
- pobieranie listy wszystkich artystów,
- pobieranie pojedynczego artysty po ID,
- aktualizację danych artysty,
- usuwanie artysty.

Router korzysta z warstwy CRUD, modeli SQLAlchemy oraz schematów Pydantic.
Operacje tworzenia i modyfikacji artystów są zabezpieczone wymogiem posiadania
uprawnień administratora.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.dependencies import admin_required
from app.models import User

router = APIRouter(prefix="/artists", tags=["Artists"])

@router.post("", response_model=schemas.ArtistOut)
def create_artist(
    artist: schemas.ArtistCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(admin_required)
):
    """
        Tworzy nowego artystę w systemie.
        Mechanizm:
        - endpoint dostępny wyłącznie dla administratorów,
        - dane wejściowe walidowane są przez schemat ArtistCreate,
        - wywoływana jest funkcja CRUD odpowiedzialna za utworzenie artysty.
        Parametry:
            artist: Dane nowego artysty (nazwa, kraj pochodzenia).
            db: Sesja bazy danych SQLAlchemy.
            _current_user: Użytkownik zweryfikowany jako administrator.
        Zwraca:
            Obiekt ArtistOut reprezentujący nowo utworzonego artystę.
    """
    return crud.create_artist(db, artist)

@router.get("")
def get_artists(db: Session = Depends(get_db)):
    """
        Zwraca listę wszystkich artystów zapisanych w bazie danych.
        Parametry:
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Lista obiektów Artist.
    """
    return db.query(models.Artist).all()

@router.get("/{artist_id}")
def get_artist(artist_id: int, db: Session = Depends(get_db)):
    """
        Pobiera pojedynczego artystę na podstawie jego identyfikatora.
        Parametry:
            artist_id: Identyfikator artysty.
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Obiekt Artist, jeśli istnieje.
        Wyjątki:
            HTTPException 404: jeśli artysta o podanym ID nie istnieje.
    """
    artist = db.query(models.Artist).get(artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist

@router.patch("/{artist_id}")
def update_artist(artist_id: int, data: schemas.ArtistCreate,
                  db: Session = Depends(get_db),
                  _current_user: User = Depends(admin_required)):
    """
        Aktualizuje dane istniejącego artysty.
        Mechanizm:
        - endpoint dostępny wyłącznie dla administratorów,
        - pobiera artystę z bazy,
        - jeśli nie istnieje - zwraca błąd 404,
        - aktualizuje tylko pola przekazane w żądaniu (exclude_unset=True),
        - zapisuje zmiany i odświeża obiekt.
        Parametry:
            artist_id: Identyfikator artysty do aktualizacji.
            data: Dane aktualizacyjne artysty.
            db: Sesja bazy danych SQLAlchemy.
            _current_user: Użytkownik zweryfikowany jako administrator.
        Zwraca:
            Zaktualizowany obiekt Artist.
        Wyjątki:
            HTTPException 404: jeśli artysta nie istnieje.
    """
    artist = db.query(models.Artist).get(artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(artist, key, value)

    db.commit()
    db.refresh(artist)
    return artist

@router.delete("/{artist_id}")
def delete_artist(artist_id: int, db: Session = Depends(get_db),
                  _current_user: User = Depends(admin_required)):
    """
        Usuwa artystę z bazy danych.
        Mechanizm:
        - endpoint dostępny wyłącznie dla administratorów,
        - sprawdza, czy artysta istnieje,
        - jeśli nie - zwraca błąd 404,
        - usuwa artystę i zapisuje zmiany.
        Parametry:
            artist_id: Identyfikator artysty do usunięcia.
            db: Sesja bazy danych SQLAlchemy.
            _current_user: Użytkownik zweryfikowany jako administrator.
        Zwraca:
            Słownik z komunikatem o pomyślnym usunięciu artysty.
        Wyjątki:
            HTTPException 404: jeśli artysta nie istnieje.
    """
    if not crud.delete_artist(db, artist_id):
        raise HTTPException(status_code=404, detail="Artist not found")
    return {"message": "Artist deleted successfully"}
