from typing import Union

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import User
from ..utils import generate_access_token
from .base import BaseService


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(BaseService):
    def __init__(self, model: User, session: AsyncSession):
        super().__init__(model, session)

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

        return await self._add(user)

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

        return generate_access_token(
            data={
                "user": {
                    "name": user.name,
                    "id": str(user.id),  # type: ignore
                },
            }
        )
