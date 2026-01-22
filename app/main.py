from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, users, artists, albums, tracks, playlists, websocket

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Playlist Manager", version="1.0.0")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(artists.router)
app.include_router(albums.router)
app.include_router(tracks.router)
app.include_router(playlists.router)
app.include_router(websocket.router)