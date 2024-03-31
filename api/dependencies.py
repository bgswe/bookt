from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from api import authentication

jwt_bearer_authentication = OAuth2PasswordBearer(
    tokenUrl="/command/login/",
    scheme_name="JWT",
)


async def jwt_bearer(token: str = Depends(jwt_bearer_authentication)):
    try:
        payload = authentication.decode_access_token(token=token)

        return payload
    except authentication.InvalidToken:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="jwt bearer token is expired, acquire a new one through the refresh endpoint",
        )
    except authentication.ExpiredToken:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="jwt bearer token is invalid, please supply a valid token",
        )
