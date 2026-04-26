from typing import Union

from fastapi import HTTPException, status
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col
from ..utils import generate_access_token

from ..api.schemas.seller import SellerCreate
from ..database.models import Seller

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SellerService:
    def __init__(self, session: AsyncSession):
        # * Get database session to perform database operations
        self.session = session

    async def get(self, email: EmailStr) -> Union[Seller, None]:
        result = await self.session.execute(
            select(Seller).where(col(Seller.email) == email),
        )

        seller = result.scalar()

        return seller

    async def add(self, credentials: SellerCreate) -> Seller:
        existing_seller = await self.get(credentials.email)

        if existing_seller:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email has been registered. Try again with another email.",
            )

        seller = Seller(
            **credentials.model_dump(exclude=["password"]),  # type: ignore
            password_hash=password_context.hash(credentials.password),
        )
        self.session.add(seller)
        await self.session.commit()
        await self.session.refresh(seller)

        return seller

    async def login(self, email: str, password: str) -> str:
        # * Get seller from db with provided email
        seller = await self.get(email)

        # * Check if seller is existed or not
        if seller is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seller with provided email is not found.",
            )

        password_correct = password_context.verify(password, seller.password_hash)

        # * Check password is correct or not
        if not password_correct:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password. Please try again!",
            )

        # * If all passed, generate token
        token = generate_access_token(
            data={
                "user": {
                    "name": seller.name,
                    "id": seller.id,
                },
            }
        )

        return token
