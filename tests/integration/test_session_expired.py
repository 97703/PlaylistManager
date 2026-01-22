def test_cannot_create_playlist_after_session_expired(client):
    """
    Test integracyjny sprawdzający, czy użytkownik nie może tworzyć playlist
    po wygaśnięciu sesji (braku ciasteczka `session_id`).

    Scenariusz:
    1. Rejestrowany jest użytkownik testowy.
    2. Użytkownik loguje się, co ustawia ciasteczko sesyjne.
    3. Użytkownik tworzy pierwszą playlistę — operacja powinna się powieść.
    4. Ciasteczka klienta są ręcznie czyszczone, co symuluje wygaśnięcie sesji.
    5. Użytkownik próbuje ponownie utworzyć playlistę.
    6. Oczekiwany status odpowiedzi to 401 (brak autoryzacji) lub 403 (brak uprawnień).

    Cel:
    Zweryfikować, że:
    - mechanizm sesji działa poprawnie,
    - endpoint /playlists wymaga aktywnej sesji użytkownika,
    - po utracie ciasteczka sesyjnego użytkownik nie może wykonywać operacji,
      które wymagają uwierzytelnienia.

    Test potwierdza poprawność zabezpieczeń związanych z autoryzacją i sesjami.
    """
    register_resp = client.post("/auth/register", json={
        "login": "sessionuser",
        "email": "session@test.pl",
        "password": "secret123",
        "birth_date": "2001-05-05"
    })
    assert register_resp.status_code == 200
    user_id = register_resp.json()["id"]

    login_resp = client.post("/auth/login", json={
        "login": "sessionuser",
        "password": "secret123"
    })
    assert login_resp.status_code == 200

    ok_resp = client.post("/playlists", json={
        "name": "My playlist",
        "owner_id": user_id
    })
    assert ok_resp.status_code == 200

    client.cookies.clear()

    forbidden_resp = client.post("/playlists", json={
        "name": "Should not work",
        "owner_id": user_id
    })

    assert forbidden_resp.status_code in (401, 403)
