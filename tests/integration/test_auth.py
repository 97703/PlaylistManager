"""
Zestaw testów integracyjnych weryfikujących działanie mechanizmów
rejestracji, logowania oraz wylogowania użytkownika w API.

Testowane są trzy kluczowe scenariusze:
- poprawna rejestracja użytkownika,
- poprawne logowanie i ustawienie ciasteczka sesyjnego,
- poprawne wylogowanie użytkownika.

Testy wykorzystują klienta TestClient oraz izolowaną bazę danych
przygotowaną przez fixture `client`.
"""

def test_register_user(client):
    """
        Testuje proces rejestracji nowego użytkownika.

        Scenariusz:
        1. Wysyłane jest żądanie POST na endpoint /auth/register
           z danymi nowego użytkownika.
        2. Oczekiwany status odpowiedzi to 200.
        3. Odpowiedź powinna zawierać login nowo utworzonego użytkownika.

        Cel:
        Zweryfikować, że rejestracja działa poprawnie i zwraca
        prawidłowe dane użytkownika.
    """
    response = client.post("/auth/register", json={
        "login": "testuser",
        "email": "test@test.pl",
        "password": "secret123",
        "birth_date": "2001-05-05"
    })
    assert response.status_code == 200
    assert response.json()["login"] == "testuser"


def test_login_and_cookie_set(client):
    """
        Testuje proces logowania oraz ustawianie ciasteczka sesyjnego.

        Scenariusz:
        1. Rejestrowany jest użytkownik testowy.
        2. Wysyłane jest żądanie POST na /auth/login z poprawnymi danymi.
        3. Oczekiwany status odpowiedzi to 200.
        4. W odpowiedzi powinno pojawić się ciasteczko `session_id`.

        Cel:
        Upewnić się, że logowanie działa poprawnie oraz że
        mechanizm sesji ustawia ciasteczko identyfikujące użytkownika.
    """
    client.post("/auth/register", json={
        "login": "loginuser",
        "email": "login@test.pl",
        "password": "secret123",
        "birth_date": "2001-05-05"
    })

    response = client.post("/auth/login", json={
        "login": "loginuser",
        "password": "secret123"
    })

    assert response.status_code == 200
    assert "session_id" in response.cookies


def test_logout(client):
    """
        Testuje proces wylogowania użytkownika.

        Scenariusz:
        1. Rejestrowany jest użytkownik testowy.
        2. Użytkownik loguje się, co ustawia ciasteczko sesyjne.
        3. Wysyłane jest żądanie POST na /auth/logout.
        4. Oczekiwany status odpowiedzi to 200.

        Cel:
        Zweryfikować, że endpoint wylogowania działa poprawnie
        i nie zwraca błędów przy usuwaniu sesji.
    """
    client.post("/auth/register", json={
        "login": "logoutuser",
        "email": "logout@test.pl",
        "password": "secret123",
        "birth_date": "2001-05-05"
    })
    client.post("/auth/login", json={
        "login": "logoutuser",
        "password": "secret123"
    })

    response = client.post("/auth/logout")
    assert response.status_code == 200

def test_get_user(client):
    """
    Test integracyjny sprawdzający poprawność pobierania danych użytkownika
    na podstawie jego identyfikatora.

    Scenariusz:
    1. Rejestrowany jest nowy użytkownik o loginie "user1".
    2. Z odpowiedzi rejestracji pobierane jest ID użytkownika.
    3. Wysyłane jest żądanie GET na endpoint /users/{user_id}.
    4. Oczekiwany status odpowiedzi to 200.
    5. Odpowiedź powinna zawierać poprawny login użytkownika.

    Cel:
    Zweryfikować, że endpoint pobierania użytkownika działa poprawnie
    i zwraca właściwe dane na podstawie ID.
    """
    reg = client.post("/auth/register", json={
        "login": "user1",
        "email": "u1@test.pl",
        "password": "secret123",
        "birth_date": "2001-05-05"
    })
    user_id = reg.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["login"] == "user1"


def test_update_user(client):
    """
    Test integracyjny sprawdzający poprawność aktualizacji danych użytkownika.

    Scenariusz:
    1. Rejestrowany jest użytkownik o loginie "user2".
    2. Z odpowiedzi rejestracji pobierane jest ID użytkownika.
    3. Wysyłane jest żądanie PATCH na endpoint /users/{user_id}
       z danymi aktualizacyjnymi: first_name i last_name.
    4. Oczekiwany status odpowiedzi to 200.
    5. Odpowiedź powinna zawierać zaktualizowane dane użytkownika,
       w szczególności first_name = "Jan".

    Cel:
    Zweryfikować, że endpoint aktualizacji użytkownika działa poprawnie,
    prawidłowo zapisuje zmiany i zwraca zaktualizowany obiekt użytkownika.
    """
    reg = client.post("/auth/register", json={
        "login": "user2",
        "email": "u2@test.pl",
        "password": "secret123",
        "birth_date": "2001-05-05"
    })
    user_id = reg.json()["id"]

    response = client.patch(f"/users/{user_id}", json={
        "first_name": "Jan",
        "last_name": "Kowalski"
    })

    assert response.status_code == 200
    assert response.json()["first_name"] == "Jan"
