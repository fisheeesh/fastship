from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
import httpx

from app.config import notification_settings

from ..utils import TEMPLATE_DIR

_THAIBULKSMS_URL = "https://api-v2.thaibulksms.com/sms"


class NotificationService:
    def __init__(self, tasks: BackgroundTasks):
        self.tasks = tasks
        self.fastmail = FastMail(
            ConnectionConfig(
                **notification_settings.model_dump(
                    exclude=[
                        "THAIBULKSMS_API_KEY",
                        "THAIBULKSMS_API_SECRET",
                        "THAIBULKSMS_SENDER",
                    ]  # type: ignore
                ),
                TEMPLATE_FOLDER=TEMPLATE_DIR,
            )
        )

    async def send_email(
        self,
        recipients: list[EmailStr],
        subject: str,
        body: str,
    ):
        self.tasks.add_task(
            self.fastmail.send_message,
            message=MessageSchema(
                recipients=recipients,  # type: ignore
                subject=subject,
                body=body,
                subtype=MessageType.plain,
            ),
        )

    async def send_email_with_template(
        self,
        recipients: list[EmailStr],
        subject: str,
        context: dict,
        template_name: str,
    ):
        self.tasks.add_task(
            self.fastmail.send_message,
            message=MessageSchema(
                recipients=recipients,  # type: ignore
                subject=subject,
                template_body=context,
                subtype=MessageType.html,
            ),
            template_name=template_name,
        )

    async def _send_sms_task(self, to: str, body: str):
        try:
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
                print(f"[SMS] Sent to {to}: {body}")
        except httpx.HTTPStatusError as e:
            print(f"[SMS] Failed to send to {to}: {e}")
            print(f"[SMS] Response body: {e.response.text}")
            print(f"[SMS] Message body was: {body}")
        except Exception as e:
            print(f"[SMS] Failed to send to {to}: {e}")
            print(f"[SMS] Message body was: {body}")

    async def send_sms(self, to: str, body: str):
        self.tasks.add_task(self._send_sms_task, to, body)
