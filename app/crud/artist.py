"""
Moduł zawiera operacje CRUD (Create, Read, Update, Delete) dla modelu Artist.
Funkcje umożliwiają:
- tworzenie nowych artystów,
- pobieranie listy wszystkich artystów,
- pobieranie pojedynczego artysty po ID,
- aktualizację danych artysty,
- usuwanie artystów z bazy danych.
Wszystkie operacje wykorzystują SQLAlchemy ORM i działają w kontekście
sesji przekazanej jako argument `db`.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Artist
from app.schemas import ArtistCreate, ArtistUpdate

def create_artist(db: Session, artist: ArtistCreate) -> Artist:
    """
        Tworzy nowego artystę na podstawie danych wejściowych z Pydantic schema.
        Parametry:
            db: Sesja SQLAlchemy.
            artist: Obiekt ArtistCreate zawierający dane nowego artysty.
        Zwraca:
            Obiekt Artist zapisany w bazie danych.
    """
    db_artist = Artist(**artist.model_dump())
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist

def get_artists(db: Session) -> list[type[Artist]]:
    """
        Zwraca listę wszystkich artystów zapisanych w bazie danych.
        Parametry:
            db: Sesja SQLAlchemy.
        Zwraca:
            Lista obiektów Artist.
    """
    return db.query(Artist).all()

def get_artist(db: Session, artist_id: int) -> Optional[Artist]:
    """
        Pobiera pojedynczego artystę na podstawie jego ID.
        Parametry:
            db: Sesja SQLAlchemy.
            artist_id: Identyfikator artysty.
        Zwraca:
            Obiekt Artist, jeśli istnieje, w przeciwnym razie None.
    """
    return db.query(Artist).get(artist_id)

def update_artist(db: Session, artist_id: int, data: ArtistUpdate) -> Optional[Artist]:
    """
        Aktualizuje dane istniejącego artysty.
        Mechanizm:
        - pobiera artystę z bazy,
        - jeśli nie istnieje - zwraca None,
        - aktualizuje tylko pola przekazane w `data` (exclude_unset=True),
        - zapisuje zmiany i odświeża obiekt.
        Parametry:
            db: Sesja SQLAlchemy.
            artist_id: Identyfikator artysty do aktualizacji.
            data: Obiekt ArtistUpdate zawierający zmieniane pola.
        Zwraca:
            Zaktualizowany obiekt Artist lub None, jeśli artysta nie istnieje.
    """
    artist = get_artist(db, artist_id)
    if not artist:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(artist, key, value)

    db.commit()
    db.refresh(artist)
    return artist

def delete_artist(db: Session, artist_id: int) -> bool:
    """
        Usuwa artystę z bazy danych.
        Parametry:
            db: Sesja SQLAlchemy.
            artist_id: Identyfikator artysty do usunięcia.
        Zwraca:
            True jeśli artysta został usunięty,
            False jeśli artysta o podanym ID nie istnieje.
    """
    artist = db.get(Artist, artist_id)
    if not artist:
        return False
    db.delete(artist)
    db.commit()
    return True
