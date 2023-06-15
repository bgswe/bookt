from time import time
from uuid import UUID

import jwt

from app import settings


class ExpiredToken(Exception):
    ...


class InvalidToken(Exception):
    ...


def get_access_token(client_id: UUID|str):
    return jwt.encode(
        {
            "exp": time() + int(settings.ACCESS_TOKEN_DURATION),
            "client_id": str(client_id),
        },
        settings.ACCESS_TOKEN_SECRET,
        algorithm=settings.HASH_ALGORITHM,
    )


def decode_access_token(token: str):
    try:
        return jwt.decode(
            token.encode("utf-8"), 
            settings.ACCESS_TOKEN_SECRET,
            algorithms=[settings.HASH_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise ExpiredToken
    except jwt.InvalidTokenError:
        raise InvalidToken


def get_refresh_token(client_id: UUID):
    return jwt.encode(
        {
            "exp": time() + int(settings.REFRESH_TOKEN_DURATION),
            "client_id": str(client_id),
        },
        settings.REFRESH_TOKEN_SECRET,
        algorithm=settings.HASH_ALGORITHM,
    )


def decode_refresh_token(token: str):
    try:
        return jwt.decode(
            token.encode("utf-8"), 
            settings.REFRESH_TOKEN_SECRET,
            algorithms=[settings.HASH_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise ExpiredToken
    except jwt.InvalidTokenError:
        raise InvalidToken

