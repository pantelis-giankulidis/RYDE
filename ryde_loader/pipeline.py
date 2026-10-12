# pyrefly: ignore [missing-import]
from pathlib import Path
import ZonePipeline
import DailyZoneRevenuePipeline
import HourlyZoneDemandPipeline
import polars as pl 
import pyodbc 

WORK_DIR = Path("/Users/pantelisgiankoulidis/Documents/nycity_cabs/ryde_transformer/data/processed")
CONN_STR = ("Driver={ODBC Driver 17 for SQL Server};" +
            "Server=localhost,1433;" +
            "Database=ryde;" +
            "UID=sa;" +
            "PWD=YourStrong!Passw0rd")
CHUNK_SIZE = 50000

trip_columns = ["VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "RatecodeID", "store_and_fwd_flag", "PULocationID", "DOLocationID", "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount", "congestion_surcharge", "Airport_fee"]

insert_trips = f"""
INSERT INTO TRIP ({', '.join(trip_columns)})
VALUES ({', '.join(['?'] * len(trip_columns))})
"""

def upsert_to_mssql(data: pl.DataFrame):
    HourlyZoneDemandPipeline.ETL(data)
    DailyZoneRevenuePipeline.ETL(data)
    ZonePipeline.ETL(data)
    with pyodbc.connect(CONN_STR) as conn:
        cursor = conn.cursor()
        cursor.fast_executemany = True 
        df = data.select(trip_columns)

        for chunk in df.iter_slices(n_rows = CHUNK_SIZE):
            rows = chunk.rows()
            cursor.executemany(insert_trips, rows)
            conn.commit() 


def Load(df: pl.DataFrame):
    print(f"Loading {df.shape} to database")
    upsert_to_mssql(df)
    print("File loaded to database")

def Extract():
    files = list(WORK_DIR.glob("*.parquet"))
    if not files:
        print("Not files found to process")
        return
    for file in files:
        print(f'Processing file: {file.name}')
        try:
            df = pl.read_parquet(file).head(10000)
            if df.is_empty():
                print(f'File is empty, skipping')
                continue
            Load(df)
        except Exception as ex:
            print(f'Failed to load {file.name}. Error: {ex}')
            continue


def etl():
    Extract()

if __name__ == "__main__":
    etl()