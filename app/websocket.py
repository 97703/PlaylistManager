"""
Endpoint WebSocket odpowiedzialny za dwukierunkową komunikację w czasie rzeczywistym
pomiędzy klientem a odtwarzaczem audio (moduł `player`).

Mechanizm działania:
Po nawiązaniu połączenia WebSocket wysyła do klienta aktualny stan odtwarzacza,
a następnie wchodzi w nieskończoną pętlę, w której:

1. Próbuje odebrać komendę JSON od klienta (z timeoutem 0.05 s).
2. Na podstawie pola "command" wywołuje odpowiednią funkcję w module `player`.
3. Wykonuje krok czasowy odtwarzacza (`player.tick()`), który:
   - zwiększa licznik czasu,
   - przełącza utwory,
   - obsługuje tryby loop.
4. Wysyła do klienta aktualny stan odtwarzacza (`send_status()`).
5. Czeka 1 sekundę, aby symulować upływ czasu odtwarzania.

Timeout pozwala na:
- płynne działanie tick() nawet bez komend od klienta,
- natychmiastową reakcję na komendy,
- brak blokowania pętli przy braku danych.

Obsługiwane komendy:
- play                 wznowienie odtwarzania lub start kolejnego utworu
- pause                pauza
- stop                 zatrzymanie i reset odtwarzania
- skip                 przejście do następnego utworu
- track_select         wybór pojedynczego utworu
- queue_add            dodanie utworu do kolejki
- queue_remove         usunięcie utworu z kolejki
- playlist_select_id   wybór playlisty po ID
- playlist_select_name wybór playlisty po nazwie
- album_select_id      wybór albumu po ID
- loop_track           włączenie/wyłączenie zapętlania utworu
- loop_playlist        włączenie/wyłączenie zapętlania playlisty/albumu

Wysyłany status zawiera:
- status: "PLAYING", "PAUSED" lub "STOPPED"
- track: tytuł aktualnego utworu lub None
- elapsed: liczba sekund od początku utworu
- duration: długość utworu
- queue: lista tytułów w kolejce
- loop_track: czy zapętlony jest utwór
- loop_playlist: czy zapętlona jest playlista/album
- time: aktualny timestamp ISO8601

Zachowanie przy błędach:
- Timeout - ignorowany (pozwala kontynuować pętlę)
- WebSocketDisconnect - przerwanie pętli i zakończenie połączenia
- Inne wyjątki - ignorowane, aby nie przerwać działania odtwarzacza

Endpoint działa dopóki klient nie zamknie połączenia.
"""
import asyncio
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from . import player

async def websocket_endpoint(ws: WebSocket):
    """
        Główny endpoint WebSocket obsługujący sterowanie odtwarzaczem audio.
        Parametry:
            ws: Obiekt WebSocket reprezentujący połączenie z klientem.
        Działanie:
            - Akceptuje połączenie WebSocket.
            - Wchodzi w pętlę, w której:
                * próbuje odebrać komendę JSON (z timeoutem 0.05 s),
                * wykonuje odpowiednią akcję w module `player`,
                * wykonuje krok czasowy odtwarzacza (`player.tick()`),
                * wysyła aktualny stan odtwarzacza do klienta,
                * czeka 1 sekundę, aby symulować upływ czasu.
            - Kończy działanie po rozłączeniu klienta.

        Obsługuje komendy:
            "play", "pause", "stop", "skip",
            "track_select", "queue_add", "queue_remove",
            "playlist_select_id", "playlist_select_name",
            "album_select_id",
            "loop_track", "loop_playlist".

        Wysyła do klienta:
            status odtwarzacza, aktualny utwór, czas, kolejkę,
            tryby loop oraz timestamp.
    """
    await ws.accept()

    async def send_status():
        """
            Wysyła do klienta aktualny stan odtwarzacza w formacie JSON.

            Zawiera:
                - status: PLAYING / PAUSED / STOPPED
                - track: tytuł aktualnego utworu lub None
                - elapsed: liczba sekund od początku utworu
                 - duration: długość aktualnego utworu
                - queue: lista tytułów w kolejce
                - loop_track: czy zapętlony jest utwór
                - loop_playlist: czy zapętlona jest playlista/album
                 - time: aktualny timestamp
        """
        await ws.send_json({
            "status": (
                "PAUSED"
                if player.current and player.is_paused
                else "PLAYING"
                if player.current
                else "STOPPED"
            ),
            "track": player.current.title if player.current else None,
            "elapsed": player.elapsed,
            "duration": player.current.duration if player.current else None,
            "queue": [t.title for t in player.get_queue()],
            "loop_track": player.loop_track,
            "loop_playlist": player.loop_playlist,
            "time": datetime.now().isoformat()
        })

    try:
        while True:
            try:
                data = await asyncio.wait_for(ws.receive_json(), timeout=0.05)
                command = data.get("command")
                payload = data.get("payload", {})
                if command == "play":
                    player.play()
                elif command == "pause":
                    player.stop()
                elif command == "stop":
                    player.stop_all()
                elif command == "skip":
                    player.skip()
                elif command == "track_select":
                    player.select_track(payload["id"])
                elif command == "queue_add":
                    player.add_to_queue(payload["track"])
                elif command == "queue_remove":
                    player.remove_from_queue(payload["id"])
                elif command == "playlist_select_id":
                    player.select_playlist_by_id(
                        playlist_id=payload["id"],
                        loop=payload.get("loop", False)
                    )
                elif command == "playlist_select_name":
                    player.select_playlist_by_name(
                        name=payload["name"],
                        loop=payload.get("loop", False)
                    )
                elif command == "album_select_id":
                    player.select_album_by_id(
                        album_id=payload["id"],
                        loop=payload.get("loop", False)
                    )
                elif command == "loop_track":
                    player.set_loop_track(bool(payload))
                elif command == "loop_playlist":
                    player.set_loop_playlist(bool(payload))

            except asyncio.TimeoutError:
                pass
            except WebSocketDisconnect:
                break
            except Exception:
                pass

            player.tick()
            await send_status()
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
