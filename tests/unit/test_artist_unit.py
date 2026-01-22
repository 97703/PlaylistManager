"""
Testy jednostkowe modelu Artist.
Sprawdzają poprawność tworzenia obiektu, aktualizacji pól
oraz reprezentacji tekstowej.
"""
from app.models import Artist, Track

def test_artist_creation():
    """
        Test sprawdzający poprawność tworzenia obiektu Artist.
        Scenariusz:
        1. Utworzenie artysty z przykładowymi danymi (id, name, country).
        2. Weryfikacja, że pola name oraz country zostały poprawnie zapisane.
        Cel:
        Upewnić się, że model Artist poprawnie przechowuje dane podstawowe
        przekazane podczas inicjalizacji.
    """
    artist = Artist(id=1, name="Artist1", country="PL")
    assert artist.name == "Artist1"
    assert artist.country == "PL"

def test_artist_update_fields():
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
    artist = Artist(id=1, name="Old", country="PL")
    artist.name = "New"
    assert artist.name == "New"

def test_track_remove_artist():
    """
    Test sprawdzający usuwanie artysty z listy powiązanych artystów utworu.

    Scenariusz:
    1. Utworzenie utworu i dwóch artystów.
    2. Dodanie ich do utworu.
    3. Usunięcie jednego artysty.
    4. Weryfikacja, że pozostał tylko drugi.

    Cel:
    Upewnić się, że relacja Track - Artist działa poprawnie przy usuwaniu.
    """
    track = Track(id=1, title="T", duration=100)
    a1 = Artist(id=1, name="A1")
    a2 = Artist(id=2, name="A2")

    track.artists.append(a1)
    track.artists.append(a2)

    track.artists.remove(a1)

    assert len(track.artists) == 1
    assert track.artists[0].name == "A2"
