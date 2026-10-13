import logging

from fastapi import FastAPI, HTTPException

#from app.consumer import process_payload

#logging.basicConfig(level=logging.INFO)
#log = logging.getLogger("rainbow-dataset-pipeline")

app = FastAPI(title="ryde_extractor")

def main():
    return app

@app.get("/health")
def health():
    return {"status": "ok", "service": "ryde_extractor"}