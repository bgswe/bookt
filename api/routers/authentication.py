from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import jwt_bearer
from api.settings import APPLICATION_NAME

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """OAuth2 compliant user login"""

    async with request.app.pool.acquire() as connection:
        user = await connection.fetchrow(
            f"""
            SELECT
                *
            FROM
                {APPLICATION_NAME}_user
            WHERE
                email = $1;
            """,
            form_data.username,
        )

        failed_auth_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

        if user is None:
            raise failed_auth_exception

        if not is_password_correct(
            password=form_data.password,
            hash=user["password"],
        ):
            raise failed_auth_exception

        client_id = str(user["id"])

        access_token = get_access_token(client_id=client_id)
        refresh_token = get_refresh_token(client_id=client_id)

        # set refresh token as httpOnly cookie, used on backend when access expires
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

        return {"access_token": access_token}


@router.get("/refresh")
async def refresh(refresh_token: Annotated[str, Cookie()]):
    """Provides authenticated clients w/ new access token"""

    try:
        payload = decode_refresh_token(token=refresh_token)
        access_token = get_access_token(client_id=payload["client_id"])

        # TODO: should this command also refresh the refresh token?
        # a configurable policy related to refresh token settings
        # would be a powerful option

        return {"access_token": access_token}

    except (ExpiredToken, InvalidToken):
        # unsure if both exceptions should be handled together
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="refresh token expired, please reauthenticate",
        )


@router.post("/logout")
async def logout(refresh_token: Annotated[str, Cookie()], response: Response):
    """Revokes refresh token to end user's session

    refresh_token cookie declared such that a 422 response is returned if it
    does not exist on the incoming request.
    """

    response.delete_cookie("refresh_token")

    return {"detail": "user logged out"}


@router.get("/dummyneedsauth")
async def dummyneedsauth(payload=Depends(jwt_bearer)):
    """Serves as a dummy endpoint wh/ requires auth, providing coverage to the auth flow"""

    print(payload)

    return {"detail": "dummy success"}
