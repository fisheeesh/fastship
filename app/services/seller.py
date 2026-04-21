from datetime import datetime, timedelta

from fastapi import HTTPException, status
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlmodel import col
from ..api.schemas.seller import SellerCreate
from ..database.models import Seller
from ..config import security_settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SellerService:
    def __init__(self, session: AsyncSession):
        # * Get database session to perform database operations
        self.session = session

    async def add(self, credentials: SellerCreate) -> Seller:
        result = await self.session.execute(
            select(Seller).where(col(Seller.email) == credentials.email),
        )

        existing_seller = result.scalar()

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
        result = await self.session.execute(
            select(Seller).where(col(Seller.email) == email),
        )

        seller = result.scalar()

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
        token = jwt.encode(
            payload={
                "user": {"name": seller.name, "email": seller.email},
                "exp": datetime.now() + timedelta(days=1),
            },
            algorithm=security_settings.JWT_ALGORITHM,
            key=security_settings.JWT_SECRET,
        )

        return token
