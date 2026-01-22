def test_create_playlist(client):
    """
    Test integracyjny sprawdzający poprawne tworzenie playlisty przez użytkownika.

    Scenariusz:
    1. Rejestrowany jest użytkownik testowy o loginie "playlistuser".
    2. Użytkownik loguje się, co powoduje ustawienie ciasteczka sesyjnego.
    3. Pobierana jest lista użytkowników, aby uzyskać ID nowo utworzonego użytkownika.
    4. Wysyłane jest żądanie POST na endpoint /playlists z danymi nowej playlisty.
    5. Oczekiwany status odpowiedzi to 200.
    6. Odpowiedź powinna zawierać nazwę playlisty "My Playlist".

    Cel:
    Zweryfikować, że:
    - użytkownik może poprawnie utworzyć playlistę,
    - endpoint /playlists działa zgodnie z oczekiwaniami,
    - dane playlisty są poprawnie zwracane w odpowiedzi API.
    """
    client.post("/auth/register", json={
        "login": "playlistuser",
        "email": "p@test.pl",
        "password": "secret123",
        "birth_date": "2001-05-05"
    })
    client.post("/auth/login", json={
        "login": "playlistuser",
        "password": "secret123"
    })

    user = client.get("/users").json()[0]
    user_id = user["id"]

    response = client.post("/playlists", json={
        "name": "My Playlist",
        "owner_id": user_id
    })

    assert response.status_code == 200
    assert response.json()["name"] == "My Playlist"
