from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import RedirectResponse
from scalar_fastapi import get_scalar_api_reference

from .services.notification import NotificationService

from .api.router import master_router
from .database.session import create_db_tables


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI(
    # * server start/stop listener
    lifespan=lifespan_handler,
)

app.include_router(master_router)


@app.get("/mail")
async def send_test_mail(tasks: BackgroundTasks):
    await NotificationService(tasks).send_email(
        recipients=["koswam779@gmail.com"],
        subject="Test Mail Coming Through Once.",
        body="You shouldn't be interested in every body...",
    )
    return {"detail": "Mail has been sent!"}


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


### Custom Response
@app.get("/custom", response_class=RedirectResponse)
def get_custom_reponse():
    return "http://localhost:8000/custom-new"


@app.get("/custom-new")
def get_new_data():
    return "NEW CUSTOM RESPON SE!"
