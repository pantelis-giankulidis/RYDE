from app.Logger import logger
from pathlib import PurePosixPath
import polars as pl

class SilverToGoldPipeline:
    def __init__(self, s3_client, bucket, key):
            self.s3_client = s3_client
            self.bucket = bucket
            self.key = key
    
    def execute(self):
        logger.info("Reading parquet data from /silver bucket directory...")
        df = self.extract()
        df = self.transform(df)
        self.load(df)
    
    def extract(self):
        s3_uri = f"s3://{self.bucket}/{self.key}"
        df = pl.read_parquet(s3_uri)
        return df
    
    def transform(self, df):
        df = self.calculate_trip_duration(df)
        df = self.calculate_pick_hour(df)
        df = self.calculate_pick_locations(df)
        return df
    
    def load(self, df):
        filename = PurePosixPath(self.key).name
        destination_key = self.key.replace("/silver/", "/gold/", 1)
        destination_uri = f"s3://{self.bucket}/{destination_key}"
        df.write_parquet(destination_uri, compression="snappy")
    
    def calculate_trip_duration(self, df):
        df = df.with_columns([(df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).alias("tpep_duration")])
        return df

    def calculate_pick_hour(self, df):
        df = df.with_columns([pl.col("tpep_dropoff_datetime").dt.truncate("1h").alias("tpep_dropoff_time"), pl.col("tpep_pickup_datetime").dt.truncate("1h").alias("tpep_pickup_time")])
        dropoff_pick = (
            df.group_by(
                pl.col("tpep_dropoff_time")
            )
            .agg(pl.len().alias("dropoff_in_hour"))
            .sort("tpep_dropoff_time")
            )
        df = df.join(dropoff_pick, how='left', on='tpep_dropoff_time')

        pickup_pick = (
            df.group_by(
                pl.col("tpep_pickup_time")
            )
            .agg(pl.len().alias("pickup_in_hour"))
            .sort("tpep_pickup_time")
        )

        return df

    def calculate_pick_locations(self, df):
        pickup_location = (
            df.group_by(
                pl.col("PULocationID")
            )
            .agg(pl.len().alias("pickups_in_location"))
            .sort("PULocationID")
        )
        df = df.join(pickup_location, how='left', on='PULocationID')

        dropoff_location = (
            df.group_by(
                pl.col("DOLocationID")
            )
            .agg(pl.len().alias("dropoffs_in_location"))
            .sort("DOLocationID")
        )

        return df

        async def upload_file():
            with tempfile.TemporaryDirectory() as tmp:
                await asyncio.to_thread(self.process_file, raw, processed)
                await asyncio.to_thread(
                    self.s3_client.upload_file,
                    str(processed),
                    self.bucket,
                    key,
                    ExtraArgs={"Metadata": {"source-etag": source_etag}},
                )