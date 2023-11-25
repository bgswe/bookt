from uuid import uuid4

import pytest

from domain.service.commands import Register


@pytest.mark.asyncio
async def test_register(producer):
    account_id = uuid4()

    command = Register(
        account_id=account_id,
        originator_email="example@email.com",
    )

    await producer.produce(message=command)

    events = producer.container.outbox()._outbox
    for e in events:
        print(e)
