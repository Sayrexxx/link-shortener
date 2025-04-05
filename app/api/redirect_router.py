from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import select
from starlette.responses import RedirectResponse

from app.db.session import async_session
from app.db.models import Link, Click
from datetime import datetime

router = APIRouter()


@router.get("/{code}")
async def redirect(code: str, request: Request):
    async with async_session() as db:
        result = await db.execute(
            select(Link).where(Link.short_code == code)
        )
        link = result.scalar()

        if not link:
            raise HTTPException(status_code=404, detail="Link not found")

        click = Click(
            link_id=link.id,
            clicked_at=datetime.utcnow(),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        db.add(click)
        await db.commit()

        return RedirectResponse(url=link.original_url, status_code=301)
