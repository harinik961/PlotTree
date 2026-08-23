from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app import models
from app.routers import auth as auth_router
from app.routers import stories as stories_router
from app.routers import sentences as sentences_router, votes as votes_router
from app.websockets import router as ws_router
from app.websockets.redis_manager import redis_manager

app = FastAPI()
app.include_router(stories_router.router, prefix="/stories", tags=["stories"])
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(sentences_router.router, prefix="/sentences", tags=["sentences"])
app.include_router(votes_router.router, prefix="/votes", tags=["votes"])
app.include_router(ws_router.router, tags=["websockets"])
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    await redis_manager.startup()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/health")
def health():
    return {"status": "ok"}
