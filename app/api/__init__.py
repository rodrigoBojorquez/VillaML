from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

# from app.api.http.middlewares import configure_middlewares
# from app.api.openapi import custom_openapi
# from app.infrastructure.common.tasks import (
#     ainit_blob_containers,
#     ainit_record_manager,
#     ainit_vector_store,
# )
from .endpoints import data, form, run
from container import Container
from ..infrastructure.data.init_db import init_db


@asynccontextmanager
async def lifespan(application: FastAPI):
    container = Container()
    application.container = container

    await init_db()
    # await ainit_blob_containers()
    # await ainit_vector_store()

    yield


app = FastAPI(
    title="LIA - Service",
    docs_url="/swagger",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ⚠️ Cambia por tu dominio frontend en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(form.router)

app.include_router(run.router)