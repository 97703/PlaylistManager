"""
seed.py — skrypt do wypełniania bazy danych przykładowymi danymi.

Cel:
    Skrypt automatycznie tworzy użytkowników, artystów, albumy, utwory
    oraz playlisty, a następnie łączy je w spójną strukturę muzycznej biblioteki.
    Umożliwia szybkie przygotowanie środowiska developerskiego oraz testowego.

Zakres działania:
    1. Tworzenie użytkowników:
        - 10 przykładowych kont z unikalnymi loginami i danymi osobowymi.
        - Rejestracja odbywa się przez crud.register_user (hashowanie haseł).

    2. Dodawanie artystów:
        - Daft Punk, Coldplay, The Weeknd.
        - Każdy artysta ma przypisany kraj pochodzenia.

    3. Dodawanie albumów:
        - Random Access Memories (Daft Punk)
        - Discovery (Daft Punk)
        - Parachutes (Coldplay)
        - After Hours (The Weeknd)
        - Każdy album ma ustawioną datę wydania i powiązanego artystę.

    4. Dodawanie utworów:
        - Utwory są pogrupowane według albumów.
        - Każdy utwór ma tytuł, czas trwania, album_id i listę artist_ids.
        - Dzięki temu albumy są automatycznie wypełnione odpowiednimi piosenkami.

    5. Tworzenie playlist:
        - Każdy z 10 użytkowników otrzymuje jedną playlistę.
        - Playlisty mają różne nazwy i właścicieli.

    6. Dodawanie utworów do playlist:
        - Każda playlista otrzymuje zestaw utworów.
        - Powiązania tworzone są przez crud.add_track_to_playlist.

    7. Zamykanie sesji:
        - Po zakończeniu seedowania połączenie z bazą jest zamykane.

Zastosowanie:
    - szybkie przygotowanie bazy do testów,
    - demonstracja działania API,
    - testowanie WebSocket Playera na realnych danych,
    - wypełnienie bazy przykładową biblioteką muzyczną.

Uruchamianie:
    python seed.py

Uwaga:
    Skrypt zakłada pustą bazę lub brak konfliktów ID.
"""
from datetime import date
from pydantic.v1 import EmailStr
from app.database import SessionLocal
from app import crud
from app.models import UserRole
from app.schemas import UserRegister, ArtistCreate, AlbumCreate, TrackCreate, PlaylistCreate

users = [
    UserRegister(
        login="user1",
        email=EmailStr("user1@example.com"),
        password="pass123",
        first_name="Adam",
        last_name="Kowalski",
        birth_date=date(2001, 5, 5),
        role=UserRole.admin
    ),
    UserRegister(
        login="user2",
        email=EmailStr("user2@example.com"),
        password="pass123",
        first_name="Ewa",
        last_name="Nowak",
        birth_date=date(2002, 3, 12),
        role=UserRole.user
    ),
    UserRegister(
        login="user3",
        email=EmailStr("user3@example.com"),
        password="pass123",
        first_name="Paweł",
        last_name="Zieliński",
        birth_date=date(2000, 11, 2),
        role=UserRole.user
    ),
    UserRegister(
        login="user4",
        email=EmailStr("user4@example.com"),
        password="pass123",
        first_name="Anna",
        last_name="Wiśniewska",
        birth_date=date(2003, 1, 20),
        role=UserRole.user
    ),
    UserRegister(
        login="user5",
        email=EmailStr("user5@example.com"),
        password="pass123",
        first_name="Marek",
        last_name="Lewandowski",
        birth_date=date(1999, 7, 14),
        role=UserRole.user
    ),
    UserRegister(
        login="user6",
        email=EmailStr("user6@example.com"),
        password="pass123",
        first_name="Karolina",
        last_name="Mazur",
        birth_date=date(2001, 9, 30),
        role=UserRole.user
    ),
    UserRegister(
        login="user7",
        email=EmailStr("user7@example.com"),
        password="pass123",
        first_name="Tomasz",
        last_name="Wójcik",
        birth_date=date(2000, 4, 18),
        role=UserRole.user
    ),
    UserRegister(
        login="user8",
        email=EmailStr("user8@example.com"),
        password="pass123",
        first_name="Magda",
        last_name="Krawczyk",
        birth_date=date(2002, 8, 9),
        role=UserRole.user
    ),
    UserRegister(
        login="user9",
        email=EmailStr("user9@example.com"),
        password="pass123",
        first_name="Kuba",
        last_name="Piotrowski",
        birth_date=date(2001, 12, 1),
        role=UserRole.user
    ),
    UserRegister(
        login="user10",
        email=EmailStr("user10@example.com"),
        password="pass123",
        first_name="Ola",
        last_name="Szymańska",
        birth_date=date(2003, 6, 22),
        role=UserRole.user
    ),
]


artists = [
    ArtistCreate(name="Daft Punk", country="France"),
    ArtistCreate(name="Coldplay", country="United Kingdom"),
    ArtistCreate(name="The Weeknd", country="Canada"),
]

albums = [
    AlbumCreate(
        title="Random Access Memories",
        release_date=date(2013, 5, 17),
        artist_id=1,
    ),
    AlbumCreate(
        title="Discovery",
        release_date=date(2001, 3, 12),
        artist_id=1,
    ),
    AlbumCreate(
        title="Parachutes",
        release_date=date(2000, 7, 10),
        artist_id=2,
    ),
    AlbumCreate(
        title="After Hours",
        release_date=date(2020, 3, 20),
        artist_id=3,
    ),
]

tracks = [
    TrackCreate(
        title="Get Lucky",
        duration=369,
        album_id=1,
        artist_ids=[1],
        file_path=None
    ),
    TrackCreate(
        title="Instant Crush",
        duration=337,
        album_id=1,
        artist_ids=[1],
        file_path=None
    ),
    TrackCreate(
        title="Harder, Better, Faster, Stronger",
        duration=224,
        album_id=2,
        artist_ids=[1],
        file_path=None
    ),
    TrackCreate(
        title="One More Time",
        duration=320,
        album_id=2,
        artist_ids=[1],
        file_path=None
    ),
    TrackCreate(
        title="Yellow",
        duration=269,
        album_id=3,
        artist_ids=[2],
        file_path=None
    ),
    TrackCreate(
        title="Trouble",
        duration=270,
        album_id=3,
        artist_ids=[2],
        file_path=None
    ),
    TrackCreate(
        title="Blinding Lights",
        duration=200,
        album_id=4,
        artist_ids=[3],
        file_path=None
    ),
    TrackCreate(
        title="Save Your Tears",
        duration=215,
        album_id=4,
        artist_ids=[3],
        file_path=None
    ),
    TrackCreate(
        title="Starboy",
        duration=230,
        album_id=4,
        artist_ids=[3],
        file_path=None
    ),
    TrackCreate(
        title="I Feel It Coming",
        duration=269,
        album_id=4,
        artist_ids=[3],
        file_path=None
    ),
]

playlists = [
    PlaylistCreate(
        name="Daft Punk Essentials",
        owner_id=1
    ),
    PlaylistCreate(
        name="Coldplay Chill",
        owner_id=2
    ),
    PlaylistCreate(
        name="The Weeknd Hits",
        owner_id=3
    ),
    PlaylistCreate(
        name="Workout Mix",
        owner_id=4
    ),
    PlaylistCreate(
        name="Evening Relax",
        owner_id=5
    ),
    PlaylistCreate(
        name="Top 10 Favorites",
        owner_id=6
    ),
    PlaylistCreate(
        name="Electronic Vibes",
        owner_id=7
    ),
    PlaylistCreate(
        name="Soft & Calm",
        owner_id=8
    ),
    PlaylistCreate(
        name="Party Mode",
        owner_id=9
    ),
    PlaylistCreate(
        name="Daily Mix",
        owner_id=10
    ),
]

def main():
    db = SessionLocal()
    try:
        for u in users:
            crud.register_user(db, u)

        for a in artists:
            crud.create_artist(db, a)

        for al in albums:
            crud.create_album(db, al)

        for t in tracks:
            crud.create_track(db, t)

        for p in playlists:
            crud.create_playlist(db, p)

        for tid in [1, 2, 3, 4]:
            crud.add_track_to_playlist(db, 1, tid)

        for tid in [5, 6]:
            crud.add_track_to_playlist(db, 2, tid)

        for tid in [7, 8, 9, 10]:
            crud.add_track_to_playlist(db, 3, tid)

        for tid in [1, 4, 7, 9]:
            crud.add_track_to_playlist(db, 4, tid)

        for tid in [2, 5, 6, 10]:
            crud.add_track_to_playlist(db, 5, tid)

        for tid in range(1, 11):
            crud.add_track_to_playlist(db, 6, tid)

        for tid in [1, 3, 4, 7]:
            crud.add_track_to_playlist(db, 7, tid)

        for tid in [5, 6, 10]:
            crud.add_track_to_playlist(db, 8, tid)

        for tid in [1, 4, 7, 8, 9]:
            crud.add_track_to_playlist(db, 9, tid)

        for tid in [2, 5, 7, 10]:
            crud.add_track_to_playlist(db, 10, tid)

        print("Seed completed.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
