"""
Testy jednostkowe modelu Track.
Sprawdzają poprawność tworzenia utworu, aktualizacji pól
oraz powiązań z albumem i artystami.
"""
from app.models import Track, Album, Artist

def test_track_creation():
    """
        Test sprawdzający poprawność tworzenia obiektu Track.
        Scenariusz:
        1. Utworzenie utworu z przykładowymi danymi (id, title, duration).
        2. Weryfikacja, że pola title i duration zostały poprawnie zapisane.
        Cel:
        Upewnić się, że model Track poprawnie przechowuje dane podstawowe
        przekazane podczas inicjalizacji.
    """
    track = Track(id=1, title="Song", duration=180)
    assert track.title == "Song"
    assert track.duration == 180

def test_track_assign_album():
    """
        Test sprawdzający powiązanie utworu z albumem.
        Scenariusz:
        1. Utworzenie albumu.
        2. Utworzenie utworu i przypisanie go do albumu.
        3. Weryfikacja, że pole album zostało poprawnie ustawione.
        Cel:
        Zweryfikować, że relacja Track → Album działa poprawnie
        na poziomie modelu.
    """
    album = Album(id=1, title="A")
    track = Track(id=1, title="T", duration=100, album=album)
    assert track.album == album

def test_track_add_artist():
    """
        Test sprawdzający powiązanie utworu z artystą.
        Scenariusz:
        1. Utworzenie utworu.
        2. Utworzenie artysty.
        3. Dodanie artysty do listy artists utworu.
        4. Weryfikacja, że artysta został poprawnie dodany.
        Cel:
        Upewnić się, że relacja Track - Artist działa poprawnie
        i że utwór może mieć przypisanych wielu artystów.
    """
    track = Track(id=1, title="T", duration=100)
    artist = Artist(id=1, name="A")
    track.artists.append(artist)
    assert track.artists[0].name == "A"

def test_track_file_path():
    """
        Test sprawdzający poprawność przechowywania ścieżki pliku MP3.
        Scenariusz:
        1. Utworzenie utworu z podaną ścieżką file_path.
        2. Weryfikacja, że ścieżka została poprawnie zapisana w modelu.
        Cel:
        Upewnić się, że model Track poprawnie przechowuje opcjonalne pole file_path.
    """
    track = Track(
        id=1,
        title="Song",
        duration=180,
        file_path="static/tracks/1.mp3"
    )

    assert track.file_path == "static/tracks/1.mp3"
