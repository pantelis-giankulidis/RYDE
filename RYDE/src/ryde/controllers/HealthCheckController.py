from fastapi import APIRouter
router = APIRouter()

@router.get("/healthCheck")
def health_check():
    return {"message": "OK"}