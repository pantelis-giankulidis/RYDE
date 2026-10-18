import logging

from fastapi import FastAPI, HTTPException
from src.ryde_extractor.LifeSpan import aws_scanner 

app = FastAPI(title="ryde_extractor", lifespan = aws_scanner)

def main():
    return app

@app.get("/health")
def health():
    return {"status": "ok", "service": "ryde_extractor"}