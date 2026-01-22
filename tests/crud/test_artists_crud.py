from app import crud, schemas

def test_create_get_update_delete_artist(db, client):
    """
    Test integracyjny sprawdzający pełny cykl życia artysty (CRUD):
    - utworzenie artysty,
    - pobranie artysty,
    - aktualizację danych artysty,
    - usunięcie artysty.

    Scenariusz:
    1. Tworzony jest obiekt ArtistCreate z nazwą "Artist1".
    2. Funkcja CRUD `create_artist` zapisuje artystę w bazie.
    3. Test weryfikuje:
       - czy artysta otrzymał identyfikator (artist.id nie jest None),
       - czy nazwa artysty została poprawnie zapisana.
    4. Artysta jest pobierany z bazy i sprawdzane są jego dane.
    5. Artysta jest aktualizowany — nazwa zmieniana na "Artist2".
    6. Test sprawdza, czy aktualizacja została poprawnie zapisana.
    7. Artysta jest usuwany z bazy.
    8. Test potwierdza:
       - że operacja usunięcia zwróciła True,
       - że artysta nie istnieje już w bazie (get_artist zwraca None).

    Cel:
    Zapewnienie, że operacje CRUD dla artystów działają poprawnie i spójnie
    w warstwie logiki aplikacji (CRUD) oraz że dane są poprawnie zapisywane,
    aktualizowane i usuwane z bazy danych.
    """
    artist_in = schemas.ArtistCreate(name="Artist1")
    artist = crud.create_artist(db, artist_in)
    assert artist.id is not None
    assert artist.name == "Artist1"

    fetched_artist = crud.get_artist(db, artist.id)
    assert fetched_artist.name == "Artist1"

    update_data = schemas.ArtistUpdate(name="Artist2")
    updated_artist = crud.update_artist(db, artist.id, update_data)
    assert updated_artist.name == "Artist2"

    result = crud.delete_artist(db, artist.id)
    assert result is True
    assert crud.get_artist(db, artist.id) is None
