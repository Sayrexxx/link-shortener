from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
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


@router.get("/{code}/stats")
async def get_link_stats(
        code: str,
        db: AsyncSession = Depends(get_db),
):
    link = await db.execute(
        select(Link).where(Link.short_code == code)
    )
    if not link.scalar():
        raise HTTPException(status_code=404, detail="Link not found")
    thirty_days_ago = datetime.now() - timedelta(days=30)

    daily_stats = await db.execute(
        select(
            extract('day', Click.clicked_at).label("day"),
            func.count().label("clicks")
        )
        .where(Click.link_id == link.id)
        .where(Click.clicked_at >= thirty_days_ago)
        .group_by("date")
        .order_by("date")
    )

    geo_data = await db.execute(
        select(
            Click.country_code,
            func.count().label("clicks")
        )
        .where(Click.link_id == link.id)
        .where(Click.country_code.is_not(None))
        .group_by(Click.country_code)
        .order_by(func.count().desc())
        .limit(10)
    )

    # Referrer data
    referrer_data = await db.execute(
        select(
            Click.referrer,
            func.count().label("visits")
        )
        .where(Click.link_id == link.id)
        .where(Click.referrer.is_not(None))
        .group_by(Click.referrer)
        .order_by(func.count().desc())
        .limit(10)
    )

    return {
        "time_series": [
            {"day": day, "clicks": clicks}
            for day, clicks in daily_stats.all()
        ],
        "geo_distribution": [
            {"country": country, "clicks": clicks}
            for country, clicks in geo_data.all()
        ],
        "top_referrers": [
            {"referrer": ref, "visits": visits}
            for ref, visits in referrer_data.all()
        ]
    }
