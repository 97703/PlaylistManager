"""
Moduł odpowiedzialny za logikę odtwarzacza audio wykorzystywanego przez WebSocket.

Zawiera:
- kolejkę odtwarzania,
- aktualny utwór,
- obsługę czasu odtwarzania,
- tryby pętli (loop track / loop playlist),
- tryb playlisty/albumu,
- funkcje sterujące (play, stop, skip, tick, select_*).

Moduł działa w trybie globalnego stanu – wszystkie funkcje operują na wspólnych
zmiennych globalnych, co pozwala na prostą integrację z WebSocketem.
"""
from collections import deque
from typing import Deque, Optional
from app.database import SessionLocal
from app.models import Track, Playlist, Album

# Kolejka utworów oczekujących na odtworzenie.
# FIFO – pierwszy dodany utwór zostanie odtworzony jako pierwszy.
queue: Deque[Track] = deque()
# Aktualnie odtwarzany utwór. None oznacza brak aktywnego odtwarzania.
current: Optional[Track] = None
# Liczba sekund od początku aktualnie odtwarzanego utworu.
elapsed: int = 0
# Flaga informująca, czy odtwarzanie jest wstrzymane.
is_paused: bool = False
# Czy aktualny utwór ma być zapętlany po zakończeniu.
loop_track: bool = False
# Czy cała playlista/album ma być zapętlany po zakończeniu.
loop_playlist: bool = False
# Czy odtwarzacz działa w trybie playlisty/albumu (True) czy kolejki (False).
playlist_mode: bool = False
# Lista utworów aktualnie wybranej playlisty lub albumu.
playlist_tracks: list[Track] = []
# Indeks aktualnie odtwarzanego utworu w playliście/albumie.
playlist_index: int = 0

def reset():
    """
        Resetuje stan odtwarzacza do wartości początkowych.

        Ustawia:
        - brak aktualnego utworu,
        - pustą kolejkę,
        - czas odtwarzania na 0,
        - wyłącza pauzę i tryby loop.
    """
    global queue, current, elapsed, loop_track, loop_playlist
    global playlist_mode, playlist_tracks, playlist_index, is_paused

    queue.clear()
    current = None
    elapsed = 0
    loop_track = False
    loop_playlist = False
    playlist_mode = False
    playlist_tracks = []
    playlist_index = 0
    is_paused = False

def is_stopped() -> bool:
    """
        Sprawdza, czy odtwarzacz jest zatrzymany.
        Zwraca:
            True jeśli nie ma aktualnie uruchomionego utworu, False w przeciwnym razie.
    """
    return current is None

def reset_loops():
    """
        Wyłącza oba tryby zapętlania:
        - loop_track,
        - loop_playlist.
    """
    global loop_track, loop_playlist
    loop_track = False
    loop_playlist = False

def add_to_queue(track_id: int) -> None:
    """
        Dodaje utwór do kolejki odtwarzania.
        Jeśli odtwarzacz jest zatrzymany, automatycznie rozpoczyna odtwarzanie.
        Parametry:
            track_id: ID utworu w bazie danych.
    """
    db = SessionLocal()
    track = db.get(Track, track_id)
    if not track:
        return

    queue.append(track)

    if current is None:
        play()

def remove_from_queue(track_id: int) -> bool:
    """
        Usuwa utwór z kolejki.
        Parametry:
            track_id: ID utworu do usunięcia.
        Zwraca:
            True jeśli utwór został usunięty, False jeśli nie znaleziono.
    """
    for t in list(queue):
        if t.id == track_id:
            queue.remove(t)
            return True
    return False

def get_queue():
    """
        Zwraca aktualną kolejkę odtwarzania jako listę Track.
        Zwraca:
            Lista utworów w kolejce.
    """
    return list(queue)

def play() -> Optional[Track]:
    """
        Wznawia odtwarzanie lub rozpoczyna odtwarzanie kolejnego utworu,
        jeśli aktualny jest pusty.
        Zwraca:
            Aktualny utwór lub None, jeśli nie ma co odtwarzać.
    """
    global is_paused

    if current is None:
        return next_track()

    is_paused = False
    return current

def stop() -> None:
    """
        Wstrzymuje odtwarzanie (pauza).
    """
    global is_paused
    if current is not None:
        is_paused = True

def skip() -> Optional[Track]:
    """
        Pomija aktualny utwór i przechodzi do następnego.
        Zwraca:
            Nowy aktualny utwór lub None, jeśli nie ma kolejnych.
    """
    return next_track()

def next_track() -> Optional[Track]:
    """
        Przechodzi do następnego utworu zgodnie z trybem odtwarzania:
        - jeśli aktywny jest tryb playlisty/albumu:
            przechodzi do kolejnego utworu w liście,
            a jeśli to:
                - restartuje playlistę jeśli loop_playlist=True,
                - zatrzymuje odtwarzanie jeśli loop_playlist=False.
        - jeśli aktywna jest kolejka:
            pobiera kolejny utwór z kolejki.
        - jeśli nie ma kolejnych utworów:
            zatrzymuje odtwarzanie.
        Zwraca:
            Nowy aktualny utwór lub None.
    """
    global current, elapsed, playlist_index, playlist_mode, is_paused

    elapsed = 0
    is_paused = False

    if playlist_mode:
        playlist_index += 1

        if playlist_index >= len(playlist_tracks):
            if loop_playlist:
                playlist_index = 0
            else:
                stop_all()
                return None

        current = playlist_tracks[playlist_index]
        return current

    if queue:
        current = queue.popleft()
        return current

    stop_all()
    return None

def stop_all():
    """
        Zatrzymuje odtwarzanie całkowicie:
        - czyści aktualny utwór,
        - resetuje czas,
        - wyłącza tryb playlisty,
        - wyłącza pauzę,
        - wyłącza tryby loop.
    """
    global current, elapsed, playlist_mode, is_paused
    current = None
    elapsed = 0
    playlist_mode = False
    is_paused = False
    reset_loops()

def tick() -> Optional[Track]:
    """
        Wykonuje pojedynczy krok czasowy (1 sekunda odtwarzania).
        Zwiększa elapsed, a jeśli utwór się kończy:
        - restartuje go (loop_track),
        - przechodzi do następnego (next_track),
        - zatrzymuje odtwarzanie jeśli nie ma kolejnych.
        Zwraca:
            Aktualny utwór lub None.
    """
    global elapsed

    if current is None or is_paused:
        return current

    elapsed += 1

    if elapsed < current.duration:
        return current

    if loop_track:
        elapsed = 0
        return current

    return next_track()

def select_track(track_id: int) -> Optional[Track]:
    """
        Ustawia wskazany utwór jako aktualny i rozpoczyna jego odtwarzanie.
        Wyłącza tryb playlisty i wszystkie tryby loop.
        Parametry:
            track_id: ID utworu.

        Zwraca:
            Wybrany utwór lub None jeśli nie istnieje.
    """
    global current, elapsed, playlist_mode, is_paused

    db = SessionLocal()
    track = db.get(Track, track_id)

    if not track:
        return None

    playlist_mode = False
    reset_loops()

    current = track
    elapsed = 0
    is_paused = False
    return current

def select_playlist_by_id(playlist_id: int, loop: bool = False):
    """
        Wybiera playlistę po ID i rozpoczyna jej odtwarzanie.
        Parametry:
            playlist_id: ID playlisty.
            loop: Czy zapętlać playlistę.
        Zwraca:
            Pierwszy utwór playlisty lub None.
    """
    db = SessionLocal()
    playlist = db.get(Playlist, playlist_id)

    if not playlist or not playlist.tracks:
        return None

    return _select_playlist(playlist.tracks, loop)

def select_playlist_by_name(name: str, loop: bool = False):
    """
        Wybiera playlistę po nazwie i rozpoczyna jej odtwarzanie.
        Parametry:
            name: Nazwa playlisty.
            loop: Czy zapętlać playlistę.

        Zwraca:
            Pierwszy utwór playlisty lub None.
    """
    db = SessionLocal()
    playlist = db.query(Playlist).filter_by(name=name).first()

    if not playlist or not playlist.tracks:
        return None

    return _select_playlist(playlist.tracks, loop)

def select_album_by_id(album_id: int, loop: bool = False):
    """
        Wybiera album po ID i rozpoczyna jego odtwarzanie.
        Album traktowany jest jak playlista:
        - playlist_mode = True
        - playlist_tracks = lista utworów albumu
        - playlist_index = 0
        Parametry:
            album_id: ID albumu.
            loop: Czy zapętlać album.
        Zwraca:
            Pierwszy utwór albumu lub None.
    """
    global playlist_mode, playlist_tracks, playlist_index
    global loop_playlist, loop_track, current, elapsed, queue

    db = SessionLocal()
    album = db.query(Album).get(album_id)
    if not album or not album.tracks:
        return None

    playlist_mode = True
    playlist_tracks = list(album.tracks)
    playlist_index = 0

    loop_playlist = loop
    loop_track = False

    queue.clear()
    current = playlist_tracks[0]
    elapsed = 0

    return current

def _select_playlist(tracks: list[Track], loop: bool):
    """
        Wewnętrzna funkcja ustawiająca tryb playlisty.
        Parametry:
            tracks: Lista utworów playlisty.
            loop: Czy zapętlać playlistę.
        Zwraca:
            Pierwszy utwór playlisty.
    """
    global playlist_mode, playlist_tracks, playlist_index
    global current, elapsed, loop_playlist, is_paused

    playlist_mode = True
    playlist_tracks = tracks
    playlist_index = 0
    loop_playlist = loop

    queue.clear()

    current = tracks[0]
    elapsed = 0
    is_paused = False
    return current

def set_loop_track(enabled: bool):
    """
        Włącza lub wyłącza zapętlanie aktualnego utworu.
        Jeśli włączone, automatycznie wyłącza loop_playlist.
        Parametry:
            enabled: True aby włączyć, False aby wyłączyć.
    """
    global loop_track, loop_playlist

    if current is None:
        return

    loop_track = enabled
    if enabled:
        loop_playlist = False


def set_loop_playlist(enabled: bool):
    """
        Włącza lub wyłącza zapętlanie playlisty/albumu.
        Działa tylko w trybie playlisty.
        Parametry:
            enabled: True aby włączyć, False aby wyłączyć.
    """
    global loop_playlist

    if not playlist_mode:
        return

    loop_playlist = enabled
