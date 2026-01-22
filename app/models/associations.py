"""
Moduł definiuje tabele asocjacyjne (łączące) wykorzystywane do obsługi relacji
wielu‑do‑wielu pomiędzy modelami Track, Artist oraz Playlist.
Tabele te nie posiadają własnych modeli ORM — są reprezentowane jako obiekty
`Table` SQLAlchemy i wykorzystywane w relacjach `secondary` w modelach ORM.

Tabele:
playlist_track
    Łączy playlisty z utworami (relacja many‑to‑many).
    Każdy rekord oznacza, że dany utwór znajduje się w danej playliście.
track_artist
    Łączy utwory z artystami (relacja many‑to‑many).
    Każdy rekord oznacza, że dany artysta brał udział w tworzeniu danego utworu.

Struktura:
Każda tabela składa się wyłącznie z dwóch kolumn będących kluczami obcymi
do odpowiednich tabel głównych. Nie posiadają one własnych kluczy głównych,
ponieważ kombinacja dwóch kluczy obcych pełni rolę unikalnego powiązania.
"""
from sqlalchemy import Table, Column, ForeignKey
from app.database import Base

playlist_track = Table(
    "playlist_track",
    Base.metadata,
    Column("playlist_id", ForeignKey("playlists.id")),
    Column("track_id", ForeignKey("tracks.id")),
)

track_artist = Table(
    "track_artist",
    Base.metadata,
    Column("track_id", ForeignKey("tracks.id")),
    Column("artist_id", ForeignKey("artists.id")),
)
