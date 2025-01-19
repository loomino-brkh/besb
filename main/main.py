from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_limiter import FastAPILimiter
from redis import asyncio as aioredis
from sqlmodel import SQLModel
import os
import uvicorn
from core.db import engine
from endpoints import absen_pengajian, absen_asramaan, data_daerah

app = FastAPI(
    docs_url=None, 
    redoc_url=None,
    openapi_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    try:
        # Create database tables
        SQLModel.metadata.create_all(engine)

        # Initialize Redis using container name
        redis = aioredis.from_url(f"redis://{os.getenv('REDIS_CONTAINER_NAME', 'localhost')}:6379", encoding="utf8", decode_responses=True)
        await FastAPILimiter.init(redis)
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    except Exception as e:
        print(f"Startup error: {e}")
        raise

app.include_router(absen_pengajian.router, prefix="/absen-pengajian", tags=["absen-pengajian"])
app.include_router(absen_asramaan.router, prefix="/absen-asramaan", tags=["absen-asramaan"])

@app.get("/")
async def root():
    return {"message": "This is API. Not web page!!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
