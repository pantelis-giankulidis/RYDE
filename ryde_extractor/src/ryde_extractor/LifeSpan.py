from src.ryde_extractor.DataCrawler import AWSTaxiDataCrawler
from src.ryde_extractor.Logger import logger
from src.ryde_extractor.DataCrawler import AWSTaxiDataCrawler
from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio 

dc = AWSTaxiDataCrawler(port = 8080)

async def periodic_health_check(interval_seconds: int = 120):
    while True:
        try:
            logger.info("Starting scheduled hourly health check...")
            dc = AWSTaxiDataCrawler()
            await dc.start()
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            logger.info("Health check task requested to cancel.")
            break
        except Exception as e:
            logger.error(f"Error during health check: {e}")
            await asyncio.sleep(10)

@asynccontextmanager
async def aws_scanner(app: FastAPI):
    logger.info("Starting AWS scanning for fresh parquet files ...")
    await dc.start()
    
    aws_scanning_task = asyncio.create_task(periodic_health_check(interval_seconds=3600))

    yield  

    logger.info("Stopping AWS scanning job...")
    aws_scanning_task.cancel()
    
    try:
        await aws_scanning_task
    except asyncio.CancelledError:
        pass

    logger.info("Shutting down AWS scanner...")
    await dc.stop()