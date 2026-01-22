"""
Moduł zawiera operacje CRUD (Create, Read, Update, Delete) dla modelu User.
Funkcje umożliwiają:
- rejestrację nowych użytkowników z bezpiecznym hashowaniem hasła,
- uwierzytelnianie użytkowników na podstawie loginu i hasła,
- pobieranie listy użytkowników,
- pobieranie pojedynczego użytkownika po ID,
- aktualizację danych użytkownika,
- usuwanie użytkowników z bazy danych.
Moduł wykorzystuje Passlib (bcrypt) do bezpiecznego hashowania haseł
oraz SQLAlchemy ORM do operacji na bazie danych.
"""
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy import literal_column
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserRegister, UserUpdate

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def register_user(db: Session, user: UserRegister) -> User:
    """
        Rejestruje nowego użytkownika i zapisuje go w bazie danych.
        Mechanizm:
        - hasło użytkownika jest hashowane przy użyciu bcrypt,
        - tworzony jest obiekt User,
        - użytkownik jest zapisywany w bazie i odświeżany.
        Parametry:
            db: Sesja SQLAlchemy.
            user: Obiekt UserRegister zawierający dane rejestracyjne.
        Zwraca:
            Obiekt User zapisany w bazie danych.
        """
    hashed = pwd.hash(user.password)
    db_user = User(
        login=user.login,
        email=user.email,
        password=hashed,
        first_name=user.first_name,
        last_name=user.last_name,
        birth_date=user.birth_date,
        role=user.role.value
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, login: str, password: str) -> Optional[User]:
    """
        Uwierzytelnia użytkownika na podstawie loginu i hasła.
        Mechanizm:
        - wyszukuje użytkownika po loginie,
        - jeśli nie istnieje - zwraca None,
        - weryfikuje hasło przy użyciu bcrypt,
        - jeśli hasło niepoprawne - zwraca None,
        - w przeciwnym razie zwraca obiekt User.
        Parametry:
            db: Sesja SQLAlchemy.
            login: Login użytkownika.
            password: Hasło w formie plaintext.
        Zwraca:
            Obiekt User, jeśli dane są poprawne, w przeciwnym razie None.
    """
    user = db.query(User).filter(literal_column("login") == login).first()
    if not user or not pwd.verify(password, user.password):
        return None
    return user

def get_users(db: Session) -> list[type[User]]:
    """
        Zwraca listę wszystkich użytkowników zapisanych w bazie danych.
        Parametry:
            db: Sesja SQLAlchemy.
        Zwraca:
            Lista obiektów User.
    """
    return db.query(User).all()

def get_user(db: Session, user_id: int) -> Optional[User]:
    """
        Pobiera pojedynczego użytkownika na podstawie jego ID.
        Parametry:
            db: Sesja SQLAlchemy.
            user_id: Identyfikator użytkownika.
        Zwraca:
            Obiekt User, jeśli istnieje, w przeciwnym razie None.
    """
    return db.query(User).get(user_id)

def update_user(db: Session, user_id: int, data: UserUpdate) -> Optional[User]:
    """
        Aktualizuje dane istniejącego użytkownika.
        Mechanizm:
        - pobiera użytkownika z bazy,
        - jeśli nie istnieje - zwraca None,
        - aktualizuje tylko pola przekazane w `data` (exclude_unset=True),
        - zapisuje zmiany i odświeża obiekt.
        Parametry:
            db: Sesja SQLAlchemy.
            user_id: Identyfikator użytkownika do aktualizacji.
            data: Obiekt UserUpdate zawierający zmieniane pola.
        Zwraca:
            Zaktualizowany obiekt User lub None, jeśli użytkownik nie istnieje.
    """
    user = get_user(db, user_id)
    if not user:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    """
        Usuwa użytkownika z bazy danych.
        Parametry:
            db: Sesja SQLAlchemy.
            user_id: Identyfikator użytkownika do usunięcia.
        Zwraca:
            True jeśli użytkownik został usunięty,
            False jeśli użytkownik o podanym ID nie istnieje.
    """
    user = db.get(User, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
