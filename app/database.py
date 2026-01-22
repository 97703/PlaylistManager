"""
Moduł odpowiedzialny za konfigurację połączenia z bazą danych oraz tworzenie
sesji SQLAlchemy wykorzystywanych w całej aplikacji.

Zawiera:
- konfigurację silnika bazy danych (`engine`),
- fabrykę sesji (`SessionLocal`),
- bazową klasę modeli (`Base`),
- zależność FastAPI `get_db()` zwracającą sesję w kontekście żądania.

Moduł korzysta z SQLite jako lokalnej bazy danych, jednak konfiguracja jest
łatwa do rozszerzenia na inne silniki (PostgreSQL, MySQL, itp.).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

"""
Ścieżka połączenia z bazą danych.
Format:
    sqlite:///./plik.db
"""
DATABASE_URL: str = "sqlite:///./playlist.db"

"""
Silnik bazy danych SQLAlchemy.
Parametr `check_same_thread=False` jest wymagany przez SQLite,
aby umożliwić korzystanie z bazy w wielu wątkach (np. w FastAPI).
"""
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
"""
Fabryka sesji SQLAlchemy.
Ustawienia:
- autocommit=False - transakcje muszą być zatwierdzane ręcznie,
- autoflush=False - SQLAlchemy nie wysyła zapytań automatycznie,
- bind=engine - sesje korzystają z utworzonego silnika.
"""
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""
Bazowa klasa dla wszystkich modeli ORM.
Każdy model powinien dziedziczyć po `Base`, aby SQLAlchemy mogło
automatycznie tworzyć tabele i mapować obiekty na rekordy.
"""
Base = declarative_base()

def get_db():
    """
    Zależność FastAPI zwracająca sesję bazy danych.
    Funkcja działa jako generator:
    - tworzy nową sesję (`SessionLocal()`),
    - udostępnia ją endpointowi poprzez `yield`,
    - po zakończeniu żądania automatycznie zamyka sesję (`db.close()`).
    Dzięki temu:
    - każda operacja HTTP ma własną, izolowaną sesję,
    - nie ma wycieków połączeń,
    - transakcje są poprawnie zarządzane.
    Zwraca:
        Generator zwracający obiekt sesji SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()