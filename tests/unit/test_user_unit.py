"""
Testy jednostkowe modelu User.
Sprawdzają poprawność tworzenia użytkownika, aktualizacji pól
oraz powiązań z playlistami.
"""
from app.models import User, Playlist

def test_user_creation():
    """
        Test sprawdzający poprawność tworzenia obiektu użytkownika.
        Scenariusz:
        1. Utworzenie użytkownika z przykładowymi danymi (id, login, email).
        2. Weryfikacja, że pola login i email zostały poprawnie zapisane.
        Cel:
        Upewnić się, że model User poprawnie przechowuje podstawowe dane
        przekazane podczas inicjalizacji.
    """
    user = User(id=1, login="test", email="a@b.pl")
    assert user.login == "test"
    assert user.email == "a@b.pl"

def test_user_update_fields():
    """
        Test sprawdzający możliwość aktualizacji pól użytkownika.
        Scenariusz:
        1. Utworzenie użytkownika z loginem "old".
        2. Zmiana loginu na "new".
        3. Weryfikacja, że pole login zostało zaktualizowane.
        Cel:
        Zweryfikować, że obiekt User pozwala na modyfikację swoich pól
        po utworzeniu instancji.
    """
    user = User(id=1, login="old")
    user.login = "new"
    assert user.login == "new"

def test_user_add_playlist():
    """
        Test sprawdzający powiązanie użytkownika z playlistą.
        Scenariusz:
        1. Utworzenie użytkownika.
        2. Utworzenie playlisty.
        3. Dodanie playlisty do listy playlist użytkownika.
        4. Weryfikacja, że użytkownik ma dokładnie jedną playlistę.
        Cel:
        Upewnić się, że relacja User - Playlist działa poprawnie
        na poziomie modelu i że playlisty można przypisywać użytkownikowi.
    """
    user = User(id=1, login="u")
    playlist = Playlist(id=1, name="P")
    user.playlists.append(playlist)
    assert len(user.playlists) == 1

def test_user_remove_playlist():
    """
    Test sprawdzający usuwanie playlisty z listy playlist użytkownika.
    Scenariusz:
    1. Utworzenie użytkownika i dwóch playlist.
    2. Dodanie playlist do użytkownika.
    3. Usunięcie jednej playlisty.
    4. Weryfikacja, że pozostała tylko jedna.
    Cel:
    Upewnić się, że relacja User - Playlist działa poprawnie przy usuwaniu.
    """
    user = User(id=1, login="u")
    p1 = Playlist(id=1, name="P1")
    p2 = Playlist(id=2, name="P2")

    user.playlists.append(p1)
    user.playlists.append(p2)

    user.playlists.remove(p1)

    assert len(user.playlists) == 1
    assert user.playlists[0].name == "P2"
