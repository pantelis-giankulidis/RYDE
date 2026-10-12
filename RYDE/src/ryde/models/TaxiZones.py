from src.ryde.database import Base
from sqlalchemy import Column, Integer, String

class TaxiZones(Base):
    __tablename__ = "TAXI_ZONES"
    zone_id = Column(Integer, primary_key=True)
    borough = Column(String)
    population = Column(Integer)
