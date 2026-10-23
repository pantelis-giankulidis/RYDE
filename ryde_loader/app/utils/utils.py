from dotenv import load_dotenv
import os

load_dotenv()

S3_PREFIX = os.getenv("TARGET_S3_PREFIX", default = None)
S3_BUCKET = os.getenv("TARGET_S3_BUCKET", default = None)

def file_name(year: int, month: int) -> str:
    return f"gold/month={year}-{month:02d}.parquet"

def s3_key(year: int, month: int) -> str:
    if S3_PREFIX is None:
        return ""
    return f"{S3_PREFIX}/year={year}/month={month:02d}/{s3_file_name(year, month)}"

def s3_file_name(year: int, month: int) -> str:
    return f"yellow_tripdata_{year}-{month:02d}.parquet"