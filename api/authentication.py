from time import time
from uuid import UUID

import jwt

from api.settings import settings


class ExpiredToken(Exception):
    ...


class InvalidToken(Exception):
    ...


def get_access_token(client_id: UUID | str):
    return jwt.encode(
        {
            "exp": time() + settings.access_token_duration,
            "client_id": str(client_id),
        },
        settings.access_token_secret,
        algorithm=settings.hash_algorithm,
    )


def decode_access_token(token: str):
    try:
        return jwt.decode(
            token.encode("utf-8"),
            settings.access_token_secret,
            algorithms=[settings.hash_algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise ExpiredToken
    except jwt.InvalidTokenError:
        raise InvalidToken


def get_refresh_token(client_id: UUID):
    return jwt.encode(
        {
            "exp": time() + settings.refresh_token_duration,
            "client_id": str(client_id),
        },
        settings.refresh_token_secret,
        algorithm=settings.hash_algorithm,
    )


def decode_refresh_token(token: str):
    try:
        return jwt.decode(
            token.encode("utf-8"),
            settings.refresh_token_secret,
            algorithms=[settings.hash_algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise ExpiredToken
    except jwt.InvalidTokenError:
        raise InvalidToken
