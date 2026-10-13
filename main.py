from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.concurrency import run_in_threadpool

from app.api.routes import router as api_router
from app.db.session import SessionLocal, engine
from app.settings import settings
from app.site.routes import router as site_router


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None]:
	application.state.db_engine = engine
	application.state.db_session_factory = SessionLocal
	try:
		yield
	finally:
		await run_in_threadpool(engine.dispose)


app = FastAPI(
	title=settings.title,
	version=settings.version,
	debug=settings.debug,
	lifespan=lifespan,
)
app.include_router(site_router)
app.include_router(api_router, prefix=settings.api_prefix, tags=["api"])