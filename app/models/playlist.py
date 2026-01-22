"""
Model ORM reprezentujący playlistę muzyczną w bazie danych.
Tabela `playlists` przechowuje informacje o playlistach tworzonych przez
użytkowników. Każda playlista ma właściciela (użytkownika) oraz może zawierać
dowolną liczbę utworów poprzez relację many‑to‑many.

Pola:
id : int
    Klucz główny playlisty.
name : str
    Nazwa playlisty. Musi mieć od 1 do 100 znaków (walidowane przez CheckConstraint).
owner_id : int
    Klucz obcy wskazujący na użytkownika będącego właścicielem playlisty.
owner : User
    Relacja ORM do modelu User (wiele playlist - jeden użytkownik).
tracks : list[Track]
    Relacja many‑to‑many do modelu Track poprzez tabelę pośrednią `playlist_track`.

Ograniczenia:
playlist_name_length :
    Zapewnia, że nazwa playlisty ma długość od 1 do 100 znaków.

Relacje:
owner :
    relacja many‑to‑one — każda playlista ma jednego właściciela.
tracks :
    relacja many‑to‑many — playlista może zawierać wiele utworów,
    a utwór może znajdować się w wielu playlistach.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import CheckConstraint
from app.database import Base
from .associations import playlist_track

class Playlist(Base):
    __tablename__ = "playlists"

    __table_args__ = (
        CheckConstraint("length(name) >= 1 AND length(name) <= 100", name="playlist_name_length"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="playlists")

    tracks = relationship("Track", secondary=playlist_track)
