import asyncio
import aiohttp
from datetime import datetime, timezone
from app.utils.utils import file_name

YEAR = 2026

class AWSTaxiFinalDataCrawler:
    def __init__(self):
        self.touched = True

    async def sync_file(self, session: aiohttp.ClientSession, month: int) -> str:

        return ""

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
                results[name] = await self.sync_file(session, month)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Failed syncing %s", name)
                results[name] = "error"  # retried on the next cycle
        return results