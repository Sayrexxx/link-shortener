import shortuuid
from sqlalchemy import select
from app.db.session import async_session
from app.db.models import Link

class CodeGenerator:
    @staticmethod
    async def generate(length: int = 8) -> str:
        async with async_session() as db:
            while True:
                code = shortuuid.uuid()[:length]
                exists = await db.execute(
                    select(Link).where(Link.short_code == code)
                )
                if not exists.scalar():
                    return code

    @staticmethod
    def validate(code: str) -> bool:
        return len(code) >= 4 and code.isalnum()
