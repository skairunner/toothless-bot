import pytest
from toothless.commandrouter import path, match_path


async def simple_command(client, message, chopped):
    return True

@pytest.mark.asyncio
async def test_path_returns_inner():
    result = path('prefix', simple_command)
    assert result.prefix == 'prefix'
    ran = await result(1, 2, 3)
    assert ran is not None
