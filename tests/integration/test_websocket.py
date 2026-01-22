"""
Zestaw testów integracyjnych weryfikujących działanie WebSocketowego
odtwarzacza muzyki (`player`). Testy symulują pełny cykl pracy odtwarzacza:
kolejkowanie utworów, odtwarzanie, pauzowanie, przewijanie, pętle,
obsługę playlist i albumów oraz automatyczne przełączanie utworów.

Każdy test otwiera połączenie WebSocket z endpointem `/ws` i komunikuje się
z odtwarzaczem poprzez wysyłanie komend JSON. Odtwarzacz zwraca cykliczne
aktualizacje stanu, które są odbierane i analizowane w testach.

Testy obejmują:
- stan początkowy odtwarzacza,
- dodawanie utworów do kolejki,
- automatyczne odtwarzanie,
- odliczanie czasu (tick),
- pętle utworu i playlisty,
- obsługę playlist i albumów,
- pauzowanie i wznawianie,
- pomijanie utworów (skip),
- przełączanie między utworami i listami.
"""
from app import player

def test_websocket_player(client):
    """
    Test sprawdzający, czy po nawiązaniu połączenia WebSocket odtwarzacz
    zwraca podstawowe informacje o stanie, takie jak `status` i `time`.

    Cel:
    Zweryfikować, że endpoint `/ws` działa i odtwarzacz wysyła poprawny
    pakiet inicjalizacyjny.
    """
    with client.websocket_connect("/ws") as ws:
        data = ws.receive_json()
        assert "status" in data
        assert "time" in data

def ws_recv(ws):
    """
    Helper: odbiera jedną wiadomość JSON.
    """
    return ws.receive_json()

def test_initial_state_no_loop(client):
    """
    Test sprawdzający stan początkowy odtwarzacza.

    Scenariusz:
    1. Po połączeniu odtwarzacz powinien być w stanie STOPPED.
    2. Próba włączenia loop_track lub loop_playlist powinna zostać odrzucona,
       ponieważ nie ma aktywnego odtwarzania.

    Cel:
    Zweryfikować, że odtwarzacz nie pozwala na aktywację pętli,
    gdy nie odtwarza żadnego utworu.
    """
    with client.websocket_connect("/ws") as ws:
        data = ws_recv(ws)
        assert data["status"] == "STOPPED"

        ws.send_json({"command": "loop_track", "payload": True})
        data = ws_recv(ws)
        assert data["loop_track"] is False

        ws.send_json({"command": "loop_playlist", "payload": True})
        data = ws_recv(ws)
        assert data["loop_playlist"] is False

def test_add_track_starts_playback(client, track):
    """
    Test sprawdzający, czy dodanie utworu do kolejki automatycznie
    rozpoczyna odtwarzanie.

    Scenariusz:
    1. Reset odtwarzacza.
    2. Dodanie utworu do kolejki.
    3. Odtwarzacz powinien przejść w stan PLAYING.
    4. Powinien zwrócić tytuł utworu oraz elapsed = 1.

    Cel:
    Zweryfikować, że kolejka działa poprawnie i automatycznie
    uruchamia odtwarzanie.
    """
    player.reset()
    with client.websocket_connect("/ws") as ws:
        ws_recv(ws)

        ws.send_json({"command": "queue_add", "payload": {"track": track.id}})
        data = ws_recv(ws)

        assert data["status"] == "PLAYING"
        assert data["track"] == track.title
        assert data["elapsed"] == 1

def test_tick_until_end_stops(client, track):
    """
    Test sprawdzający, czy odtwarzacz odlicza czas aż do końca utworu,
    a następnie przechodzi w stan STOPPED.

    Scenariusz:
    1. Dodanie utworu do kolejki.
    2. Odbieranie kolejnych ticków aż do przekroczenia czasu trwania utworu.
    3. Odtwarzacz powinien zatrzymać się i wyczyścić aktualny utwór.

    Cel:
    Zweryfikować poprawność mechanizmu tick() oraz zakończenia odtwarzania.
    """
    with client.websocket_connect("/ws") as ws:
        ws_recv(ws)

        ws.send_json({"command": "queue_add", "payload": {"track": track.id}})
        ws_recv(ws)

        for _ in range(track.duration + 1):
            data = ws_recv(ws)

        assert data["status"] == "STOPPED"
        assert data["track"] is None

def test_loop_track(client, track):
    """
    Test sprawdzający działanie pętli pojedynczego utworu (loop_track).

    Scenariusz:
    1. Dodanie utworu do kolejki.
    2. Włączenie pętli utworu.
    3. Po zakończeniu utworu odtwarzacz powinien rozpocząć go od nowa
       (elapsed = 0).

    Cel:
    Zweryfikować, że loop_track działa poprawnie i restartuje utwór.
    """
    with client.websocket_connect("/ws") as ws:
        ws_recv(ws)

        ws.send_json({"command": "queue_add", "payload": {"track": track.id}})
        ws_recv(ws)

        ws.send_json({"command": "loop_track", "payload": True})
        ws_recv(ws)

        for _ in range(track.duration - 2):
            data = ws_recv(ws)

        assert data["track"] == track.title
        assert data["elapsed"] == 0

def test_two_tracks_queue(client, track, track2):
    """
    Test sprawdzający przełączanie między utworami w kolejce.

    Scenariusz:
    1. Dodanie dwóch utworów do kolejki.
    2. Po zakończeniu pierwszego odtwarzacz powinien automatycznie
       przejść do drugiego.

    Cel:
    Zweryfikować poprawność obsługi kolejki wielu utworów.
    """
    with client.websocket_connect("/ws") as ws:
        ws_recv(ws)

        ws.send_json({"command": "queue_add", "payload": {"track": track.id}})
        ws_recv(ws)

        ws.send_json({"command": "queue_add", "payload": {"track": track2.id}})
        ws_recv(ws)

        for _ in range(track.duration + 1):
            data = ws_recv(ws)

        assert data["track"] == track2.title

def test_playlist_loop(client, playlist):
    """
    Test sprawdzający odtwarzanie playlisty z włączoną pętlą.

    Scenariusz:
    1. Wybranie playlisty po ID z parametrem loop=True.
    2. Odtwarzacz powinien odtworzyć wszystkie utwory po kolei.
    3. Po zakończeniu ostatniego powinien wrócić do pierwszego.

    Cel:
    Zweryfikować, że playlista działa jak kolejka oraz że pętla playlisty
    działa poprawnie.
    """
    with client.websocket_connect("/ws") as ws:
        ws_recv(ws)

        ws.send_json({
            "command": "playlist_select_id",
            "payload": {"id": playlist.id, "loop": True}
        })
        data = ws_recv(ws)

        first = playlist.tracks[0].title

        for t in playlist.tracks:
            for _ in range(t.duration):
                data = ws_recv(ws)

        assert data["track"] == first

def test_pause_and_resume(client, track):
    """
    Test sprawdzający działanie pauzy i wznawiania odtwarzania.

    Scenariusz:
    1. Dodanie utworu do kolejki.
    2. Wysłanie komendy "pause" - status powinien być PAUSED.
    3. Kolejny tick nie powinien zwiększać elapsed.
    4. Wysłanie komendy "play" - odtwarzanie powinno zostać wznowione.
    5. elapsed powinien ponownie rosnąć.

    Cel:
    Zweryfikować poprawność mechanizmu pauzy i wznowienia.
    """
    with client.websocket_connect("/ws") as ws:
        ws_recv(ws)

        ws.send_json({"command": "queue_add", "payload": {"track": track.id}})
        ws_recv(ws)

        ws.send_json({"command": "pause"})
        data = ws_recv(ws)
        assert data["status"] == "PAUSED"

        elapsed_before = data["elapsed"]

        data = ws_recv(ws)
        assert data["elapsed"] == elapsed_before

        ws.send_json({"command": "play"})
        data = ws_recv(ws)
        assert data["status"] == "PLAYING"

        data = ws_recv(ws)
        assert data["elapsed"] == elapsed_before + 2

def test_skip(client, track, track2):
    """
    Test sprawdzający działanie komendy "skip".

    Scenariusz:
    1. Dodanie dwóch utworów do kolejki.
    2. Wysłanie komendy "skip".
    3. Odtwarzacz powinien natychmiast przejść do drugiego utworu.

    Cel:
    Zweryfikować poprawność pomijania utworów.
    """
    with client.websocket_connect("/ws") as ws:
        ws_recv(ws)

        ws.send_json({"command": "queue_add", "payload": {"track": track.id}})
        ws_recv(ws)

        ws.send_json({"command": "queue_add", "payload": {"track": track2.id}})
        ws_recv(ws)

        ws.send_json({"command": "skip"})
        data = ws_recv(ws)

        assert data["track"] == track2.title

def test_album_selection(client, album, track, track2):
    """
    Test sprawdzający odtwarzanie albumu po ID.

    Scenariusz:
    1. Wybranie albumu po ID.
    2. Odtwarzacz powinien odtworzyć wszystkie utwory albumu po kolei.
    3. Po zakończeniu ostatniego powinien przejść w stan STOPPED.

    Cel:
    Zweryfikować, że album działa jak playlista bez pętli.
    """
    with client.websocket_connect("/ws") as ws:
        ws_recv(ws)

        ws.send_json({
            "command": "album_select_id",
            "payload": {"id": album.id, "loop": False}
        })
        data = ws_recv(ws)

        assert data["track"] == album.tracks[0].title

        for t in album.tracks:
            for _ in range(t.duration):
                data = ws_recv(ws)

        assert data["status"] == "STOPPED"

def test_album_loop(client, album, track, track2):
    """
    Test sprawdzający odtwarzanie albumu w pętli.

    Scenariusz:
    1. Wybranie albumu po ID z parametrem loop=True.
    2. Odtwarzacz powinien odtworzyć wszystkie utwory albumu.
    3. Po zakończeniu ostatniego powinien wrócić do pierwszego.

    Cel:
    Zweryfikować poprawność pętli albumu.
    """
    with client.websocket_connect("/ws") as ws:
        ws_recv(ws)

        ws.send_json({
            "command": "album_select_id",
            "payload": {"id": album.id, "loop": True}
        })
        data = ws_recv(ws)

        first = album.tracks[0].title

        for t in album.tracks:
            for _ in range(t.duration):
                data = ws_recv(ws)

        assert data["track"] == first