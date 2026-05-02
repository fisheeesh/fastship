from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from twilio.rest import Client  # type: ignore

from app.config import notification_settings

from ..utils import TEMPLATE_DIR


class NotificationService:
    def __init__(self, tasks: BackgroundTasks):
        self.tasks = tasks
        self.fastmail = FastMail(
            ConnectionConfig(
                **notification_settings.model_dump(
                    exclude=["TWILIO_SID", "TWILIO_AUTH_TOKEN", "TWILIO_NUMBER"]  # type: ignore
                ),
                TEMPLATE_FOLDER=TEMPLATE_DIR,
            )
        )
        self.twilio_client = Client(
            notification_settings.TWILIO_SID,
            notification_settings.TWILIO_AUTH_TOKEN,
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
            await self.twilio_client.messages.create_async(
                from_=notification_settings.TWILIO_NUMBER,
                to=to,
                body=body,
            )
            print(f"[SMS] Sent to {to}: {body}")
        except Exception as e:
            print(f"[SMS] Failed to send to {to}: {e}")
            print(f"[SMS] Message body was: {body}")

    async def send_sms(self, to: str, body: str):
        self.tasks.add_task(self._send_sms_task, to, body)
