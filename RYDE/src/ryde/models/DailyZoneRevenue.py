from src.ryde.database import Base 
from sqlalchemy import Column, Integer, Date, Float, ForeignKey

class DailyZoneRevenue(Base):
    __tablename__ = "DAILY_ZONE_REVENUE"
    id = Column(Integer, primary_key = True)
    zone_id = Column(Integer, ForeignKey("TAXI_ZONES.zone_id"), nullable = False)
    day = Column(Date, nullable = False)
    total_revenue = Column(Float, nullable = False)
    tip_amount = Column(Float, nullable = False)
    total_trips = Column(Integer, nullable = False)