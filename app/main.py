from fastapi import APIRouter, FastAPI

from app.config import get_settings
from app.routers import contracts, store, users, webhook

settings = get_settings()

app = FastAPI(
    title="Luweero Build - Escrow & Marketplace Backend",
    version="1.0.0",
    description="Milestone escrow + hardware marketplace API for Ugandan construction projects.",
)

api_v1 = APIRouter(prefix=settings.api_v1_prefix)
api_v1.include_router(contracts.router)
api_v1.include_router(store.router)
api_v1.include_router(webhook.router)
api_v1.include_router(users.router)
app.include_router(api_v1)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}
