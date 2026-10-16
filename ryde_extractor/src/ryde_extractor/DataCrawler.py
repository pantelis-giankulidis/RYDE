from collections import defaultdict
import aiohttp
# pyrefly: ignore [missing-import]
from aiohttp import web
from datetime import datetime, timezone
from pathlib import Path
from src.ryde_extractor.Logger import logger
from contextlib import asynccontextmanager
from botocore.exceptions import ClientError
import os
import boto3 
import asyncio
import tempfile
import contextlib
import pyarrow.parquet as pq

S3_BUCKET = os.getenv("TARGET_S3_BUCKET", "my-data-warehouse-lake")
S3_PREFIX = os.getenv("TARGET_S3_PREFIX", "nyc-taxi/yellow/processed")
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
s3_client = boto3.client("s3")
YEAR = 2026

def file_name(year: int, month: int) -> str:
    return f"yellow_tripdata_{year}-{month:02d}.parquet"
 
 
def s3_key(year: int, month: int) -> str:
    return f"{S3_PREFIX}/year={year}/month={month:02d}/{file_name(year, month)}"



class AWSTaxiDataCrawler:
    def __init__(self, port: int = 8888, health_check_interval: int = 30):
        self.port = port
        self.backends: list[BackendServer] = []
        self.current_backend_index = 0
        self.health_check_interval = health_check_interval
        self.connection_counts = defaultdict(int) #Active connections
        self.session = None # To make requests to backend
        self.health_check_task = None

    def stored_source_etag(self, key: str) -> str | None:
        """Source ETag we saved as metadata on our processed copy, or None if not stored."""
        try:
            head = s3_client.head_object(Bucket=S3_BUCKET, Key=key)
        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
                return None
            raise
        return head.get("Metadata", {}).get("source-etag")

    def process_file(self, src: Path, dst: Path) -> None:
        """Your 'some work' on the parquet goes here (blocking, runs in a thread)."""
        table = pq.read_table(src)
        # e.g. drop bad rows, cast columns, add columns ...
        pq.write_table(table, dst, compression="zstd")

    async def fetch_source_etag(self, session: aiohttp.ClientSession, url: str) -> str | None:
        """HEAD the source file. Returns its ETag, or None if it isn't published yet."""
        async with session.head(url, allow_redirects=True) as resp:
            # CloudFront answers 403 (sometimes 404) for files that don't exist yet
            if resp.status in (403, 404):
                return None
            resp.raise_for_status()
            return resp.headers.get("ETag", "").strip('"') or resp.headers.get("Content-Length", "")

    async def download(self, session: aiohttp.ClientSession, url: str, dest: Path) -> None:
        async with session.get(url) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                async for chunk in resp.content.iter_chunked(1 << 20):
                    f.write(chunk)

    

    async def sync_month(self, session: aiohttp.ClientSession, month: int) -> str:
        url = f"{BASE_URL}/{file_name(YEAR, month)}"
        key = s3_key(YEAR, month)
 
        source_etag = await self.fetch_source_etag(session, url)
        if source_etag is None:
            return "not_published"
 
        if await asyncio.to_thread(self.stored_source_etag, key) == source_etag:
            return "up_to_date"
 
        with tempfile.TemporaryDirectory() as tmp:
            raw, processed = Path(tmp) / "raw.parquet", Path(tmp) / "processed.parquet"
            await self.download(session, url, raw)
            await asyncio.to_thread(self.process_file, raw, processed)
            await asyncio.to_thread(
                s3_client.upload_file,
                str(processed),
                S3_BUCKET,
                key,
                ExtraArgs={"Metadata": {"source-etag": source_etag}},
            )
        return "uploaded"

    async def start(self, session: aiohttp.ClientSession) -> dict[str, str]:
        now = datetime.now(timezone.utc)
        if YEAR < now.year:
            last_month = 12
        elif YEAR == now.year:
            last_month = now.month
        else:
            last_month = 0
 
        results: dict[str, str] = {}
        for month in range(1, last_month + 1):
            name = file_name(YEAR, month)
            try:
                results[name] = await self.sync_month(session, month)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Failed syncing %s", name)
                results[name] = "error"  # retried on the next cycle
        return results

    
