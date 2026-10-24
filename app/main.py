import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import auth_route
from app.core.config import settings
from app.core.database import engine, get_db
from app.core.logging_config import configure_logging
from app.core.rate_limit import limiter
from app.exceptions.handlers import register_exception_handlers

configure_logging(settings.log_level)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started")
    yield
    await engine.dispose()
    logger.info("Application stopped")


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
register_exception_handlers(app)

app.include_router(auth_route.router, prefix="/auth", tags=["auth"])


@app.get("/")
def root():
    return {"message": "Welcome"}


@app.get("/health/db")
async def db_health(db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        result = await db.execute(text("SELECT 1"))
        value = result.scalar_one()
        return {"database": "connected", "value": value}
    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavaiable",
        )
