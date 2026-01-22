"""
Model ORM reprezentujący album muzyczny w bazie danych.
Tabela `albums` przechowuje podstawowe informacje o albumach oraz ich powiązania
z artystami i utworami. Każdy album należy do jednego artysty, natomiast może
zawierać wiele utworów (relacja jeden‑do‑wielu).

Pola:
id : int
    Klucz główny albumu.
title : str
    Tytuł albumu. Ograniczony do 1–150 znaków (walidowane przez CheckConstraint).
release_date : date | None
    Data wydania albumu. Pole opcjonalne.
artist_id : int
    Klucz obcy wskazujący na artystę, do którego należy album.
artist : Artist
    Relacja ORM do modelu Artist (wiele albumów - jeden artysta).
tracks : list[Track]
    Relacja ORM do modelu Track (jeden album - wiele utworów).

Ograniczenia:
album_title_length :
    Zapewnia, że tytuł albumu ma długość od 1

Relacje:
artist :
    relacja many‑to‑one — każdy album ma jednego artystę.
tracks :
    relacja one‑to‑many — album może zawierać wiele utworów.
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import CheckConstraint
from app.database import Base

class Album(Base):
    __tablename__ = "albums"

    __table_args__ = (
        CheckConstraint("length(title) >= 1 AND length(title) <= 150", name="album_title_length"),
    )

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    release_date = Column(Date, nullable=True)

    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    artist = relationship("Artist")

    tracks = relationship("Track", back_populates="album")
