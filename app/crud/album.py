"""
Moduł zawiera operacje CRUD (Create, Read, Update, Delete) dla modelu Album.
Funkcje w tym module umożliwiają:
- tworzenie nowych albumów,
- pobieranie listy albumów,
- pobieranie pojedynczego albumu po ID,
- aktualizację danych albumu,
- usuwanie albumów z bazy danych.
Wszystkie operacje wykorzystują SQLAlchemy ORM i działają w kontekście
sesji przekazanej jako argument `db`.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Album
from app.schemas import AlbumCreate, AlbumUpdate

def create_album(db: Session, album: AlbumCreate) -> Album:
    """
        Tworzy nowy album na podstawie danych wejściowych z Pydantic schema.
        Parametry:
            db: Sesja SQLAlchemy.
            album: Obiekt AlbumCreate zawierający dane nowego albumu.
        Zwraca:
            Obiekt Album zapisany w bazie danych.
    """
    db_album = Album(**album.model_dump())
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album

def get_albums(db: Session) -> list[type[Album]]:
    """
        Zwraca listę wszystkich albumów zapisanych w bazie danych.
        Parametry:
            db: Sesja SQLAlchemy.
        Zwraca:
            Lista obiektów Album.
    """
    return db.query(Album).all()

def get_album(db: Session, album_id: int) -> Optional[Album]:
    """
        Pobiera pojedynczy album na podstawie jego ID.
        Parametry:
            db: Sesja SQLAlchemy.
            album_id: Identyfikator albumu.
        Zwraca:
            Obiekt Album, jeśli istnieje, w przeciwnym razie None.
    """
    return db.query(Album).get(album_id)

def update_album(db: Session, album_id: int, data: AlbumUpdate) -> Optional[Album]:
    """
        Aktualizuje dane istniejącego albumu.
        Mechanizm:
        - pobiera album z bazy,
        - jeśli nie istnieje - zwraca None,
        - aktualizuje tylko pola przekazane w `data` (exclude_unset=True),
        - zapisuje zmiany i odświeża obiekt.
        Parametry:
            db: Sesja SQLAlchemy.
            album_id: Identyfikator albumu do aktualizacji.
            data: Obiekt AlbumUpdate zawierający zmieniane pola.
        Zwraca:
            Zaktualizowany obiekt Album lub None, jeśli album nie istnieje.
    """
    album = get_album(db, album_id)
    if not album:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(album, key, value)

    db.commit()
    db.refresh(album)
    return album

def delete_album(db: Session, album_id: int) -> bool:
    """
        Usuwa album z bazy danych.
        Parametry:
            db: Sesja SQLAlchemy.
            album_id: Identyfikator albumu do usunięcia.
        Zwraca:
            True jeśli album został usunięty,
            False jeśli album o podanym ID nie istnieje.
    """
    album = db.get(Album, album_id)
    if not album:
        return False
    db.delete(album)
    db.commit()
    return True
