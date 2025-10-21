# app/main.py
from fastapi import FastAPI
from app.api.v1.api_router import api_router

app = FastAPI(
    title="Banking AI Agent API",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Banking AI Agent API"}