import pytest
from toothless.commandrouter import path, match_path


async def simple_command(client, message, chopped):
    return True

async def identity_command(client, message, chopped):
    return chopped

async def foo(c, m, ch):
    return 'foo'

async def bar(c, m, ch):
    return 'bar'

async def barr(c, m, ch):
    return 'barr'

@pytest.mark.asyncio
async def test_path_returns_inner():
    result = path('prefix', simple_command)
    assert result.prefix == 'prefix'
    ran = await result(1, 2, 3)
    assert ran is not None

@pytest.mark.asyncio
async def test_match_matches_multiple():
    paths = [
        path('foo', foo),
        path('bar', bar)
    ]
    result = await match_path(paths, '', '', 'foo')
    assert result == 'foo'
    result = await match_path(paths, '', '', 'bar')
    assert result == 'bar'

@pytest.mark.asyncio
async def test_match_matches_first_one():
    paths = [
        path('bar', bar),
        path('bar', foo)
    ]
    result = await match_path(paths, '', '', 'bar')
    assert result == 'bar'

@pytest.mark.asyncio
async def test_match_requires_trailing_space():
    paths = [
        path('barr', barr),
        path('bar', bar)
    ]
    result = await match_path(paths, '', '', 'bar')
    assert result == 'bar'
    result = await match_path(paths, '', '', 'bar ')
    assert result == 'bar'

@pytest.mark.asyncio
async def test_chopped_calculated_correctly():
    paths = [
        path('state', [
            path('bla', identity_command),
            path('me', identity_command)
        ])
    ]
    result = await match_path(paths, '', '', 'state bla zla')
    assert result == 'zla'
    result = await match_path(paths, '', '', 'state me')
    assert result == ''
