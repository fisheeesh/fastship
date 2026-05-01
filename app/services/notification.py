from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from ..config import notification_settings


class NotificationService:
    def __init__(self, tasks: BackgroundTasks):
        self.fastmail = FastMail(
            ConnectionConfig(
                **notification_settings.model_dump(),
            )
        )
        self.tasks = tasks

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
