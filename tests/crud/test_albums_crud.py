from datetime import date
from app import crud, schemas

def test_create_get_update_delete_album(db, client):
    """
    Test integracyjny sprawdzający pełny cykl życia albumu (CRUD):
    - utworzenie albumu,
    - pobranie albumu,
    - aktualizację albumu,
    - usunięcie albumu.

    Scenariusz:
    1. Tworzony jest artysta, który będzie właścicielem albumu.
    2. Tworzony jest album z wykorzystaniem schematu AlbumCreate.
    3. Test weryfikuje:
       - czy album został zapisany (album.id nie jest None),
       - czy pola albumu mają poprawne wartości.
    4. Album jest pobierany z bazy i sprawdzane są jego dane.
    5. Album jest aktualizowany (zmiana tytułu na "Album2").
    6. Test sprawdza, czy aktualizacja została poprawnie zapisana.
    7. Album jest usuwany z bazy.
    8. Test potwierdza:
       - że operacja usunięcia zwróciła True,
       - że album nie istnieje już w bazie.

    Cel:
    Zapewnienie, że operacje CRUD dla albumów działają poprawnie i spójnie
    w warstwie logiki aplikacji (CRUD) oraz że dane są poprawnie zapisywane
    i usuwane z bazy danych.
    """
    artist = crud.create_artist(db, schemas.ArtistCreate(name="Artist1", country=None))

    album_in = schemas.AlbumCreate(
        title="Album1",
        release_date=date(2009, 5, 1),
        artist_id=artist.id
    )

    album = crud.create_album(db, album_in)
    assert album.id is not None
    assert album.title == "Album1"

    fetched_album = crud.get_album(db, album.id)
    assert fetched_album.title == "Album1"

    update_data = schemas.AlbumUpdate(title="Album2")
    updated_album = crud.update_album(db, album.id, update_data)
    assert updated_album.title == "Album2"

    result = crud.delete_album(db, album.id)
    assert result is True
    assert crud.get_album(db, album.id) is None

