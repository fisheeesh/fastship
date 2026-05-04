from time import sleep

from celery import Celery  # type: ignore
from asgiref.sync import async_to_sync
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
import httpx
from pydantic import EmailStr
from app.config import db_settings, notification_settings
from ..utils import TEMPLATE_DIR

_THAIBULKSMS_URL = "https://api-v2.thaibulksms.com/sms"

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


@app.task
def send_email_with_template(
    recipients: list[EmailStr],
    subject: str,
    context: dict,
    template_name: str,
):
    send_message(
        message=MessageSchema(
            recipients=recipients,  # type: ignore
            subject=subject,
            template_body=context,
            subtype=MessageType.html,
        ),
        template_name=template_name,
    )


async def _send_sms_request(to: str, body: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            _THAIBULKSMS_URL,
            headers={
                "accept": "application/json",
                "content-type": "application/x-www-form-urlencoded",
            },
            data={
                "msisdn": to,
                "message": body,
                "sender": notification_settings.THAIBULKSMS_SENDER,
            },
            auth=(
                notification_settings.THAIBULKSMS_API_KEY,
                notification_settings.THAIBULKSMS_API_SECRET,
            ),
        )
        response.raise_for_status()


send_sms_request = async_to_sync(_send_sms_request)


@app.task
def send_sms(to: str, body: str):
    try:
        send_sms_request(to, body)
        print(f"[SMS] Sent successfully to {to}")
    except httpx.HTTPStatusError as e:
        print(f"[SMS] HTTP error {e.response.status_code}: {e.response.text}")
        print(f"[SMS] Message body was: {body}")
    except Exception as e:
        print(f"[SMS] Failed to send to {to}: {repr(e)}")
        print(f"[SMS] Message body was: {body}")


@app.task
def background_task(name: str, data: dict):
    sleep(5)
    return name
