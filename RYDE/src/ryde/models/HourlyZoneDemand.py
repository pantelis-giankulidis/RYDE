from src.ryde.database import Base 
from sqlalchemy import Column, Integer, ForeignKey, Date

class HourlyZoneDemand(Base):
    __tablename__ = "HOURLY_ZONE_DEMAND"
    id = Column(Integer, primary_key = True)
    zone_id = Column(Integer, ForeignKey("TAXI_ZONES.zone_id"), nullable = False)
    day = Column(Date, nullable = False)
    hour = Column(Integer, nullable = False)
    trip_count = Column(Integer, nullable = False)