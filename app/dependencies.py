"""
Moduł odpowiedzialny za uwierzytelnianie i autoryzację użytkowników w aplikacji.
Zawiera dwie główne zależności FastAPI:
1. get_current_user
   - pobiera identyfikator użytkownika z ciasteczka `session_id`,
   - weryfikuje ważność sesji,
   - pobiera użytkownika z bazy danych,
   - zwraca obiekt User lub zgłasza błąd HTTP 401.
2. admin_required
   - rozszerza get_current_user,
   - sprawdza, czy użytkownik ma rolę administratora,
   - w przeciwnym razie zgłasza błąd HTTP 403.
Mechanizm ten pozwala na łatwe zabezpieczanie endpointów FastAPI
poprzez dodanie Depends(get_current_user) lub Depends(admin_required).
"""
from fastapi import Depends, Cookie, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .session import get_user_id
from .models import User

def get_current_user(
    session_id: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> type[User]:
    """
        Zwraca aktualnie zalogowanego użytkownika na podstawie ciasteczka sesji.
        Mechanizm działania:
        1. Pobiera wartość ciasteczka `session_id` z żądania HTTP.
        2. Funkcja `get_user_id()` sprawdza:
            - czy sesja istnieje,
            - czy nie wygasła,
            - czy jest poprawna.
        3. Jeśli sesja jest nieprawidłowa - HTTP 401 "Not authenticated".
        4. Jeśli sesja jest poprawna:
            - pobiera użytkownika z bazy danych,
            - jeśli użytkownik nie istnieje - HTTP 401 "Invalid session".
        5. Zwraca obiekt User.
        Parametry:
            session_id: Identyfikator sesji pobrany z ciasteczka (lub None).
            db: Sesja bazy danych wstrzyknięta przez FastAPI.
        Zwraca:
            Obiekt User reprezentujący aktualnie zalogowanego użytkownika.
        Wyjątki:
            HTTPException(401): gdy sesja jest nieprawidłowa lub wygasła.
        """
    user_id = get_user_id(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    return user

def admin_required(user: User = Depends(get_current_user)):
    """
        Wymaga, aby aktualnie zalogowany użytkownik posiadał rolę administratora.
        Funkcja działa jako dodatkowa warstwa autoryzacji:
        - najpierw wywoływana jest zależność get_current_user,
        - następnie sprawdzana jest rola użytkownika,
        - jeśli rola ≠ "admin" - zgłaszany jest błąd HTTP 403.
        Parametry:
            user: Obiekt User pobrany automatycznie przez FastAPI.
        Zwraca:
            Obiekt User, jeśli użytkownik ma rolę administratora.
        Wyjątki:
            HTTPException(403): jeśli użytkownik nie jest administratorem.
    """
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user