from contextlib import asynccontextmanager
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_limiter import FastAPILimiter
from redis import asyncio as aioredis
from sqlmodel import SQLModel

from core.db import engine
from endpoints import (
    absen_asramaan,
    absen_pengajian,
    biodata_generus,
    data_daerah,
    data_materi,
    sesi,
    url,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Create database tables
        SQLModel.metadata.create_all(engine)

        # Initialize Redis using container name
        redis = aioredis.from_url(
            f"redis://{os.getenv('REDIS_CONTAINER_NAME', 'localhost')}:6379",
            encoding="utf8",
            decode_responses=True,
        )
        await FastAPILimiter.init(redis)
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    except Exception as e:
        print(f"Startup error: {e}")
        raise
    yield

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ngaji.brkh.work", "https://29.brkh.work"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(absen_pengajian.router, prefix="/absen-pengajian", tags=["absen-pengajian"])
app.include_router(absen_asramaan.router, prefix="/absen-asramaan", tags=["absen-asramaan"])
app.include_router(biodata_generus.router, prefix="/biodata/generus", tags=["biodata-generus"])
app.include_router(data_daerah.router, prefix="/data/daerah", tags=["data-daerah"])
app.include_router(sesi.router, prefix="/data/sesi", tags=["sesi"])
app.include_router(url.router, prefix="/url", tags=["url"])
app.include_router(data_materi.router, prefix="/data/materi", tags=["data-materi"])

@app.get("/")
async def root():
    return {"message": "ERRORR!!! This is API. Not web page!!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
