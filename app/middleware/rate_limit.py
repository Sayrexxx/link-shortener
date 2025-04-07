from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from app.core.rate_limiter import RateLimiter
from datetime import timedelta

limiter = RateLimiter(
    max_requests=100,
    period=timedelta(minutes=1)
)

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    if not await limiter.check_limit(client_ip):
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests"
        )
    return await call_next(request)
