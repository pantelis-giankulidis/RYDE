from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.Logger import logger
from app.BronzeToSilverPipeline import BronzeToSilverPipeline
import aiohttp
import asyncio
import aioboto3
import os
from dotenv import load_dotenv

load_dotenv()

QUEUE_URL = os.getenv("QUEUE_URL")

SYNC_INTERVAL_SECONDS = 3600*24

pl = BronzeToSilverPipeline()

async def aws_listener() -> None:
    session = aioboto3.Session()
    async with session.client("sqs") as sqs:
        while True:
            try:
                response = await sqs.receive_message(
                    QueueUrl=QUEUE_URL,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20,  # Long-polling reduces API costs
                )

                messages = response.get("Messages", [])
                for msg in messages:
                    body = json.loads(msg["Body"])
                    
                    # Extract S3 bucket and object key
                    for record in body.get("Records", []):
                        bucket = record["s3"]["bucket"]["name"]
                        key = record["s3"]["object"]["key"]
                        logger.info(f"Processing fresh parquet: s3://{bucket}/{key}")
                        res = await pl.execute()
                        logger.info(f"Parquet s3://{bucket}/{key} processed with result {res}")

                    # Delete message so it is not reprocessed
                    await sqs.delete_message(
                        QueueUrl=QUEUE_URL,
                        ReceiptHandle=msg["ReceiptHandle"],
                    )
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error reading SQS: {e}")
                await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AWS subscription for fresh bronze(raw) parquet files ...")
    app.state.sync_status = {"last_run": None, "results": {}}
    aws_scanning_task = asyncio.create_task(aws_listener())

    try:
        yield  
    finally:
        logger.info("Stopping AWS subscription for Bronze files job...")
        aws_scanning_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await aws_scanning_task

    logger.info("Shutting down AWS subscriber...")