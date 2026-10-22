from fastapi import FastAPI

from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Luweero Build - Escrow & Marketplace Backend",
    version="1.0.0",
    description="Milestone escrow + hardware marketplace API for Ugandan construction projects.",
)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}
