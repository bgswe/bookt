from __future__ import annotations

from enum import StrEnum, auto
from typing import List
from uuid import UUID, uuid4

import bcrypt
from cosmos.domain import AggregateRoot, DomainEvent
from pydantic import Field


class UserRoles(StrEnum):
    APP_ADMIN = auto()
    ACCOUNT_ADMIN = auto()
    ACCOUNT_USER = auto()


class UserRoles(StrEnum):
    APP_ADMIN = auto()
    ACCOUNT_ADMIN = auto()
    ACCOUNT_USER = auto()


class User(AggregateRoot):
    def _mutate(self, event: DomainEvent):
        if isinstance(event, UserCreated):
            self._apply_create(event=event)

    def create(
        self,
        *,
        id: UUID = None,
        account_id: UUID,
        email: str,
        roles: List[UserRoles],
        first_name: str = None,
        last_name: str = None,
    ):
        """Entry point into account creation"""

        if id is None:
            id = uuid4()

        self.mutate(
            event=UserCreated(
                stream_id=id,
                account_id=account_id,
                email=email,
                roles=roles,
                first_name=first_name,
                last_name=last_name,
            )
        )

    def _apply_create(self, event: UserCreated):
        """Initialize a new instance of the User aggregate root"""

        random_password = "password"
        hashed_password = bcrypt.hashpw(
            random_password.encode("utf-8"), bcrypt.gensalt(10)
        )
        hashed_password = hashed_password.decode("utf-8")

        self._initialize(
            id=event.stream_id,
            account_id=event.account_id,
            email=event.email,
            first_name=event.first_name,
            last_name=event.last_name,
            hashed_password=hashed_password,
        )


class UserCreated(DomainEvent):
    account_id: UUID
    email: str
    roles: List[UserRoles]
    first_name: str | None = None
    last_name: str | None = None
