from contextlib import asynccontextmanager
from fastapi import FastAPI
# from app.api.http.middlewares import configure_middlewares
# from app.api.openapi import custom_openapi
# from app.infrastructure.common.tasks import (
#     ainit_blob_containers,
#     ainit_record_manager,
#     ainit_vector_store,
# )
from .endpoints import models, dashboard, form, run
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

app.include_router(models.router)
app.include_router(dashboard.router)
app.include_router(form.router)

app.include_router(run.router)