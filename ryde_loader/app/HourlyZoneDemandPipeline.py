import polars as pl
import pyodbc 
import os
from dotenv import load_dotenv

load_dotenv()

CONN_STR = os.getenv("CONN_STR")

insert_hourly_zone_demand = """
INSERT INTO HOURLY_ZONE_DEMAND (id, zone_id, day, hour, trip_count)
SELECT v.id, v.zone_id, v.day, v.hour, v.trip_count
FROM (VALUES (?, ?, ?, ?, ?)) AS v(zone_id, day, hour, trip_count, id)
WHERE NOT EXISTS (
    SELECT 1 FROM HOURLY_ZONE_DEMAND d WHERE d.id = v.id
)
"""

def Transform(df: pl.DataFrame) -> pl.DataFrame:
    hourlyZoneDemand = df.with_columns(day = pl.col("tpep_pickup_datetime").cast(pl.Date), hour = pl.col("tpep_pickup_datetime").dt.hour())
    hourlyZoneDemand = hourlyZoneDemand.group_by(["PULocationID", "day", "hour"]).agg(pl.col("VendorID").count().alias("total_trips"))
    hourlyZoneDemand = hourlyZoneDemand.with_columns([pl.arange(1, hourlyZoneDemand.shape[0] + 1).cast(pl.Int32).alias("id"), pl.col("total_trips").cast(pl.Int32)])
    return hourlyZoneDemand

def Load(df: pl.DataFrame):
    with pyodbc.connect(CONN_STR) as conn:
        cursor = conn.cursor()
        cursor.fast_executemany = True 
        cursor.execute("SET IDENTITY_INSERT HOURLY_ZONE_DEMAND ON")
        conn.commit()
        for chunk in df.iter_slices(n_rows = 10000):
            rows = chunk.rows()
            cursor.executemany(insert_hourly_zone_demand, rows)
            conn.commit() 
        cursor.execute("SET IDENTITY_INSERT HOURLY_ZONE_DEMAND OFF")
        conn.commit()
    print(f"Hourly zone demand loaded into MS-SQL")

def ETL(df: pl.DataFrame):
    df_transformed = Transform(df)
    Load(df_transformed)
