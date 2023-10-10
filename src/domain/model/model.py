from enum import StrEnum, auto
from uuid import UUID

import bcrypt
from cosmos.domain import AggregateRoot, Event
from domain.events import AccountCreated


class Role(StrEnum):
    SAAS_ADMIN = auto()
    SAAS_SUPPORT = auto()
    ACCOUNT_ADMIN = auto()
    ACCOUNT_USER = auto()


class User(AggregateRoot):
    email: str
    first_name: str | None
    last_name: str | None
    roles: List[Role]
    hashed_password: str
    account_id: str

    @classmethod
    def create(
        cls,
        *,
        id: UUID = None,
        email: str,
        password: str,
        account_id: UUID,
        roles: List[Role] = None,
        first_name: str = None,
        last_name: str = None,
    ):
        if roles is None:
            roles = [Role.ACCOUNT_ADMIN]

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(10))
        hashed_password = hashed_password.decode("utf-8")

        return Entity.create_entity(
            cls=cls,
            id=id,
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            roles=roles,
            account_id=account_id,
        )
