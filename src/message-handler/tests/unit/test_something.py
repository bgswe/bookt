from uuid import uuid4

import pytest

from domain.service.command_handlers import handle_registration
from domain.service.commands import Register


@pytest.mark.asyncio
async def test_x(producer):
    command = Register(
        account_id=uuid4(),
        originator_email="example@email.com",
    )

    await producer.produce(message=command)
    print("after produce")
