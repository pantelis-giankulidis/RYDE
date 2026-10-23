import asyncio
import aiohttp
from datetime import datetime, timezone
from app.utils.utils import file_name
from app.utils.utils import S3_BUCKET
from app.utils.utils import s3_key

YEAR = 2026

class AWSTaxiFinalDataCrawler:
    def __init__(self):
        self.touched = True

    async def execute_pipelines(bucket: str, key: str):
        df = self.read_parquet(bucket, key)
        await asyncio.to_thread(pl.execute)
        if extracted_key["source"] == "silver":
            pl = SilverToGoldPipeline(s3_client, bucket, extracted_key["decoded_key"])
            return await asyncio.to_thread(pl.execute)

    def read_parquet(self, bucket: str, key: str):
        s3_uri = f"s3://{bucket}/{key}"
        df = pl.read_parquet(s3_uri)
        return df

    async def fetch_source_etag(self, month: int) -> str | None:
        if S3_BUCKET is not None:
            df = self.read_parquet(S3_BUCKET, s3_key(YEAR, month))
            return df
        return None

    async def sync_file(self, month: int) -> str:
        source_etag = self.fetch_source_etag(month)
        if source_etag is None:
            return "not_published"
         
        if await asyncio.to_thread(self.stored_source_etag, key) == source_etag:
            return "up_to_date"

    async def start(self) -> dict[str, str]:
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
                results[name] = await self.sync_file(month)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Failed syncing %s", name)
                results[name] = "error"  # retried on the next cycle
        return results