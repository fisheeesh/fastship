from celery import Celery  # type: ignore
from asgiref.sync import async_to_sync
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app.config import db_settings, notification_settings
from ..utils import TEMPLATE_DIR

fast_mail = FastMail(
    ConnectionConfig(
        **notification_settings.model_dump(
            exclude=[
                "THAIBULKSMS_API_KEY",
                "THAIBULKSMS_API_SECRET",
                "THAIBULKSMS_SENDER",
            ],  # type: ignore
        ),
        TEMPLATE_FOLDER=TEMPLATE_DIR,
    )
)

send_message = async_to_sync(fast_mail.send_message)

# $ Inside of celery tasks, only synchronous code is allowed
# $ -> task should be synchronous function
app = Celery(
    "api_tasks",
    # ? Our task queue on which we can add a task and celery will pick up 
    # ? and assign to available worker
    broker=db_settings.REDIS_URL(9),
    # ? A place to store return func resopnse data and send it back to api server
    backend=db_settings.REDIS_URL(9),
)


@app.task
def send_mail(
    recipients: list[str],
    subject: str,
    body: str,
):
    send_message(
        MessageSchema(
            recipients=recipients,  # type: ignore
            subject=subject,
            body=body,
            subtype=MessageType.plain,
        )
    )

    return "Message Sent!"
