from src.ryde_extractor.DataCrawler import AWSTaxiDataCrawler
from src.ryde_extractor.Logger import logger
from src.ryde_extractor.DataCrawler import AWSTaxiDataCrawler
from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio 
import aiohttp
import contextlib
from datetime import datetime, timezone

SYNC_INTERVAL_SECONDS = 36000

dc = AWSTaxiDataCrawler()

async def periodic_parquet_check(app: FastAPI, interval_seconds: int = 120) -> None:
    timeout = aiohttp.ClientTimeout(total=None, sock_connect=15, sock_read=120)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            logger.info("Starting scheduled hourly parquet files check...")
            try:
                results = await dc.start(session)
                app.state.sync_status = {
                    "last_run": datetime.now(timezone.utc).isoformat(),
                    "results": results,
                }
                logger.info("Sync finished: %s", results)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Sync run failed")
            await asyncio.sleep(SYNC_INTERVAL_SECONDS)
    

@asynccontextmanager
async def aws_scanner(app: FastAPI):
    logger.info("Starting AWS scanning for fresh parquet files ...")
    app.state.sync_status = {"last_run": None, "results": {}}
    aws_scanning_task = asyncio.create_task(periodic_parquet_check(app, 3600))

    try:
        yield  
    finally:
        logger.info("Stopping AWS scanning job...")
        aws_scanning_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await aws_scanning_task

    logger.info("Shutting down AWS scanner...")