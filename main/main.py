import os
import uvicorn
import logging
from datetime import datetime
from contextlib import asynccontextmanager
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
    data_hobi,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.startup_time = datetime.now()
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
    runtime = datetime.now() - app.state.startup_time
    logger.info(f"Application ran for {runtime}")


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ngaji.brkh.work",
        "https://29.brkh.work",
        "https://hj.brkh.work",
        "https://hd.brkh.work",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = [
    (absen_pengajian.router, "/absen-pengajian", ["absen-pengajian"]),
    (absen_asramaan.router, "/absen-asramaan", ["absen-asramaan"]),
    (biodata_generus.router, "/biodata/generus", ["biodata-generus"]),
    (data_daerah.router, "/data/daerah", ["data-daerah"]),
    (sesi.router, "/data/sesi", ["sesi"]),
    (url.router, "/url", ["url"]),
    (data_materi.router, "/data/materi", ["data-materi"]),
    (data_hobi.router, "/data/hobi", ["data-hobi"]),
]

for router, prefix, tags in routers:
    app.include_router(router, prefix=prefix, tags=[str(tag) for tag in tags])


@app.get("/")
async def root():
    return {
        "error": "Invalid access. This endpoint is intended for API only."
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
