"""
Schematy Pydantic odpowiedzialne za walidację danych wejściowych
związanych z tworzeniem i aktualizacją albumów muzycznych.

AlbumCreate:
    Używany podczas tworzenia nowego albumu. Wymaga tytułu oraz ID artysty.
    Data wydania jest opcjonalna.

AlbumUpdate:
    Używany podczas aktualizacji istniejącego albumu. Wszystkie pola są opcjonalne,
    a aktualizowane są tylko te, które zostały przekazane przez użytkownika.
"""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class AlbumCreate(BaseModel):
    """
        Schemat danych używany do tworzenia nowego albumu.

        Pola:
        title : str
            Tytuł albumu. Musi mieć od 1 do 150 znaków.
        release_date : date | None
            Opcjonalna data wydania albumu.
        artist_id : int
            Identyfikator artysty, do którego należy album. Musi być większy od 0.

        Walidacja:
        - title: min_length=1, max_length=150
        - artist_id: gt=0
    """
    title: str = Field(..., min_length=1, max_length=150)
    release_date: Optional[date] = None
    artist_id: int = Field(..., gt=0)

class AlbumUpdate(BaseModel):
    """
        Schemat danych używany do aktualizacji istniejącego albumu.
        Wszystkie pola są opcjonalne — aktualizowane są tylko te,
        które zostały przekazane (exclude_unset=True w CRUD).
    """
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    release_date: Optional[str] = Field(None, max_length=50)
    artist_id: Optional[int] = Field(None, gt=0)