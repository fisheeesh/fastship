from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.api.router import master_router

from .database.session import create_db_tables

# ? Dependency injection means providing data in our context, providing data to our endpoints
# ? Instead of creating a static db vari like before, we can instead get a fresh db session on each req
# ? And that by simply adding it to our handler function as an argument to create a session


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI(
    # Server start/stop listener
    lifespan=lifespan_handler,
)

app.include_router(master_router)


@app.get("/", include_in_schema=False)
def start_server():
    return {"detail": "Server is running..."}


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
