from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from .database.infra import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
