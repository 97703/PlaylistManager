"""
Testy jednostkowe modelu Album.
Sprawdzają poprawność tworzenia albumu, powiązania z artystą
oraz dodawania utworów.
"""
from app.models import Album, Artist, Track

def test_album_creation():
    """
        Test sprawdzający poprawność tworzenia obiektu Album.
        Scenariusz:
        1. Utworzenie artysty.
        2. Utworzenie albumu i przypisanie go do artysty.
        3. Weryfikacja, że pola title oraz artist zostały poprawnie ustawione.
        Cel:
        Upewnić się, że model Album poprawnie przechowuje dane podstawowe
        oraz relację z obiektem Artist.
    """
    artist = Artist(id=1, name="A")
    album = Album(id=1, title="Album1", artist=artist)
    assert album.title == "Album1"
    assert album.artist == artist

def test_album_add_track():
    """
        Test sprawdzający możliwość dodawania utworów do albumu.
        Scenariusz:
        1. Utworzenie albumu.
        2. Utworzenie utworu.
        3. Dodanie utworu do listy tracks albumu.
        4. Weryfikacja, że utwór został poprawnie dodany.
        Cel:
        Zweryfikować, że relacja Album → Track działa poprawnie
        i że album może przechowywać wiele utworów.
    """
    album = Album(id=1, title="A")
    track = Track(id=1, title="T", duration=100)
    album.tracks.append(track)
    assert len(album.tracks) == 1
    assert album.tracks[0].title == "T"
