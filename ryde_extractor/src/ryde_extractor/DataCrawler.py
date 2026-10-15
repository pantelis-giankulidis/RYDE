from collections import defaultdict
import aiohttp
# pyrefly: ignore [missing-import]
from aiohttp import web
import os
import boto3 

S3_BUCKET = os.getenv("TARGET_S3_BUCKET", "my-data-warehouse-lake")
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
s3_client = boto3.client("s3")


class AWSTaxiDataCrawler:
    def __init__(self, port: int = 8888, health_check_interval: int = 30):
        self.port = port
        self.backends: list[BackendServer] = []
        self.current_backend_index = 0
        self.health_check_interval = health_check_interval
        self.connection_counts = defaultdict(int) #Active connections
        self.session = None # To make requests to backend
        self.health_check_task = None

    def _health_endpoint(self,request: aiohttp.web.Request):
        """Health check endpoint for the load balancer itself"""
        healthy_backends = sum(1 for b in self.backends if b.healthy)

        if healthy_backends > 0:
            return aiohttp.web.json_response({
                "status": "healthy",
                "healthy_backends": healthy_backends,
                "total_backends": len(self.backends)
            })
        else:
            return aiohttp.web.json_response({
                "status": "unhealthy",
                "healthy_backends": 0,
                "total_backends": len(self.backends)
            }, status=503)

    def run_sync_job(taxi_type: str, start_year: int, end_year: int):
        """Worker task that scans missing months and syncs them."""
        with httpx.Client() as client:
            for year in range(start_year, end_year + 1):
                for month in range(1, 13):
                    month_str = f"{month:02d}"
                    filename = f"{taxi_type}_tripdata_{year}-{month_str}.parquet"
                    source_url = f"{BASE_URL}/{filename}"
                    s3_key = f"raw/nyctaxi/{taxi_type}/year={year}/month={month_str}/{filename}"

                    # 1. Skip if already processed
                    if s3_file_exists(S3_BUCKET, s3_key):
                        continue

                    # 2. Check if published upstream
                    head_resp = client.head(source_url, follow_redirects=True)
                    if head_resp.status_code == 200:
                        # 3. Stream direct to target S3 warehouse
                        stream_url_to_s3(source_url, S3_BUCKET, s3_key)

    async def check_remote_file_exists(client: httpx.AsyncClient, url: str) -> bool:
        """Uses a HEAD request to verify file publication without downloading payload."""
        response = await client.head(url, follow_redirects=True)
        return response.status_code == 200

    async def start(self):
        app = web.Application()
        app.router.add_route('*', '/health', self._health_endpoint)
        runner = aiohttp.web.AppRunner(app)
        # Asynchronously initializes the application so it’s ready to serve requests.
        await runner.setup()

        # TCPSite represents a concrete listening endpoint
        # could create multiple sites (e.g., different addresses/ports) for the same application.
        site = aiohttp.web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()

    async def stop(self):
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass

        if self.session:
            await self.session.close()
