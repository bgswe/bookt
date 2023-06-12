import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer


jwt_bearer_authentication = OAuth2PasswordBearer(
    tokenUrl="/command/login/",
    scheme_name="JWT",
)

async def jwt_bearer(token: str = Depends(jwt_bearer_authentication)):
    try:
        jwt.decode(
            token.encode("utf-8"), "SOME_SECRET_VALUE", algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="jwt bearer token is expired, acquire a new one through the refresh endpoint",
        )
    except jwt.InvalidTokenError as e:
        print(token, e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="jwt bearer token is invalid, please supply a valid token"
        )
