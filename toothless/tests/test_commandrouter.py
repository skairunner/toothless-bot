import mock
import pytest
from toothless import commandrouter as cr
from toothless import tokens as tok
import asyncio

def new_curry_inner(inner):
    async def newinner(*args, **kwargs):
        return inner(*args, **kwargs)
    return newinner

def run(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

# Patches out curry_inner to direclty return result
def path(route, inner):
    with mock.patch('toothless.commandrouter.curry_inner', new_curry_inner):
        return cr.Path(route, inner)

def test_match_prototokens_to_tokens_success():
    # Case 1: Ending with a Remainder proto
    prototokens = [tok.RemainderProto('nom')]
    tokens = ['first', 'second', 'third']
    results, matchcount = cr.match_prototokens_to_tokens(prototokens, tokens)
    assert matchcount == (1, 3)
    assert len(results) == 1
    assert results[0] == 'first second third'
    # Case 2: Equal tokens to paths
    prototokens = [tok.IntProto('int'), tok.StringProto('str')]
    tokens = ['143', 'a s d f']
    results, matchcount = cr.match_prototokens_to_tokens(prototokens, tokens)
    assert matchcount == (2, 2)
    assert results[0] == 143
    assert results[1] == 'a s d f'
    # Case 3: More tokens than paths
    tokens = ['1', 'a', 'b']
    results, matchcount = cr.match_prototokens_to_tokens(prototokens, tokens)
    assert matchcount == (2, 2)
    assert results[1] == 'a'

def test_match_prototokens_toomanyproto():
    prototokens = [tok.IntProto('int'), tok.IntProto('int')]
    tokens = ['1']
    with pytest.raises(cr.PathMismatch):
        cr.match_prototokens_to_tokens(prototokens, tokens)

# Not all tokens before the Remainder token match
def test_match_prototokens_remainder_not_enough():
    prototokens = [tok.IntProto('int'), tok.RemainderProto('r')]
    tokens = ['asd']
    with pytest.raises(cr.PathMismatch):
        cr.match_prototokens_to_tokens(prototokens, tokens)

def test_nested_path_matching():
    paths = [
        path(
            'foo',
            [path('bar', lambda x, y: 'foo bar'), path('baz', lambda x, y: 'foo baz')]
        )
    ]
    tokens = ['foo', 'baz']
    result = run(cr.match_path(paths, tokens, {}, {}))
    assert result == 'foo baz'

def test_nested_path_failure_returns_to_top():
    paths = [
        path('foo', [path('fuzz', lambda x, y: 'foo fuzz')]),
        path('foo', lambda x, y: 'foo')
    ]
    tokens = ['foo']
    assert run(cr.match_path(paths, tokens, {}, {})) == 'foo'

# a path that is '' should always pass thru
def test_empty_prototoken_passes_through():
    # import rpdb2; rpdb2.start_embedded_debugger('1234')
    paths = [
        path('', [path('foo', lambda x, y: 'foo')])
    ]
    tokens = ['foo']
    assert run(cr.match_path(paths, tokens, {}, {})) == 'foo'
