from contextlib import asynccontextmanager
import contextlib
import json
from fastapi import FastAPI
from app.Logger import logger
import asyncio
import aiohttp
from datetime import datetime, timezone
from app.DataCrawler import AWSTaxiFinalDataCrawler

SYNC_INTERVAL_SECONDS = 3600

dc = AWSTaxiFinalDataCrawler()

async def aws_reader(app: FastAPI, interval_seconds: int = SYNC_INTERVAL_SECONDS) -> None:
    timeout = aiohttp.ClientTimeout(total=None, sock_connect=15, sock_read=120)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            logger.info("Starting scheduled daily parquet files check...")
            try:
                results = await dc.start()
                app.state.sync_status = {
                    "last_run": datetime.now(timezone.utc).isoformat(),
                    "results": results,
                }
                logger.info("Sync finished: %s", results)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Sync run failed")
            await asyncio.sleep(interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting migrating parquet files to postgres job ...")
    app.state.sync_status = {"last_run": None, "results": {}}
    aws_loading_parquet_task = asyncio.create_task(aws_reader(app, 3600))

    try:
        yield  
    finally:
        logger.info("Stopping migrating parquet files to postgres job...")
        aws_loading_parquet_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await aws_loading_parquet_task

    logger.info("Shutting down ryde loader...")