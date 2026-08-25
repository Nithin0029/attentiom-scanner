from fastapi import FastAPI
from src.api.server import app

app = FastAPI(
    title="Attention Scanner API",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "attention-scanner",
    }