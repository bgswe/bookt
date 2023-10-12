from uuid import uuid4

import pytest

from domain.service.commands import Register


@pytest.mark.asyncio
async def test_register(producer):
    command = Register(
        account_id=uuid4(),
        originator_email="example@email.com",
    )

    await producer.produce(message=command)
