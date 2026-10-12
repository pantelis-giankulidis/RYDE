from sqlalchemy import Float
from src.ryde.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mssql import DATETIME2

class Trip(Base):
    __tablename__ = "TRIP"
    VendorId = Column(Integer, primary_key = True)
    tpep_pickup_datetime = Column(DATETIME2(precision=4), nullable = False)
    tpep_dropoff_datetime = Column(DATETIME2(precision=4), nullable = False)
    passenger_count = Column(Integer)
    trip_distance = Column(Float(precision=4))
    RatecodeID = Column(Integer)
    store_and_fwd_flag = Column(String)
    PULocationID = Column(Integer, ForeignKey("TAXI_ZONES.zone_id"), nullable = False)
    DOLocationID = Column(Integer, ForeignKey("TAXI_ZONES.zone_id"), nullable = False)
    payment_type = Column(Integer)
    fare_amount = Column(Float(precision=4))
    extra = Column(Float(precision=4))
    mta_tax = Column(Float(precision=4))
    tip_amount = Column(Float(precision=4))
    tolls_amount = Column(Float(precision=4))
    improvement_surcharge = Column(Float(precision=4))
    total_amount = Column(Float(precision=4))
    congestion_surcharge = Column(Float(precision=4))
    Airport_fee = Column(Float(precision=4))
