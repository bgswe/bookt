from typing import Annotated
from fastapi import APIRouter, Cookie, Depends, Request, Response, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from authentication import ExpiredToken, InvalidToken, decode_refresh_token, get_access_token, get_refresh_token, is_password_correct


router = APIRouter(
    prefix="/command",
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
            """
            SELECT
                *
            FROM 
                usr
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
            hash=user["password_hash"],
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
