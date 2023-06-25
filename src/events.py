from uuid import UUID

from cosmos.domain import Event


class OrganizationCreated(Event):
    organization_id: UUID
    organization_name: str
    admin_email: str
