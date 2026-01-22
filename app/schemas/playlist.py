"""
Schematy Pydantic odpowiedzialne za walidację danych wejściowych i wyjściowych
związanych z tworzeniem, aktualizacją oraz prezentacją playlist.

PlaylistCreate:
    Używany podczas tworzenia nowej playlisty. Wymaga nazwy oraz ID właściciela.
PlaylistUpdate:
    Używany podczas aktualizacji istniejącej playlisty. Wszystkie pola są opcjonalne,
    a aktualizowane są tylko te, które zostały przekazane.
PlaylistOut:
    Schemat wyjściowy używany do zwracania danych playlisty w odpowiedziach API.
    Zawiera listę identyfikatorów utworów oraz wspiera konwersję z modeli ORM.
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class PlaylistCreate(BaseModel):
    """
        Schemat danych używany do tworzenia nowej playlisty.

        Pola:
        name : str
            Nazwa playlisty. Musi mieć od 1 do 100 znaków.
        owner_id : int
            Identyfikator użytkownika będącego właścicielem playlisty.
            Musi być większy od 0.

        Walidacja:
        - name: min_length=1, max_length=100
        - owner_id: gt=0
    """
    name: str = Field(..., min_length=1, max_length=100)
    owner_id: int = Field(..., gt=0)

class PlaylistUpdate(BaseModel):
    """
        Schemat danych używany do aktualizacji istniejącej playlisty.

        Wszystkie pola są opcjonalne — aktualizowane są tylko te,
        które zostały przekazane (exclude_unset=True w CRUD).

        Pola:
        name : str | None
            Nowa nazwa playlisty. Musi mieć od 1 do 100 znaków.
        owner_id : int | None
            Nowy identyfikator właściciela playlisty. Musi być większy od 0.

        Walidacja:
        - name: min_length=1, max_length=100
        - owner_id: gt=0
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    owner_id: Optional[int] = Field(None, gt=0)

class PlaylistOut(BaseModel):
    """
        Schemat danych wyjściowych używany do zwracania informacji o playliście.
        Konfiguracja:
        from_attributes = True
            Pozwala na automatyczne tworzenie obiektu PlaylistOut
            bezpośrednio z modelu ORM (SQLAlchemy).
    """
    id: int
    name: str
    owner_id: int
    track_ids: List[int] = []

    class Config:
        from_attributes = True
