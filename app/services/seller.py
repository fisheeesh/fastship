from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.schemas.seller import SellerCreate
from ..database.models import Seller
from .user import UserService

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SellerService(UserService):
    def __init__(self, session: AsyncSession):
        super().__init__(Seller, session)  # type: ignore

    async def add(self, seller_create: SellerCreate) -> Seller:
        return await self._add_user(
            seller_create.model_dump(),
        )  # type: ignore

    async def login(self, email: str, password: str) -> str:
        return await self._login(email, password)
