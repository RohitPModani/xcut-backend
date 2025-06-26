import redis.asyncio as redis
from dotenv import load_dotenv
import os

load_dotenv()

redis_url = os.getenv("REDIS_URL")

redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)