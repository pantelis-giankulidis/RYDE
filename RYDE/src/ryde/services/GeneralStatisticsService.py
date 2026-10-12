from src.ryde.database import get_batabase_session
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.ryde.models.Trip import Trip
from sqlalchemy import select, func
from datetime import datetime 

class GeneralStatisticsService: 
    def __init__(self, db: AsyncSession):
        self.db = db 


    async def get_average_distance_trip(self, fro: datetime, to: datetime):
        query = select(func.avg(Trip.trip_distance)).where(Trip.tpep_pickup_datetime >= fro, Trip.tpep_dropoff_datetime <= to)
        result = await self.db.execute(query)
        return result.mappings().all()

def get_general_statistics_service(db: AsyncSession = Depends(get_batabase_session)) -> GeneralStatisticsService:
    return GeneralStatisticsService(db)