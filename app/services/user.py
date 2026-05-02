from datetime import timedelta
from typing import Union
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException, status
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .notification import NotificationService

from ..database.models import User
from ..utils import (
    decode_url_safe_token,
    generate_access_token,
    generate_url_safe_token,
)
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

    async def verify_email(self, token: str):
        token_data = decode_url_safe_token(token)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token.",
            )

        user = await self._get(UUID(token_data["id"]))
        user.email_verified = True  # type: ignore

        await self._update(user)  # type: ignore

    async def _add_user(self, data: dict, router_prefix: str):
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

        # * Add the use to database and get refreshed data
        user = await self._add(user)
        # * Generate the token with user id
        token = generate_url_safe_token(
            {
                # ? Email can be skipped as not use in our case
                # "email": user.email,  # type: ignore
                "id": str(user.id),  # type: ignore
            }
        )

        # * Send registration email with verification link
        await self.notification_service.send_email_with_template(
            recipients=[user.email],  # type: ignore
            subject="Verify Your Account with FastShip",
            context={
                "username": user.name,  # type: ignore
                "verification_url": f"http://{app_settings.APP_DOMAIN}/{router_prefix}/verify?token={token}",
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

    async def send_password_reset_link(self, email: EmailStr, router_prefix: str):
        user = await self._get_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{router_prefix.title()} not found.",
            )

        token = generate_url_safe_token(
            {
                "id": str(user.id)  # type: ignore
            },
            salt="password-reset",
        )

        await self.notification_service.send_email_with_template(
            recipients=[user.email],  # type: ignore
            subject="FastShip Account Password Reset",
            context={
                "username": user.name,
                "reset_url": f"http://{app_settings.APP_DOMAIN}{router_prefix}/reset-password?token={token}",
            },
            template_name="mail_password_reset.html",
        )

    async def reset_password(self, token: str, password: str):
        token_data = decode_url_safe_token(
            token,
            salt="password-reset",
            expiry=timedelta(days=1),
        )

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token.",
            )

        user = await self._get(UUID(token_data["id"]))  # type: ignore

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found.",
            )

        user.password_hash = password_context.hash(password)

        await self._update(user)
