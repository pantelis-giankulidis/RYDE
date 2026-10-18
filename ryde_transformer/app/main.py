import logging

from fastapi import FastAPI, HTTPException
from app.LifeSpan import lifespan

app = FastAPI(title="ryde_transformer", lifespan = lifespan)

def main():
    return app

@app.get("/health")
def health():
    return {"status": "ok", "service": "ryde_transformer"}