from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as url_router
import os
from dotenv import load_dotenv

load_dotenv()

frontend_url = os.getenv("FRONTEND_URL")

app = FastAPI(
    title="URL Shortener API",
    description="A modern URL shortener with analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(url_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the URL Shortener API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }