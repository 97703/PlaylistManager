"""
Model ORM reprezentujący utwór muzyczny (track) w bazie danych.
Tabela `tracks` przechowuje informacje o pojedynczych utworach, takich jak
tytuł, czas trwania oraz powiązania z albumami i artystami. Model zawiera
ograniczenia walidujące poprawność danych oraz relacje do innych tabel.

Pola:
id : int
    Klucz główny utworu.
title : str
    Tytuł utworu. Musi mieć od 1 do 200 znaków (walidowane przez CheckConstraint).
duration : int
    Czas trwania utworu w sekundach. Musi być większy od 0 i mniejszy niż 86400.
album_id : int | None
    Klucz obcy wskazujący na album, do którego należy utwór. Pole opcjonalne.
album : Album | None
    Relacja ORM do modelu Album (wiele utworów - jeden album).
artists : list[Artist]
    Relacja many‑to‑many do modelu Artist poprzez tabelę pośrednią `track_artist`.

Ograniczenia:
duration_range :
    Zapewnia, że czas trwania utworu mieści się w zakresie 1–86399 sekund.
track_title_length :
    Zapewnia, że tytuł utworu ma długość od 1 do 200 znaków.

Relacje:
album :
    relacja many‑to‑one — utwór może należeć do jednego albumu.
artists :
    relacja many‑to‑many — utwór może mieć wielu artystów,
    a artysta może być powiązany z wieloma utworami.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import CheckConstraint
from app.database import Base
from .associations import track_artist

class Track(Base):
    __tablename__ = "tracks"

    __table_args__ = (
        CheckConstraint("duration > 0 AND duration < 86400", name="duration_range"),
        CheckConstraint("length(title) >= 1 AND length(title) <= 200", name="track_title_length"),
    )

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    duration = Column(Integer, nullable=False)

    file_path = Column(String, nullable=True)

    album_id = Column(Integer, ForeignKey("albums.id"))
    album = relationship("Album", back_populates="tracks")

    artists = relationship("Artist", secondary=track_artist)
