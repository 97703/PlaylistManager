def test_add_and_remove_track_from_playlist(client):
    """
    Test integracyjny sprawdzający poprawność dodawania i usuwania utworu
    z playlisty poprzez endpointy API.

    Scenariusz:
    1. Rejestrowany jest użytkownik z rolą administratora.
    2. Użytkownik loguje się, co ustawia ciasteczko sesyjne.
    3. Tworzony jest artysta poprzez endpoint /artists.
    4. Tworzony jest album powiązany z artystą.
    5. Tworzony jest utwór powiązany z albumem i artystą.
    6. Tworzona jest playlista należąca do zalogowanego użytkownika.
    7. Test weryfikuje:
       - czy wszystkie obiekty (artist, album, track, playlist) zostały poprawnie utworzone,
       - czy każdy z nich posiada identyfikator.
    8. Wysyłane jest żądanie POST dodające utwór do playlisty.
       Oczekiwany status odpowiedzi: 200.
    9. Pobierana jest lista utworów z playlisty:
       - powinna zawierać dokładnie jeden utwór,
       - jego ID powinno odpowiadać ID utworzonego utworu.
    10. Wysyłane jest żądanie DELETE usuwające utwór z playlisty.
        Oczekiwany status odpowiedzi: 200.
    11. Ponowne pobranie listy utworów powinno zwrócić pustą listę.

    Cel:
    Zweryfikować poprawność działania endpointów:
    - dodawania utworu do playlisty,
    - pobierania zawartości playlisty,
    - usuwania utworu z playlisty.

    Test potwierdza, że relacje many-to-many między playlistami a utworami
    działają poprawnie na poziomie API oraz że dane są spójne w bazie.
    """
    user_resp = client.post("/auth/register", json={
        "login": "musicuser",
        "email": "m@test.pl",
        "password": "secret123",
        "birth_date": "2001-05-05",
        "role": "admin"
    })
    user_data = user_resp.json()
    user_id = user_data["id"]
    assert "id" in user_data

    login_resp = client.post("/auth/login", json={
        "login": "musicuser",
        "password": "secret123"
    })
    assert login_resp.status_code == 200

    artist_resp = client.post("/artists", json={"name": "Artist"})
    artist_data = artist_resp.json()
    artist_id = artist_data["id"]
    assert "id" in artist_data

    album_resp = client.post("/albums", json={
        "title": "Album",
        "release_date": "2023-01-01",
        "artist_id": artist_id
    })
    album_data = album_resp.json()
    album_id = album_data["id"]
    assert "id" in album_data

    track_resp = client.post("/tracks", json={
        "title": "Song",
        "duration": 180,
        "album_id": album_id,
        "artist_ids": [artist_id]
    })
    track_data = track_resp.json()
    track_id = track_data["id"]
    assert "id" in track_data

    playlist_resp = client.post("/playlists", json={
        "name": "Playlist",
        "owner_id": user_id
    })
    playlist_data = playlist_resp.json()
    playlist_id = playlist_data["id"]
    assert "id" in playlist_data

    add_resp = client.post(f"/playlists/{playlist_id}/tracks/{track_id}")
    assert add_resp.status_code == 200

    tracks_resp = client.get(f"/playlists/{playlist_id}/tracks")
    tracks = tracks_resp.json()
    assert len(tracks) == 1
    assert tracks[0]["id"] == track_id

    remove_resp = client.delete(f"/playlists/{playlist_id}/tracks/{track_id}")
    assert remove_resp.status_code == 200

    tracks_resp = client.get(f"/playlists/{playlist_id}/tracks")
    tracks = tracks_resp.json()
    assert len(tracks) == 0
