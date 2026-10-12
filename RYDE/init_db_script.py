from dotenv import load_dotenv

import pymssql
import os 

load_dotenv()

conn = pymssql.connect(
    server="localhost",
    port=1433,
    user=os.getenv("MS_SQL_USER"),
    password=os.getenv("MS_SQL_PASSWORD"),
    database="master", 
    autocommit=True,     
)
cursor = conn.cursor()
#cursor.execute("CREATE DATABASE ryde;")
cursor.execute("USE ryde")
cursor.execute("DELETE FROM alembic_version")
#cursor.execute("USE ryde; CREATE TABLE TRIP(VendorId INT NULL, tpep_pickup_datetime DATETIME2(4) NULL, tpep_dropoff_datetime DATETIME2(4) NULL, passenger_count INT NULL, trip_distance FLOAT(53) NULL, RatecodeID INT NULL, store_and_fwd_flag NCHAR(1) NULL, PULocationID INT NULL, DOLocationID INT NULL, payment_type INT NULL, fare_amount FLOAT(53) NULL, extra FLOAT(53) NULL, mta_tax FLOAT(53) NULL, tip_amount FLOAT(53) NULL, tolls_amount FLOAT(53) NULL, improvement_surcharge FLOAT(53) NULL, total_amount FLOAT(53) NULL, congestion_surcharge FLOAT(53) NULL, Airport_fee FLOAT(53) NULL)")
conn.close()