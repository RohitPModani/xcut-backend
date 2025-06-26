from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from app.redis_client import redis_client
from app.schemas import URLBase, URLResponse
from app.crud import create_url, get_url_by_short_key, update_url_visit, get_url_visits
from app.database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
import shortuuid
from typing import Optional
import re
from datetime import UTC, datetime
import os
from dotenv import load_dotenv

load_dotenv()

frontend_url = os.getenv("FRONTEND_URL")

router = APIRouter()

# Constants
URL_CACHE_EXPIRY = 3600  # 1 hour
MAX_RETRIES = 3
SHORT_URL_LENGTH = 6

async def get_db():
    async with SessionLocal() as session:
        yield session

def validate_short_key(short_key: str) -> bool:
    """Validate the format of the short key."""
    return bool(re.match("^[A-Za-z0-9_-]{6}$", short_key))

async def update_visit_count(db: AsyncSession, short_key: str):
    """Background task to update visit count."""
    await update_url_visit(db, short_key)

@router.post("/shorten", response_model=URLResponse)
async def shorten_url(url: URLBase, db: AsyncSession = Depends(get_db)):
    for _ in range(MAX_RETRIES):
        short_key = shortuuid.random(length=SHORT_URL_LENGTH)
        if not await get_url_by_short_key(db, short_key):
            db_url = await create_url(db, short_key, str(url.target_url))
            # Cache the URL with expiration
            await redis_client.setex(short_key, URL_CACHE_EXPIRY, str(url.target_url))
            return URLResponse(
                short_url=f"{frontend_url}/{short_key}",
                target_url=str(url.target_url),
                visits=0,
                created_at=datetime.now(UTC)
            )
    
    raise HTTPException(
        status_code=500,
        detail="Failed to generate unique short URL. Please try again."
    )

@router.get("/{short_key}")
async def redirect_to_url(
    short_key: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    # Get client IP and user agent to create a unique visit identifier
    client_ip = request.client.host
    user_agent = request.headers.get("useragent", "")
    visit_key = f"visit:{short_key}:{client_ip}:{user_agent}"
    
    # Check if we've already processed this visit recently
    recent_visit = await redis_client.get(visit_key)
    if recent_visit:
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "target_url": recent_visit,
                "short_key": short_key
            }
        )

    if not validate_short_key(short_key):
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "Invalid URL format"}
        )

    target_url = await redis_client.get(short_key)
    
    if not target_url:
        db_url = await get_url_by_short_key(db, short_key)
        if not db_url:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "URL not found"}
            )
        target_url = db_url.target_url
        await redis_client.setex(short_key, URL_CACHE_EXPIRY, target_url)
    
    # Store this visit in Redis for 5 minutes to prevent duplicate counting
    await redis_client.setex(visit_key, 300, target_url)
    
    background_tasks.add_task(update_visit_count, db, short_key)
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "target_url": target_url,
            "short_key": short_key
        }
    )

@router.get("/visits/{short_key}")
async def get_visits(short_key: str, db: AsyncSession = Depends(get_db)):
    visits = await get_url_visits(db, short_key)
    return {"status": "success", "visits": visits}