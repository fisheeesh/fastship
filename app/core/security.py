from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer

from app.utils import decode_access_token

oauth2_scheme_seller = OAuth2PasswordBearer(tokenUrl="/seller/token")
oauth2_scheme_partner = OAuth2PasswordBearer(tokenUrl="/partner/token")


# ? That's what we will done if we are not using OAuth2PasswordBearer
class AccessTokenBearer(HTTPBearer):
    async def __call__(self, request):
        auth_credentials = await super().__call__(request)
        token = auth_credentials.credentials

        token_data = decode_access_token(token)

        if token_data is None:
            raise HTTPException(
                status=status.HTTP_401_UNAUTHORIZED, detail="Not authorized!"
            )

        return token_data


access_token_bearer = AccessTokenBearer()

Annotated[dict, Depends(access_token_bearer)]
