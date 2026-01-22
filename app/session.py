"""
Moduł implementujący prosty mechanizm sesji użytkowników oparty na pamięci RAM.

Sesje są przechowywane w słowniku `_sessions`, gdzie kluczem jest identyfikator
sesji (UUID), a wartością krotka `(user_id, expires_at)`:

- `user_id` — identyfikator użytkownika powiązanego z sesją,
- `expires_at` — znacznik czasu (timestamp), po którego przekroczeniu sesja wygasa.

Mechanizm działa w pełni w pamięci, bez bazy danych, i jest przeznaczony do
prostych zastosowań, testów lub środowisk jednoużytkownikowych.

Cechy systemu:
- sesje mają ograniczony czas życia (TTL),
- każdorazowe odczytanie sesji przedłuża jej ważność,
- wygasłe sesje są automatycznie usuwane,
- sesje można usuwać ręcznie.

Zmienne globalne:
_sessions: Dict[str, Tuple[int, float]]
    Słownik przechowujący aktywne sesje.

SESSION_TTL: int
    Czas życia sesji w sekundach (domyślnie 3 minuty).
"""
import uuid
import time
from typing import Dict, Tuple

_sessions: Dict[str, Tuple[int, float]] = {}

SESSION_TTL = 3 * 60

def create_session(user_id: int) -> str:
    """
        Tworzy nową sesję użytkownika.
        Generuje losowy identyfikator sesji (UUID), oblicza czas wygaśnięcia
        i zapisuje sesję w pamięci.
        Parametry:
            user_id: Identyfikator użytkownika, dla którego tworzona jest sesja.
        Zwraca:
            Identyfikator sesji jako string (UUID).
    """
    session_id = str(uuid.uuid4())
    expires_at = time.time() + SESSION_TTL
    _sessions[session_id] = (user_id, expires_at)
    return session_id

def get_user_id(session_id: str | None) -> int | None:
    """
        Pobiera identyfikator użytkownika powiązanego z daną sesją.
        Funkcja:
        - zwraca None, jeśli sesja nie istnieje lub wygasła,
        - automatycznie usuwa wygasłe sesje,
        - przedłuża ważność aktywnej sesji o kolejne SESSION_TTL sekund.
        Parametry:
            session_id: Identyfikator sesji (UUID) lub None.
        Zwraca:
            Id użytkownika lub None, jeśli sesja jest nieprawidłowa lub wygasła.
    """
    if not session_id:
        return None

    data = _sessions.get(session_id)
    if not data:
        return None

    user_id, expires_at = data

    if time.time() > expires_at:
        del _sessions[session_id]
        return None

    _sessions[session_id] = (user_id, time.time() + SESSION_TTL)
    return user_id

def delete_session(session_id: str | None) -> None:
    """
        Usuwa sesję z pamięci, jeśli istnieje.
        Parametry:
            session_id: Identyfikator sesji do usunięcia.
    """
    if session_id in _sessions:
        del _sessions[session_id]