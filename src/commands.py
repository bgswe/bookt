from uuid import UUID

from cosmos.domain import Command
from pydantic import EmailStr


class Signup(Command):
    organization_id: UUID | None = None
    organization_name: str
    admin_email: EmailStr
