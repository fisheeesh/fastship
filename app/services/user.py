from typing import Union

from fastapi import BackgroundTasks, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.notification import NotificationService

from ..database.models import User
from ..utils import generate_access_token, generate_url_safe_tokn
from .base import BaseService
from app.config import app_settings


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(BaseService):
    def __init__(self, model: User, session: AsyncSession, tasks: BackgroundTasks):
        super().__init__(model, session)
        self.notification_service = NotificationService(tasks)

    async def _get_by_email(self, email) -> Union[User, None]:
        return await self.session.scalar(
            select(self.model).where(self.model.email == email),  # type: ignore
        )

    async def _add_user(self, data: dict):
        existing_user = await self._get_by_email(data["email"])

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email has been registered. Try again with another email.",
            )

        user_data = dict(data)
        password = user_data.pop("password", None)
        if password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required.",
            )

        user = self.model(
            **user_data,
            password_hash=password_context.hash(password),
        )  # type: ignore

        user = await self._add(user)

        token = generate_url_safe_tokn(
            {
                "email": user.email,  # type: ignore
                "id": user.id,  # type: ignore
            }
        )

        await self.notification_service.send_email_with_template(
            recipients=[user.email],  # type: ignore
            subject="Verify Your Account with FastShip",
            context={
                "username": user.name,  # type: ignore
                "verification_url": f"http://{app_settings.APP_DOMAIN}/user/verify?token={token}",
            },
            template_name="mail_email_verify.html",
        )

        return user

    async def _login(self, email, password) -> str:
        user = await self._get_by_email(email)

        if user is None or not password_context.verify(
            password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid email or password.",
            )

        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified.",
            )

        return generate_access_token(
            data={
                "user": {
                    "name": user.name,
                    "id": str(user.id),  # type: ignore
                },
            }
        )
