from dotenv import load_dotenv
import os

load_dotenv()

S3_PREFIX = os.getenv("TARGET_S3_PREFIX", default = None)

def s3_key(year: int, month: int) -> str:
    if S3_PREFIX is None:
        return ""
    return f"{S3_PREFIX}/year={year}/month={month:02d}/{file_name(year, month)}"

def file_name(year: int, month: int) -> str:
    return f"yellow_tripdata_{year}-{month:02d}.parquet"