from app.models import URL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, UTC

async def get_url_by_short_key(db: AsyncSession, short_key: str) -> URL:
    result = await db.execute(select(URL).where(URL.short_key == short_key))
    return result.scalar_one_or_none()

async def create_url(
    db: AsyncSession,
    short_key: str,
    target_url: str,
) -> URL:
    db_url = URL(
        short_key=short_key,
        target_url=target_url,
    )
    db.add(db_url)
    await db.commit()
    await db.refresh(db_url)
    return db_url

async def update_url_visit(db:AsyncSession, short_key:str) -> URL:
    url = await get_url_by_short_key(db, short_key)
    url.visits += 1
    db.add(url)
    await db.commit()
    await db.refresh(url)
    return url

async def get_url_visits(db:AsyncSession, short_key:str) -> int:
    url = await get_url_by_short_key(db, short_key)
    return url.visits