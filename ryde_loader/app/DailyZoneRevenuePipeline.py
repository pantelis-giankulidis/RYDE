import polars as pl
import pyodbc 
import os
from dotenv import load_dotenv
from Logger import logger
load_dotenv()

CONN_STR = os.getenv("CONN_STR", default = None)

class DailyZoneRevenuePipeline:
    def __init__(self, raw_dataframe: pl.DataFrame):
        self.df = raw_datarame

    def query(self):
        return """
            INSERT INTO DAILY_ZONE_REVENUE (id, zone_id, day, total_revenue, tip_amount, total_trips)
            SELECT v.id, v.zone_id, v.day, v.total_revenue, v.tip_amount, v.total_trips
            FROM (VALUES (?, ?, ?, ?, ?, ?)) AS v(zone_id, day, total_revenue, tip_amount, total_trips, id)
            WHERE NOT EXISTS (
                SELECT 1 FROM DAILY_ZONE_REVENUE d WHERE d.id = v.id
            )
            """

    def Transform(self):
        self.df = self.df.with_columns(tpep_pickup_date = pl.col("tpep_pickup_datetime").cast(pl.Date))
        dailyZoneRevenue = self.df.group_by(["PULocationID", "tpep_pickup_date"]).agg([pl.col("total_amount").sum().alias("total_revenue"), pl.col("tip_amount").sum().alias("tip_amount"), pl.col("VendorID").count().alias("total_trips")])
        dailyZoneRevenue = dailyZoneRevenue.rename({"PULocationID" : "zone_id", "tpep_pickup_date" : "day"})
        dailyZoneRevenue = dailyZoneRevenue.with_columns([pl.arange(1, dailyZoneRevenue.shape[0] + 1).cast(pl.Int32).alias("id"), pl.col("total_trips").cast(pl.Int32)])
        self.df = dailyZoneRevenue 

    def Load(self):
        with pyodbc.connect(CONN_STR) as conn:
            cursor = conn.cursor()
            cursor.fast_executemany = False 
            cursor.execute("SET IDENTITY_INSERT DAILY_ZONE_REVENUE ON")
            conn.commit()
            for chunk in self.df.iter_slices(n_rows = 10000):
                rows = chunk.rows()
                cursor.executemany(self.query(), rows)
                conn.commit() 
            cursor.execute("SET IDENTITY_INSERT DAILY_ZONE_REVENUE OFF")
            conn.commit()
        logger.info(f"Daily Zone Revenue loaded into postgres")

    def ETL():
        df_transformed = Transform(df)
        Load(df_transformed)

