import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from sqlmodel import SQLModel
from .routes.programa import router as programa_router
from .routes.transferencia import router as transferencia_router
from .routes.unidade_gestora import router as unidade_gestora_router
from .routes.municipio import router as municipio_router
from loguru import logger
from .database.infra import engine

LOGGER_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message} - Additional information: {extra}</level>"
)

logger.remove()
logger.add(sys.stderr, format=LOGGER_FORMAT)
logger.add("actions.log")


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    inner_log = logger
    inner_log.info(f"Receiving request: {request.method} {request.url}")

    response = None

    try:
        response = await call_next(request)
        inner_log.info(f"Response: {response.status_code}")
    except Exception as error:
        inner_log.error(f"Response: 500")
        raise error

    return response


app.include_router(programa_router)
app.include_router(transferencia_router)
app.include_router(unidade_gestora_router)
app.include_router(municipio_router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
