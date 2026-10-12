import polars as pl 
import pyodbc 
import os
from dotenv import load_dotenv

load_dotenv()

CONN_STR = os.getenv("CONN_STR")

insert_zones = f"""
INSERT INTO TAXI_ZONES (zone_id, borough, population)
SELECT v.zone_id, v.borough, v.population
FROM (VALUES (?, ?, ?)) AS v(zone_id, borough, population)
WHERE NOT EXISTS (
    SELECT 1 FROM TAXI_ZONES t WHERE t.zone_id = v.zone_id
)
"""

def Transform(df: pl.DataFrame):
    zones = pl.concat([df["PULocationID"], df["DOLocationID"]], how='vertical').unique().to_frame("zone_id")
    zones = zones.with_columns([pl.lit("NY").alias("borough"), pl.lit(0).alias("population")])
    return zones

def Load(zones: pl.DataFrame):
    with pyodbc.connect(CONN_STR) as conn:
        cursor = conn.cursor()
        cursor.fast_executemany = True 
        cursor.execute("SET IDENTITY_INSERT TAXI_ZONES ON")
        conn.commit()
        for chunk in zones.iter_slices(n_rows = 10000):
            rows = chunk.rows()
            cursor.executemany(insert_zones, rows)
            conn.commit() 
        cursor.execute("SET IDENTITY_INSERT TAXI_ZONES OFF")
        conn.commit()
    print(f"Zones loaded into MS-SQL")

def ETL(df: pl.DataFrame):
    print(f"Starting ETL pipeline for NY Zones")
    zones = Transform(df)
    print(f"Loaded {zones.shape} to database")
    Load(zones)