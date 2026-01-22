"""
Schematy Pydantic odpowiedzialne za walidację danych wejściowych i wyjściowych
związanych z tworzeniem, aktualizacją oraz prezentacją danych artystów.

ArtistCreate:
    Używany podczas tworzenia nowego artysty. Wymaga nazwy artysty,
    opcjonalnie przyjmuje kraj pochodzenia.
ArtistUpdate:
    Używany podczas aktualizacji istniejącego artysty. Wszystkie pola są opcjonalne,
    a aktualizowane są tylko te, które zostały przekazane.
ArtistOut:
    Schemat wyjściowy używany do zwracania danych artysty w odpowiedziach API.
    Wspiera konwersję z modeli ORM dzięki `from_attributes = True`.
"""
from pydantic import BaseModel, Field
from typing import Optional

class ArtistCreate(BaseModel):
    """
        Schemat danych używany do tworzenia nowego artysty.

        Pola:
        name : str
            Nazwa artysty. Musi mieć od 2 do 100 znaków.
        country : str | None
            Kraj pochodzenia artysty. Pole opcjonalne, maksymalnie 50 znaków.

        Walidacja:
        - name: min_length=2, max_length=100
        - country: max_length=50
    """
    name: str = Field(..., min_length=2, max_length=100)
    country: Optional[str] = Field(None, max_length=50)

class ArtistUpdate(BaseModel):
    """
        Schemat danych używany do aktualizacji istniejącego artysty.
        Wszystkie pola są opcjonalne — aktualizowane są tylko te,
        które zostały przekazane (exclude_unset=True w CRUD).
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    country: Optional[str] = Field(None, max_length=50)

class ArtistOut(BaseModel):
    """
        Schemat danych wyjściowych używany do zwracania informacji o artyście.
        Konfiguracja:
        from_attributes = True
            Pozwala na automatyczne tworzenie obiektu ArtistOut
            bezpośrednio z modelu ORM (SQLAlchemy).
    """
    id: int
    name: str
    country: Optional[str] = None

    class Config:
        from_attributes = True
