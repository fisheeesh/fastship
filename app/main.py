from contextlib import asynccontextmanager
from datetime import datetime

from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import RedirectResponse
from scalar_fastapi import get_scalar_api_reference

from app.api.tag import APITag
from app.worker.tasks import background_task, send_mail
from app.core.exceptions import add_exception_handlers

from .services.notification import NotificationService

from .api.router import master_router
from .database.session import create_db_tables


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield


description = """
Delivery Management System for sellers and delivery agents.
### Seller
- Submit shipment efforlessly
- Share tracking links with customers

### Delivery Agent
- Auto accept shipments
- Track and update shipment status
- Email and SMS notifications
"""
app = FastAPI(
    # * server start/stop listener
    lifespan=lifespan_handler,
    title="FastShip",
    description=description,
    docs_url=None,
    redoc_url=None,
    version="0.1.0",
    terms_of_service="https://fastship.com/terms",
    contact={
        "name": "FastShip Support",
        "url": "https://fastship.com/support",
        "email": "support@fastship.com",
    },
    openapi_tags=[
        {
            "name": APITag.SHIPMENT,
            "description": "Operations related to shipments."
        },
        {
            "name": APITag.SELLER,
            "description": "Operations related to seller."
        },
        {
            "name": APITag.PARTNER,
            "description": "Operations related to delivery partner."
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_methods=["*"],
)

app.include_router(master_router)

# ? Exception handlers
add_exception_handlers(app)


@app.get("/mail")
async def send_test_mail(tasks: BackgroundTasks):
    await NotificationService(tasks).send_email(
        recipients=["koswam779@gmail.com"],
        subject="Test Mail Coming Through Once.",
        body="You shouldn't be interested in every body...",
    )
    return {"detail": "Mail has been sent!"}


@app.get("/docs", include_in_schema=False)
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


@app.get("/test")
def test():
    send_mail.delay(
        recipients=["koswam779@gmail.com"],
        subject="hi",
        body="hi",
    )

    now = datetime.now()
    background_task.delay(
        f"Background Task {now.second}",
        data={
            "min": now.minute,
            "sec": now.second,
        },
    )
