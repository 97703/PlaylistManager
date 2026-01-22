"""
Router odpowiedzialny za obsługę mechanizmów uwierzytelniania użytkowników.

Udostępnia trzy główne operacje:
- rejestrację nowego użytkownika,
- logowanie użytkownika i tworzenie sesji,
- wylogowanie użytkownika i usuwanie sesji.

Mechanizm sesji oparty jest na ciasteczku `session_id`, które przechowuje
identyfikator aktywnej sesji użytkownika. Router wykorzystuje warstwę CRUD
do operacji na użytkownikach oraz walidację danych poprzez schematy Pydantic.
"""
from fastapi import APIRouter, Depends, Response, Cookie, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.session import create_session, delete_session

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    """
        Rejestruje nowego użytkownika w systemie.
        Mechanizm:
        - sprawdza, czy login nie jest już zajęty,
        - sprawdza, czy adres e‑mail nie jest już zarejestrowany,
        - wywołuje funkcję CRUD odpowiedzialną za utworzenie użytkownika,
        - obsługuje wyjątek IntegrityError (np. konflikt unikalności),
        - zwraca dane nowo utworzonego użytkownika.
        Parametry:
            user: Dane rejestracyjne użytkownika (login, email, hasło, dane osobowe).
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Obiekt UserOut zawierający dane nowo utworzonego użytkownika.
        Wyjątki:
            HTTPException 400: jeśli login lub email są już zajęte.
    """
    existing_login = db.query(models.User).filter_by(login=user.login).first()
    if existing_login:
        raise HTTPException(status_code=400, detail="Login already registered")

    existing_email = db.query(models.User).filter_by(email=user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        new_user = crud.register_user(db, user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email or login already registered")

    return schemas.UserOut(
        id=new_user.id,
        login=new_user.login,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        birth_date=new_user.birth_date,
        role=new_user.role
    )

@router.post("/login")
def login(data: schemas.UserLogin, response: Response, db: Session = Depends(get_db)):
    """
        Loguje użytkownika i tworzy nową sesję.
        Mechanizm:
        - weryfikuje login i hasło użytkownika,
        - jeśli dane są poprawne, generuje identyfikator sesji,
        - zapisuje identyfikator sesji w ciasteczku HTTP-only,
        - ciasteczko ma ograniczony czas życia (max_age=180 sekund).
        Parametry:
            data: Dane logowania (login i hasło).
            response: Obiekt odpowiedzi HTTP, używany do ustawienia ciasteczka.
            db: Sesja bazy danych SQLAlchemy.
        Zwraca:
            Słownik z komunikatem o poprawnym logowaniu.
        Wyjątki:
            HTTPException 401: jeśli login lub hasło są niepoprawne.
    """
    user = crud.authenticate_user(db, data.login, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid login or password")

    session_id = create_session(user.id)

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=180,
        samesite="lax",
    )

    return {"message": "Logged in successfully"}

@router.post("/logout")
def logout(response: Response, session_id: str | None = Cookie(default=None)):
    """
        Wylogowuje użytkownika poprzez usunięcie aktywnej sesji.
        Mechanizm:
        - usuwa sesję z pamięci serwera,
        - usuwa ciasteczko `session_id` z przeglądarki użytkownika.
        Parametry:
            response: Obiekt odpowiedzi HTTP, używany do usunięcia ciasteczka.
            session_id: Identyfikator sesji pobrany z ciasteczka.
        Zwraca:
            Słownik z komunikatem o poprawnym wylogowaniu.
    """
    delete_session(session_id)
    response.delete_cookie("session_id")
    return {"message": "Logged out"}
