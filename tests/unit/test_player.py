"""
Zestaw testów jednostkowych weryfikujących logikę modułu odtwarzacza audio
(`player`), który działa w oparciu o globalny stan. Testy sprawdzają
podstawowe operacje na stanie odtwarzacza, takie jak resetowanie,
sprawdzanie stanu STOPPED, obsługę flag zapętlania, pauzowanie oraz
uruchamianie odtwarzania z kolejki.

Testy obejmują:
- resetowanie pełnego stanu odtwarzacza,
- sprawdzanie, czy odtwarzacz jest zatrzymany,
- wyłączanie trybów zapętlania,
- ustawianie pauzy,
- wznawianie odtwarzania,
- automatyczne pobieranie utworu z kolejki przy starcie odtwarzania.

Celem testów jest potwierdzenie, że logika zarządzania stanem działa
poprawnie w izolacji, bez udziału WebSocketów, FastAPI ani bazy danych.
"""
import app.player as player
from app.models import Track

def test_reset_clears_state():
    """
        Test sprawdzający, czy funkcja reset() poprawnie czyści cały stan
        odtwarzacza.
        Scenariusz:
        1. Ustawienie przykładowych wartości globalnych (kolejka, current,
           elapsed, tryby loop, tryb playlisty, pauza).
        2. Wywołanie reset().
        3. Weryfikacja, że wszystkie pola wróciły do wartości początkowych.
        Cel:
        Upewnić się, że reset() przywraca odtwarzacz do stanu początkowego.
    """
    dummy_track = Track(id=1, title="track1", duration=180)
    player.queue.append(dummy_track)
    player.current = "track"
    player.elapsed = 42
    player.loop_track = True
    player.loop_playlist = True
    player.playlist_mode = True
    player.playlist_tracks = ["t1", "t2"]
    player.playlist_index = 1
    player.is_paused = True

    player.reset()

    assert list(player.queue) == []
    assert player.current is None
    assert player.elapsed == 0
    assert player.loop_track is False
    assert player.loop_playlist is False
    assert player.playlist_mode is False
    assert player.playlist_tracks == []
    assert player.playlist_index == 0
    assert player.is_paused is False

def test_is_stopped_true_when_no_track():
    """
        Test sprawdzający, że is_stopped() zwraca True, gdy nie ma
        aktualnie odtwarzanego utworu.
        Cel:
        Potwierdzić poprawność wykrywania stanu STOPPED.
    """
    player.reset()
    assert player.is_stopped() is True

def test_is_stopped_false_when_track_active():
    """
        Test sprawdzający, że is_stopped() zwraca False, gdy current
        jest ustawiony.
        Cel:
        Upewnić się, że odtwarzacz poprawnie rozpoznaje aktywny utwór.
    """
    player.reset()
    player.current = "track"
    assert player.is_stopped() is False

def test_reset_loops_disables_both():
    """
        Test sprawdzający, czy reset_loops() wyłącza oba tryby zapętlania:
        loop_track oraz loop_playlist.
        Cel:
        Zweryfikować poprawność czyszczenia flag zapętlania.
    """
    player.loop_track = True
    player.loop_playlist = True
    player.reset_loops()
    assert player.loop_track is False
    assert player.loop_playlist is False

def test_stop_sets_pause_flag():
    """
        Test sprawdzający, czy stop() ustawia flagę pauzy, jeśli istnieje
        aktualnie odtwarzany utwór.
        Cel:
        Upewnić się, że pauza działa poprawnie.
    """
    player.reset()
    player.current = "track"
    player.stop()
    assert player.is_paused is True

def test_play_resumes_if_current_exists():
    """
        Test sprawdzający, że play() wznawia odtwarzanie, jeśli current
        jest ustawiony i odtwarzacz był wstrzymany.
        Cel:
        Zweryfikować poprawność wznawiania odtwarzania.
    """
    player.reset()
    player.current = "track"
    player.is_paused = True
    result = player.play()
    assert result == "track"
    assert player.is_paused is False

def test_play_starts_from_queue():
    """
        Test sprawdzający, że play() pobiera pierwszy utwór z kolejki,
        jeśli current jest None.
        Scenariusz:
        1. Reset odtwarzacza.
        2. Dodanie utworu do kolejki.
        3. Wywołanie play().
        4. Oczekiwane: current ustawiony na pierwszy element kolejki.
        Cel:
        Upewnić się, że odtwarzacz poprawnie startuje odtwarzanie z kolejki.
    """
    player.reset()
    dummy = Track(id=1, title="track1", duration=180)
    player.queue.append(dummy)

    result = player.play()

    assert result == dummy
    assert player.current == dummy

