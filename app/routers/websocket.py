"""
Router odpowiedzialny za obsługę połączeń WebSocket w aplikacji.

Udostępnia jeden endpoint WebSocket, który deleguje obsługę komunikacji
do funkcji `websocket_endpoint` znajdującej się w module `app.websocket`.

Mechanizm WebSocket umożliwia dwukierunkową komunikację w czasie rzeczywistym,
"""
from fastapi import APIRouter, WebSocket
from app import websocket

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws")
async def ws(socket: WebSocket):
    """
        Obsługuje połączenie WebSocket pod adresem `/ws`.
        Mechanizm:
        - akceptuje połączenie WebSocket od klienta,
        - przekazuje obiekt WebSocket do funkcji `websocket_endpoint`,
          która realizuje właściwą logikę komunikacji,
        - umożliwia dwukierunkową wymianę danych w czasie rzeczywistym.
        Parametry:
            socket: Obiekt WebSocket reprezentujący aktywne połączenie z klientem.
        Zwraca:
            Brak wartości zwracanej — funkcja działa asynchronicznie,
            utrzymując połączenie WebSocket do momentu jego zamknięcia.
    """
    await websocket.websocket_endpoint(socket)