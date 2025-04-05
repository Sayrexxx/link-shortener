from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from app.db.models import Link
from app.services.validation import URLValidator
from app.services.code_generator import CodeGenerator
from app.core.config import settings


class LinkService:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )

    async def create_link(
            self,
            original_url: str,
            custom_code: Optional[str] = None,
            db: AsyncSession = None
    ) -> Link:
        """
        Creates a shortened link with caching.

        Args:
            original_url: URL to shorten
            custom_code: Optional custom short code
            db: Async database session

        Returns:
            Link: Created link object

        Raises:
            ValueError: For invalid URLs or duplicate codes
        """
        if not URLValidator.is_valid(original_url):
            raise ValueError("Invalid URL format")

        cache_key = f"link:{custom_code}" if custom_code else None
        if cache_key:
            cached_url = await self.redis.get(cache_key)
            if cached_url:
                raise ValueError("Custom code already exists")

        if custom_code:
            if not CodeGenerator.validate(custom_code):
                raise ValueError("Custom code must be 4-16 alphanumeric chars")
            code = custom_code
        else:
            code = await CodeGenerator.generate()

        existing_link = await db.execute(
            select(Link).where(Link.short_code == code)
        )
        if existing_link.scalar():
            raise ValueError("Short code already in use")

        link = Link(
            original_url=original_url,
            short_code=code,
            created_at=datetime.utcnow()
        )
        db.add(link)
        await db.commit()
        await db.refresh(link)

        await self.redis.set(
            f"link:{code}",
            original_url,
            ex=settings.REDIS_TTL
        )

        return link
