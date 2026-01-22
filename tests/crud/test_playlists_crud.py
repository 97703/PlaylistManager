from datetime import date

from app import crud, schemas

def test_create_add_get_remove_playlist_tracks(db, client):
    """
    Test integracyjny sprawdzający pełny cykl zarządzania utworami w playliście:
    - utworzenie playlisty,
    - dodanie utworu do playlisty,
    - pobranie listy utworów z playlisty,
    - usunięcie utworu z playlisty.

    Scenariusz:
    1. Tworzony jest użytkownik testowy poprzez funkcję CRUD `register_user`.
    2. Tworzony jest artysta, który będzie właścicielem albumu i utworu.
    3. Tworzony jest album powiązany z artystą.
    4. Tworzony jest utwór powiązany z albumem i artystą (relacja many-to-many).
    5. Tworzona jest playlista należąca do użytkownika.
    6. Test weryfikuje:
       - czy playlista została poprawnie utworzona,
       - czy otrzymała identyfikator.
    7. Utwór jest dodawany do playlisty za pomocą `add_track_to_playlist`.
    8. Test sprawdza:
       - czy operacja zwróciła True,
       - czy playlista zawiera dokładnie jeden utwór,
       - czy ID utworu zgadza się z oczekiwanym.
    9. Utwór jest usuwany z playlisty.
    10. Test potwierdza:
        - że operacja usunięcia zwróciła True,
        - że playlista nie zawiera już żadnych utworów.

    Cel:
    Zweryfikować poprawność operacji CRUD związanych z zarządzaniem zawartością playlist:
    dodawaniem, pobieraniem i usuwaniem utworów. Test potwierdza, że relacje many-to-many
    między playlistami a utworami działają poprawnie i są spójne w warstwie CRUD.
    """
    user = crud.register_user(
        db,
        schemas.UserRegister(login="playlistuser", email="pl@test.pl", password="123456", birth_date=date(2010,5,5))
    )
    artist = crud.create_artist(db, schemas.ArtistCreate(name="PlArtist"))

    album = crud.create_album(
        db,
        schemas.AlbumCreate(title="PlAlbum", artist_id=artist.id)
    )

    track = crud.create_track(
        db,
        schemas.TrackCreate(
            title="PlTrack",
            duration=200,
            album_id=album.id,
            artist_ids=[artist.id]
        )
    )

    playlist_in = schemas.PlaylistCreate(name="MyPlaylist", owner_id=user.id)
    playlist = crud.create_playlist(db, playlist_in)
    assert playlist.id is not None
    assert playlist.name == "MyPlaylist"

    added = crud.add_track_to_playlist(db, playlist.id, track.id)
    assert added is True

    tracks = crud.get_playlist_tracks(db, playlist.id)
    assert len(tracks) == 1
    assert tracks[0].id == track.id

    removed = crud.remove_track_from_playlist(db, playlist.id, track.id)
    assert removed is True
    tracks = crud.get_playlist_tracks(db, playlist.id)
    assert len(tracks) == 0

