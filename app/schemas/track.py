"""
Schematy Pydantic odpowiedzialne za walidację danych wejściowych i wyjściowych
związanych z tworzeniem, aktualizacją oraz prezentacją utworów muzycznych.

TrackCreate:
    Używany podczas tworzenia nowego utworu. Wymaga tytułu, czasu trwania,
    opcjonalnego ID albumu oraz listy identyfikatorów artystów.
TrackUpdate:
    Używany podczas aktualizacji istniejącego utworu. Wszystkie pola są opcjonalne,
    a aktualizowane są tylko te, które zostały przekazane.
TrackOut:
    Schemat wyjściowy używany do zwracania danych utworu w odpowiedziach API.
    Zawiera listę identyfikatorów artystów oraz wspiera konwersję z modeli ORM.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Annotated

class TrackCreate(BaseModel):
    """
        Schemat danych używany do tworzenia nowego utworu muzycznego.

        Pola:
        title : str
            Tytuł utworu. Musi mieć od 1 do 200 znaków.
        duration : int
            Czas trwania utworu w sekundach. Musi być większy od 0 i mniejszy niż 86400.
        album_id : int | None
            Opcjonalny identyfikator albumu, do którego należy utwór.
            Jeśli podany, musi być większy od 0.
        artist_ids : list[int]
            Lista identyfikatorów artystów powiązanych z utworem.
            Musi zawierać co najmniej jeden element.

        Walidacja:
        - title: min_length=1, max_length=200
        - duration: gt=0, lt=86400
        - album_id: gt=0 (jeśli podane)
        - artist_ids: min_length=1, wszystkie wartości > 0

        Dodatkowa walidacja:
        validate_artist_ids:
            Sprawdza, czy wszystkie ID artystów są większe od 0.
    """
    title: str = Field(..., min_length=1, max_length=200)
    duration: int = Field(..., gt=0, lt=86400)
    album_id: Optional[int] = Field(None, gt=0)

    artist_ids: Annotated[
        List[int],
        Field(..., min_length=1)
    ]

    file_path: Optional[str] = Field(None,
                                     description="Lokalna ścieżka do pliku MP3")

    @field_validator("artist_ids")
    @classmethod
    def validate_artist_ids(cls, v: List[int]):
        if any(a <= 0 for a in v):
            raise ValueError("All artist IDs must be greater than 0")
        return v

class TrackUpdate(BaseModel):
    """
        Schemat danych używany do aktualizacji istniejącego utworu.
        Wszystkie pola są opcjonalne — aktualizowane są tylko te,
        które zostały przekazane (exclude_unset=True w CRUD).
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    duration: Optional[int] = Field(None, gt=0, lt=86400)
    album_id: Optional[int] = Field(None, gt=0)

    artist_ids: Optional[
        Annotated[List[int], Field(min_length=1)]
    ] = None

    file_path: Optional[str] = Field(None,
                                     description="Lokalna ścieżka do pliku MP3")

    @field_validator("artist_ids")
    @classmethod
    def validate_artist_ids(cls, v: Optional[List[int]]):
        if v is not None and any(a <= 0 for a in v):
            raise ValueError("All artist IDs must be greater than 0")
        return v

class TrackOut(BaseModel):
    """
        Schemat danych wyjściowych używany do zwracania informacji o utworze.
        Konfiguracja:
        from_attributes = True
            Pozwala na automatyczne tworzenie obiektu TrackOut
            bezpośrednio z modelu ORM (SQLAlchemy).
    """
    id: int
    title: str
    duration: int
    album_id: Optional[int]
    artist_ids: List[int] = []
    file_path: Optional[str]

    class Config:
        from_attributes = True
