from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.db import init_db
from app.core.utils.logger import logger_config

logger = logger_config(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating DB tables")
    await init_db()
    logger.info("DB tables Creation Successfull")
    yield


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url=f"{settings.API_STR}/docs",
    openapi_url=f"{settings.API_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    servers=[{"url": "http://localhost:8000", "description": "Development Server"}],
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_STR)
