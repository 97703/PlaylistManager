"""
Model ORM reprezentujący artystę muzycznego w bazie danych.

Tabela `artists` przechowuje podstawowe informacje o artyście, takie jak jego
nazwa sceniczna oraz kraj pochodzenia. Model zawiera również ograniczenia
walidujące długość nazwy artysty.

Pola:
id : int
    Klucz główny artysty.
name : str
    Nazwa artysty. Musi mieć od 2 do 100 znaków (walidowane przez CheckConstraint).
country : str | None
    Kraj pochodzenia artysty. Pole opcjonalne, maksymalnie 50 znaków.

Ograniczenia:
artist_name_length :
    Zapewnia, że nazwa artysty ma długość od 2 do 100 znaków.

Relacje:
Relacje są definiowane w innych modelach (np. Track, Album), które mogą
odwoływać się do artysty poprzez klucze obce lub tabele asocjacyjne.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import CheckConstraint
from app.database import Base

class Artist(Base):
    __tablename__ = "artists"

    __table_args__ = (
        CheckConstraint("length(name) >= 2 AND length(name) <= 100", name="artist_name_length"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    country = Column(String(50))
