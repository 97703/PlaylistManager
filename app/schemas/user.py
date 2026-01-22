"""
Schematy Pydantic odpowiedzialne za walidację danych wejściowych i wyjściowych
związanych z rejestracją, logowaniem, aktualizacją oraz prezentacją danych użytkowników.

UserRegister:
    Używany podczas rejestracji nowego użytkownika. Waliduje login, e‑mail,
    hasło, dane osobowe oraz wiek użytkownika.
UserOut:
    Schemat wyjściowy używany do zwracania danych użytkownika w odpowiedziach API.
UserLogin:
    Schemat danych używany podczas logowania — wymaga loginu i hasła.
UserUpdate:
    Schemat danych używany do aktualizacji danych użytkownika. Wszystkie pola są opcjonalne.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Optional
from app.models import UserRole

class UserRegister(BaseModel):
    """
        Schemat danych używany do rejestracji nowego użytkownika.

        Pola:
        login : str
            Login użytkownika. Musi mieć od 3 do 30 znaków.
        email : EmailStr
            Adres e‑mail użytkownika. Musi być poprawnym adresem i mieć maks. 255 znaków.
        password : str
            Hasło użytkownika. Minimalna długość: 6 znaków.
        first_name : str | None
            Imię użytkownika. Pole opcjonalne, maksymalnie 50 znaków.
        last_name : str | None
            Nazwisko użytkownika. Pole opcjonalne, maksymalnie 50 znaków.
        birth_date : date | None
            Data urodzenia użytkownika. Walidowana pod kątem wieku i poprawności.
        role : UserRole | None
            Rola użytkownika w systemie. Domyślnie: UserRole.user.

        Walidacja:
        - login: min_length=3, max_length=30
        - email: poprawny format, max_length=255
        - password: min_length=6
        - first_name, last_name: max_length=50
        - birth_date: nie może być z przyszłości, użytkownik musi mieć ≥ 15 lat

        Dodatkowa walidacja:
        validate_birth_date:
            Sprawdza, czy użytkownik nie urodził się w przyszłości
            oraz czy ma co najmniej 15 lat.
    """
    login: str = Field(..., min_length=3, max_length=30)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=6)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    birth_date: date = Field(None)
    role: Optional[UserRole] = UserRole.user

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value):
        today = date.today()
        if value > today:
            raise ValueError("Birth date cannot be in the future")

        age = today.year - value.year - (
            (today.month, today.day) < (value.month, value.day)
        )
        if age < 15:
            raise ValueError("User must be at least 15 years old")

        return value

class UserOut(BaseModel):
    """
        Schemat danych wyjściowych używany do zwracania informacji o użytkowniku.
        Konfiguracja:
        from_attributes = True
            Pozwala na automatyczne tworzenie obiektu UserOut
            bezpośrednio z modelu ORM (SQLAlchemy).
    """
    id: int
    login: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    birth_date: Optional[date]
    role: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """
        Schemat danych używany podczas logowania użytkownika.

        Pola:
        login : str
            Login użytkownika. Musi mieć od 3 do 30 znaków.
        password : str
            Hasło użytkownika. Minimalna długość: 6 znaków.

        Walidacja:
        - login: min_length=3, max_length=30
        - password: min_length=6
    """
    login: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    """
        Schemat danych używany do aktualizacji danych użytkownika.

        Wszystkie pola są opcjonalne — aktualizowane są tylko te,
        które zostały przekazane (exclude_unset=True w CRUD).

        Pola:
        email : EmailStr | None
            Nowy adres e‑mail użytkownika. Maksymalnie 255 znaków.
        first_name : str | None
            Nowe imię użytkownika. Maksymalnie 50 znaków.
        last_name : str | None
            Nowe nazwisko użytkownika. Maksymalnie 50 znaków.

        Walidacja:
        - email: poprawny format, max_length=255
        - first_name, last_name: max_length=50
    """
    email: Optional[EmailStr] = Field(None, max_length=255)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
