"""
Testy jednostkowe modelu Playlist.
Sprawdzają poprawność tworzenia playlisty, dodawania utworów
oraz powiązania z właścicielem.
"""
from app.models import Playlist, User, Track

def test_playlist_creation():
    """
        Test sprawdzający poprawność tworzenia obiektu Artist.
        Scenariusz:
        1. Utworzenie artysty z przykładowymi danymi (id, name, country).
        2. Weryfikacja, że pola name oraz country zostały poprawnie zapisane.
        Cel:
        Upewnić się, że model Artist poprawnie przechowuje dane podstawowe
        przekazane podczas inicjalizacji.
    """
    user = User(id=1, login="u")
    playlist = Playlist(id=1, name="MyPlaylist", owner=user)
    assert playlist.name == "MyPlaylist"
    assert playlist.owner == user

def test_playlist_add_track():
    """
        Test sprawdzający możliwość aktualizacji pól obiektu Artist.
        Scenariusz:
        1. Utworzenie artysty z nazwą "Old".
        2. Zmiana nazwy artysty na "New".
        3. Weryfikacja, że pole name zostało poprawnie zaktualizowane.
        Cel:
        Zweryfikować, że obiekt Artist pozwala na modyfikację swoich pól
        po utworzeniu instancji.
    """
    playlist = Playlist(id=1, name="P")
    track = Track(id=1, title="T", duration=100)
    playlist.tracks.append(track)
    assert len(playlist.tracks) == 1

def test_playlist_remove_track():
    """
    Test sprawdzający usuwanie utworu z playlisty.
    Scenariusz:
    1. Utworzenie playlisty i dwóch utworów.
    2. Dodanie ich do playlisty.
    3. Usunięcie jednego utworu.
    4. Weryfikacja, że pozostał tylko drugi.
    Cel:
    Zweryfikować poprawność relacji Playlist - Track przy usuwaniu.
    """
    playlist = Playlist(id=1, name="P")
    t1 = Track(id=1, title="T1", duration=100)
    t2 = Track(id=2, title="T2", duration=120)

    playlist.tracks.append(t1)
    playlist.tracks.append(t2)

    playlist.tracks.remove(t1)

    assert len(playlist.tracks) == 1
    assert playlist.tracks[0].title == "T2"
