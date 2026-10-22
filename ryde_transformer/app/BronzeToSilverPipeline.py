from app.Logger import logger
from pathlib import PurePosixPath
import polars as pl


class BronzeToSilverPipeline:
    def __init__(self, s3_client, bucket, key):
        self.s3_client = s3_client
        self.bucket = bucket
        self.key = key

    def execute(self):
        logger.info("Reading parquet data from /bronze bucket directory ...")
        df = self.extract()
        df = self.transform(df)
        self.load(df)

    def extract(self):
        s3_uri = f"s3://{self.bucket}/{self.key}"
        df = pl.read_parquet(s3_uri)
        return df

    def transform(self, df):
        df = self.clean_up_data(df)
        return df

    def load(self, df):
        filename = PurePosixPath(self.key).name
        destination_key = self.key.replace("/bronze/", "/silver/", 1)
        destination_uri = f"s3://{self.bucket}/{destination_key}"
        df.write_parquet(destination_uri, compression="snappy")

    def clean_up_data(self, df):
        df = (
            df.filter(pl.col("trip_distance") > 0)
                .filter(~pl.all_horizontal(pl.all().is_null()))
                .unique()
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
