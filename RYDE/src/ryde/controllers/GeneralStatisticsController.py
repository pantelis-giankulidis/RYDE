import fastapi
from fastapi import Depends 
from src.ryde.services.GeneralStatisticsService import GeneralStatisticsService, get_general_statistics_service
from datetime import datetime 

router = fastapi.APIRouter(prefix = "/stats")

@router.get("/trip_distance")
async def get_average_distance_trip(from_date: datetime, to_date: datetime, service: GeneralStatisticsService = Depends(get_general_statistics_service)):
    res = await service.get_average_distance_trip(from_date, to_date)
    return {"message": "OK"}