from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

class RateLimiter:
    def __init__(self, max_requests: int, period: timedelta):
        self.max_requests = max_requests
        self.period = period
        self.request_logs = defaultdict(list)
        self.lock = asyncio.Lock()

    async def check_limit(self, key: str) -> bool:
        async with self.lock:
            now = datetime.now()
            self.request_logs[key] = [
                t for t in self.request_logs[key]
                if t > now - self.period
            ]

            if len(self.request_logs[key]) >= self.max_requests:
                return False

            self.request_logs[key].append(now)
        return True
