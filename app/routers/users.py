"""
Router odpowiedzialny za operacje CRUD związane z użytkownikami systemu.

Udostępnia następujące funkcjonalności:
- aktualizację danych użytkownika,
- pobieranie listy wszystkich użytkowników,
- pobieranie pojedynczego użytkownika po ID,
- usuwanie użytkownika.

Router korzysta z warstwy CRUD, modeli SQLAlchemy oraz schematów Pydantic.
Operacje nie wymagają uprawnień administratora, jednak mogą być zabezpieczone
na poziomie logiki aplikacji (np. w warstwie CRUD lub middleware).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/users", tags=["Users"])

@router.patch("/{user_id}")
def update_user(user_id: int, data: schemas.UserUpdate, db: Session = Depends(get_db)):
    """
        Aktualizuje dane istniejącego użytkownika.
        Mechanizm:
        - wywołuje funkcję CRUD odpowiedzialną za aktualizację użytkownika,
        - jeśli użytkownik nie istnieje - zwraca błąd 404,
        - aktualizuje tylko pola przekazane w żądaniu (exclude_unset=True).
        Parametry:
            user_id: Identyfikator użytkownika do aktualizacji.
            data: Dane aktualizacyjne użytkownika.
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Zaktualizowany obiekt użytkownika.
        Wyjątki:
            HTTPException 404: jeśli użytkownik nie istnieje.
    """
    user = crud.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("")
def get_users(db: Session = Depends(get_db)):
    """
        Zwraca listę wszystkich użytkowników zapisanych w bazie danych.
        Parametry:
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Lista obiektów User.
    """
    return crud.get_users(db)

@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
        Pobiera pojedynczego użytkownika na podstawie jego identyfikatora.
        Parametry:
            user_id: Identyfikator użytkownika.
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Obiekt User, jeśli istnieje.
        Wyjątki:
            HTTPException 404: jeśli użytkownik o podanym ID nie istnieje.
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
        Usuwa użytkownika z bazy danych.
        Mechanizm:
        - wywołuje funkcję CRUD usuwającą użytkownika,
        - jeśli użytkownik nie istnieje - błąd 404.
        Parametry:
            user_id: Identyfikator użytkownika do usunięcia.
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Słownik z komunikatem o pomyślnym usunięciu użytkownika.
        Wyjątki:
            HTTPException 404: jeśli użytkownik nie istnieje.
    """
    if not crud.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
