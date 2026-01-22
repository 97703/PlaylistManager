"""
Model ORM reprezentujący użytkownika systemu.
Tabela `users` przechowuje dane kont użytkowników, w tym informacje
logowania, dane osobowe oraz rolę użytkownika w systemie. Model zawiera
ograniczenia walidujące długość loginu oraz minimalną długość hasła
(hasło jest przechowywane w formie zahashowanej).

Enum:
UserRole :
    Określa rolę użytkownika w systemie. Dostępne wartości:
    - "admin" — użytkownik z uprawnieniami administracyjnymi,
    - "user" — zwykły użytkownik.

Pola:
id : int
    Klucz główny użytkownika.
login : str
    Login użytkownika. Musi mieć od 3 do 30 znaków i być unikalny.
email : str
    Adres e‑mail użytkownika. Musi być unikalny.
password : str
    Zahashowane hasło użytkownika. Minimalna długość 60 znaków (hash bcrypt).
first_name : str | None
    Imię użytkownika. Pole opcjonalne.
last_name : str | None
    Nazwisko użytkownika. Pole opcjonalne.
birth_date : date | None
    Data urodzenia użytkownika. Pole opcjonalne.
role : UserRole
    Rola użytkownika w systemie. Domyślnie "user".

Relacje:
playlists :
    relacja one‑to‑many — użytkownik może posiadać wiele playlist.
    Powiązanie z modelem Playlist poprzez `owner` (back_populates).
"""
import enum
from sqlalchemy import Column, Integer, String, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import CheckConstraint
from app.database import Base

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint("length(login) >= 3 AND length(login) <= 30", name="login_length"),
        CheckConstraint("length(password) >= 60", name="password_hash_length"),
    )

    id = Column(Integer, primary_key=True)
    login = Column(String(30), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    birth_date = Column(Date, nullable=False)

    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)

    playlists = relationship("Playlist", back_populates="owner")
