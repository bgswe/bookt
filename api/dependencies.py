from bookt_domain.model.authentication import (
    ExpiredToken,
    InvalidToken,
    decode_access_token,
)
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

jwt_bearer_authentication = OAuth2PasswordBearer(
    tokenUrl="/command/login/",
    scheme_name="JWT",
)


async def jwt_bearer(token: str = Depends(jwt_bearer_authentication)):
    try:
        payload = decode_access_token(token=token)

        return payload
    except InvalidToken:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="jwt bearer token is expired, acquire a new one through the refresh endpoint",
        )
    except ExpiredToken:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="jwt bearer token is invalid, please supply a valid token",
        )
