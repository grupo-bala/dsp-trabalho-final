from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel
from src.routes.programa import router as programa_router
from src.routes.transferencia import router as transferencia_router
from src.routes.unidade_gestora import router as unidade_gestora

from .database.infra import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(programa_router)
app.include_router(transferencia_router)
app.include_router(unidade_gestora)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
