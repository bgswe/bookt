from enum import StrEnum, auto
from typing import List
from uuid import UUID

import bcrypt
from cosmos.domain import AggregateRoot, Entity

from events import OrganizationCreated


class Role(StrEnum):
    SAAS_ADMIN = auto()
    SAAS_SUPPORT = auto()
    ORGANIZATION_ADMIN = auto()
    ORGANIZATION_USER = auto()


class User(AggregateRoot):
    email: str
    first_name: str | None
    last_name: str | None
    roles: List[Role]
    hashed_password: str
    organization_id: str

    @classmethod
    def create(
        cls,
        *,
        id: UUID = None,
        email: str,
        password: str,
        organization_id: UUID,
        roles: List[Role] = None,
        first_name: str = None,
        last_name: str = None,
    ):
        if roles is None:
            roles = [Role.ORGANIZATION_ADMIN]

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
            organization_id=organization_id,
        )


class Organization(AggregateRoot):
    name: str

    @classmethod
    def create(
        cls,
        *,
        id: UUID = None,
        name: str,
        admin_email: str,
    ):
        organization = Entity.create_entity(
            cls=cls,
            id=id,
            name=name,
        )

        organization.new_event(
            OrganizationCreated(
                organization_id=organization.id,
                organization_name=organization.name,
                admin_email=admin_email,
            )
        )

        return organization
