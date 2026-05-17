from fastapi import FastAPI
from src.frontend.routes import auth

app = FastAPI(title="FastAPI Frontend")

app.include_router(auth.router)

@app.get("/health")
async def health():
    return {"status": "ok"}