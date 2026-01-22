"""
Zestaw fixture pytest wykorzystywanych w testach integracyjnych aplikacji FastAPI.

Plik przygotowuje:
- izolowaną bazę danych SQLite dla testów,
- klienta TestClient z nadpisaną zależnością get_db,
- zestaw obiektów testowych (User, Artist, Album, Track, Playlist),
  które mogą być wykorzystywane w wielu testach.

Fixture’y zapewniają pełną izolację środowiska testowego:
- przed każdym testem tworzona jest nowa baza danych,
- po teście baza jest usuwana,
- każdy fixture tworzy i zwraca w pełni zapisany obiekt ORM.

Dzięki temu testy są deterministyczne, powtarzalne i nie wpływają na siebie nawzajem.
"""
from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import database
from app.database import Base, get_db
from app.models import Artist, Track, User, Album, Playlist

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(bind=engine)
database.SessionLocal = TestingSessionLocal

from app.main import app

@pytest.fixture()
def client():
    """
        Tworzy instancję TestClient z nadpisaną zależnością get_db,
        tak aby każdy test korzystał z osobnej sesji bazy danych.
        Mechanizm:
        - tworzy strukturę tabel w testowej bazie SQLite,
        - nadpisuje zależność get_db, aby zwracała TestingSessionLocal,
        - uruchamia TestClient w kontekście,
        - po zakończeniu testu usuwa wszystkie tabele.
        Zwraca:
            TestClient — klient HTTP do wykonywania żądań w testach.
    """
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db():
    """
        Tworzy sesję bazy danych SQLAlchemy dla testów jednostkowych,
        które wymagają bezpośredniego dostępu do ORM.
        Mechanizm:
        - tworzy strukturę tabel,
        - zwraca sesję TestingSessionLocal,
        - po teście zamyka sesję i usuwa tabele.
        Zwraca:
            Session — sesja SQLAlchemy gotowa do użycia.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def user(db):
    """
    Tworzy i zapisuje w bazie testowego użytkownika.
    Zwraca:
        User — obiekt użytkownika z wypełnionym ID.
    """
    user = User(
        login="testuser",
        email="test@test.pl",
        password="x" * 60,
        first_name="Test",
        last_name="User",
        birth_date=date(2001, 5, 5),
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def artist(db):
    """
        Tworzy i zapisuje w bazie testowego artystę.
        Zwraca:
            Artist — obiekt artysty z wypełnionym ID.
    """
    artist = Artist(name="Test Artist", country="PL")
    db.add(artist)
    db.commit()
    db.refresh(artist)
    return artist

@pytest.fixture
def album(db, artist):
    """
        Tworzy album powiązany z testowym artystą.
        Zwraca:
            Album — obiekt albumu z wypełnionym ID.
    """
    album = Album(
        title="Test Album",
        release_date=date(2024, 1, 1),
        artist_id=artist.id
    )
    db.add(album)
    db.commit()
    db.refresh(album)
    return album

@pytest.fixture
def track(db, artist, album):
    """
        Tworzy utwór powiązany z albumem i artystą.
        Mechanizm:
        - tworzy obiekt Track,
        - przypisuje artystę do relacji many-to-many,
        - zapisuje w bazie.
        Zwraca:
            Track — obiekt utworu.
    """
    track = Track(
        title="Track 1",
        duration=5,
        album_id=album.id
    )
    track.artists.append(artist)

    db.add(track)
    db.commit()
    db.refresh(track)
    return track

@pytest.fixture
def track2(db, artist, album):
    """
        Tworzy drugi testowy utwór powiązany z albumem i artystą.
        Zwraca:
            Track — obiekt utworu.
    """
    track = Track(
        title="Track 2",
        duration=5,
        album_id=album.id
    )
    track.artists.append(artist)

    db.add(track)
    db.commit()
    db.refresh(track)
    return track

@pytest.fixture
def playlist(db, user, track, track2):
    """
        Tworzy playlistę powiązaną z użytkownikiem oraz dwoma utworami.
        Mechanizm:
        - tworzy obiekt Playlist,
        - przypisuje do niej dwa utwory,
        - zapisuje w bazie.
        Zwraca:
            Playlist — obiekt playlisty z pełnymi relacjami.
    """
    playlist = Playlist(
        name="Test Playlist",
        owner_id=user.id
    )
    playlist.tracks.extend([track, track2])

    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist
