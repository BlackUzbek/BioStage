import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as api_router
from backend.bot.telegram_runtime import init_telegram, router as telegram_router, telegram_app
from backend.core.config import get_settings
from backend.database.models import Base
from backend.database.session import AsyncSessionLocal, engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(telegram_router)


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await init_telegram(AsyncSessionLocal)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    if telegram_app:
        await telegram_app.shutdown()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
