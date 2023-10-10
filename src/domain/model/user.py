from __future__ import annotations

from typing import List
from uuid import UUID

import bcrypt
from cosmos.domain import AggregateRoot, DomainEvent


class User(AggregateRoot):
    def _mutate(self, event: DomainEvent):
        if isinstance(event, UserCreated):
            self._apply_create(event=event)

    def create(
        self, *, id: UUID = None, email: str, roles: List[str], first_name: str = None
    ):
        """Entry point into account creation"""

        self.mutate(
            event=UserCreated(
                stream_id=id,
                email=email,
            )
        )

    def _apply_create(self, event: UserCreated):
        """Call AggregateRoot.__init__ with the attributes of the Account"""

        random_password = "password"
        hashed_password = bcrypt.hashpw(
            random_password.encode("utf-8"), bcrypt.gensalt(10)
        )
        hashed_password = hashed_password.decode("utf-8")

        self._initialize(
            id=event.stream_id,
            email=event.email,
            hashed_password=hashed_password,
        )


class UserCreated(DomainEvent):
    account_id: UUID
    email: str
    roles: List[str]
    first_name: str = None
    last_name: str = None
