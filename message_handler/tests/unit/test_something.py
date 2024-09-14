from uuid import uuid4

import pytest
from bookt_domain.model.commands import RegisterTenant


@pytest.mark.asyncio
async def test_register_tenant(producer):
    tenant_id = uuid4()

    command = RegisterTenant(
        tenant_id=tenant_id,
        tenant_name="Some Tenant Name",
    )

    await producer.produce(message=command)

    events = producer.container.outbox()._outbox
    for e in events:
        print(e)
