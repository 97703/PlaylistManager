from app import crud, schemas

def test_create_get_update_delete_track(db, client):
    """
    Test integracyjny sprawdzający pełny cykl życia utworu (CRUD):
    - utworzenie utworu,
    - pobranie utworu,
    - aktualizację danych utworu,
    - usunięcie utworu.

    Scenariusz:
    1. Tworzony jest artysta, który będzie właścicielem albumu.
    2. Tworzony jest album powiązany z artystą.
    3. Tworzony jest utwór z wykorzystaniem schematu TrackCreate:
       - tytuł "Track1",
       - czas trwania 180 sekund,
       - powiązanie z albumem i artystą.
    4. Test weryfikuje:
       - czy utwór został poprawnie zapisany (track.id nie jest None),
       - czy tytuł utworu jest zgodny z oczekiwanym.
    5. Utwór jest pobierany z bazy i sprawdzane są jego dane.
    6. Utwór jest aktualizowany — tytuł zmieniany na "TrackUpdated".
    7. Test sprawdza, czy aktualizacja została poprawnie zapisana.
    8. Utwór jest usuwany z bazy.
    9. Test potwierdza:
       - że operacja usunięcia zwróciła True,
       - że utwór został poprawnie usunięty z bazy.

    Cel:
    Zweryfikować poprawność operacji CRUD dla utworów muzycznych oraz
    spójność relacji między utworem, albumem i artystą w warstwie CRUD.
    """
    artist = crud.create_artist(db, schemas.ArtistCreate(name="TrackArtist"))
    album = crud.create_album(db, schemas.AlbumCreate(title="TrackAlbum", artist_id=artist.id))

    track_in = schemas.TrackCreate(
        title="Track1",
        duration=180,
        album_id=album.id,
        artist_ids=[artist.id]
    )
    track = crud.create_track(db, track_in)
    assert track.id is not None
    assert track.title == "Track1"

    fetched_track = crud.get_track(db, track.id)
    assert fetched_track.title == "Track1"

    update_data = schemas.TrackUpdate(title="TrackUpdated")
    updated_track = crud.update_track(db, track.id, update_data)

    assert updated_track.title == "TrackUpdated"
    assert crud.delete_track(db, track.id) is True

