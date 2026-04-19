from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from .api.router import router
from .database.session import create_db_tables


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI(
    # * server start/stop listener
    lifespan=lifespan_handler,
)

app.include_router(router)


@app.get("/", include_in_schema=False)
def root():
    return {
        "success": True,
        "message": "fastship api server is running",
        "version": "1.0.0",
        "author": "fisheeesh",
        "timestamp": datetime.now(),
    }


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
