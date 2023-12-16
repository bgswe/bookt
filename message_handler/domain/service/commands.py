from uuid import UUID

from cosmos.domain import Command
from pydantic import EmailStr


class Register(Command):
    account_id: UUID | None = None
    originator_email: EmailStr
