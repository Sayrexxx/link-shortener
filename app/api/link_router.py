from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import Link, Click

router = APIRouter(prefix="/api/links", tags=["links"])


@router.get("/{code}/info")
async def get_link_info(
        code: str,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Link).where(Link.short_code == code)
    )
    link = result.scalar()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    clicks = await db.execute(
        select(func.count(Click.id)).where(Click.link_id == link.id)
    )

    return {
        "original_url": link.original_url,
        "short_code": link.short_code,
        "clicks": clicks.scalar(),
        "created_at": link.created_at.isoformat()
    }
