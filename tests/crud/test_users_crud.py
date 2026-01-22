from datetime import date
from pydantic.v1 import EmailStr
from app import crud, schemas

def test_register_and_get_user(db):
    """
    Test integracyjny sprawdzający proces rejestracji użytkownika oraz
    pobierania jego danych z bazy.

    Scenariusz:
    1. Tworzony jest obiekt UserRegister zawierający pełne dane użytkownika:
       login, email, hasło, imię, nazwisko oraz datę urodzenia.
    2. Funkcja CRUD `register_user` zapisuje użytkownika w bazie.
    3. Test weryfikuje:
       - czy użytkownik otrzymał identyfikator (user.id nie jest None),
       - czy login został poprawnie zapisany.
    4. Użytkownik jest pobierany z bazy za pomocą `get_user`.
    5. Test potwierdza, że pobrany użytkownik ma poprawny login.

    Cel:
    Zweryfikować, że rejestracja użytkownika działa poprawnie oraz że dane
    są prawidłowo zapisywane i odczytywane z bazy danych.
    """
    user_in = schemas.UserRegister(
        login="testuser",
        email=EmailStr("test@test.pl"),
        password="secret123",
        first_name="Jan",
        last_name="Kowalski",
        birth_date=date(2010,5,5)
    )
    user = crud.register_user(db, user_in)
    assert user.id is not None
    assert user.login == "testuser"

    fetched_user = crud.get_user(db, user.id)
    assert fetched_user.login == "testuser"

def test_authenticate_user_success_and_fail(db, client):
    """
    Test integracyjny sprawdzający działanie mechanizmu uwierzytelniania użytkownika.

    Scenariusz:
    1. Rejestrowany jest użytkownik o loginie "authuser" i haśle "password123".
    2. Funkcja CRUD `authenticate_user` jest wywoływana z poprawnymi danymi:
       - powinna zwrócić obiekt użytkownika.
    3. Test weryfikuje:
       - że użytkownik został poprawnie uwierzytelniony,
       - że login zwróconego użytkownika jest zgodny z oczekiwanym.
    4. Funkcja `authenticate_user` jest wywoływana ponownie, tym razem z błędnym hasłem.
    5. Oczekiwany wynik: None.

    Cel:
    Zweryfikować, że mechanizm uwierzytelniania:
    - poprawnie rozpoznaje prawidłowe dane logowania,
    - odrzuca niepoprawne hasło.
    """
    login = "authuser"
    password = "password123"
    user_in = schemas.UserRegister(login=login, email=EmailStr("auth@test.pl"), password=password, birth_date=date(2010,5,5))
    crud.register_user(db, user_in)

    auth_user = crud.authenticate_user(db, login, password)
    assert auth_user is not None
    assert auth_user.login == login

    auth_fail = crud.authenticate_user(db, login, "wrongpass")
    assert auth_fail is None

def test_update_and_delete_user(db, client):
    """
    Test integracyjny sprawdzający aktualizację oraz usuwanie użytkownika.

    Scenariusz:
    1. Rejestrowany jest użytkownik o loginie "upduser".
    2. Tworzony jest obiekt UserUpdate zawierający nowe imię użytkownika.
    3. Funkcja CRUD `update_user` aktualizuje dane użytkownika.
    4. Test weryfikuje, że pole first_name zostało poprawnie zmienione.
    5. Funkcja CRUD `delete_user` usuwa użytkownika z bazy.
    6. Test potwierdza:
       - że operacja usunięcia zwróciła True,
       - że użytkownik nie istnieje już w bazie (get_user zwraca None).

    Cel:
    Zweryfikować poprawność operacji CRUD związanych z aktualizacją
    i usuwaniem użytkowników oraz spójność danych w bazie.
    """
    user_in = schemas.UserRegister(login="upduser", email=EmailStr("upd@test.pl"), password="123456",birth_date=date(2010,5,5))
    user = crud.register_user(db, user_in)

    update_data = schemas.UserUpdate(first_name="NoweImie")
    updated_user = crud.update_user(db, user.id, update_data)
    assert updated_user.first_name == "NoweImie"

    result = crud.delete_user(db, user.id)
    assert result is True
    assert crud.get_user(db, user.id) is None
